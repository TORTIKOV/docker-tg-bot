from aiogram import Bot, types, Dispatcher
from config import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# Create the storage instance
storage = MemoryStorage()

# Pass the storage to the Dispatcher
dp = Dispatcher(bot, storage=storage)