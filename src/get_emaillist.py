from coffeehost import *
import sys
import os

dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json(f"{dirname}/../data/hosts_2023_789.json")

# print email list
print("host email list")
newhosts.get_email_list()

# print reminder
print("next week reminder")
newhosts.get_weekly_list(reminder=True)
