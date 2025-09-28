from coffeehost import Hosts
import os

dirname = os.path.dirname(__file__)

# initialize host list with assigned dates from json file
newhosts = Hosts()
newhosts.from_json(f"{dirname}/../data/holidays_2026.json")
# old holidays
for year in ["2023", "2024", "2025"]:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/holidays_{year}.json")
    newhosts += tmphosts

periods = ["2023_3", "2023_4", "2024_1", "2024_2", "2024_3", "2025_1", "2025_2", "2025_3"]
for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    newhosts += tmphosts
tmphosts.assignment_email(period=period)

# print assignments
tmphosts.show()

# create calenders
j = 0
for i, month in enumerate(range(1, 0, -1)):
    newhosts.output_calendar(2026, month, num=j)
    j += 1
for i, month in enumerate(range(12, 0, -1)):
    newhosts.output_calendar(2025, month, num=j)
    j += 1
# old calendar with fixed number
for i, month in enumerate(range(12, 0, -1)):
    newhosts.output_calendar(2024, month, num=99)

for i, month in enumerate(range(12, 6, -1)):
    newhosts.output_calendar(2023, month, num=99)
