from aiogram import types

from data.config import ADMINS


async def set_default_commands(dp):
    message: types.Message
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish. Начинать"),
            types.BotCommand("help", "Yordam. Помощь"),
            types.BotCommand("change_language", "Tilni o'zgartirish. Изменение языка"),
            types.BotCommand("stop_bot", "Botni to'xtatish. Остановка бота")
        ]
    )

