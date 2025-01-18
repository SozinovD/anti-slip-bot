# anti-slip-bot
This bot messages you once a random time to get you out of tiktok addiction or any other useless activities

Telegram token can be provided:
- by env var `TG_BOT_TOKEN` (priority)
- in config file, section `bot.token`

Env vars used:
| Key            | Content                                            | 
|----------------|----------------------------------------------------|
| `TG_BOT_TOKEN` | telegram bot token                                 |
| `CONFIG_FILE`  | override default config file (configs/config.yaml) |
| `TIMEZONE`     | override timezone                                  |
| `DB_FILENAME`  | override db filename mentioned in config           |

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
docker pull sozinovdm/anti_slip_bot
```
