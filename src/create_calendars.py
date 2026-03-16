"""Generate calendar/periods.json manifest and print assignment emails."""

from coffeehost import Hosts
import json
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

periods = [
    "2023_3",
    "2023_4",
    "2024_1",
    "2024_2",
    "2024_3",
    "2025_1",
    "2025_2",
    "2025_3",
    "2026_1",
]

for period in periods:
    tmphosts = Hosts()
    tmphosts.from_json(f"{dirname}/../data/hosts_{period}.json")
    newhosts += tmphosts
tmphosts.assignment_email(period=period)

# print assignments
tmphosts.show()

# write calendar/periods.json manifest for the static calendar page
holiday_years = ["2023", "2024", "2025", "2026"]
manifest = {"periods": periods, "holiday_years": holiday_years}
calendar_dir = os.path.join(dirname, "../calendar")
os.makedirs(calendar_dir, exist_ok=True)
with open(os.path.join(calendar_dir, "periods.json"), "w") as fp:
    json.dump(manifest, fp, indent=2)
print("Written calendar/periods.json")
