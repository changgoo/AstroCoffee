from coffeehost import *
import sys
import os

dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json(f"{dirname}/../data/holidays_2023.json")
periods = ["2023_3", "2023_4"]
for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    newhosts += tmphosts
tmphosts.assignment_email(period=period)

# print assignments
newhosts.show()

# create calenders
for i, month in enumerate(range(7, 13)):
    newhosts.output_calendar(2023, month, num=6 - i)
