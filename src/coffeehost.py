from datetime import date, timedelta
import calendar
import json
import os
import holidays
import subprocess

dirpath = os.path.dirname(__file__)


def get_weekdays(year, month, exclude=[]):
    weekdays = []
    mycal = calendar.monthcalendar(year, month)

    for w in mycal:
        for d in w:
            if d == 0:
                continue

            day = date(year, month, d)
            i = day.weekday()
            if calendar.day_name[i] in ["Saturday", "Sunday"] + exclude:
                continue
            weekdays.append(day)
    return weekdays


class Host(object):
    def __init__(self, name="", email=""):
        self.name = name
        name_split = name.split(" ")
        self.first = " ".join(name_split[:-1])
        self.last = name_split[-1]
        self.email = email
        self.restriction = []
        self.hostdate = []

    def __repr__(self):
        out = f"{self.last} [{len(self.hostdate)}]:"
        for mydate in sorted(self.hostdate):
            out += f" {mydate}"
        return out

    def add_restriction(self, d1, d2):
        """add restriction

        Parameter
        ---------
        restriction : slice of date
        """
        self.restriction.append([d1, d2])

    def test_available(self, date):
        okay = True
        for r in self.restriction:
            if (date >= r[0]) & (date <= r[1]):
                okay = False
        return okay

    def add_date(self, date):
        if self.test_available(date):
            self.hostdate.append(date)
            return True
        else:
            return False

    def clean_date(self):
        self.hostdate = []

    def to_json(self):
        mydict = dict()
        for k, v in self.__dict__.items():
            mydict[k] = v
        mydict["hostdate"] = [d.isoformat() for d in mydict["hostdate"]]
        mydict["restriction"] = [
            [d1.isoformat(), d2.isoformat()] for (d1, d2) in mydict["restriction"]
        ]
        return json.dumps(mydict, indent=4)

    def from_json(self, myjson):
        mydict = json.loads(myjson)
        self.from_dict(mydict)

    def from_dict(self, mydict):
        mydict["hostdate"] = [date.fromisoformat(d) for d in mydict["hostdate"]]
        mydict["restriction"] = [
            [date.fromisoformat(d1), date.fromisoformat(d2)]
            for (d1, d2) in mydict["restriction"]
        ]
        self.__dict__ = mydict


