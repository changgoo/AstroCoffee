"""Tests for reminder scheduling logic in coffeehost.py and send_reminder.py."""

import os
import sys
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from coffeehost import Host, Hosts
from send_reminder import et_date_at_midnight_utc

ET = ZoneInfo("America/New_York")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_hosts_with_date(host_date: date) -> Hosts:
    """Return a Hosts instance with one host assigned to *host_date*."""
    h = Host("Test User", "test@example.com")
    h.hostdate = [host_date]
    hosts = Hosts()
    hosts["testuser"] = h
    return hosts


# ---------------------------------------------------------------------------
# Daily reminder trigger
# ---------------------------------------------------------------------------


class TestDailyReminderTrigger:
    """generate_reminder should send a daily reminder iff tomorrow has a host."""

    def test_fires_when_tomorrow_has_host(self, tmp_path):
        """Daily reminder fires when tomorrow's date has an assigned host."""
        today = date(2026, 3, 16)  # Monday
        tomorrow = today + timedelta(days=1)
        hosts = make_hosts_with_date(tomorrow)

        with patch.object(hosts, "write_daily_reminder") as mock_daily, patch.object(
            hosts, "write_weekly_reminder"
        ) as mock_weekly:
            hosts.generate_reminder(today=today, send=False, basedir=str(tmp_path))

        mock_daily.assert_called_once()
        mock_weekly.assert_not_called()

    def test_skips_when_tomorrow_has_no_host(self, tmp_path):
        """Daily reminder is skipped when no host is assigned to tomorrow."""
        today = date(2026, 3, 16)  # Monday, nothing assigned Tuesday
        hosts = Hosts()

        with patch.object(hosts, "write_daily_reminder") as mock_daily, patch.object(
            hosts, "write_weekly_reminder"
        ) as mock_weekly:
            hosts.generate_reminder(today=today, send=False, basedir=str(tmp_path))

        mock_daily.assert_not_called()
        mock_weekly.assert_not_called()

    def test_targets_tomorrow_not_today(self, tmp_path):
        """Daily reminder passes tomorrow's date, not today's, to write_daily_reminder."""
        today = date(2026, 3, 16)  # Monday
        tomorrow = date(2026, 3, 17)  # Tuesday
        hosts = make_hosts_with_date(tomorrow)

        with patch.object(hosts, "write_daily_reminder") as mock_daily:
            hosts.generate_reminder(today=today, send=False, basedir=str(tmp_path))

        _, called_day = mock_daily.call_args[0][:2]
        assert called_day == tomorrow


# ---------------------------------------------------------------------------
# Weekly reminder trigger
# ---------------------------------------------------------------------------


class TestWeeklyReminderTrigger:
    """generate_reminder should send a weekly reminder only on Saturday."""

    def test_fires_on_saturday(self, tmp_path):
        """Weekly reminder fires when today (ET) is Saturday."""
        today = date(2026, 3, 14)  # Saturday
        assert today.weekday() == 5
        hosts = Hosts()

        with patch.object(hosts, "write_weekly_reminder") as mock_weekly:
            hosts.generate_reminder(today=today, send=False, basedir=str(tmp_path))

        mock_weekly.assert_called_once()

    @pytest.mark.parametrize(
        "today",
        [
            date(2026, 3, 16),  # Monday
            date(2026, 3, 17),  # Tuesday
            date(2026, 3, 18),  # Wednesday
            date(2026, 3, 19),  # Thursday
            date(2026, 3, 20),  # Friday
            date(2026, 3, 15),  # Sunday
        ],
    )
    def test_does_not_fire_on_non_saturday(self, today, tmp_path):
        """Weekly reminder is not sent on any day other than Saturday."""
        hosts = Hosts()

        with patch.object(hosts, "write_weekly_reminder") as mock_weekly:
            hosts.generate_reminder(today=today, send=False, basedir=str(tmp_path))

        mock_weekly.assert_not_called()

    def test_weekly_covers_monday_to_friday(self, tmp_path):
        """Weekly reminder covers the Mon–Fri immediately following Saturday."""
        today = date(2026, 3, 14)  # Saturday
        expected = [
            date(2026, 3, 16),  # Monday
            date(2026, 3, 17),  # Tuesday
            date(2026, 3, 18),  # Wednesday
            date(2026, 3, 19),  # Thursday
            date(2026, 3, 20),  # Friday
        ]
        hosts = Hosts()

        with patch.object(hosts, "write_weekly_reminder") as mock_weekly:
            hosts.generate_reminder(today=today, send=False, basedir=str(tmp_path))

        _, dlist = mock_weekly.call_args[0][:2]
        assert dlist == expected


# ---------------------------------------------------------------------------
# ET timezone correctness
# ---------------------------------------------------------------------------


