from coffeehost import Hosts, Host, date, get_weekdays
import pandas as pd
import os
import sys

base = os.path.dirname(__file__)

# [Update this] Abort if the output file exists
outfile = f"{base}/../data/hosts_2025_3.json"
if os.path.isfile(outfile):
    print(
        f"Warning: the host file {os.path.basename(outfile)} exists. "
        "Please make sure to remove it or make a backup before running this script."
    )
    sys.exit()

# [Update this] read host file from the responses
hostfile = f"{base}/../data/Coffee-Hosts-2025-3.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[f"{h.last.lower()}_{h.first.lower()[0]}"] = h

hosts.show()

# [Update this] add host specific restrictions
hosts["modak_s"].add_restriction(date(2025, 7, 28), date(2025, 8, 11))

# [Update this] add dates to assign
hosts.add_dates(get_weekdays(2025, 10))
hosts.add_dates(get_weekdays(2025, 11))
hosts.add_dates(get_weekdays(2025, 12))
hosts.add_dates(get_weekdays(2026, 1))

# [Update this] exclude dates
Holidays = Hosts()
Holidays.from_json(f"{base}/../data/holidays_2025.json")
Holidays2 = Hosts()
Holidays2.from_json(f"{base}/../data/holidays_2026.json")
Holidays += Holidays2
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
