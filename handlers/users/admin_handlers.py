# from filters import AdminFilter
# from loader import dp, bot
# from aiogram import types
#
# @dp.message_handler(AdminFilter(), command='sendMessageToAll')
# async def send_message_to_All():
#     f = open("ids.txt", 'r')
#     num_list = f.split(',')
#     f.close()
#     text = """
#     Iltimos /start komandasini bosib botga start bering.\n\n
#     Илтимос /start командасини босиб ботга старт беринг.\n\n
#     Пожалуйста, отправьте команду /start для перезапуска бота.\n\n
#     Please, send command /start to restart the bot.
#     """
#     for value in num_list:
#         await bot.send_message(chat_id=int(value), text=text)