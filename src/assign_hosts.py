"""Assign hosts for the October 2026 through January 2027 period."""

import os
import sys
from datetime import date

import pandas as pd

from coffeehost import Host, Hosts, get_weekdays

base = os.path.dirname(__file__)

# [Update this] Abort if the output file exists
outfile = f"{base}/../data/hosts_2026_3.json"
if os.path.isfile(outfile):
    print(
        f"Warning: the host file {os.path.basename(outfile)} exists. "
        "Please make sure to remove it or make a backup before running this script."
    )
    sys.exit()

# [Update this] read host file from the responses
hostfile = f"{base}/../data/Coffee-Hosts-2026-3.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[f"{h.last.lower()}_{h.first.lower()[0]}"] = h

hosts.show()

# [Update this] add host specific restrictions
hosts["rusakov_a"].add_weekday_restriction(0, 2)  # Monday, Wednesday
hosts["hamilton_c"].add_weekday_restriction(3, 4)  # Thursday, Friday
hosts["khoo_l"].add_weekday_restriction(0, 1, 3, 5, 6)  # Wednesday/Friday only
hosts["sunseri_j"].add_weekday_restriction(4)  # Friday
hosts["winter_m"].add_weekday_restriction(2)  # Wednesday
hosts["loudas_n"].set_monthly_limit(1)

hosts["lammers_c"].add_restriction(date(2026, 10, 12), date(2026, 10, 14))
hosts["lammers_c"].add_restriction(date(2026, 10, 19), date(2026, 10, 19))
hosts["lammers_c"].add_restriction(date(2026, 10, 26), date(2026, 10, 26))
hosts["lammers_c"].add_restriction(date(2026, 11, 4), date(2026, 11, 4))
hosts["spitkovsky_a"].add_restriction(date(2026, 11, 1), date(2026, 11, 20))
hosts["spitkovsky_a"].add_restriction(date(2026, 11, 30), date(2026, 12, 9))
hosts["spitkovsky_a"].add_restriction(date(2026, 12, 20), date(2027, 1, 31))
hosts["quataert_e"].add_restriction(date(2026, 10, 2), date(2026, 10, 13))
hosts["quataert_e"].add_restriction(date(2026, 10, 20), date(2026, 10, 25))
hosts["quataert_e"].add_restriction(date(2026, 11, 6), date(2026, 11, 9))
hosts["quataert_e"].add_restriction(date(2026, 11, 17), date(2026, 11, 19))
hosts["quataert_e"].add_restriction(date(2026, 12, 8), date(2026, 12, 8))
hosts["quataert_e"].add_restriction(date(2027, 1, 3), date(2027, 1, 23))
hosts["sunseri_j"].add_restriction(date(2026, 10, 22), date(2026, 11, 3))
hosts["sunseri_j"].add_restriction(date(2026, 11, 15), date(2026, 11, 21))
hosts["loudas_n"].add_restriction(date(2026, 11, 7), date(2026, 11, 17))
hosts["govreen-segal_t"].add_restriction(date(2026, 10, 26), date(2026, 10, 31))
hosts["govreen-segal_t"].add_restriction(date(2026, 12, 1), date(2026, 12, 31))
hosts["rom_b"].add_restriction(date(2026, 11, 23), date(2026, 12, 6))

# [Update this] add dates to assign
hosts.add_dates([day for day in get_weekdays(2026, 10) if day >= date(2026, 10, 5)])
hosts.add_dates(get_weekdays(2026, 11))
hosts.add_dates(get_weekdays(2026, 12))
hosts.add_dates(get_weekdays(2027, 1))

# [Update this] exclude dates
Holidays = Hosts()
Holidays.from_json(f"{base}/../data/holidays_2026.json")
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
