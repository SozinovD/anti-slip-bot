import sqlite3
import os
from tables import tables_arr

import functions as funcs

def check_init(db_filename:str):
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  try:
    conn = sqlite3.connect(db_filename)
  except Exception as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()

  if os.stat(db_filename).st_size == 0:
    result = init_db(db_filename)
    return result

  return True

def init_db(db_filename:str):
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

def select(db_filename:str, table:str, fields:str='*', filters:str=None):
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

def add_many_records_to_db(db_filename:str, table:str, fields_arr:list):
  ''' fields is an array of arrys: [field_name, value] is one key=value pair in record
      'fields_arr' is a array of 'fields' arrs '''
  try:
    request_template = 'INSERT INTO {tbl_name} ({flds}) VALUES ({qstn_marks})'

    for fields in fields_arr:
      field_names = ''
      question_marks = ''
      values = ''
      conn = sqlite3.connect(db_filename)
      c = conn.cursor()
      for counter, field in enumerate(fields):
        field_names += field[0]
        question_marks += '?'
        values += str(field[1])
        if counter == len(fields) - 1:
          break
        field_names += ', '
        question_marks += ','
        values +='`'
      values = tuple(values.split('`'))

      request = request_template.format(tbl_name=table, flds=field_names, qstn_marks=question_marks)
      c.execute(request, (values))
      result = conn.commit()

    if result == None:
      result = fields_arr
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def add_record_to_db(db_filename:str, table:str, fields: dict):
  ''' fields is an array of arrys: [field_name, value] is one key=value pair in record '''
  try:
    request_template = 'INSERT INTO {tbl_name} ({flds}) VALUES ({qstn_marks})'
    field_names = ''
    question_marks = ''
    values = ''
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    for counter, field in enumerate(fields):
      field_names += field[0]
      question_marks += '?'
      values += str(field[1])
      if counter == len(fields) - 1:
        break
      field_names += ', '
      question_marks += ','
      values +='`'
    values = tuple(values.split('`'))

    request = request_template.format(tbl_name=table, flds=field_names, qstn_marks=question_marks)
    c.execute(request, (values))
    result = conn.commit()

    if result == None:
      result = fields
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def del_records_from_db(db_filename:str, table:str, filters:dict):
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

def update_records_in_db(db_filename:str, table:str, new_data:str, filters:str):
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
