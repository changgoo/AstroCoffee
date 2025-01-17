from coffeehost import Hosts
import os

dirname = os.path.dirname(__file__)

# initialize recent host list
hosts = Hosts()
periods = ["2024_1", "2024_2", "2024_3"]
for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    hosts += tmphosts

# show the available hosts
hosts.showlist()
