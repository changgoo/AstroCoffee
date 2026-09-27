import calendar
import json
import os
import subprocess
from datetime import date, datetime, timedelta
from email import message_from_string
from typing import Any
from zoneinfo import ZoneInfo

import holidays

dirpath = os.path.dirname(__file__)


DRY_RUN_EMAIL = "changgoo@princeton.edu"


def _send_email_gmail(content: str, dry_run: bool = False) -> None:
    """Send an email via Gmail SMTP, parsing To/From/Cc/Bcc/Subject from content headers.

    Requires ``GMAIL_USER`` and ``GMAIL_APP_PASSWORD`` environment variables.
    The From header is overridden with ``GMAIL_USER`` since Gmail only allows
    sending from the authenticated account.
    When ``dry_run`` is True, all recipients are replaced with ``DRY_RUN_EMAIL``.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    gmail_user = os.environ["GMAIL_USER"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    msg = message_from_string(content)
    body = msg.get_payload()

    mime = MIMEMultipart()
    mime["From"] = gmail_user
    mime["Subject"] = msg["Subject"]
    mime.attach(MIMEText(body, "plain"))

    if dry_run:
        print(f"[dry-run] redirecting all recipients to {DRY_RUN_EMAIL}")
        recipients = [DRY_RUN_EMAIL]
        mime["To"] = DRY_RUN_EMAIL
    else:
        recipients = []
        if msg["To"]:
            to_addrs = [a.strip() for a in msg["To"].split(",")]
            mime["To"] = ", ".join(to_addrs)
            recipients.extend(to_addrs)
        if msg["Cc"]:
            cc_addrs = [a.strip() for a in msg["Cc"].split(",")]
            mime["Cc"] = ", ".join(cc_addrs)
            recipients.extend(cc_addrs)
        if msg["Bcc"]:
            recipients.extend(a.strip() for a in msg["Bcc"].split(","))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, app_password)
        smtp.sendmail(gmail_user, recipients, mime.as_string())


def get_weekdays(year: int, month: int, exclude: list[str] | None = None) -> list[date]:
    """Return weekdays in a month, omitting named weekdays in exclude."""
    if exclude is None:
        exclude = []
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


class Host:
    """Represent a host and their date and weekday availability."""

    def __init__(self, name: str = "", email: str = "") -> None:
        """Initialize a host with no assignments or restrictions."""
        self.name = name
        name_split = name.split(" ")
        self.first = " ".join(name_split[:-1])
        self.last = name_split[-1]
        self.fullname = self.first.lower() + self.last.lower()
        self.email = email
        self.restriction = []
        self.weekday_restriction: list[int] = []
        self.monthly_limit: int | None = None
        self.hostdate = []

    def __repr__(self) -> str:
        """Show the host and assigned dates."""
        out = f"{self.first} {self.last} [{len(self.hostdate)}]:"
        for mydate in sorted(self.hostdate):
            out += f" {mydate}({mydate.weekday()})"
        return out

    def __add__(self, h2: "Host") -> "Host":
        """Merge the assignments and restrictions of matching hosts."""
        if self.name == h2.name:
            ranges = {tuple(r) for r in self.restriction + h2.restriction}
            self.restriction = [list(r) for r in sorted(ranges)]
            self.weekday_restriction = sorted(
                set(self.weekday_restriction + h2.weekday_restriction)
            )
            limits = [
                limit
                for limit in (self.monthly_limit, h2.monthly_limit)
                if limit is not None
            ]
            self.monthly_limit = min(limits) if limits else None
            self.hostdate = sorted(set(self.hostdate + h2.hostdate))
            return self
        else:
            raise TypeError(f"Two host names do not match {self.name} and {h2.name}")

    def add_restriction(self, d1: date, d2: date) -> None:
        """Block every date from d1 through d2, inclusive."""
        self.restriction.append([d1, d2])

    def add_weekday_restriction(self, *weekdays: int) -> None:
        """Block recurring weekdays using Monday=0 through Sunday=6."""
        if any(day not in range(7) for day in weekdays):
            raise ValueError("Weekdays must be integers from 0 (Monday) to 6 (Sunday)")
        self.weekday_restriction = sorted(set(self.weekday_restriction).union(weekdays))

    def set_monthly_limit(self, limit: int) -> None:
        """Cap a host's assignments in each calendar month."""
        if limit < 1:
            raise ValueError("Monthly assignment limit must be positive")
        self.monthly_limit = limit

    def test_available(self, day: date) -> bool:
        """Check date windows, weekdays, and the monthly assignment limit."""
        if day.weekday() in self.weekday_restriction:
            return False
        for r in self.restriction:
            if r[0] <= day <= r[1]:
                return False
        if self.monthly_limit is not None:
            other_dates_this_month = sum(
                assigned.year == day.year
                and assigned.month == day.month
                and assigned != day
                for assigned in self.hostdate
            )
            if other_dates_this_month >= self.monthly_limit:
                return False
        return True

    def add_date(self, day: date) -> bool:
        """Assign a date if the host is available."""
        if self.test_available(day):
            self.hostdate.append(day)
            return True
        return False

    def clean_date(self) -> None:
        """Clear assigned dates while retaining restrictions."""
        self.hostdate = []

    def to_json(self) -> str:
        """Serialize this host with ISO date strings."""
        mydict = {}
        for k, v in self.__dict__.items():
            mydict[k] = v
        mydict["hostdate"] = [d.isoformat() for d in mydict["hostdate"]]
        mydict["restriction"] = [
            [d1.isoformat(), d2.isoformat()] for (d1, d2) in mydict["restriction"]
        ]
        return json.dumps(mydict, indent=4)

    def from_json(self, myjson: str) -> None:
        """Load a host from a JSON string."""
        mydict = json.loads(myjson)
        self.from_dict(mydict)

    def from_dict(self, mydict: dict[str, Any]) -> None:
        """Load a host from a dictionary, including older host files."""
        mydict["hostdate"] = [date.fromisoformat(d) for d in mydict["hostdate"]]
        mydict["restriction"] = [
            [date.fromisoformat(d1), date.fromisoformat(d2)]
            for (d1, d2) in mydict["restriction"]
        ]

        mydict["weekday_restriction"] = mydict.get("weekday_restriction", [])
        mydict["monthly_limit"] = mydict.get("monthly_limit")
        self.__dict__ = mydict


