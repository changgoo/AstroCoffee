from coffeehost import Hosts, Host, get_weekdays
from datetime import date
import pandas as pd
import os
import sys

base = os.path.dirname(__file__)

# [Update this] Abort if the output file exists
outfile = f"{base}/../data/hosts_2026_2.json"
if os.path.isfile(outfile):
    print(
        f"Warning: the host file {os.path.basename(outfile)} exists. "
        "Please make sure to remove it or make a backup before running this script."
    )
    sys.exit()

# [Update this] read host file from the responses
hostfile = f"{base}/../data/Coffee-Hosts-2026-2.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[f"{h.last.lower()}_{h.first.lower()[0]}"] = h

hosts.show()

# [Update this] add host specific restrictions
hosts["liu_h"].add_restriction(date(2026, 6, 1), date(2026, 7, 14))
hosts["loudas_n"].add_restriction(date(2026, 7, 6), date(2026, 7, 19))
hosts["loudas_n"].add_restriction(date(2026, 8, 7), date(2026, 9, 8))
hosts["rusakov_a"].add_restriction(date(2026, 7, 7), date(2026, 7, 17))
hosts["modak_s"].add_restriction(date(2026, 6, 4), date(2026, 6, 15))
hosts["modak_s"].add_restriction(date(2026, 7, 13), date(2026, 7, 17))
hosts["modak_s"].add_restriction(date(2026, 8, 1), date(2026, 9, 30))
hosts["strauss_m"].add_restriction(date(2026, 6, 1), date(2026, 6, 7))
hosts["strauss_m"].add_restriction(date(2026, 7, 25), date(2026, 8, 22))
hosts["quataert_e"].add_restriction(date(2026, 6, 1), date(2026, 6, 8))
hosts["quataert_e"].add_restriction(date(2026, 6, 15), date(2026, 6, 16))
hosts["quataert_e"].add_restriction(date(2026, 6, 26), date(2026, 6, 26))
hosts["quataert_e"].add_restriction(date(2026, 7, 3), date(2026, 7, 11))
hosts["quataert_e"].add_restriction(date(2026, 8, 12), date(2026, 8, 24))
hosts["greene_j"].add_restriction(date(2026, 6, 1), date(2026, 8, 31))
hosts["mbarek_r"].add_restriction(date(2026, 6, 4), date(2026, 7, 10))
hosts["mbarek_r"].add_restriction(date(2026, 8, 26), date(2026, 9, 15))
hosts["andalman_z"].add_restriction(date(2026, 6, 8), date(2026, 6, 12))
hosts["andalman_z"].add_restriction(date(2026, 7, 13), date(2026, 7, 31))
hosts["andalman_z"].add_restriction(date(2026, 8, 24), date(2026, 9, 4))
hosts["winter_m"].add_restriction(date(2026, 8, 1), date(2026, 8, 21))
hosts["sunseri_j"].add_restriction(date(2026, 6, 8), date(2026, 8, 31))
hosts["lammers_c"].add_restriction(date(2026, 6, 18), date(2026, 6, 28))
hosts["lammers_c"].add_restriction(date(2026, 7, 18), date(2026, 8, 3))
hosts["rui_n"].add_restriction(date(2026, 6, 13), date(2026, 6, 27))
hosts["rui_n"].add_restriction(date(2026, 7, 5), date(2026, 7, 10))
hosts["rui_n"].add_restriction(date(2026, 8, 1), date(2026, 8, 31))
hosts["setton_d"].add_restriction(date(2026, 9, 1), date(2026, 9, 30))

# [Update this] add dates to assign
hosts.add_dates(get_weekdays(2026, 6))
hosts.add_dates(get_weekdays(2026, 7))
hosts.add_dates(get_weekdays(2026, 8))
hosts.add_dates(get_weekdays(2026, 9))

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
