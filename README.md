# WOKObot

A bot to let me know when new ads pop up on the WOKO website. I really want to move out and there's no way to catch a room unless I cheat.

### How to run

To run in the background, just create a cron job:

```
    crontab -e
```

Then add the command to run every 5 minutes:

```
    */5 * * * * python run.py
```