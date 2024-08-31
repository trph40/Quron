import time
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import callback_query

from data.config import ADMINS
from handlers.users.Quran import quran_cmd
from keyboards.inline.choose_language import create_choosing_language_kb
from states.language_state import Language
from loader import dp, bot, db_users
from keyboards.default.List_of_books_kb import list_of_books

delete = bool


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    cmds = """
    /arabicAudio  -  Arabcha sura audio fayllarini kiritish.\n
    /uzbekAudio   -  O'zbekcha sura audio fayllarini kiritish\n
    """
    cmds_first_admin = """
    /getall_arabic  -  Barcha kiritilgan arabcha suralar sonini olish\n
    /getall_uzbek  -  Barcha kiritilgan o'zbekcha suralar sonini olish
    """
    if str(message.from_user.id) in ADMINS:
        if str(message.chat.id) == ADMINS[0]:
            cmds = cmds+cmds_first_admin
        await message.answer(cmds)
    if db_users.get_user_language(id=int(message.from_user.id)) is None:
        greeting_message = f"""Assalomu alaykum, {message.from_user.full_name}. Bu yerda siz Qur'on kitobini o'qish uchun 
        barcha yo'llardan osonlikcha foydalanishingiz mumkin. Davom etish uchun iltimos tilni tanlang!\n\nAссалому 
        алайкум, {message.from_user.full_name}. Здесь вы можете легко использовать все способы чтения книги Корана. 
        Пожалуйста, выберите язык для продолжения! \n\n Assalomu alaykum, {message.from_user.full_name}. Here you can 
        easily use all the ways to read the Quran. Please choose a
        language to continue!"""
        await message.answer(text=greeting_message, reply_markup=create_choosing_language_kb)
        await Language.Choosing_language.set()
    else:
        await Language.Choosing_book.set()
        await quran_cmd(message, state)


@dp.callback_query_handler(state=Language.Choosing_language)
async def change_interface_language(call: callback_query.CallbackQuery, state: FSMContext):
    try:
        db_users.add_user(id=call.message.chat.id, language=str(call.data))
    except Exception:
        pass
    lang_changed = {
        "uzl":"Interfeys o'zbekchaga o'zgartirildi.",
        "uzk":"Интерфейс ўзбекчага ўзгартирилди.",
        "ru":"Интерфейс изменен на русский.",
        "en":"Interface was changed into English."
    }
    await call.message.answer(text=lang_changed[call.data])
    time.sleep(3)
    id = call.message.message_id+1
    await call.message.delete()
    await bot.delete_message(chat_id=call.message.chat.id, message_id=id)
    await Language.Choosing_book.set()
    await quran_cmd(call.message, state)







