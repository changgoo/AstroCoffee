from coffeehost import *
import sys
import os

dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json(f"{dirname}/../data/hosts_2023_789.json")

# print assignments
newhosts.show()

# create assignment emails
newhosts.assignment_email()

# create calenders
for month in range(7, 13):
    newhosts.output_calendar(2023, month)
