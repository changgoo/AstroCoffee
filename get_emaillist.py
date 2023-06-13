from coffeehost import *
import sys

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json("hosts_2023_789.json")

# print email list
print("host email list")
newhosts.get_email_list()

# print reminder
print("next week reminder")
newhosts.get_weekly_list(today=date(2023, 7, 20), reminder=True)
