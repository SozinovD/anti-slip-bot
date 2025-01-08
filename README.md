# anti-slip-bot
This bot messages you once a random time to get you out of tiktok addiction or any other useless activities

Telegram token can be provided:
- by env var `TG_BOT_TOKEN` (priority)
- in config file, section `bot.token`

Commands:

```
start - start bot with default settings 
setup - change settings
now - send message now
cancel - cancel current action and return to default state
stop - stop sending messages
```

To use docker image just type

```
docker pull sozinovdm/anti_slilp_bot
```