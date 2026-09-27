"""Send assignment emails through the Gmail account used by reminders."""

import argparse
import io
import os
import re
import smtplib
from contextlib import redirect_stdout
from email import policy
from email.message import EmailMessage
from email.parser import Parser
from email.utils import getaddresses
from pathlib import Path

from coffeehost import Host, Hosts

ROOT = Path(__file__).resolve().parent.parent
DATE_LINE = re.compile(r"\d{4}-\d{2}-\d{2}")
PERIOD = re.compile(r"\d{4}_[0-9]+")


def prepare_drafts(period: str, basedir: Path = ROOT) -> list[tuple[Host, Path]]:
    """Generate and verify one current assignment draft per assigned host."""
    if not PERIOD.fullmatch(period):
        raise ValueError("Period must look like 2026_3")
    source = basedir / "data" / f"hosts_{period}.json"
    hosts = Hosts()
    hosts.from_json(str(source))
    assigned = [host for host in hosts.hosts.values() if host.hostdate]
    if not assigned:
        raise ValueError(f"No assignments found in {source}")

    with redirect_stdout(io.StringIO()):
        hosts.assignment_email(period=period, basedir=str(basedir))
    drafts = []
    for host in assigned:
        path = (
            basedir
            / "emails"
            / f"assignment_{period}_{host.first[0].lower()}_{host.last.lower()}.txt"
        )
        parsed = Parser(policy=policy.default).parsestr(path.read_text())
        to_addresses = [
            address.lower() for _, address in getaddresses([str(parsed["To"])])
        ]
        dates = sorted(
            line.strip()
            for line in str(parsed.get_payload()).splitlines()
            if DATE_LINE.fullmatch(line.strip())
        )
        if to_addresses != [host.email.lower()] or dates != sorted(
            day.isoformat() for day in host.hostdate
        ):
            raise ValueError(f"Draft does not match assignments for {host.name}")
        drafts.append((host, path))
    return drafts


def send_assignments(
    period: str, basedir: Path = ROOT, skip_recipients: str = ""
) -> int:
    """Send a period's assignment emails, omitting already sent hosts."""
    drafts = prepare_drafts(period, basedir)
    skipped = {
        address.strip().lower()
        for address in skip_recipients.split(",")
        if address.strip()
    }
    unknown = skipped - {host.email.lower() for host, _ in drafts}
    if unknown:
        raise ValueError(f"Unknown host email(s) to skip: {', '.join(sorted(unknown))}")
    drafts = [
        (host, path) for host, path in drafts if host.email.lower() not in skipped
    ]
    if not drafts:
        raise ValueError("No assignment recipients remain after skipping")
    if skipped:
        print(f"Skipping already sent host(s): {', '.join(sorted(skipped))}")

    gmail_user = os.environ.get("GMAIL_USER")
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not app_password:
        raise RuntimeError("GMAIL_USER and GMAIL_APP_PASSWORD are required")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(gmail_user, app_password)
        for host, path in drafts:
            source = Parser(policy=policy.default).parsestr(path.read_text())
            message = EmailMessage()
            message["From"] = gmail_user
            message["Subject"] = str(source["Subject"])
            message["To"] = str(source["To"])
            if source["Cc"]:
                message["Cc"] = str(source["Cc"])
            recipients = [
                address
                for _, address in getaddresses(
                    [
                        str(source[header])
                        for header in ("To", "Cc", "Bcc")
                        if source[header]
                    ]
                )
                if address
            ]
            message.set_content(str(source.get_payload()))
            refused = smtp.send_message(
                message, from_addr=gmail_user, to_addrs=recipients
            )
            if refused:
                raise RuntimeError(
                    f"Gmail refused recipients for {host.name}: {refused}; "
                    "other recipients may have been accepted"
                )
            print(f"Gmail accepted assignment email for {host.name} to {host.email}")
    return len(drafts)


def main() -> None:
    """Parse the period and send its assignment emails."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("period", help="Assignment period such as 2026_3")
    parser.add_argument(
        "--skip-recipients",
        default="",
        help="Comma-separated host emails already accepted by Gmail",
    )
    args = parser.parse_args()
    count = send_assignments(args.period, skip_recipients=args.skip_recipients)
    print(f"Gmail accepted {count} message(s)")


if __name__ == "__main__":
    main()
