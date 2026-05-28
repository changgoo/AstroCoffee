# Princeton Astro Coffee Host Management Scripts

* Astro Coffee Program (new): https://changgoo.github.io/astro-coffee-page/
* Astro Coffee Program (old): https://coffee.astro.princeton.edu/astroph-coffee/papers/today
* Astro Coffee Calendar: https://changgoo.github.io/AstroCoffee/

The repo contains the assignment scripts, reminder email templates, and the
static calendar site used on GitHub Pages.

# Create New Assignments

This is a semi-automated script, requiring quite a bit of human intervention.

First, update host information in `data/Coffee-Hosts-????.csv`.

Second, run the assignment script:

```sh
cd src/
python assign_hosts.py
```

Before running this script, a few manual updates maybe needed.
* Update the output file name
* Update the host list
* Update the holiday file (including colloquium schedule)
* Add restrictions
* Add months to assign

Third, run the script to create assignment emails and calendar.

```sh
cd src/
python create_calendars.py
```

This writes the `calendar/periods.json` manifest and copies the static calendar
files into `_site/` during the build step.

Finally, get responses and update host assignments. The calendar will be updated automatically.

## Local Calendar Preview

Build and serve the static calendar locally from the repo root:

```sh
make serve
```

This builds `_site/` and serves it at `http://localhost:8080/`.

If you only want to build the files without serving them:

```sh
make build
```

The calendar pulls `calendar/periods.json` and `data/*.json` at runtime, so use
the served site rather than opening `calendar/index.html` directly from disk.


# Automated Reminders

Reminder emails are sent automatically via a GitHub Actions scheduled workflow (`.github/workflows/send_reminder.yml`) using Gmail app-password credentials.

- Daily reminders are sent the evening before a host's scheduled date.
- Weekly reminders are sent every Saturday with the coming week's schedule.

To trigger manually (e.g. for testing), use the `workflow_dispatch` trigger in the GitHub Actions UI. Providing a date runs in dry-run mode — emails are sent to `changgoo@princeton.edu` only instead of actual recipients.

**Setup:** add `GMAIL_USER` and `GMAIL_APP_PASSWORD` secrets in the repo settings.

## Requesting Assignment Changes

The calendar includes a `Request Change` link in the latest-term panel. It
opens a GitHub issue template with fields for:

* Original assignment date
* Proposed swap or new hosting date

Use that for swap requests or schedule corrections instead of editing the data
manually.
