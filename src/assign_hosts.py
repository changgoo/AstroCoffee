from coffeehost import Hosts, Host, date, get_weekdays
import pandas as pd
import os
import sys

base = os.path.dirname(__file__)

# [Update this] Abort if the output file exists
outfile = f"{base}/../data/hosts_2025_2.json"
if os.path.isfile(outfile):
    print(
        f"Warning: the host file {os.path.basename(outfile)} exists. "
        "Please make sure to remove it or make a backup before running this script."
    )
    sys.exit()

# [Update this] read host file from the responses
hostfile = f"{base}/../data/Coffee-Hosts-2025-2.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[f"{h.last.lower()}_{h.first.lower()[0]}"] = h

hosts.show()

# [Update this] add host specific restrictions
hosts["modak_s"].add_restriction(date(2025, 7, 28), date(2025, 8, 11))
hosts["quataert_e"].add_restriction(date(2025, 6, 9), date(2025, 6, 16))
hosts["quataert_e"].add_restriction(date(2025, 8, 11), date(2025, 8, 23))
hosts["saydjari_a"].add_restriction(date(2025, 6, 2), date(2025, 6, 6))
hosts["saydjari_a"].add_restriction(date(2025, 6, 16), date(2025, 6, 18))
hosts["saydjari_a"].add_restriction(date(2025, 6, 23), date(2025, 6, 27))
hosts["saydjari_a"].add_restriction(date(2025, 7, 10), date(2025, 7, 25))
hosts["jespersen_c"].add_restriction(date(2025, 5, 1), date(2025, 6, 27))
hosts["jespersen_c"].add_restriction(date(2025, 5, 1), date(2025, 6, 27))
for wd in get_weekdays(2025, 7, exclude=["Friday"]):
    hosts["jespersen_c"].add_restriction(wd, wd)
for wd in get_weekdays(2025, 8, exclude=["Friday"]):
    hosts["jespersen_c"].add_restriction(wd, wd)
for wd in get_weekdays(2025, 9, exclude=["Friday"]):
    hosts["jespersen_c"].add_restriction(wd, wd)
hosts["goodman_j"].add_restriction(date(2025, 5, 30), date(2025, 6, 9))
hosts["strauss_m"].add_restriction(date(2025, 5, 30), date(2025, 6, 8))
hosts["strauss_m"].add_restriction(date(2025, 7, 14), date(2025, 7, 28))
hosts["greene_j"].add_restriction(date(2025, 6, 1), date(2025, 6, 30))
hosts["greene_j"].add_restriction(date(2025, 8, 1), date(2025, 9, 30))
hosts["andalman_z"].add_restriction(date(2025, 5, 26), date(2025, 6, 2))
hosts["andalman_z"].add_restriction(date(2025, 7, 14), date(2025, 7, 17))
hosts["andalman_z"].add_restriction(date(2025, 7, 25), date(2025, 8, 1))
hosts["liu_h"].add_restriction(date(2025, 6, 1), date(2025, 6, 30))
hosts["mohapatra_r"].add_restriction(date(2025, 6, 1), date(2025, 6, 5))
hosts["mohapatra_r"].add_restriction(date(2025, 7, 1), date(2025, 8, 15))

# [Update this] add dates to assign
hosts.add_dates(get_weekdays(2025, 6))
hosts.add_dates(get_weekdays(2025, 7))
hosts.add_dates(get_weekdays(2025, 8))
hosts.add_dates(get_weekdays(2025, 9))

# [Update this] exclude dates
Holidays = Hosts()
Holidays.from_json(f"{base}/../data/holidays_2024.json")
Holidays2 = Hosts()
Holidays2.from_json(f"{base}/../data/holidays_2025.json")
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
