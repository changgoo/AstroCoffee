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
        out = f"{self.first} {self.last} [{len(self.hostdate)}]:"
        for mydate in sorted(self.hostdate):
            out += f" {mydate}"
        return out

    def __add__(self, h2):
        if self.name == h2.name:
            r1 = list(set([r[0] for r in self.restriction + h2.restriction]))
            r2 = list(set([r[1] for r in self.restriction + h2.restriction]))
            hd = list(set([d for d in self.hostdate + h2.hostdate]))
            self.restriction = [r for r in zip(r1, r2)]
            self.hostdate = [d for d in hd]
            return self
        else:
            raise TypeError(f"Two host names do not match {self.name} and {h2.name}")

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

    def __add__(self, hosts2):
        for n, h in hosts2.hosts.items():
            if n in self.hosts:
                self.hosts[n] += h
            else:
                self.hosts[n] = h
        return self

    def clean(self):
        for n, h in self.hosts.items():
            h.clean_date()

    def set_holidays(self):
        self.holidays = holidays.US()

    def add_dates(self, dates):
        self.dates = sorted(list(set(self.dates + dates)))

    def exclude_dates(self, dates):
        self.dates = sorted(list(set(self.dates) - set(dates)))

    def assign_dates(self, verbose=True):
        from itertools import cycle
        import numpy as np

        self.clean()
        hiter = cycle(self.hosts)
        mylist = [wd for wd in np.unique(self.dates)]
        while mylist:
            wd = mylist.pop()
            #            if wd in self.holidays:
            #                if verbose:
            #                    print(f"{wd} is {self.holidays.get(wd)}")
            #            else:
            assigned = False
            while not assigned:
                h = self.hosts[next(hiter)]
                assigned = h.add_date(wd)
                if verbose and assigned:
                    print(f"{wd} is assigned to {h.name}")

    def show(self):
        for n, h in self.hosts.items():
            print(h)

    def showlist(self):
        for n, h in self.hosts.items():
            print(h.name)

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
        send=False,
        basedir=os.path.join(dirpath, "../"),
    ):
        if not os.path.isdir(os.path.join(basedir, "emails")):
            os.mkdir(os.path.join(basedir, "emails"))

        tomorrow = today + timedelta(days=1)

        # find tomorrow host
        h = self.find_host(tomorrow)
        if h and hasattr(h, "email"):
            self.write_daily_reminder(h, tomorrow, send=send)

        # find all for next week
        # today = today - timedelta(days=1)
        if calendar.day_name[today.weekday()] == "Saturday":
            dlist = [today + timedelta(days=i) for i in range(2, 7)]
            hlist = [self.find_host(d) for d in dlist]
            self.write_weekly_reminder(hlist, dlist, send=send)

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
        with open(outfname, "r") as fp:
            if send:
                print(f"daily reminder is sent to {h.email}")
                subprocess.run(["sendmail", "-t", "-oi"], stdin=fp)
            else:
                print(reminder)

    def write_weekly_reminder(
        self, hlist, dlist, send=False, basedir=os.path.join(dirpath, "../")
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

        kwargs = dict(names=", ".join(names))
        kwargs.update(days)
        kwargs.update(hosts)

        email = "Chang-Goo Kim<changgoo@princeton.edu>"
        # for email in emails:
        kwargs.update(emails=", ".join(emails), email=email)
        with open(outfname, "w") as fp:
            reminder = remindertxt.format(**kwargs)
            fp.write(reminder)
        with open(outfname, "r") as fp:
            if send:
                print(f"weekly reminder is sent to {emails}")
                subprocess.run(["sendmail", "-t", "-oi"], stdin=fp)
            else:
                print(reminder)

    def assignment_email(self, period="2023_4", basedir=os.path.join(dirpath, "../")):
        if not os.path.isdir(os.path.join(basedir, "emails")):
            os.mkdir(os.path.join(basedir, "emails"))
        with open(f"{basedir}/templates/assignment.txt", "r") as fp:
            remindertxt = fp.read()
            for day, h in self.hosts.items():
                if not hasattr(h, "email"):
                    continue
                outfname = f"{basedir}/emails/assignment_{period}_{h.last.lower()}.txt"
                with open(outfname, "w") as fp:
                    reminder = remindertxt.format(
                        fullname=h.name,
                        email=h.email,
                        name=h.first,
                        dates="\n".join([d.isoformat() for d in sorted(h.hostdate)]),
                    )
                    fp.write(reminder)
                print(f"cat {outfname} | sendmail -t -oi")

    def output_calendar(self, year, month, num=0, basedir=os.path.join(dirpath, "../")):
        if not os.path.isdir(os.path.join(basedir, "docs/calendar")):
            os.mkdir(os.path.join(basedir, "docs/calendar"))
        c = calendar.Calendar(calendar.SUNDAY)
        mycal = c.monthdayscalendar(year, month)

        fp = open(
            f"{basedir}/docs/calendar/calendar_{num:02d}_{month:02d}_{year}.md", "w"
        )
        fp.write(f"# {year}-{month}\n\n")
        wstr = "|"
        for i in range(7):
            day = calendar.day_abbr[(i + calendar.SUNDAY) % 7]
            wstr += f"<div style='max-width:100px;width:100px'><p>{day}</p></div>|"
        fp.write(wstr + "\n")

        wstr = "|"
        for day in calendar.day_name:
            wstr += ":-:|"
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
                    wstr += f"<p align='left'>{d}</p>"
                    if calendar.day_name[wd.weekday()] not in [
                        "Saturday",
                        "Sunday",
                    ]:
                        if h:
                            if hasattr(h, "email"):
                                if len(h.first) > 7:
                                    wstr += f"<p>{h.first}<br/> {h.last}</p>"
                                else:
                                    wstr += f"<p>{h.name}<br/><br/></p>"
                            else:
                                wstr += (
                                    "<p>"
                                    + color_text(h.name, "blue")
                                    + "<br/><br/></p>"
                                )
                        elif wd in self.holidays:
                            # wstr += f"<p align='left'>{d}</p>"
                            # wstr += color_text(self.holidays.get(wd), "")
                            wstr += f"<p>{self.holidays.get(wd)}</p>"
                            if len(self.holidays.get(wd)) < 12:
                                wstr += "<br/><br/>"
                            else:
                                wstr += "<br/>"
                        else:
                            unassigned.append(wd.isoformat())
                            wstr += (
                                "<p>"
                                + color_text("Unassigned", "red")
                                + "<br/><br/></p>"
                            )
                    else:
                        wstr += "<p><br/><br/></p>"
                    wstr += "|"

            # wstr += "\n"
            fp.write(wstr + "\n")
        fp.close()
        print(
            f"{len(unassigned)} unassgined dates in "
            f"{calendar.month_name[month]}, {year} :",
            ",".join(unassigned),
        )


def color_text(text, color):
    return f"<span style='color:{color}'>{text}</span>"
