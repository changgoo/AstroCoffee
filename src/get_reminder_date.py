"""Print the ET date at midnight UTC for use in the send-reminder workflow."""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from send_reminder import et_date_at_midnight_utc

print(et_date_at_midnight_utc(date.today()))