class Hosts(object):
    def __init__(self):
        self.hosts = dict()
        self.dates = []
        self.set_holidays()

    def __getitem__(self, key):
        return self.hosts[key]

    def __setitem__(self, key, value):
        self.hosts[key] = value

    def clean(self):
        for n, h in self.hosts.items():
            h.clean_date()

    def set_holidays(self):
        self.holidays = holidays.US()

    def add_dates(self, dates):
        self.dates += dates

    def assign_dates(self, verbose=True):
        from itertools import cycle
        import numpy as np

        self.clean()
        hiter = cycle(self.hosts)
        mylist = [wd for wd in np.unique(self.dates)]
        while mylist:
            wd = mylist.pop()
            if wd in self.holidays:
                if verbose:
                    print(f"{wd} is {self.holidays.get(wd)}")
            else:
                assigned = False
                while not assigned:
                    h = self.hosts[next(hiter)]
                    assigned = h.add_date(wd)
                    if verbose and assigned:
                        print(f"{wd} is assigned to {h.name}")

    def show(self):
        for n, h in self.hosts.items():
            print(h)

    def find_host(self, date):
        for n, h in self.hosts.items():
            if date in h.hostdate:
                return h
        return False

    def to_json(self, fname, overwrite=True):
        if overwrite:
            if os.path.isfile(fname):
                os.remove(fname)
        with open(fname, "a") as fp:
            outstr = ["["]
            for n, h in self.hosts.items():
                outstr.append(h.to_json())
                outstr.append(",")
            outstr[-1] = "]"
            fp.write("".join(outstr))

    def from_json(self, fname):
        with open(fname, "r") as fp:
            myjson = json.load(fp)
            for h_json in myjson:
                h = Host()
                h.from_dict(h_json)
                self.hosts[h.last.lower()] = h

    def get_email_list(self):
        for n, v in self.hosts.items():
            print(f"{v.name}<{v.email}>")

    def generate_reminder(
        self,
        today=date.today(),
        reminder=True,
        send=False,
        basedir=os.path.join(dirpath, "../"),
    ):
        if not os.path.isdir(os.path.join(basedir, "emails")):
            os.mkdir(os.path.join(basedir, "emails"))

        tomorrow = today + timedelta(days=1)

        # find tomorrow host
        h = self.find_host(tomorrow)
        if h and reminder and hasattr(h, "email"):
            self.write_daily_reminder(h, tomorrow, send=send)

        # find all for next week
        # today = today - timedelta(days=1)
        if calendar.day_name[today.weekday()] == "Sunday":
            dlist = [today + timedelta(days=i) for i in range(1, 6)]
            hlist = [self.find_host(d) for d in dlist]
            if reminder:
                self.write_weekly_reminder(dlist, hlist, send=send)

    def write_daily_reminder(
        self, h, day, send=False, basedir=os.path.join(dirpath, "../")
    ):
        with open(f"{basedir}/templates/daily_reminder.txt", "r") as fp:
            remindertxt = fp.read()
        outfname = f"{basedir}/emails/reminder_{h.last.lower()}_{day.isoformat()}.txt"
        with open(outfname, "w") as fp:
            reminder = remindertxt.format(
                fullname=h.name,
                email=h.email,
                name=h.first,
                day=calendar.day_name[day.weekday()],
                date=day.isoformat(),
            )
            fp.write(reminder)
            if send:
                print(f"daily reminder is sent to {h.email}")
                p = subprocess.Popen(["sendmail", "-t", "-oi"], stdin=subprocess.PIPE)
                p.communicate(reminder.encode("utf-8"))

    def write_weekly_reminder(
        self, dlist, hlist, send=False, basedir=os.path.join(dirpath, "../")
    ):
        with open(f"{basedir}/templates/weekly_reminder.txt", "r") as fp:
            remindertxt = fp.read()
        outfname = f"{basedir}/emails/reminder_{dlist[0].isoformat()}.txt"

        emails = []
        names = []
        days = dict()
        hosts = dict()
        for i, (d, h) in enumerate(zip(dlist, hlist)):
            days[f"day{i+1}"] = d.isoformat()
            if h and hasattr(h, "email"):
                emails.append(f"{h.name}<{h.email}>")
                names.append(f"{h.first}")
                hosts[f"host{i+1}"] = h.first
            else:
                try:
                    hosts[f"host{i+1}"] = f"no astrocoffee ({h.name})"
                except AttributeError:
                    hosts[f"host{i+1}"] = f"no astrocoffee ({self.holidays.get(d)})"

        emails = set(emails)
        names = set(names)

        kwargs = dict(emails=",".join(emails), names=", ".join(names))
        kwargs.update(days)
        kwargs.update(hosts)
        with open(outfname, "w") as fp:
            reminder = remindertxt.format(**kwargs)
            fp.write(reminder)
            if send:
                for email in emails:
                    print(f"weekly reminder is sent to {email}")
                    p = subprocess.Popen(
                        ["sendmail", "-t", "-oi"], stdin=subprocess.PIPE
                    )
                    p.communicate(reminder.encode("utf-8"))

    def assignment_email(self, basedir=os.path.join(dirpath, "../")):
        if not os.path.isdir(os.path.join(basedir, "emails")):
            os.mkdir(os.path.join(basedir, "emails"))
        with open(f"{basedir}/templates/assignment.txt", "r") as fp:
            remindertxt = fp.read()
            for day, h in self.hosts.items():
                if not hasattr(h, "email"):
                    continue
                outfname = f"{basedir}/emails/assignment_{h.last.lower()}.txt"
                with open(outfname, "w") as fp:
                    reminder = remindertxt.format(
                        fullname=h.name,
                        email=h.email,
                        name=h.first,
                        dates="\n".join([d.isoformat() for d in sorted(h.hostdate)]),
                    )
                    fp.write(reminder)
                # print(f"cat {outfname} | sendmail -t {h.email}")

    def output_calendar(self, year, month, basedir=os.path.join(dirpath, "../")):
        if not os.path.isdir(os.path.join(basedir, "docs/calendar")):
            os.mkdir(os.path.join(basedir, "docs/calendar"))
        c = calendar.Calendar(calendar.SUNDAY)
        mycal = c.monthdayscalendar(year, month)

        fp = open(f"{basedir}/docs/calendar/calendar_{month:02d}.md", "w")
        fp.write(f"# {year}-{month}\n\n")
        wstr = "|"
        for i in range(7):
            day = calendar.day_abbr[(i + calendar.SUNDAY) % 7]
            wstr += f"<div style='max-width:100px;width:100px'><p>{day}</p></div>|"
        fp.write(wstr + "\n")

        wstr = "|"
        for day in calendar.day_name:
            wstr += f":-:|"
        fp.write(wstr + "\n")

        unassigned = []
        for w in mycal:
            wstr = "|"
            for d in w:
                if d == 0:
                    wstr += "<p><br/><br/></p> |"
                else:
                    wd = date(year, month, d)
                    h = self.find_host(wd)
                    if h:
                        wstr += f"<p align='left'>{d}</p>"
                        if len(h.first) > 7:
                            wstr += f"<p>{h.first}<br/> {h.last}</p>"
                        else:
                            wstr += f"<p>{h.name}<br/><br/></p>"
                    elif wd in self.holidays:
                        wstr += f"<p align='left'>{d}</p>"
                        # wstr += color_text(self.holidays.get(wd), "")
                        wstr += f"<p>{self.holidays.get(wd)}</p>"
                        if len(self.holidays.get(wd)) < 12:
                            wstr += "<br/><br/>"
                        else:
                            wstr += "<br/>"
                    else:
                        wstr += f"<p align='left'>{d}</p>"

                        if not calendar.day_name[wd.weekday()] in [
                            "Saturday",
                            "Sunday",
                        ]:
                            unassigned.append(wd.isoformat())
                            wstr += color_text("Unassigned", "red") + "<br/><br/>"
                        else:
                            wstr += "<p><br/><br/></p>"
                    wstr += "|"

            # wstr += "\n"
            fp.write(wstr + "\n")
        fp.close()
        print(
            f"{len(unassigned)} unassgined dates in {calendar.month_name[month]} :",
            ",".join(unassigned),
        )


def color_text(text, color):
    return f"<span style='color:{color}'>{text}</span>"
