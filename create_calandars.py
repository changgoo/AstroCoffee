from coffeehost import *
import sys

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json('hosts_2023_789.json')

# create calenders
for month in range(7,13):
    newhosts.output_calendar(2023,month)