class Hosts:
    """Manage hosts, assignment dates, and reminder emails."""

    def __init__(self) -> None:
        """Initialize an empty host collection."""
        self.hosts = {}
        self.dates = []
        self.set_holidays()

    def __getitem__(self, key: str) -> Host:
        """Return a host by key."""
        return self.hosts[key]

    def __setitem__(self, key: str, value: Host) -> None:
        """Store a host by key."""
        self.hosts[key] = value

    def __add__(self, hosts2: "Hosts") -> "Hosts":
        """Merge another host collection into this one."""
        for n, h in hosts2.hosts.items():
            if n in self.hosts:
                self.hosts[n] += h
            else:
                self.hosts[n] = h
        return self

    def clean(self) -> None:
        """Clear every host's assigned dates."""
        for h in self.hosts.values():
            h.clean_date()

    def set_holidays(self) -> None:
        """Load the US holiday calendar."""
        self.holidays = holidays.US()

    def add_dates(self, dates: list[date]) -> None:
        """Add assignment candidates without duplicates."""
        self.dates = sorted(set(self.dates + dates))

    def exclude_dates(self, dates: list[date]) -> None:
        """Remove closed dates from assignment candidates."""
        self.dates = sorted(set(self.dates) - set(dates))

    def assign_dates(self, verbose: bool = True) -> None:
        """Assign each candidate date to the next available host."""
        from itertools import cycle

        import numpy as np

        self.clean()
        hiter = cycle(self.hosts)
        mylist = [wd for wd in np.unique(self.dates)]
        while mylist:
            wd = mylist.pop()
            assigned = False
            for _ in range(len(self.hosts)):
                h = self.hosts[next(hiter)]
                assigned = h.add_date(wd)
                if verbose and assigned:
                    print(f"{wd}[{wd.weekday()}] is assigned to {h.name}")
                if assigned:
                    break
            if not assigned:
                raise ValueError(f"No available host for {wd}")

    def show(self) -> None:
        """Print hosts with their assigned dates."""
        for n, h in self.hosts.items():
            print(n, h)

    def showlist(self) -> None:
        """Print names and email addresses."""
        hostlist = []
        hostemail = {}
        for n, h in self.hosts.items():
            hostlist.append(h.name)
            hostemail[h.name] = h.email
        for n in sorted(hostlist):
            print(f"{n},{hostemail[n]}")

    def find_host(self, day: date) -> Host | bool:
        """Find the host assigned to a date, if any."""
        found_host = []
        for h in self.hosts.values():
            if day in h.hostdate:
                found_host.append(h)
        if len(found_host) > 1:
            print(f"{len(found_host)} are found on {day}:")
            for h in found_host:
                print(h)
        elif len(found_host) == 1:
            return found_host[0]

        return False

    def to_json(self, fname: str, overwrite: bool = True) -> None:
        """Write the host collection as a JSON array."""
        if overwrite and os.path.isfile(fname):
            os.remove(fname)
        with open(fname, "a") as fp:
            outstr = ["["]
            for h in self.hosts.values():
                outstr.append(h.to_json())
                outstr.append(",")
            outstr[-1] = "]"
            fp.write("".join(outstr))

    def from_json(self, fname: str) -> None:
        """Load hosts from a JSON array."""
        with open(fname, "r") as fp:
            myjson = json.load(fp)
            for h_json in myjson:
                h = Host()
                h.from_dict(h_json)
                if not hasattr(h, "fullname"):
                    h.fullname = h.first.lower() + h.last.lower()
                self.hosts[h.fullname.lower()] = h

    def get_email_list(self) -> None:
        """Print each host's name and email address."""
        for v in self.hosts.values():
            print(f"{v.name}<{v.email}>")

    def generate_reminder(
        self,
        today: date | None = None,
        send: bool = False,
        dry_run: bool = False,
        basedir: str = os.path.join(dirpath, "../"),
    ) -> None:
        """Generate and optionally send daily and weekly reminder emails.

        Parameters
        ----------
        today : date
            Reference date (default: today).
        send : bool
            If True, send emails; otherwise print to stdout.
        dry_run : bool
            If True, send emails to ``DRY_RUN_EMAIL`` only (for testing).
        basedir : str
            Base directory for email output files.
        """
        if today is None:
            today = datetime.now(ZoneInfo("America/New_York")).date()
        if not os.path.isdir(os.path.join(basedir, "emails")):
            os.mkdir(os.path.join(basedir, "emails"))

        tomorrow = today + timedelta(days=1)

        # find tomorrow host
        h = self.find_host(tomorrow)
        if h and hasattr(h, "email"):
            self.write_daily_reminder(h, tomorrow, send=send, dry_run=dry_run)

        # find all for next week
        # today = today - timedelta(days=1)
        if calendar.day_name[today.weekday()] == "Saturday":
            dlist = [today + timedelta(days=i) for i in range(2, 7)]
            hlist = [self.find_host(d) for d in dlist]
            self.write_weekly_reminder(hlist, dlist, send=send, dry_run=dry_run)

    def write_daily_reminder(
        self,
        h: Host,
        day: date,
        send: bool = False,
        dry_run: bool = False,
        basedir: str = os.path.join(dirpath, "../"),
    ) -> None:
        """Write and optionally send one host's daily reminder."""
        with open(f"{basedir}/templates/daily_reminder_green_hall.txt", "r") as fp:
            remindertxt = fp.read()
        outfname = f"{basedir}/emails/reminder_{h.first[0].lower}_{h.last.lower()}_{day.isoformat()}.txt"
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
            if os.environ.get("GMAIL_USER"):
                _send_email_gmail(reminder, dry_run=dry_run)
            else:
                with open(outfname, "r") as fp:
                    subprocess.run(["sendmail", "-t", "-oi"], stdin=fp, check=False)
        else:
            print(reminder)

    def write_weekly_reminder(
        self,
        hlist: list[Host | bool],
        dlist: list[date],
        send: bool = False,
        dry_run: bool = False,
        basedir: str = os.path.join(dirpath, "../"),
    ) -> None:
        """Write and optionally send the next week's reminders."""
        with open(f"{basedir}/templates/weekly_reminder.txt", "r") as fp:
            remindertxt = fp.read()
        outfname = f"{basedir}/emails/reminder_{dlist[0].isoformat()}.txt"

        emails = []
        names = []
        days = {}
        hosts = {}
        for i, (d, h) in enumerate(zip(dlist, hlist)):
            days[f"day{i + 1}"] = d.isoformat()
            if h and hasattr(h, "email"):
                emails.append(f"{h.name}<{h.email}>")
                names.append(f"{h.name}")
                hosts[f"host{i + 1}"] = h.name
            else:
                try:
                    hosts[f"host{i + 1}"] = f"no astrocoffee ({h.name})"
                except AttributeError:
                    hosts[f"host{i + 1}"] = f"no astrocoffee ({self.holidays.get(d)})"

        emails = set(emails)
        names = set(names)

        kwargs = {"names": ", ".join(names)}
        kwargs.update(days)
        kwargs.update(hosts)

        email = "Chang-Goo Kim<astrocoffee.princeton@gmail.com>"
        # for email in emails:
        kwargs.update(emails=", ".join(emails), email=email)
        with open(outfname, "w") as fp:
            reminder = remindertxt.format(**kwargs)
            fp.write(reminder)
        if send:
            print(f"weekly reminder is sent to {emails}")
            if os.environ.get("GMAIL_USER"):
                _send_email_gmail(reminder, dry_run=dry_run)
            else:
                with open(outfname, "r") as fp:
                    subprocess.run(["sendmail", "-t", "-oi"], stdin=fp, check=False)
        else:
            print(reminder)

    def assignment_email(
        self, period: str = "2023_4", basedir: str = os.path.join(dirpath, "../")
    ) -> None:
        """Write per-host assignment emails from the assignment template.

        Derives start_month, end_month, and year from the assigned host dates
        and the period string (e.g. '2026_2').
        """
        if not os.path.isdir(os.path.join(basedir, "emails")):
            os.mkdir(os.path.join(basedir, "emails"))

        year = period.split("_")[0]

        all_dates = [
            d
            for h in self.hosts.values()
            if hasattr(h, "email") and h.hostdate
            for d in h.hostdate
        ]
        if all_dates:
            start_month = date(min(all_dates).year, min(all_dates).month, 1).strftime(
                "%B"
            )
            end_month = date(max(all_dates).year, max(all_dates).month, 1).strftime(
                "%B"
            )
            end_year = str(max(all_dates).year)
        else:
            start_month = end_month = ""
            end_year = year

        with open(f"{basedir}/templates/assignment.txt", "r") as fp:
            remindertxt = fp.read()
            for h in self.hosts.values():
                if not hasattr(h, "email"):
                    continue
                if len(h.hostdate) == 0:
                    continue
                outfname = f"{basedir}/emails/assignment_{period}_{h.first[0].lower()}_{h.last.lower()}.txt"
                with open(outfname, "w") as fp:
                    reminder = remindertxt.format(
                        fullname=h.name,
                        email=h.email,
                        name=h.first,
                        dates="\n".join([d.isoformat() for d in sorted(h.hostdate)]),
                        start_month=start_month,
                        end_month=end_month,
                        year=year,
                        end_year=end_year,
                    )
                    fp.write(reminder)
                print(f"cat {outfname} | sendmail -t -oi")
