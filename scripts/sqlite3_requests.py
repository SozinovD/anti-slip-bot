import sqlite3
import os
from tables import tables_arr

import functions as funcs

db_filename = funcs.read_config_file("configs/config.yaml")['server']["db_filename"]

def check_init():
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  try:
    conn = sqlite3.connect(db_filename)
  except Exception as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()

  if os.stat(db_filename).st_size == 0:
    result = init_db()
    return result

  return True

def init_db():
  ''' Init db, create tables, input default values '''
  print('Init db, filename:\'' + db_filename + '\'')
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # create tables
    for table in tables_arr:
      c.execute(table)
    # make sure changes are permanent
    conn.commit()
    return True
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()

def select(table:str, fields:str='*', filters:str=None):
  ''' Make SELECT request to db '''
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    request = 'SELECT ' + fields + ' FROM ' + table
    if not filters == None:
      request += ' WHERE ' + filters
    c.execute(request)

    result = c.fetchall()
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def count(table:str, fields:str='*', filters:str=None):
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    request = 'SELECT COUNT (*)' + fields + ' FROM ' + table
    if not filters == None:
      request += ' WHERE ' + filters
    c.execute(request)
    result = c.fetchall()
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result[0][0]

def add_many_records_to_db(table:str, fields_list:list):
  ''' fields is an array of arrys: [field_name, value] is one key=value pair in record
      'fields_list' is a array of 'fields' arrs '''
  try:
    request_template = 'INSERT INTO {tbl_name} ({flds}) VALUES ({qstn_marks})'

    for fields_dict in fields_list:
      field_names = ''
      question_marks = ''
      values = list()
      conn = sqlite3.connect(db_filename)
      c = conn.cursor()
      for counter, field in enumerate(fields_dict.keys()):
        field_names += field
        question_marks += '?'
        values.append(str(fields_dict[field]))
        if counter == len(fields_dict.keys()) - 1:
          break
        field_names += ', '
        question_marks += ','
      values = tuple(values)

      request = request_template.format(tbl_name=table, flds=field_names, qstn_marks=question_marks)
      c.execute(request, (values))
      result = conn.commit()

    if result == None:
      result = fields_list
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def add_record_to_db(table:str, fields_dict: dict):
  ''' fields dict: [field_name] = value is one key=value pair in record '''
  try:
    request_template = 'INSERT INTO {tbl_name} ({flds}) VALUES ({qstn_marks})'
    field_names = ''
    question_marks = ''
    values = list()
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    for counter, field in enumerate(fields_dict.keys()):
      field_names += field
      question_marks += '?'
      values.append(str(fields_dict[field]))
      if counter == len(fields_dict.keys()) - 1:
        break
      field_names += ', '
      question_marks += ','
    values = tuple(values)

    request = request_template.format(tbl_name=table, flds=field_names, qstn_marks=question_marks)
    c.execute(request, (values))
    result = conn.commit()

    if result == None:
      result = fields_dict
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def del_records_from_db(table:str, filters:str):
  ''' Delete records from any table in db by filters '''
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    request = 'DELETE FROM ' + table + ' WHERE ' + filters
    c.execute(request)
    result = conn.commit()
    if result == None:
      result = filters
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def update_records_in_db(table:str, new_data:str, filters:str):
  ''' Update records in db by filters '''
  try:
    request_template = 'UPDATE {tbl} SET {data} WHERE {fltrs}'
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    request = request_template.format(tbl=table, data=new_data, fltrs=filters)
    c.execute(request)
    result = conn.commit()

  except sqlite3.Error as e:
    return 'Error: ' + str(e)
  finally:
    if conn:
      conn.close()
  return result
