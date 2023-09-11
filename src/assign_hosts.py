from coffeehost import *
import pandas as pd

# read host file from the responses
hostfile = "../data/Princeton Astro Coffee Host- Fall 2023.csv"
hostfile = "../data/Coffee-Hosts-2023-4.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[h.last.lower()] = h

# add host specific restrictions
hosts["kim"].add_restriction(date(2023, 7, 30), date(2023, 8, 5))
hosts["kim"].add_restriction(date(2023, 8, 14), date(2023, 9, 30))
hosts["kim"].add_restriction(date(2023, 11, 5), date(2023, 11, 10))
hosts["kim"].add_restriction(date(2023, 12, 5), date(2023, 12, 20))
hosts["mohapatra"].add_restriction(date(2023, 10, 5), date(2023, 11, 6))
hosts["mohapatra"].add_restriction(date(2023, 12, 15), date(2023, 12, 31))
hosts["strauss"].add_restriction(date(2023, 8, 7), date(2023, 8, 11))
hosts["strauss"].add_restriction(date(2023, 8, 28), date(2023, 9, 1))
hosts["escala"].add_restriction(date(2023, 8, 28), date(2023, 9, 1))
hosts["goodman"].add_restriction(date(2023, 10, 10), date(2023, 10, 20))
hosts["greene"].add_restriction(date(2023, 7, 1), date(2023, 9, 1))
hosts["ward"].add_restriction(date(2023, 10, 1), date(2023, 11, 6))
hosts["ward"].add_restriction(date(2023, 11, 29), date(2023, 12, 8))
hosts["sur"].add_restriction(date(2023, 7, 1), date(2023, 9, 15))

# add dates to assign
hosts.add_dates(get_weekdays(2023, 10, exclude=["Tuesday"]))
hosts.add_dates(get_weekdays(2023, 11, exclude=["Tuesday"]))
hosts.add_dates(get_weekdays(2023, 12, exclude=["Tuesday"]))

# assign dates
hosts.assign_dates()

# show the results by hosts
hosts.show()

# show the available hosts
hosts.showlist()

# store it to json file
hosts.to_json("../data/hosts_2023_4.json")
