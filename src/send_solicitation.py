"""Script to format and send the AstroCoffee host solicitation email."""

import os
import subprocess
import sys

DIRNAME = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(DIRNAME, "../templates/solicitation.txt")
OUTPUT_PATH = os.path.join(DIRNAME, "../emails/solicitation.txt")


def load_template(path: str) -> str:
    """Load the solicitation email template from disk."""
    with open(path) as f:
        return f.read()


def format_email(
    template: str,
    list_email: str,
    start_month: str,
    end_month: str,
    year: str,
    deadline: str,
) -> str:
    """Fill in the solicitation template with the given values."""
    return template.format(
        list_email=list_email,
        start_month=start_month,
        end_month=end_month,
        year=year,
        deadline=deadline,
    )


def write_email(content: str, path: str) -> None:
    """Write the formatted email to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def send_email(path: str) -> None:
    """Send the email file via sendmail."""
    with open(path) as f:
        subprocess.run(["sendmail", "-t", "-oi"], stdin=f)


def main() -> None:
    """Format and optionally send the solicitation email.

    Run without arguments to send the email.
    Run with any argument (e.g. '--dry-run') to print without sending.
    """
    send = len(sys.argv) == 1

    # [Update these] values for the new period
    list_email = "astro-all@princeton.edu"
    start_month = "February"
    end_month = "May"
    year = "2026"
    deadline = "end of this week"

    template = load_template(TEMPLATE_PATH)
    email = format_email(template, list_email, start_month, end_month, year, deadline)

    write_email(email, OUTPUT_PATH)

    if send:
        print(f"Sending solicitation to {list_email}...")
        send_email(OUTPUT_PATH)
    else:
        print(email)


if __name__ == "__main__":
    main()
