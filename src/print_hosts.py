from coffeehost import Hosts
import os

dirname = os.path.dirname(__file__)

# initialize recent host list
hosts = Hosts()
periods = ["2026_1"]
for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    hosts += tmphosts

hosts.assignment_email(period=period)
# show the available hosts
hosts.show()