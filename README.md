# Princeton Astro Coffee Host Management Scripts

* Astro Coffee Program (new): https://changgoo.github.io/astro-coffee-page/
* Astro Coffee Program (old): https://coffee.astro.princeton.edu/astroph-coffee/papers/today
* Astro Coffee Calendar: https://changgoo.github.io/AstroCoffee/intro.html

# Create New Assignments

This is a semi-automated script, requiring quite a bit of human intervention.

First, update host information in `data/Coffee-Hosts-????.csv`.

Second, run the assignment script:

```sh
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
python create_calendars.py
```

Finally, get responses and update host assignments. The calendar will be updated automatically.


# Automated Reminders

Reminder emails are sent automatically via a GitHub Actions scheduled workflow (`.github/workflows/send_reminder.yml`), which runs daily at 02:00 UTC (~9 PM ET) using SendGrid.

- Daily reminders are sent the evening before a host's scheduled date.
- Weekly reminders are sent every Saturday with the coming week's schedule.

To trigger manually (e.g. for testing), use the `workflow_dispatch` trigger in the GitHub Actions UI. Providing a date runs in dry-run mode — emails are sent to `changgoo@princeton.edu` only instead of actual recipients.

**Setup:** add a `SEND_GRID_API_KEY` secret in the repo settings with a valid SendGrid API key.
