import requests as req
from keyboards.default.List_of_books_kb import list_of_books
from loader import dp, bot, db_surah, db_users
from aiogram import types
from aiogram.dispatcher import FSMContext
from states.states_for_Quran import states_for_Quran
from states.language_state import Language
from .Quran import quran_cmd
from utils.misc import surahs_and_juzs_info
number_of_ayahs_in_every_surah = surahs_and_juzs_info.number_of_ayahs_in_every_surah
from utils.misc.transliterate import transliterate
from keyboards.inline.kb_for_surahs import end_surah, kb_surah_option_to_continue, ten_ayahs



@dp.callback_query_handler(state=states_for_Quran.surah)
async def sending_list_of_surahs(call: types.callback_query, state: FSMContext):
    msg = {
        "uzl": "Yuqorida berilgan suralardan birini tanlang va sura raqamini yuboring!",
        "uzk": "Юқорида берилган суралардан бирини танланг ва сура рақамини юборинг!",
        "ru": "Выберите одну из сур, приведенных выше, и укажите номер суры!",
        "en": "Choose one of the surahs above and send the number!"
    }
    sending = {
        "uzl": "Yuborilmoqda...",
        "uzk": "Юборилмоқда...",
        "ru": "Oтправляю...",
        "en": "Sending..."
    }

    lang = db_users.get_user_language(id=call.message.chat.id)[0]

    if call.data == 'list-of-surahs':
        await call.message.answer(text=sending[lang])
        line1, line2, line3, line4 = await surahs_and_juzs_info.Names_of_surahs(lang)

        await call.message.answer(text=line1)
        await call.message.answer(text=line2)
        await call.message.answer(text=line3)
        await call.message.answer(text=line4)
        await call.message.answer(text=msg[lang])
        print(line1)
        print(line2)
        print(line3)
        print(line4)
    elif call.data == "choose-Quran-reading-options":
        await quran_cmd(call.message, state)
    elif call.data == "main-menu":
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)




@dp.callback_query_handler(state=states_for_Quran.ayah)
@dp.callback_query_handler(state=states_for_Quran.choosing_end_surah)
async def send_10_ayahs(call: types.callback_query.CallbackQuery, state: FSMContext):
    lang = db_users.get_user_language(id=call.message.chat.id)[0]
    if call.data == "next-10-ayahs":
        await call.message.delete()

        async with state.proxy() as data:
            data['one-ayah'] = False
        await sending_ayahs(call.message, state)
    elif call.data == "another-surah":
        await call.message.delete()

        async with state.proxy() as data:
            data['latest-ayah'] = 1
        dig_n_surah = {
            "uzl":"Boshqa sura raqamini yuboring!",
            "uzk":"Бошқа сура рақамини юборинг!",
            "ru":"Отправить другой номер суры",
            "en":"Send another surah number"
        }
        await states_for_Quran.surah.set()
        await call.message.answer(text=dig_n_surah[lang])

    elif call.data == "main-menu":
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)
    elif call.data == "next-ayah":
        await call.message.delete()
        async with state.proxy() as data:
            data['one-ayah'] = True
        await sending_ayahs(call.message, state)
    elif call.data == "full-surah-audio":
        await call.message.delete()
        await sendAudio_ar(call.message, state)
    elif call.data == 'full-surah-audio-uz':
        await call.message.delete()
        await sendAudio_uz(call.message, state)

def making_msg(ayah, arabic, transliteration, translation, lang, translation_ru, translation_en):
    audioURL = f"https://cdn.islamic.network/quran/audio/64/ar.alafasy/{arabic['ayahs'][ayah]['number']}.mp3"
    ayah_num = str(arabic['ayahs'][ayah]['numberInSurah'])
    arabic_ver = str(arabic['ayahs'][ayah]['text']) + "\n"
    lit_ver = str(transliteration[ayah]['text']) + "\n"
    translation_uzk = str(translation[ayah]['text'])
    trans_ru = str(translation_ru[ayah]['text'])
    trans_en = str(translation_en[ayah]['text'])
    if lang == 'uzl':
        ayah_num = ayah_num + "-oyat\n"
        lit_ver = "Transliteratsiya: \n" + lit_ver + "\n"
        translation = "Tarjima: \n" + transliterate(translation_uzk, "latin") + "\n"
    elif lang == 'uzk':
        ayah_num = ayah_num + "-оят\n"
        lit_ver = "Транслитерация: \n" + lit_ver + "\n"
        translation = translation_uzk + "\n"
    elif lang == 'ru':
        ayah_num = "Aят " + ayah_num + "\n"
        lit_ver = "Транслитерация: \n" + lit_ver+ "\n"
        translation = "Перевод: \n" + trans_ru + "\n"
    elif lang == 'en':
        ayah_num = "Ayah " + ayah_num + "\n"
        lit_ver = "Transliteration: \n" + lit_ver + "\n"
        translation = "Translation: \n" + trans_en + "\n"

    text = ayah_num + arabic_ver + lit_ver + translation
    return text, audioURL, ayah_num


