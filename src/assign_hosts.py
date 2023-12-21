from coffeehost import Hosts, Host, date, get_weekdays
import pandas as pd

# read host file from the responses
hostfile = "../data/Coffee-Hosts-2024.csv"
hostlist = pd.read_csv(hostfile)

# initialize host list
hosts = Hosts()
for n, e in zip(hostlist["Your Name"], hostlist["Email Address"]):
    h = Host(n, e)
    hosts[h.last.lower()] = h

# add host specific restrictions
hosts["secunda"].add_restriction(date(2024, 4, 1), date(2024, 4, 12))
hosts["mohapatra"].add_restriction(date(2024, 1, 21), date(2024, 3, 2))
hosts["mohapatra"].add_restriction(date(2024, 4, 15), date(2024, 4, 30))
hosts["ward"].add_restriction(date(2024, 1, 1), date(2024, 4, 1))
hosts["ward"].add_restriction(date(2024, 5, 15), date(2024, 5, 31))
hosts["kempski"].add_restriction(date(2024, 2, 4), date(2024, 2, 24))
hosts["strauss"].add_restriction(date(2024, 4, 4), date(2024, 4, 9))
hosts["spitkovsky"].add_restriction(date(2024, 1, 5), date(2024, 1, 16))
hosts["spitkovsky"].add_restriction(date(2024, 2, 29), date(2024, 3, 1))
hosts["spitkovsky"].add_restriction(date(2024, 3, 25), date(2024, 3, 29))
hosts["spitkovsky"].add_restriction(date(2024, 4, 8), date(2024, 4, 10))
hosts["spitkovsky"].add_restriction(date(2024, 4, 15), date(2024, 4, 18))
for wd in get_weekdays(2024, 2, exclude=["Monday", "Tuesday", "Wednesday", "Friday"]):
    hosts["spitkovsky"].add_restriction(wd, wd)
hosts["sur"].add_restriction(date(2024, 1, 1), date(2024, 2, 10))
hosts["goodman"].add_restriction(date(2024, 4, 11), date(2024, 4, 12))
hosts["kunz"].add_restriction(date(2024, 1, 1), date(2024, 1, 31))


# add dates to assign
hosts.add_dates(get_weekdays(2024, 1))
hosts.add_dates(get_weekdays(2024, 2))
hosts.add_dates(get_weekdays(2024, 3))
hosts.add_dates(get_weekdays(2024, 4))
hosts.add_dates(get_weekdays(2024, 5))

# exclude dates
Holidays = Hosts()
Holidays.from_json("../data/holidays_2024.json")
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
hosts.to_json("../data/hosts_2024_1.json")
