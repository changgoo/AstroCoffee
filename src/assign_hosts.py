from coffeehost import Hosts, Host, date, get_weekdays
import pandas as pd
import os
import sys

base = os.path.dirname(__file__)

# [Update this] Abort if the output file exists
outfile = f"{base}/../data/hosts_2024_2.json"
if os.path.isfile(outfile):
    print(
        "Warning: the host file exists. Please make sure to remove it or make a backup before running this script."
    )
    sys.exit()

# [Update this] read host file from the responses
hostfile = f"{base}/../data/Coffee-Hosts-2024.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[h.fullname] = h

# [Update this] add host specific restrictions
# for wd in get_weekdays(2024, 2, exclude=["Monday", "Tuesday", "Wednesday", "Friday"]):
# hosts["spitkovsky"].add_restriction(wd, wd)
hosts["kunz"].add_restriction(date(2024, 1, 1), date(2024, 8, 31))
hosts["su"].add_restriction(date(2024, 1, 1), date(2024, 8, 31))
hosts["greene"].add_restriction(date(2024, 1, 1), date(2024, 8, 31))
hosts["modak"].add_restriction(date(2024, 1, 1), date(2024, 8, 31))
hosts["sun"].add_restriction(date(2024, 8, 12), date(2024, 8, 16))
hosts["sun"].add_restriction(date(2024, 9, 16), date(2024, 10, 4))
hosts["ward"].add_restriction(date(2024, 6, 1), date(2024, 6, 30))
hosts["ward"].add_restriction(date(2024, 7, 17), date(2024, 7, 21))
hosts["ward"].add_restriction(date(2024, 8, 26), date(2024, 9, 6))
hosts["secunda"].add_restriction(date(2024, 6, 3), date(2024, 6, 12))
hosts["secunda"].add_restriction(date(2024, 6, 17), date(2024, 6, 25))
hosts["secunda"].add_restriction(date(2024, 8, 21), date(2024, 12, 31))
hosts["pan"].add_restriction(date(2024, 6, 1), date(2024, 8, 31))
hosts["loudas"].add_restriction(date(2024, 6, 1), date(2024, 8, 10))
hosts["strauss"].add_restriction(date(2024, 6, 6), date(2024, 6, 27))
hosts["strauss"].add_restriction(date(2024, 7, 15), date(2024, 7, 26))
hosts["bambic"].add_restriction(date(2024, 9, 1), date(2024, 10, 1))

# [Update this] add dates to assign
hosts.add_dates(get_weekdays(2024, 6))
hosts.add_dates(get_weekdays(2024, 7))
hosts.add_dates(get_weekdays(2024, 8))
hosts.add_dates(get_weekdays(2024, 9))
# hosts.add_dates(get_weekdays(2024, 5))

# [Update this] exclude dates
Holidays = Hosts()
Holidays.from_json(f"{base}/../data/holidays_2024.json")
dates = []
for k in Holidays.hosts:
    for hd in Holidays[k].hostdate:
        dates += [hd]
hosts.exclude_dates(dates)

# assign dates
hosts.assign_dates()

# show the results by hosts
hosts.show()

# show the available hosts
hosts.showlist()

# store it to json file
hosts.to_json(outfile)
