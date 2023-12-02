#!/usr/bin/env python3

import classes

import time
from datetime import datetime
import sqlite3_requests as db_requests

from tables import tables_arr

import time

def start(db_filename:str):
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  return db_requests.check_init(db_filename)

def add_rec(db_filename:str, new_rec:dict):
  ''' Add new record to db, return result '''
  fields_arr = new_rec.get_arr()
  # print(fields_arr)
  result = db_requests.add_record_to_db(db_filename, 'records', fields_arr)
  if type(result) == type(list()):
    last_rec = get_last_n_recs(fields_arr[0][1], 1)[0]
    # print('last_rec', last_rec)
    new_rec.set_id(last_rec.id)
    return new_rec
  else:
    return result

def get_new_rec_num(db_filename:str):
  ''' Get last record num, return +1 '''
  try:
    last_rec_num = db_requests.select(db_filename, 'records')[-1][0]
    new_rec_num = int(last_rec_num) + 1
  except Exception as e:
    new_rec_num = 1
  return new_rec_num

def get_recs_all(db_filename:str):
  ''' Return all records from db in array '''
  rec_all_arr = []
  recs = db_requests.select(db_filename, 'records')
  new_rec = classes.Record()
  for rec in recs:
    rec_all_arr.append(new_rec.get_obj_from_arr(rec))
  return rec_all_arr

def get_recs_by_filter(db_filename:str, user_id:int, filters:str=None):
  ''' Return record selected by 'field':'value' for one user_id in array '''
  recs_arr = []
  filt = 'user_id="' + str(user_id) + '"'
  if filters != None:
    filt += ' AND ' + filters
  recs = db_requests.select(db_filename, 'records', '*', filt)
  # print('get_recs_by_filter: ', recs)
  new_rec = classes.Record()
  for rec in recs:
    recs_arr.append(new_rec.get_obj_from_arr(rec))
  return recs_arr

def get_last_n_recs(db_filename:str, user_id:int, rec_num:int):
  recs_arr = []
  min_num = get_new_rec_num(db_filename) - rec_num
  recs_arr = get_recs_by_filter(db_filename, user_id, 'id >= ' + str(min_num))
  return recs_arr

def del_last_rec_1_day(db_filename:str, user_id:int, forced:bool=False):
  ''' Delete last record if it was made less then 1 day ago '''
  last_rec = get_last_n_recs(db_filename,user_id, 1)[0]
  # if more than 1 day passed
  if round(time.time(), 0) - last_rec.date_ts > 86400 and forced == False:
    return 'Can\'t delete record older than 1 day'
  filters = 'id="' + str(last_rec.id) + '"'
  result = db_requests.del_records_from_db(db_filename, 'records', filters)
  if result == filters:
    result = 'Record deleted'
  return result
