from coffeehost import *
import pandas as pd

# read host file from the responses
hostfile = "./data/Princeton Astro Coffee Host- Fall 2023.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[h.last.lower()] = h

# add host specific restrictions
hosts["kim"].add_restriction(date(2023, 7, 30), date(2023, 8, 5))
hosts["kim"].add_restriction(date(2023, 8, 14), date(2023, 9, 30))
hosts["draine"].add_restriction(date(2023, 9, 1), date(2023, 12, 31))
hosts["mohapatra"].add_restriction(date(2023, 10, 5), date(2023, 11, 6))
hosts["mohapatra"].add_restriction(date(2023, 12, 15), date(2023, 12, 31))
hosts["strauss"].add_restriction(date(2023, 8, 7), date(2023, 8, 11))
hosts["strauss"].add_restriction(date(2023, 8, 28), date(2023, 9, 1))
hosts["escala"].add_restriction(date(2023, 8, 28), date(2023, 9, 1))
hosts["goodman"].add_restriction(date(2023, 10, 10), date(2023, 10, 20))
hosts["greene"].add_restriction(date(2023, 7, 1), date(2023, 9, 1))
hosts["ward"].add_restriction(date(2023, 10, 1), date(2023, 10, 7))
hosts["ward"].add_restriction(date(2023, 11, 27), date(2023, 12, 15))
hosts["sur"].add_restriction(date(2023, 7, 1), date(2023, 9, 15))
hosts["albrecht"].add_restriction(date(2023, 7, 12), date(2023, 12, 31))

# add dates to assign
hosts.add_dates(get_weekdays(2023, 7))
hosts.add_dates(get_weekdays(2023, 8))
hosts.add_dates(get_weekdays(2023, 9, exclude=["Tuesday"]))

# assign dates
hosts.assign_dates()

# show the results by hosts
hosts.show()

# store it to json file
hosts.to_json("data/hosts_2023_789.json")
