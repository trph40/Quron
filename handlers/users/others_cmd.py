import time

from aiogram.dispatcher import FSMContext
from keyboards.inline.choose_language import create_choosing_language_kb
from loader import dp, db_surah, db_users
import sqlite3
from aiogram.types import Message, ContentTypes
from states.enter_file_id_states import getting_file_ids_for
from states.language_state import Language


@dp.message_handler(state='*', commands=['stop_bot'])
async def cancel_everything(message: Message, state: FSMContext):
    await state.finish()



@dp.message_handler(state='*', commands=['getall_arabic'])
async def getallAR(message: Message):
    num = db_surah.count_surahs_ar()[0]
    await message.answer(str(num) + " ta sura kiritilgan!")




@dp.message_handler(state='*', commands='change_language')
async def change_language(message: Message):
    lang = db_users.get_user_language(id=message.chat.id)[0]
    choose_lang = {
        "uzl": "Tilni tanlang!",
        "uzk": "Тилни танланг!",
        "ru": "Выберите язык ниже",
        "en": "Choose the language below!"
    }
    await message.answer(text=choose_lang[lang], reply_markup=create_choosing_language_kb)
    db_users.delete_user(id=message.chat.id)
    await Language.Choosing_language.set()



@dp.message_handler(state=getting_file_ids_for.write_ar, content_types=ContentTypes.AUDIO)
@dp.message_handler(state=getting_file_ids_for.write_uz, content_types=ContentTypes.AUDIO)
async def get_id_for_surah(message: Message, state: FSMContext):
    async with state.proxy() as data:
        num = data['surah-number']
    time.sleep(3)
    file_id = message.audio.file_id
    while str(await state.get_state()) == 'getting_file_ids_for:write_ar':
        try:
            db_surah.add_file_id_ar(surah_num=num, file_id=file_id)

        except sqlite3.IntegrityError as err:
            await message.answer(err)

    while str(await state.get_state()) == "getting_file_ids_for:write_uz":
        try:
            db_surah.add_file_id_uz(surah_num=num, file_id=file_id)

        except sqlite3.IntegrityError as err:
            await message.answer(err)
    async with state.proxy() as data:
        data['surah-number'] = num + 1


@dp.message_handler(state=getting_file_ids_for.check_uz)
@dp.message_handler(state=getting_file_ids_for.check_ar)
async def check_number(message: Message, state: FSMContext):
    number = int(message.text)
    if not message.text.isdigit() or (1 > number > 114):
        await message.answer("1 va 114 orasidagi raqamlardan birini kiriting!")
    else:
        if str(await state.get_state()) == 'getting_file_ids_for:check_ar':
            await message.answer("Arabcha sura audiosini yuboring!")
            await getting_file_ids_for.write_ar.set()

        elif str(await state.get_state()) == "getting_file_ids_for:check_uz":
            await message.answer("O'zbekcha sura audiosini yuboring!")
            await getting_file_ids_for.write_uz.set()
        async with state.proxy() as data:
            data['surah-number'] = number


@dp.message_handler(state='*', commands='arabicAudio')
async def add_arabic_audios(message: Message):
    await message.answer("Sura raqamini kiriting!")
    await getting_file_ids_for.check_ar.set()


@dp.message_handler(state='*', commands='uzbekAudio')
async def add_uzbek_audios(message: Message):
    await message.answer("boshlangich sura: ")
    await getting_file_ids_for.check_uz.set()
