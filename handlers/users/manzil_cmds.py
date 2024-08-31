from aiogram import types

import requests as req
from aiogram.dispatcher import FSMContext

from handlers.users.Quran import quran_cmd
from keyboards.inline.kb_for_manzils import kb_endOfManzil, kb_manzil_option_to_continue
from loader import db_users, dp, bot
from states.language_state import Language
from utils.misc.transliterate import transliterate

lang = ''


async def get_json(manzil_num):
    arabic_arr = req.get(f"http://api.alquran.cloud/v1/manzil/{manzil_num}/quran-uthmani").json()['data']['ayahs']
    transliteration = req.get(f"http://api.alquran.cloud/v1/manzil/{manzil_num}/en.transliteration").json()['data'][
        'ayahs']
    translation_en_arr = req.get(f"http://api.alquran.cloud/v1/manzil/{manzil_num}/en.asad").json()['data']['ayahs']
    translation_ru_arr = req.get(f"http://api.alquran.cloud/v1/manzil/{manzil_num}/ru.porokhova").json()['data'][
        'ayahs']
    translation_uz_arr = req.get(f"http://api.alquran.cloud/v1/manzil/{manzil_num}/uz.sodik").json()['data']['ayahs']
    return arabic_arr, transliteration, translation_en_arr, translation_ru_arr, translation_uz_arr


@dp.callback_query_handler(state='manzil')
async def manzil_callbacks(call: types.callback_query, state: FSMContext):
    lang = db_users.get_user_language(id=call.message.chat.id)[0]

    if call.data == "next-ayahs-manzil":
        async with state.proxy() as data:
            data['latest-ayah'] = data['latest-ayah'] + 1
            manzil = data['manzil']
        await call.message.delete()
        await send_messages(call.message, state, manzil, lang)
    elif call.data == "calling-manzil":
        await call.message.delete()

        dig_n_manzil = {"uzl": "Boshqa manzil raqamini yuboring!", "uzk": "Бошқа манзил рақамини юборинг!",
            "ru": "Отправить другой номер манзили", "en": "Send another manzil number"}
        await state.set_state('manzil')
        async with state.proxy() as data:
            data['latest-ayah'] = 1
        await call.message.answer(text=dig_n_manzil[lang])
    elif call.data == "main-menu":
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)
    elif call.data == "back-manzil":
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)


async def make_msg(num, lang, arabic_arr, transliteration_arr, translation_uz_arr, translation_ru_arr,
                   translation_en_arr):
    arabicName = str(arabic_arr[num]['surah']['name']) + "\n"
    engName = str(arabic_arr[num]['surah']['englishName'])
    arabicVer = str(arabic_arr[num]['text']) + "\n"
    lit_version = str(transliteration_arr[num]['text']) + "\n"
    translation_uzk = str(translation_uz_arr[num]['text'])
    surahNum = str(arabic_arr[num]['surah']['number'])
    NumInSurah = str(arabic_arr[num]['numberInSurah'])
    ayat_num = NumInSurah
    translation_ru = str(translation_ru_arr[num]['text'])
    translation_en = str(translation_en_arr[num]['text'])

    if lang == 'uzl':
        engName = engName + " surasi\n"
        surahNum = surahNum + "-sura\n"
        NumInSurah = str(arabic_arr[num]['numberInSurah']) + "-oyat\n"
        translationF = transliterate(translation_uzk, 'latin') + "\n"
    elif lang == 'uzk':
        engName = transliterate(text=engName + " -сураси\n", to_variant='cyrillic') + "\n"
        surahNum = transliterate(text=surahNum + "-сура", to_variant='cyrillic') + '\n'
        NumInSurah = transliterate(text=str(arabic_arr[num]['numberInSurah']) + "-oyat", to_variant='cyrillic') + '\n'
        translationF = translation_uzk
    elif lang == 'ru':
        engName = "Сура " + transliterate(engName, 'cyrillic') + "\n"
        surahNum = "Номер суры: " + surahNum + "\n"
        NumInSurah = "Номер аяти: " + str(arabic_arr[num]['numberInSurah']) + "\n"
        translationF = translation_ru
    elif lang == 'en':
        engName = "Surah " + engName + "\n"
        surahNum = "Surah number: " + surahNum + "\n"
        NumInSurah = "Ayah: " + str(arabic_arr[num]['numberInSurah']) + "\n"
        translationF = translation_en
    if ayat_num == '1':
        text = arabicName + engName + surahNum + NumInSurah + arabicVer + lit_version + translationF
    else:
        text = NumInSurah + arabicVer + lit_version + translationF

    audioURl = f"https://cdn.islamic.network/quran/audio/128/ar.alafasy/{arabic_arr[num]['number']}.mp3"
    return audioURl, text, NumInSurah


