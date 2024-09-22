from coffeehost import Hosts, Host, date, get_weekdays
import pandas as pd
import os
import sys

base = os.path.dirname(__file__)

# [Update this] Abort if the output file exists
outfile = f"{base}/../data/hosts_2024_3.json"
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
    hosts[f"{h.last.lower()}_{h.first.lower()[0]}"] = h

hosts.show()

# [Update this] add host specific restrictions
# for wd in get_weekdays(2024, 2, exclude=["Monday", "Tuesday", "Wednesday", "Friday"]):
# hosts["spitkovsky"].add_restriction(wd, wd)
hosts["ward_c"].add_restriction(date(2024, 10, 1), date(2024, 10, 30))
hosts["goodman_j"].add_restriction(date(2024, 10, 1), date(2025, 1, 31))
hosts["sun_j"].add_restriction(date(2024, 10, 1), date(2025, 1, 31))
hosts["greene_j"].add_restriction(date(2024, 10, 1), date(2025, 1, 31))
hosts["kunz_m"].add_restriction(date(2024, 10, 1), date(2025, 1, 31))
hosts["spitkovsky_a"].add_restriction(date(2024, 10, 16), date(2024, 10, 18))
hosts["spitkovsky_a"].add_restriction(date(2024, 10, 24), date(2024, 10, 31))
hosts["spitkovsky_a"].add_restriction(date(2024, 11, 1), date(2024, 11, 5))
hosts["spitkovsky_a"].add_restriction(date(2024, 11, 11), date(2024, 11, 15))
hosts["spitkovsky_a"].add_restriction(date(2024, 11, 21), date(2024, 11, 27))
hosts["spitkovsky_a"].add_restriction(date(2024, 12, 10), date(2024, 12, 31))
hosts["orusa_l"].add_restriction(date(2024, 10, 14), date(2024, 10, 21))
hosts["gupta_s"].add_restriction(date(2024, 12, 1), date(2024, 12, 31))
hosts["kempski_p"].add_restriction(date(2024, 10, 1), date(2024, 10, 31))
hosts["mohapatra_r"].add_restriction(date(2024, 10, 1), date(2024, 10, 15))
hosts["mohapatra_r"].add_restriction(date(2024, 11, 23), date(2025, 1, 31))

# [Update this] add dates to assign
hosts.add_dates(get_weekdays(2024, 10))
hosts.add_dates(get_weekdays(2024, 11))
hosts.add_dates(get_weekdays(2024, 12))
hosts.add_dates(get_weekdays(2025, 1))

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
