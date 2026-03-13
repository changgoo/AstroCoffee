# Development Log

## 2026-03-13 — Daily reminder template update

Updated `templates/daily_reminder.txt`:
- Replaced old astrocoffee program link with the new page (https://changgoo.github.io/astro-coffee-page/), keeping the old link as a reference
- Added feedback request for the new page
- Rewrote "Usual Information" section with separate Technical and Scientific bullet-point sections covering Owl setup, Zoom/Apple TV screen sharing, and how to run the coffee discussion

## 2026-03-13 — GitHub Actions + SendGrid email reminders

Replaced local cronjob with a GitHub Actions scheduled workflow for sending AstroCoffee reminder emails via SendGrid.

**Files changed:**
- `.github/workflows/send_reminder.yml` — new daily workflow (cron `0 23 * * *`, ~6-7 PM ET); also supports `workflow_dispatch` for manual runs
- `src/coffeehost.py` — added `_send_email_sendgrid()` helper that parses email headers from the existing templates and sends via the SendGrid Python SDK; `write_daily_reminder` and `write_weekly_reminder` now prefer SendGrid when `SENDGRID_API_KEY` is set, falling back to `sendmail`
- `requirements.txt` — added `sendgrid`

**Setup required:**
- GitHub secret `SEND_GRID_API_KEY` must be set in repo settings
- Sender address (`changgoo@princeton.edu`) must be verified in SendGrid