class TestETTimezone:
    """Verify that 02:00 UTC maps to the previous calendar day in ET."""

    def test_02_utc_tuesday_is_monday_et(self):
        """02:00 UTC on Tuesday equals 9 PM ET on Monday (UTC-5 winter)."""
        utc_dt = datetime(2026, 3, 17, 2, 0, tzinfo=timezone.utc)  # Tuesday UTC
        et_date = utc_dt.astimezone(ET).date()
        assert et_date == date(2026, 3, 16)  # Monday ET

    def test_02_utc_saturday_is_friday_et(self):
        """02:00 UTC Saturday is ET Friday — weekly reminder must NOT fire."""
        utc_dt = datetime(2026, 3, 14, 2, 0, tzinfo=timezone.utc)  # Saturday UTC
        et_date = utc_dt.astimezone(ET).date()
        assert et_date == date(2026, 3, 13)  # Friday ET
        assert et_date.weekday() == 4  # Friday, not Saturday

    def test_02_utc_sunday_is_saturday_et(self):
        """02:00 UTC Sunday is ET Saturday — weekly reminder SHOULD fire."""
        utc_dt = datetime(2026, 3, 15, 2, 0, tzinfo=timezone.utc)  # Sunday UTC
        et_date = utc_dt.astimezone(ET).date()
        assert et_date == date(2026, 3, 14)  # Saturday ET
        assert et_date.weekday() == 5  # Saturday

    def test_daily_reminder_uses_et_date_not_utc(self, tmp_path):
        """Using ET date ensures the daily reminder targets the correct host.

        At 02:00 UTC Tuesday, UTC tomorrow = Wednesday, but ET today = Monday
        so ET tomorrow = Tuesday — the correct host to remind about.
        """
        # ET today = Monday, ET tomorrow = Tuesday
        et_today = date(2026, 3, 16)   # Monday
        et_tomorrow = date(2026, 3, 17)  # Tuesday — should be reminded
        utc_tomorrow = date(2026, 3, 18)  # Wednesday — wrong if UTC date used

        hosts_et = make_hosts_with_date(et_tomorrow)
        hosts_utc = make_hosts_with_date(utc_tomorrow)

        with patch.object(hosts_et, "write_daily_reminder") as mock_et:
            hosts_et.generate_reminder(today=et_today, send=False, basedir=str(tmp_path))
        mock_et.assert_called_once()  # correct: ET tomorrow has a host

        utc_today = date(2026, 3, 17)  # Tuesday UTC (wrong date to pass)
        with patch.object(hosts_utc, "write_daily_reminder") as mock_utc:
            hosts_utc.generate_reminder(today=utc_today, send=False, basedir=str(tmp_path))
        mock_utc.assert_called_once()  # would miss ET Tuesday host if UTC used


# ---------------------------------------------------------------------------
# Scheduled run date pinning (delay-proof)
# ---------------------------------------------------------------------------


class TestScheduledDatePinning:
    """et_date_at_midnight_utc pins the reminder to the ET date at 00:00 UTC,
    so GitHub Actions delays never cause a midnight ET rollover."""

    def test_midnight_utc_monday_gives_sunday_et(self):
        """00:00 UTC Monday = 8 PM ET Sunday (EDT) — Sunday is the pinned date."""
        utc_date = date(2026, 3, 16)  # Monday UTC
        assert et_date_at_midnight_utc(utc_date) == date(2026, 3, 15)  # Sunday ET

    def test_pinned_date_matches_delayed_run(self):
        """Even if the job runs at 04:30 UTC (delayed), the pin gives Sunday ET."""
        # Delayed run: datetime.now(ET) would return Monday (wrong)
        delayed_utc_dt = datetime(2026, 3, 16, 4, 30, tzinfo=timezone.utc)
        actual_et_date = delayed_utc_dt.astimezone(ET).date()
        assert actual_et_date == date(2026, 3, 16)  # Monday — wrong without pinning

        # Pinned date: always Sunday regardless of delay
        pinned = et_date_at_midnight_utc(date(2026, 3, 16))
        assert pinned == date(2026, 3, 15)  # Sunday — correct

    def test_midnight_utc_sunday_gives_saturday_et(self):
        """00:00 UTC Sunday = 8 PM ET Saturday — weekly reminder fires correctly."""
        utc_date = date(2026, 3, 15)  # Sunday UTC
        et = et_date_at_midnight_utc(utc_date)
        assert et == date(2026, 3, 14)  # Saturday ET
        assert et.weekday() == 5  # Saturday → weekly reminder fires

    def test_midnight_utc_saturday_gives_friday_et(self):
        """00:00 UTC Saturday = 8 PM ET Friday — weekly reminder must NOT fire."""
        utc_date = date(2026, 3, 14)  # Saturday UTC
        et = et_date_at_midnight_utc(utc_date)
        assert et == date(2026, 3, 13)  # Friday ET
        assert et.weekday() == 4  # Friday → no weekly reminder
