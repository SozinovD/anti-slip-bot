from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import db_handler as db
import functions as funcs
import keyboards as kb
import asyncio
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import os

class Form(StatesGroup): # Will be represented in storage as 'Form:state'
  tz = State()
  worktime = State()
  period = State()
  msg_txt = State()

config_file = os.getenv("CONFIG_FILE")
if not config_file:
    print("Env 'CONFIG_FILE' is empty, use default: 'configs/config.yaml'")
    config_file = "configs/config.yaml"
print("CONFIG_FILE:", config_file)
config = funcs.read_config_file(config_file)
storage = MemoryStorage()

bot_token = os.getenv("TG_BOT_TOKEN")
if not bot_token:
    print("Token not found in 'TG_BOT_TOKEN' env var")

if not bot_token:
    try:
        bot_token = config.get("bot").get("token")
    except:
        print("Token not found in 'bot.token' section of config, exit")
        import sys
        sys.exit(1)

bot = Bot(bot_token)
dp = Dispatcher(bot, storage=storage)

# data_divider_in_callback = "`"

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    ''' Allow user to cancel any action '''
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands="start")
async def show_help(message: types.Message):
    ''' Show help msg at start, write default settings for new users'''
    db.add_def_settings(message.from_user.id, config['user']['default_send_period_sec'],
                         config['user']['default_messages'])
    db.change_setting(message.from_user.id, 'send_messages', 1)
    await message.answer(funcs.get_help_msg())

@dp.message_handler(commands="setup")
async def setup(message: types.Message):
    ''' Menu for changing settings '''
    await message.answer(f"Choose setting to change, current: \
                         {funcs.get_user_settings_readable(message.from_user.id)}", reply_markup=kb.setup())

@dp.message_handler(commands="now")
async def now(message: types.Message):
    await send_scheduled_message(message.from_user.id)

@dp.message_handler(commands="stop")
async def stop(message: types.Message):
    ''' Set "send_messages" to 0, so user won't get new messages '''
    db.change_setting(message.from_user.id, 'send_messages', 0)
    await message.answer("New messages will not be scheduled until you /start bot again")

@dp.callback_query_handler(Text('set_tz'))
async def set_tz(callback: types.CallbackQuery):
    ''' Change context, so handler of timezone change will catch next message '''
    await Form.tz.set()
    line = 'Send your timezone\n+6 or 6 means UTC+6\n-2 means UTC-2'
    await bot.send_message(callback.from_user.id, line, parse_mode="Markdown")

@dp.message_handler(state=Form.tz)
async def set_tz(message: types.Message, state: FSMContext):
    ''' Set new timezone '''
    tz = 0
    if message.text[0] == '+': tz = message.text[1:]
    else: tz = message.text
    try:
        tz = int(tz)
        if tz > 12 or tz < -12:
            await message.answer(f'Timezone out of range (from -12, to 12):\n{tz}')
        else:
            await message.answer(f'Set timezone to UTC{tz}')
            db.change_setting(message.from_user.id, 'tz', tz)
    except Exception:
        await message.answer(f'Should be number (from -12, to 12): {tz}')
    await state.finish()

@dp.callback_query_handler(Text('set_worktime'))
async def set_worktime(callback: types.CallbackQuery):
    line = 'Send bot worktime\n9-23 means it starts at 9:00, ends 23:00 according to your timezone'
    await bot.send_message(callback.from_user.id, line, parse_mode="Markdown")
    await Form.worktime.set()

@dp.message_handler(state=Form.worktime)
async def set_worktime(message: types.Message, state: FSMContext):
    ''' Set new worktime '''
    wt = message.text
    await message.answer(f"New worktime is set: '{wt}'")
    db.change_setting(message.from_user.id, 'worktime', wt)
    await state.finish()

@dp.callback_query_handler(Text('set_period'))
async def set_period(callback: types.CallbackQuery):
    line = 'Send period to send messages in minutes\n120 means they will be sent in some time every 120 minutes'
    await bot.send_message(callback.from_user.id, line, parse_mode="Markdown")
    await Form.period.set()

@dp.message_handler(state=Form.period)
async def set_period(message: types.Message, state: FSMContext):
    ''' Set new messaging period '''
    try:
        pd = int(message.text)
        await message.answer(f"New worktime is set: '{pd}' minutes")
        db.change_setting(message.from_user.id, 'period_sec', pd*60)
    except Exception:
        await message.answer("Invalid period, it should be just number of minutes, nothing else")
    await state.finish()

@dp.callback_query_handler(Text('set_msg_txt'))
async def set_msg_txt(callback: types.CallbackQuery):
    await Form.msg_txt.set()
    line = "Send every message in new line, current are:"
    await bot.send_message(callback.from_user.id, line, parse_mode="Markdown")
    await bot.send_message(callback.from_user.id, funcs.get_all_msg_readable(callback.from_user.id),
                            parse_mode="Markdown")

@dp.message_handler(state=Form.msg_txt)
async def set_msg_txt(message: types.Message, state: FSMContext):
    ''' Set new messages '''
    res = funcs.set_new_messages(message.from_user.id, message.text)
    if res == None: res = ""
    if len(res) != 0:
        await message.answer(res + " or type /cancel")
    else:
        await message.answer("New messages are set")
        await state.finish()

async def send_scheduled_message(user_id:int):
    ''' Send scheduled message with needed args '''
    # await bot.send_message(user_id, funcs.get_random_msg(user_id), reply_markup=kb.happiness())
    await bot.send_message(user_id, funcs.get_random_msg(user_id))

def message_schedule_loop(loop:asyncio.unix_events._UnixSelectorEventLoop, scheduler: AsyncIOScheduler):
    ''' Schedule messages, runs in loop '''
    loop.call_later(config['bot']['schedule_loop_timeout_sec'], message_schedule_loop, loop, scheduler)
    active_users = db.get_active_user_ids()
    curr_ts = int(datetime.timestamp(datetime.now()))
    for user_id in active_users:
        next_window_start_ts = db.get_next_window_start_ts(user_id)
        if next_window_start_ts == 0:
            print('Write new ts:', curr_ts)
            db.change_setting(user_id, 'next_window_start_ts', curr_ts)
            continue
        if next_window_start_ts < curr_ts:
            next_msg_interval = funcs.get_random_interval(user_id)
            nex_msg_date = datetime.fromtimestamp(curr_ts + next_msg_interval,
                                                      tz=timezone(timedelta(hours=config['server']['timezone']
                                                                            ))).strftime('%Y-%m-%d %H:%M:%S')
            print(f'Message to "{user_id}" will be sent at: {nex_msg_date}')
            scheduler.add_job(send_scheduled_message, 'date', run_date=nex_msg_date, args=(user_id,))
            db.change_setting(user_id, 'next_window_start_ts', curr_ts + int(db.get_user_settings(user_id)['period']))

def main():
    db_started = db.start()
    print('Start db:', db_started)

    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler()
    scheduler.start()
    message_schedule_loop(loop, scheduler)
    executor.start_polling(dp)

if __name__ == "__main__":
    main()
