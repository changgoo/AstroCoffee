# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AstroCoffee is a Python-based host management system for Princeton's Astrophysics Coffee talk program. It assigns faculty/postdocs to host weekly coffee talks, generates reminder emails, and publishes an interactive calendar via GitHub Pages.

## Common Commands

Run scripts from the `src/` directory (they use relative paths via `os.path.dirname(__file__)`):

```sh
cd src/
python assign_hosts.py       # Assign hosts for a new semester
python create_calendars.py   # Generate calendar markdown and assignment emails
python send_reminder.py      # Send daily/weekly reminder emails (also run via GitHub Actions)
python print_hosts.py        # Display current host list
```

Build and preview the calendar locally:
```sh
make serve   # builds _site/ and serves at http://localhost:8080
make build   # builds _site/ without serving
make clean   # removes _site/
```

Lint:
```sh
ruff check --fix
ruff format .
```

## Architecture

All core logic lives in `src/coffeehost.py` with two main classes:

- **`Host`** — represents one person; tracks assigned dates and unavailability windows (`restriction`). Key methods: `add_restriction(d1, d2)`, `add_date(date)`, `test_available(date)`, `to_json()`/`from_json()`.
- **`Hosts`** — dict-like container of `Host` objects; owns the assignment algorithm. Key methods: `assign_dates()` (round-robin), `find_host(date)`, `generate_reminder()`, `output_calendar()`, `to_json(fname)`/`from_json(fname)`.

**Data files** in `data/` (all JSON, version-controlled):
- `hosts_YYYY_Q.json` — host assignments per academic period (e.g. `2026_1`)
- `holidays_YYYY.json` — closures/colloquia stored as pseudo-hosts with blocked dates
- `Coffee-Hosts-YYYY-Q.csv` — raw CSV input from Google Form responses

**Calendar output**: `create_calendars.py` reads all period JSON files and writes `calendar/periods.json` (a manifest of periods and holiday years). The static calendar in `calendar/` (`index.html`, `calendar.js`, `style.css`) reads this manifest and fetches `data/*.json` directly at runtime. GitHub Actions (`deploy-calendar.yml`) assembles `calendar/` + `data/` into `_site/` and deploys to GitHub Pages. The old Jupyter Book calendar is preserved in the `archive` branch.

**Email flow**: Templates in `templates/` are filled via `.format(**kwargs)` and written to `emails/` (gitignored). Emails are sent via SendGrid (GitHub Actions sets `SENDGRID_API_KEY`); falls back to `sendmail` if the env var is absent.

**Reminder timing**: The cron fires at 02:00 UTC (~9 PM ET the previous day). `send_reminder.py` uses `datetime.now(ZoneInfo("America/New_York")).date()` so that "today" and "tomorrow" are always ET dates. Without this, the daily reminder would target the wrong host and the weekly reminder would fire on ET Friday instead of Saturday.

## New Assignment Workflow

### Step 1 — Collect responses
- Send out the Google Form to faculty/postdocs.
- Download the responses as a CSV and save to `data/Coffee-Hosts-YYYY-Q.csv` (e.g. `Coffee-Hosts-2026-2.csv`).

### Step 2 — Update the holidays file
- If the new period spans a new calendar year, create `data/holidays_YYYY.json` (copy and edit the previous year's file).
- Add or update entries for: colloquia Tuesdays, university recesses, and any other no-coffee days. Each entry is a pseudo-host object with a `name` and `hostdate` list (ISO date strings).

### Step 3 — Edit `assign_hosts.py`
The file has `# [Update this]` comments marking every field to change:
1. `outfile` — new period JSON path, e.g. `data/hosts_2026_2.json`
2. `hostfile` — CSV path from Step 1
3. Restriction blocks — add `hosts["lastname_firstinitial"].add_restriction(date(...), date(...))` for anyone with known conflicts
4. `hosts.add_dates(get_weekdays(...))` calls — add/remove months to cover the period
5. Holiday JSON files loaded into `Holidays` — include any new year's file from Step 2

### Step 4 — Run the assignment script
```sh
cd src/
python assign_hosts.py
```
Review the printed assignment list. If the distribution looks uneven or someone got a bad slot, manually edit the output `data/hosts_YYYY_Q.json` to swap dates between hosts (keep the JSON structure intact).

### Step 5 — Update `create_calendars.py`
1. Add the new period string to the `periods` list (e.g. `"2026_2"`).
2. Add the new year's holiday file to the loading block at the top if it's a new year.
3. Update the `output_calendar` loops to cover any new months/year.

### Step 6 — Generate the calendar and assignment emails
```sh
python create_calendars.py
```
This updates `calendar/periods.json` and prints assignment email commands for each host.

### Step 7 — Send assignment emails
Run the printed `cat ... | sendmail -t -oi` commands for each host, or pipe them together:
```sh
for f in ../emails/assignment_YYYY_Q_*.txt; do cat "$f" | sendmail -t -oi; done
```

### Step 8 — Update `send_reminder.py`
Add the new period to the `periods` list so the GitHub Actions workflow picks up the new assignments when sending daily/weekly reminders.

### Step 9 — Deploy the calendar
Push to `main`. GitHub Actions (`deploy-calendar.yml`) will automatically assemble and deploy the static calendar to GitHub Pages.

## Python Coding Standards

When editing or writing any Python file:
- Add short docstrings to all functions, methods, and classes.
- Add type hints to all function/method signatures.
- Run `ruff format <file>` on the file after editing.

## Key Conventions

- Hosts are keyed in the `Hosts` dict as `"lastname_firstinitial"` (e.g. `"kim_c"`).
- Holidays/closures are stored as a `Hosts` object in JSON using the same `Host` data model, but without real email addresses; `find_host()` returns them for calendar display.
- Scripts must be run from `src/` or paths break (they use `os.path.dirname(__file__)` to anchor relative paths).
- The `emails/` directory and `*.md` files in the repo root are gitignored.
