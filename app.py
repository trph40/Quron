from aiogram.utils import executor

from loader import dp, db_surah, db_users
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)

    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)
    try:
        db_surah.create_table_surah_audio_ar()
    except Exception as err:
        pass
    try:
        db_surah.create_table_surah_audio_uz()
    except Exception as err:
        pass
    try:
        db_users.create_table_users()
    except Exception as err:
        pass



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
