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

from coffeehost import DRY_RUN_EMAIL, Host, Hosts

ROOT = Path(__file__).resolve().parent.parent
DATE_LINE = re.compile(r"\d{4}-\d{2}-\d{2}")


def prepare_drafts(period: str, basedir: Path = ROOT) -> list[tuple[Host, Path]]:
    """Generate and verify one current assignment draft per assigned host."""
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
    period: str, mode: str, recipient: str = "", basedir: Path = ROOT
) -> int:
    """Send one preview to self or all selected hosts via one Gmail login."""
    drafts = prepare_drafts(period, basedir)
    if recipient:
        drafts = [
            (host, path)
            for host, path in drafts
            if host.email.lower() == recipient.lower()
        ]
        if not drafts:
            raise ValueError(f"No assignment email for {recipient}")
    if mode == "preview":
        drafts = drafts[:1]
    elif mode != "send":
        raise ValueError(f"Unknown mode: {mode}")

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
            if mode == "preview":
                message.replace_header("Subject", f"[preview] {source['Subject']}")
                message["To"] = DRY_RUN_EMAIL
                recipients = [DRY_RUN_EMAIL]
            else:
                message["To"] = str(source["To"])
                if source["Cc"]:
                    message["Cc"] = str(source["Cc"])
                recipients = [
                    address
                    for _, address in getaddresses(
                        [str(source.get(header, "")) for header in ("To", "Cc", "Bcc")]
                    )
                ]
            message.set_content(str(source.get_payload()))
            refused = smtp.send_message(
                message, from_addr=gmail_user, to_addrs=recipients
            )
            if refused:
                raise RuntimeError(
                    f"Gmail refused recipients for {host.name}: {refused}"
                )
            destination = DRY_RUN_EMAIL if mode == "preview" else host.email
            print(f"Gmail accepted assignment email for {host.name} to {destination}")
    return len(drafts)


def main() -> None:
    """Parse the requested period and preview or send mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("period", help="Assignment period such as 2026_3")
    parser.add_argument("--mode", choices=("preview", "send"), required=True)
    parser.add_argument("--recipient", default="", help="Optional single host email")
    args = parser.parse_args()
    count = send_assignments(args.period, args.mode, args.recipient)
    print(f"Gmail accepted {count} message(s)")


if __name__ == "__main__":
    main()
