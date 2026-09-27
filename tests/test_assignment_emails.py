"""Tests for manual Gmail assignment sending without network access."""

import os
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from coffeehost import Host, Hosts
from send_assignment_emails import prepare_drafts, send_assignments


def make_period(basedir: Path, period: str) -> None:
    """Create a small assignment period and its email template."""
    (basedir / "data").mkdir()
    (basedir / "templates").mkdir()
    template = Path(__file__).resolve().parents[1] / "templates" / "assignment.txt"
    (basedir / "templates" / "assignment.txt").write_text(template.read_text())
    hosts = Hosts()
    first = Host("Test One", "one@example.com")
    first.add_date(date(2026, 10, 5))
    second = Host("Test Two", "two@example.com")
    second.add_date(date(2027, 1, 11))
    hosts["one_t"] = first
    hosts["two_t"] = second
    hosts.to_json(str(basedir / "data" / f"hosts_{period}.json"))


def test_period_input_cannot_escape_data_directory(tmp_path: Path) -> None:
    """Reject malformed period names before reading assignment data."""
    with pytest.raises(ValueError, match="Period must look like"):
        prepare_drafts("../../private", basedir=tmp_path)


def test_live_send_uses_gmail_once_for_distinct_hosts(tmp_path: Path) -> None:
    """Send both current drafts through one authenticated SMTP session."""
    make_period(tmp_path, "2026_4")
    with (
        patch.dict(
            os.environ,
            {"GMAIL_USER": "gmail@example.com", "GMAIL_APP_PASSWORD": "test"},
        ),
        patch("send_assignment_emails.smtplib.SMTP_SSL") as smtp_class,
    ):
        smtp = smtp_class.return_value.__enter__.return_value
        smtp.send_message.return_value = {}
        assert send_assignments("2026_4", basedir=tmp_path) == 2

    smtp.login.assert_called_once_with("gmail@example.com", "test")
    assert smtp.send_message.call_count == 2
    calls = smtp.send_message.call_args_list
    assert {call.kwargs["to_addrs"][0] for call in calls} == {
        "one@example.com",
        "two@example.com",
    }
    for call in calls:
        assert call.kwargs["from_addr"] == "gmail@example.com"
        assert "changgoo@princeton.edu" in call.kwargs["to_addrs"]
        assert call.args[0]["From"] == "gmail@example.com"
