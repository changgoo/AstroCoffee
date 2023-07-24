from coffeehost import *
import sys
import os

if len(sys.argv) == 2:
    try:
        today = date.fromisoformat(sys.argv[1])
    except:
        print(f"{sys.argv[1]} must be in isoformat YYYY-MM-DD")
    send = False
else:
    today = date.today()
    send = True
dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json(f"{dirname}/../data/hosts_2023_789.json")

# send daily and weekly reminders
newhosts.generate_reminder(today=today, send=send)
