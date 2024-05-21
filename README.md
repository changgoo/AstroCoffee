# Princeton Astro Coffee Host Management Scripts

* Astro Coffee Program: https://coffee.astro.princeton.edu/astroph-coffee/papers/today
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


# Cron job setup

I created a bash script at $HOME to call the `send_reminder.py` script.

```sh
#!/bin/bash
python ~/Sources/AstroCoffee/src/send_reminder.py
```

Then, the following cron job is added by `crontabl -e`
```
00 21 * * * /bin/bash -l ./send_reminder.sh
```
