from coffeehost import *
import sys
import os

dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json(f"{dirname}/../data/hosts_2023_789.json")

# send daily and weekly reminders
newhosts.generate_reminder(
    #    today=date.today() - timedelta(days=1),
    # today=date(2023,6,29),
    reminder=True,
    send=True,
)
