"""Tests for recurring host availability and JSON compatibility."""

import json
import os
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from coffeehost import Host, Hosts


def test_weekday_restrictions_survive_assignment_and_json(tmp_path: Path) -> None:
    """Reject blocked weekdays before and after saving assignments."""
    hosts = Hosts()
    host = Host("Test Host", "test@example.com")
    host.add_weekday_restriction(0, 3)
    hosts["host_t"] = host
    hosts["backup_b"] = Host("Backup Host", "backup@example.com")
    hosts.add_dates([date(2026, 10, 5), date(2026, 10, 6)])
    hosts.assign_dates(verbose=False)

    assert host.hostdate == [date(2026, 10, 6)]
    path = tmp_path / "hosts.json"
    hosts.to_json(str(path))
    loaded = Hosts()
    loaded.from_json(str(path))
    restored = next(iter(loaded.hosts.values()))
    assert restored.weekday_restriction == [0, 3]
    assert not restored.test_available(date(2026, 10, 12))
    assert restored.test_available(date(2026, 10, 13))


def test_old_json_defaults_to_no_weekday_restrictions() -> None:
    """Load historical records that predate recurring restrictions."""
    original = Host("Test Host", "test@example.com")
    data = json.loads(original.to_json())
    del data["weekday_restriction"]
    loaded = Host()
    loaded.from_dict(data)
    assert loaded.weekday_restriction == []
    assert loaded.test_available(date(2026, 10, 5))


def test_merging_hosts_keeps_date_range_pairs() -> None:
    """Keep complete restriction windows when combining periods."""
    earlier = Host("Test Host", "test@example.com")
    later = Host("Test Host", "test@example.com")
    earlier.add_restriction(date(2026, 10, 5), date(2026, 10, 9))
    later.add_restriction(date(2026, 11, 2), date(2026, 11, 6))
    later.add_weekday_restriction(4)
    earlier += later

    assert earlier.restriction == [
        [date(2026, 10, 5), date(2026, 10, 9)],
        [date(2026, 11, 2), date(2026, 11, 6)],
    ]
    assert earlier.weekday_restriction == [4]


def test_assignment_reports_unfillable_weekday() -> None:
    """Fail clearly if every host is unavailable on a candidate date."""
    hosts = Hosts()
    host = Host("Test Host", "test@example.com")
    host.add_weekday_restriction(0)
    hosts["host_t"] = host
    hosts.add_dates([date(2026, 10, 5)])

    with pytest.raises(ValueError, match="No available host for 2026-10-05"):
        hosts.assign_dates(verbose=False)


def test_monthly_assignment_limit_survives_json() -> None:
    """Allow one assignment per month when a host has a monthly cap."""
    host = Host("Test Host", "test@example.com")
    host.set_monthly_limit(1)
    assert host.add_date(date(2027, 1, 11))
    assert not host.add_date(date(2027, 1, 29))
    assert host.add_date(date(2027, 2, 1))

    loaded = Host()
    loaded.from_json(host.to_json())
    assert loaded.monthly_limit == 1
    assert not loaded.test_available(date(2027, 1, 29))
    assert loaded.test_available(date(2027, 3, 1))
