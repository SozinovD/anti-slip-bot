from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import db_handler as db
import functions as funcs

config = funcs.read_config_file("configs/config.yaml")
storage = MemoryStorage()
bot = Bot(config["bot_token"])
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    ''' Allow user to cancel any action '''
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands="start")
async def show_help(message: types.Message):
    ''' Show help msg at start '''
    await message.answer(funcs.get_help_msg())


def main():
    db_started = db.start(config["db_filename"])
    print('Start db:', db_started)

    executor.start_polling(dp)


if __name__ == "__main__":
    main()