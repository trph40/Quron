from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils.db_api.sqlite import DatabaseForSurahs
from utils.db_api.db_cmds_for_users import DatabaseForUsers
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_surah = DatabaseForSurahs(path_to_db="data/surahs_file_id.db")
db_users = DatabaseForUsers(path_to_db="data/users.db")
