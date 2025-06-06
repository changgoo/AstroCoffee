from coffeehost import Hosts, date
import sys
import os

if len(sys.argv) == 2:
    try:
        today = date.fromisoformat(sys.argv[1])
    except IndexError:
        print(f"{sys.argv[1]} must be in isoformat YYYY-MM-DD")
    send = False
else:
    today = date.today()
    send = True
dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
periods = ["2024_1", "2024_2", "2024_3", "2025_1", "2025_2"]
for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    newhosts += tmphosts

# send daily and weekly reminders
newhosts.generate_reminder(today=today, send=send)
