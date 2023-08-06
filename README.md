# Princeton Astro Coffee Host Management Scripts

* Astro Coffee Program: https://coffee.astro.princeton.edu/astroph-coffee/papers/today
* Astro Coffee Calendar: https://changgoo.github.io/AstroCoffee/intro.html

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
