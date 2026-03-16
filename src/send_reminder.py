from coffeehost import Hosts, date
from datetime import datetime
from zoneinfo import ZoneInfo
import sys
import os

ET = ZoneInfo("America/New_York")

if len(sys.argv) == 2:
    # Date argument → dry-run mode (emails sent to self only, for testing)
    try:
        today = date.fromisoformat(sys.argv[1].strip())
    except ValueError:
        print(f"{sys.argv[1]} must be in isoformat YYYY-MM-DD")
        sys.exit(1)
    send = True
    dry_run = True
elif os.environ.get("REMINDER_DATE"):
    # Pinned date from workflow (scheduled runs) → real send, no dry-run
    today = date.fromisoformat(os.environ["REMINDER_DATE"])
    send = True
    dry_run = False
else:
    today = datetime.now(ET).date()
    send = True
    dry_run = False
dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
periods = ["2024_1", "2024_2", "2024_3", "2025_1", "2025_2", "2025_3", "2026_1"]
for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    newhosts += tmphosts

# send daily and weekly reminders
newhosts.generate_reminder(today=today, send=send, dry_run=dry_run)
