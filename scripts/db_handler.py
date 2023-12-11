from classes import Record

import time
from datetime import datetime
import sqlite3_requests as db_requests
import time

messages_list = { "Как настроение?", "Что ты сейчас хочешь?", "Может, пора поесть?", "Ты устал?", 
                 "Хочешь переключиться?", "Может, пришло время сделать паузу?", "Тело в порядке?"
                 }

def start():
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  return db_requests.check_init()

def add_def_settings(user_id:int, period_sec:int):
  ''' Add default settings for new user '''
  if db_requests.count("settings", 'user_id', f'user_id={user_id}') != 0:
    print("User already exists")
    return
  messages_str = str()
  for line in messages_list:
    messages_str += line + "/"
  def_settings = {"user_id": user_id,
                  "send_messages": 1,
                  "tz": "6",
                  "period_sec": period_sec,
                  "worktime": "9-23",
                  "messages": messages_str,
                  "next_window_start_ts": 0}
  db_requests.add_record_to_db('settings', def_settings)

def change_setting(user_id:int, set_name:str, set_val):
  ''' Change one setting for this user '''
  return db_requests.update_records_in_db("settings", f'{set_name}={set_val}', f'user_id={user_id}')

def get_active_user_ids():
  ''' Returns users that have 1 in "send_messages" field '''
  result = list()
  for id in db_requests.select('settings', 'user_id', 'send_messages=1'): result.append(id[0])
  return list(result)

def get_next_window_start_ts(user_id:int):
  ''' Return start of next "window for message" for this user '''
  return int(db_requests.select('settings', 'next_window_start_ts', f'user_id={user_id}')[0][0])

def get_user_settings(user_id:int):
  settings = list(db_requests.select("settings", filters=f"user_id={user_id}")[0])[2:]
  settings_dict = {'send_msg': settings[0],
                   'tz': settings[1],
                   'worktime': settings[2],
                   'period': settings[3],
                   'messages': settings[4]}
  return settings_dict

def add_rec(new_rec:Record):
  ''' Add new record to db, return result '''
  fields_dict = new_rec.get_dict()
  # print(fields_dict)
  result = db_requests.add_record_to_db('records', fields_dict)
  if type(result) == type(list()):
    last_rec = get_last_n_recs(fields_dict[0][1], 1)[0]
    # print('last_rec', last_rec)
    new_rec.set_id(last_rec.id)
    return new_rec
  else:
    return result

def get_new_rec_num():
  ''' Get last record num, return +1 '''
  try:
    last_rec_num = db_requests.select('records')[-1][0]
    new_rec_num = int(last_rec_num) + 1
  except Exception as e:
    new_rec_num = 1
  return new_rec_num

def get_recs_all():
  ''' Return all records from db in array '''
  rec_all_list = list()
  recs = db_requests.select('records')
  new_rec = Record()
  for rec in recs:
    rec_all_list.append(new_rec.get_obj_from_arr(rec))
  return rec_all_list

def get_recs_by_filter(user_id:int, filters:str=None):
  ''' Return record selected by 'field':'value' for one user_id in array '''
  rec_list = list()
  filt = 'user_id="' + str(user_id) + '"'
  if filters != None:
    filt += ' AND ' + filters
  recs = db_requests.select('records', '*', filt)
  # print('get_recs_by_filter: ', recs)
  new_rec = Record()
  for rec in recs:
    rec_list.append(new_rec.get_obj_from_arr(rec))
  return rec_list

def get_last_n_recs(user_id:int, rec_num:int):
  ''' Return last N records, for example 5 '''
  rec_list = list()
  min_num = get_new_rec_num() - rec_num
  rec_list = get_recs_by_filter(user_id, 'id >= ' + str(min_num))
  return rec_list

def del_last_rec_1_day(user_id:int, forced:bool=False):
  ''' Delete last record if it was made less then 1 day ago '''
  last_rec = get_last_n_recs(user_id, 1)[0]
  # if more than 1 day passed
  if round(time.time(), 0) - last_rec.date_ts > 86400 and forced == False:
    return 'Can\'t delete record older than 1 day'
  filters = 'id="' + str(last_rec.id) + '"'
  result = db_requests.del_records_from_db('records', filters)
  if result == filters:
    result = 'Record deleted'
  return result
