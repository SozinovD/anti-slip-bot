import db_handler as db
import datetime
from matplotlib import pyplot as plt
import yaml
import os, os.path
from io import BytesIO
import keyboards as kb
import random

help_msg = '''
This bot messages you once a random time to get you out of tiktok addiction or any other useless activities

List of commands:
/start - start bot with default settings and show help
/setup - change settings
/now - send message now
/cancel - cancel current action and return to default state
/stop - stop sending messages
'''

def read_config_file(filename:str):
    ''' Open config file, return dict '''
    config = dict()
    file_ext = os.path.splitext(filename)[1]
    if file_ext == '.yaml' or file_ext == '.yml':
        with open(filename, "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError:
                print(f"ERROR: {filename} is corrupted")
                exit(1)
    return config

def get_help_msg():
  ''' Just return help msg '''
  return help_msg

def day_end_ts(t:datetime):
  ''' Return end of the day '''
  dt = t.replace(second=59, microsecond=59, minute=59, hour=23)
  ts = int(dt.timestamp())
  return str(ts)

def get_target_day_ts(days:int):
  ''' Return ts of end of the day that was N days ago '''
  today_end_ts = day_end_ts(datetime.datetime.now())
  days_ts_delta = days * 24 * 60 * 60
  target_date_ts = int(today_end_ts) - int(days_ts_delta)
  return target_date_ts

def get_graph(user_id:int, days:int):
  ''' Get graph of happiness dynamic for last N days '''

  target_day_ts = get_target_day_ts(days)
  filter = 'date_ts > ' + str(target_day_ts)
  records = db.get_recs_by_filter(user_id, filter)
  
  plt.figure()
  title_tmplt = 'happiness dynamic: {date_from} - {date_to}'
  title = title_tmplt.format(date_from=datetime.datetime.utcfromtimestamp(target_day_ts).strftime('%Y-%m-%d'), 
                             date_to=datetime.datetime.today().strftime('%Y-%m-%d'))
  plt.title(title)
  plt.xlabel('Date')
  plt.xticks(rotation=20)
  plt.ylabel('happiness (1-10)')

  dates_arr = []
  happiness_arr = []

  records.sort(key=lambda x: x.date_ts, reverse = False)

  for rec in records:
    dates_arr.append(datetime.datetime.utcfromtimestamp(rec.date_ts).strftime('%Y-%m-%d'))
    happiness_arr.append(rec.happiness)

  plt.plot(dates_arr, happiness_arr)
  plt.scatter(dates_arr, happiness_arr)
  plt.grid(ls=':')

  buff = BytesIO()

  plt.savefig(buff, format="png")

  buff.seek(0)

  return buff


def make_rec_readable(rec):
  ''' Make readable line with record info '''
  line_template = 'id = {id}\n' \
                  'date UTC: {date}\n' \
                  'happiness: {happiness}\n' \
                  'comment: {comment}'

  line = line_template.format(id=rec.id, date=datetime.datetime.utcfromtimestamp(rec.date_ts).strftime('%Y-%m-%d %H:%M:%S'),
                              happiness=rec.happiness, comment=rec.comment )
  return line

def send_messages():
  active_users = db.get_active_users()
  print(active_users)

def get_random_msg(user_id:int):
  messages = db.get_curr_settings(user_id)['messages'].split(',')
  return str(random.choice(messages)).strip("'")

def get_random_interval(user_id:int):
  max_interval = db.get_curr_settings(user_id)['period']
  return int(random.randint(int(max_interval/10), max_interval))

def get_curr_settings(user_id:int):
  settings_dict = db.get_user_settings(user_id)
  return f'''
- Send messages(0/1): {settings_dict['send_msg']}
- Timezone: {settings_dict['tz']}
- Work time: {settings_dict['worktime']}
- Period (minutes): {int(settings_dict['period']/60)}
- Messages: {settings_dict['messages']}
  '''
