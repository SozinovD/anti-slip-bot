import db_handler as db
from aiogram import types
from datetime import datetime

def back_to_start_btn(divider:str):
  ''' Return btn with callback data that tells to go to start '''
  return types.InlineKeyboardButton(text='Back to start', callback_data=enc_callback_data(divider, 'back_to_start', '.'))

def enc_callback_data(divider:str, *words):
  ''' Encode data into one line for callback using a divider, return line '''
  call_data = ''
  for word in words:
    call_data += str(word) + str(divider)
  return call_data

def dec_callback_data(divider:str, call_data:str):
  ''' Decode data from callback using a divider, return in array '''
  data_arr = []
  for word in call_data.split(divider):
    data_arr.append(word)
  return data_arr

def setup():
  ''' Returns default keyboard for /add_record func  '''
  btn_list = []
  btn_list.append(['Timezone', 'set_tz'])
  btn_list.append(['Worktime', 'set_worktime'])
  btn_list.append(['Period', 'set_period'])
  btn_list.append(['Message text', 'set_msg_txt'])
  return get_btns_in_rows(2, btn_list)

def happiness():
  btn_list = list()
  for n in range(1,11):
    btn_list.append([n, f'happy_{n}'])
  return get_btns_in_rows(5, btn_list)

def get_btns_in_rows(columns_num, btn_data_arr):
  ''' Return keyboard that is sorted in rows and columns '''
  counter = 0
  btn_arr = []
  key = types.InlineKeyboardMarkup()
  for btn in btn_data_arr:
    if int(counter) >= int(columns_num):
      counter = 0
      key.row(*btn_arr)
      btn_arr = []
    counter += 1
    btn_arr.append(types.InlineKeyboardButton(text=btn[0], callback_data=btn[1]))
  if btn_arr:
    key.row(*btn_arr)
  return key