async def send_messages(message: types.Message, state: FSMContext, manzil, lang):
    async with state.proxy() as data:
        st_ayah = data['latest-ayah']
    if st_ayah == 1:
        sending = {"uzl": "Yuborilmoqda...", "uzk": "Юборилмоқда...", "ru": "Oтправляю...", "en": "Sending..."}
        await message.reply(sending[lang])

    arabic_arr, transliteration_arr, translation_en_arr, translation_ru_arr, translation_uz_arr = await get_json(manzil)

    if st_ayah == 1:
        if lang == 'uzl':
            await message.answer(str(manzil) + "-manzil")
        elif lang == 'uzk':
            await message.answer(str(manzil) + "-манзил")
        elif lang == 'ru':
            await message.answer("Манзил номер: " + str(manzil))
        elif lang == 'en':
            await message.answer("Manzil number: " + str(manzil))

    if st_ayah + 10 > len(arabic_arr):
        lt_ayah = len(arabic_arr)
    else:
        lt_ayah = st_ayah + 9
        rem_ayahs = 10
    for i in range(st_ayah - 1, lt_ayah):
        audioURL, text, numberInSurah = await make_msg(i, lang, arabic_arr, transliteration_arr, translation_uz_arr,
                                                       translation_ru_arr, translation_en_arr)
        if len(text) > 4096:
            firstpart, secondpart = text[:len(text) // 2], text[len(text) // 2:]
            await bot.send_audio(chat_id=message.chat.id, audio=audioURL, caption=numberInSurah)
            await message.answer(text=firstpart)
            await message.answer(text=secondpart)
        elif len(text) > 1024:
            await bot.send_audio(chat_id=message.chat.id, audio=audioURL, caption=numberInSurah)
            await message.answer(text=text)
        else:
            await bot.send_audio(chat_id=message.chat.id, audio=audioURL, caption=text)

    if lt_ayah + 10 > len(arabic_arr):
        rem_ayahs = len(arabic_arr) - st_ayah - 9

    if lt_ayah == len(arabic_arr):
        end_manzil = {"uzl": "Manzil oxiriga yetdingiz. Pastdagilardan birini tanlang!",
            "uzk": "Манзил охирига етдингиз. Пастдагилардан бирини танланг!",
            "ru": "Вы дошли до конца манзили. Выберите один ниже!",
            "en": "You've reached the end of this manzil. Please choose one of the options below!"}
        await message.answer(text=end_manzil[lang], reply_markup=kb_endOfManzil(lang))
        await state.set_state('manzil-end')
    else:
        ch_bel = {"uzl": "Pastdagilardan birini tanlang!", "uzk": "Пастдагилардан бирини танланг!",
            "ru": "Выберите один ниже!", "en": "Please choose one of the options below!"}
        await message.answer(text=ch_bel[lang], reply_markup=kb_manzil_option_to_continue(rem_ayahs, lang))
    async with state.proxy() as data:
        data['latest-ayah'] = lt_ayah


@dp.message_handler(state='manzil')
async def checkNumber(message: types.Message, state: FSMContext):
    global lang
    lang = db_users.get_user_language(id=message.chat.id)[0]
    if message.text.isdigit() == False:
        en_num = {"uzl": "Iltimos raqam kiriting!", "uzk": "Илтимос рақам киритинг!",
            "ru": "Пожалуйста, введите номер!", "en": "Please, enter number!"}
        await message.answer(en_num[lang])
    else:
        manzil = int(message.text)
    if manzil > 7 or manzil < 1:
        en_num_limit = {"uzl": "Iltimos 1 va 7 orasida bo'lgan raqam kiriting!",
            "uzk": "Илтимос 1 ва 7 орасида бўлган рақам киритинг!", "ru": "Пожалуйста, введите число от 1 до 7!",
            "en": "Please, enter a number between 1 and 7, inclusively!"}
        await message.answer(en_num_limit[lang])
    else:
        async with state.proxy() as data:
            data['manzil'] = manzil
        await send_messages(message, state, manzil, lang)
