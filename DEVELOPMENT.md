# Development Log

## 2026-03-13 — GitHub Actions + SendGrid email reminders

Replaced local cronjob with a GitHub Actions scheduled workflow for sending AstroCoffee reminder emails via SendGrid.

**Files changed:**
- `.github/workflows/send_reminder.yml` — new daily workflow (cron `0 23 * * *`, ~6-7 PM ET); also supports `workflow_dispatch` for manual runs
- `src/coffeehost.py` — added `_send_email_sendgrid()` helper that parses email headers from the existing templates and sends via the SendGrid Python SDK; `write_daily_reminder` and `write_weekly_reminder` now prefer SendGrid when `SENDGRID_API_KEY` is set, falling back to `sendmail`
- `requirements.txt` — added `sendgrid`

**Setup required:**
- GitHub secret `SEND_GRID_API_KEY` must be set in repo settings
- Sender address (`changgoo@princeton.edu`) must be verified in SendGrid