def get_json(surahNum):
    arabic = req.get(
        f"http://api.alquran.cloud/v1/surah/{surahNum}").json()['data']
    transliteration = \
        req.get(
            f"http://api.alquran.cloud/v1/surah/{surahNum}/editions/en.transliteration").json()['data'][0]['ayahs']
    translation = req.get(
        f"http://api.alquran.cloud/v1/surah/{surahNum}/editions/uz.sodik").json()['data'][0]['ayahs']

    translation_ru = req.get(f"http://api.alquran.cloud/v1//surah/{surahNum}/editions/ru.porokhova").json()['data'][0]['ayahs']
    translation_en = req.get(f"http://api.alquran.cloud/v1//surah/{surahNum}/editions/en.ahmedali").json()['data'][0][
        'ayahs']

    return arabic, transliteration, translation, translation_ru, translation_en


async def sending_ayahs(message: types.Message, state: FSMContext):
    lang = db_users.get_user_language(id=message.chat.id)[0]
    async with state.proxy() as data:
        surahNum = data['surah-number']
        st_ayah = data['latest-ayah']
        one_ayah = data['one-ayah']


    arabic, transliteration, translation, translation_ru, translation_en = get_json(surahNum)
    if st_ayah == 1:
        if lang == 'uzl':
            await message.answer(str(arabic['englishName']) + " surasi. " + str(arabic['number']) + "-sura.")
        if lang == 'uzk':
            await message.answer(
                transliterate(str(arabic['englishName']), 'cyrillic') + " сураси. " + str(arabic['number']) + "-сура.")
        if lang == 'ru':
            await message.answer(
                "Сура " + transliterate(str(arabic['englishName']), 'cyrillic') + str(arabic['number']))
        if lang == 'en':
            await message.answer("Surah " + str(arabic['englishName']) + "Surah number: " + str(arabic['number']))

    if one_ayah == True:
        lt_ayah = st_ayah
        rem_ayahs = 10
    elif one_ayah == True and st_ayah + 10 > number_of_ayahs_in_every_surah[surahNum]:
        lt_ayah = st_ayah
    elif st_ayah + 10 > number_of_ayahs_in_every_surah[surahNum]:
        lt_ayah = number_of_ayahs_in_every_surah[surahNum]
        rem_ayahs = number_of_ayahs_in_every_surah[surahNum] - st_ayah
    else:
        lt_ayah = st_ayah + 9
        rem_ayahs = 10
    for i in range(st_ayah - 1, lt_ayah):
        caption, audio, ayah_num = making_msg(
            i, arabic, transliteration, translation, lang, translation_ru, translation_en)
        if len(caption) > 4096:
            firstpart, secondpart = caption[:len(
                caption) // 2], caption[len(caption) // 2:]
            await bot.send_audio(chat_id=message.chat.id, audio=audio, caption=ayah_num)
            await message.answer(text=firstpart)
            await message.answer(text=secondpart)
        elif len(caption) > 1024:
            await bot.send_audio(chat_id=message.chat.id, audio=audio, caption=ayah_num)
            await message.answer(text=caption)
        else:
            await bot.send_audio(chat_id=message.chat.id, audio=audio, caption=caption)
    if lt_ayah + 10 > number_of_ayahs_in_every_surah[surahNum] and one_ayah == False:
        rem_ayahs = number_of_ayahs_in_every_surah[surahNum] - st_ayah - 9
    elif one_ayah == True and st_ayah + 10 > number_of_ayahs_in_every_surah[surahNum]:
        lt_ayah = st_ayah
        rem_ayahs = number_of_ayahs_in_every_surah[surahNum] - st_ayah
    if lt_ayah == number_of_ayahs_in_every_surah[surahNum]:
        e_surah = {
            "uzl":"Sura oxiriga yetdingiz. Pastdagilardan birini tanlang!",
            "uzk":"Сура охирига етдингиз. Пастдагилардан бирини танланг!",
            "ru":"Вы дошли до конца cури. Выберите один ниже!",
            "en":"You've reached the end of this surah. Please choose one of the options below!"
        }
        await message.answer(text=e_surah[lang],
                             reply_markup=await end_surah(lang))
        await states_for_Quran.choosing_end_surah.set()
    else:
        ch_bel = {
            "uzl":"Pastdagilardan birini tanlang!",
            "uzk":"Пастдагилардан бирини танланг!",
            "ru":"Выберите один ниже!",
            "en":"Choose one of the options below!"
        }
        await message.answer(text=ch_bel[lang],
                             reply_markup=kb_surah_option_to_continue(rem_ayahs, lang))
        await states_for_Quran.choosing_end_surah.set()
    async with state.proxy() as data:
        data['latest-ayah'] = lt_ayah + 1
        data['one-way'] = False


@dp.message_handler(state=states_for_Quran.ayah)
async def choosing_way(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['one-ayah'] = True
        data['latest-ayah'] = int(message.text)
    await sending_ayahs(message, state)


@dp.message_handler(state=states_for_Quran.surah)
async def surah_cmd(message: types.Message, state: FSMContext):
    lang = db_users.get_user_language(id=message.chat.id)[0]

    en_num = {
        "uzl":"Iltimos raqam kiriting!",
        "uzk":"Илтимос рақам киритинг!",
        "ru":"Пожалуйста, введите номер!",
        "en":"Please, enter number!"
    }
    en_num_limit= {
        "uzl":"Iltimos 1 va 114 orasida bo'lgan raqam kiriting!",
        "uzk":"Илтимос 1 ва 114 орасида бўлган рақам киритинг!",
        "ru":"Пожалуйста, введите число от 1 до 114!",
        "en":"Please, enter a number between 1 and 114"
    }
    if message.text.isdigit() == False:
        await message.answer(en_num[lang])
    else:
        num = int(message.text)
    if num > 114 or num < 1:
        await message.answer(en_num_limit[lang])
    else:
        surah_num = int(message.text)
        async with state.proxy() as data:
            data['surah-number'] = surah_num

        if 10 > number_of_ayahs_in_every_surah[surah_num]:
            AYAHS = number_of_ayahs_in_every_surah[surah_num]
        else:
            AYAHS = 10
        ask_continue = {
            "uzl": f"Oyat raqamini kiriting yoki keyingi {AYAHS} ta oyatni olish uchun pastdagi tugmani bosing!",
            "uzk": f"Оят рақамини киритинг ёки кейинги {AYAHS} та оятни олиш учун пастдаги тугмани босинг!",
            "ru": f"Введите номер аята или нажмите кнопку ниже, чтобы получить следующие {AYAHS} аятов",
            "en": f"Enter the ayah number or click the button below to get next {AYAHS} ayahs"
        }
        await message.answer(text=ask_continue[lang],
            reply_markup=ten_ayahs(surah_num, number_of_ayahs_in_every_surah, lang))
        await states_for_Quran.ayah.set()


async def sendAudio_ar(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        surahNum = int(data['surah-number'])

    lang = db_users.get_user_language(id=message.chat.id)[0]


    file_id = db_surah.select_surah_ar(surah_num=surahNum)


    await bot.send_audio(chat_id=message.chat.id, audio=file_id[0])
    await states_for_Quran.choosing_end_surah.set()
    ch_bel = {
        "uzl": "Pastdagilardan birini tanlang!",
        "uzk": "Пастдагилардан бирини танланг!",
        "ru": "Выберите один ниже!",
        "en": "Choose one of the options below!"
    }
    await message.answer(ch_bel[lang], reply_markup=await end_surah(lang))

async def sendAudio_uz(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        surah_num = int(data['surah-number'])

    lang = db_users.get_user_language(id=message.chat.id)[0]

    file_id = db_surah.select_surah_uz(surah_num=surah_num)

    await bot.send_audio(chat_id=message.chat.id, audio=file_id[0])
    await states_for_Quran.choosing_end_surah.set()
    ch_bel = {
        "uzl": "Pastdagilardan birini tanlang!",
        "uzk": "Пастдагилардан бирини танланг!",
    }
    await message.answer(ch_bel[lang], reply_markup=await end_surah(lang))