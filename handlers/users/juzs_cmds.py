import requests as req
from aiogram import types
from loader import dp, bot, db_users
from aiogram.dispatcher import FSMContext
from states.states_for_Quran import states_for_Quran
from utils.misc import surahs_and_juzs_info
from utils.misc.transliterate import transliterate
from googletrans import Translator
from .Quran import quran_cmd

tr = Translator()

from states.language_state import Language
from keyboards.inline.kb_for_juzs import kb_endOfJuz, kb_juz_option_to_continue, kb_go_back


@dp.callback_query_handler(state=states_for_Quran.juz)
async def sending_list_of_juzs(call: types.callback_query, state: FSMContext):
    lang = db_users.get_user_language(id=call.message.chat.id)[0]

    if call.data == "list-of-juzs":
        msg1 = ''
        msg2 = ''
        if lang == 'uzl':
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs1.items():
                msg1 += key + "-juz: " + value + "\n\n"
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs2.items():
                msg2 += key + "-juz: " + value + "\n\n"
        elif lang == 'uzk':
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs1.items():
                value = transliterate(value, 'cyrillic')
                msg1 += key + "-Жуз: " + value + "\n\n"
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs2.items():
                value = transliterate(value, 'cyrillic')
                msg2 += key + "-Жуз: " + value + "\n\n"
        elif lang == 'ru':
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs1.items():
                value = tr.translate(text=value, src='uz', dest='ru').text
                msg1 += "Жуз " + key + ": " + value + "\n\n"
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs2.items():
                value = tr.translate(text=value, src='uz', dest='ru').text
                msg2 += "Жуз " + key + ": " + value + "\n\n"
        elif lang == 'en':
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs1.items():
                value = tr.translate(text=value, src='uz', dest='en').text
                msg1 += "Juz " + key + ": " + str(value) + "\n\n"
            for key, value in surahs_and_juzs_info.parts_of_Quran_in_juzs2.items():
                value = tr.translate(text=value, src='uz', dest='en').text
                msg2 += "Juz " + key + ": " + str(value) + "\n\n"
        await call.message.answer(text=msg1)
        await call.message.answer(text=msg2)
        text = {'uzl': "Juz raqamini kiriting! Yoki pastdagi tugmani bosing!",
            'uzk': "Жуз рақамини киритинг! Ёки пастдаги тугмани босинг!",
            'ru': "Введите номер жуза! Или нажмите кнопку ниже!", 'en': "Enter juz number. Or click the button below"}
        await call.message.answer(text=text[lang], reply_markup=kb_go_back(lang))

    if call.data == "next-ayahs-juz":
        async with state.proxy() as data:
            data['latest-ayah-juz'] = data['latest-ayah-juz'] + 1

        await send_ayahs(call.message, state)
    elif call.data == "calling-juz":
        await call.message.delete()
        dig_n_juz = {"uzl": "Boshqa juz raqamini yuboring!", "uzk": "Бошқа жуз рақамини юборинг!",
            "ru": "Отправить другой номер жузи", "en": "Send another juz number"}
        await states_for_Quran.juz.set()
        async with state.proxy() as data:
            data['latest-ayah-juz'] = 1
        await call.message.answer(text=dig_n_juz[lang])
    elif call.data == "main-menu":
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)
    elif call.data == "back-juz":
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)


def making_msg(ayah, arabic, transliteration, translation, translation_ru, translation_en, lang):
    audioURL = f"https://cdn.islamic.network/quran/audio/128/ar.alafasy/{arabic[ayah]['number']}.mp3"
    arabicName = str(arabic[ayah]['surah']['name']) + "\n"
    engName = str(arabic[ayah]['surah']['englishName'])
    arabicVer = str(arabic[ayah]['text']) + "\n"
    lit_version = str(transliteration[ayah]['text']) + "\n"
    translation_uzk = str(translation[ayah]['text'])
    surahNum = str(arabic[ayah]['surah']['number'])
    NumInSurah = str(arabic[ayah]['numberInSurah'])
    ayat_num = NumInSurah
    translation_ru = str(translation_ru[ayah]['text'])
    translation_en = str(translation_en[ayah]['text'])

    if lang == 'uzl':
        engName = engName + " surasi\n"
        surahNum = surahNum + "-sura\n"
        NumInSurah = str(arabic[ayah]['numberInSurah']) + "-oyat\n"
        translationF = transliterate(translation_uzk, 'latin') + "\n"
    elif lang == 'uzk':
        engName = transliterate(text=engName + " -сураси\n", to_variant='cyrillic') + "\n"
        surahNum = transliterate(text=surahNum + "-сура", to_variant='cyrillic') + '\n'
        NumInSurah = transliterate(text=str(arabic[ayah]['numberInSurah']) + "-oyat", to_variant='cyrillic') + '\n'
        translationF = translation_uzk
    elif lang == 'ru':
        engName = "Сура " + transliterate(engName, 'cyrillic') + "\n"
        surahNum = "Номер суры: " + surahNum + "\n"
        NumInSurah = "Номер аяти: " + str(arabic[ayah]['numberInSurah']) + "\n"
        translationF = translation_ru
    elif lang == 'en':
        engName = "Surah " + engName + "\n"
        surahNum = "Surah number: " + surahNum + "\n"
        NumInSurah = "Ayah: " + str(arabic[ayah]['numberInSurah']) + "\n"
        translationF = translation_en

    if ayat_num == '1':
        text = arabicName + engName + surahNum + NumInSurah + arabicVer + lit_version + translationF
    else:
        text = NumInSurah + arabicVer + lit_version + "\n" + translationF
    return text, audioURL, NumInSurah


async def send_ayahs(message: types.Message, state: FSMContext):
    lang = db_users.get_user_language(id=message.chat.id)[0]

    async with state.proxy() as data:
        juzNum = data['juz-number']
        st_ayah = data['latest-ayah-juz']
    if st_ayah == 1:
        sending = {"uzl": "Yuborilmoqda...", "uzk": "Юборилмоқда...", "ru": "Oтправляю...", "en": "Sending..."}
        await message.reply(sending[lang])
    arabic = req.get(f"http://api.alquran.cloud/v1/juz/{juzNum}").json()['data']['ayahs']
    transliteration = req.get(f"http://api.alquran.cloud/v1/juz/{juzNum}/en.transliteration").json()['data']['ayahs']
    translation = req.get(f"http://api.alquran.cloud/v1/juz/{juzNum}/uz.sodik").json()['data']['ayahs']
    translation_ru = req.get(f"http://api.alquran.cloud/v1/juz/{juzNum}/ru.porokhova").json()['data']['ayahs']
    translation_en = req.get(f"http://api.alquran.cloud/v1/juz/{juzNum}/en.ahmedali").json()['data']['ayahs']

    if st_ayah == 1:
        if lang == 'uzl':
            await message.answer(str(juzNum) + "-juz")
        elif lang == 'uzk':
            await message.answer(str(juzNum) + "-жуз")
        elif lang == 'ru':
            await message.answer("Жуз номер: " + str(juzNum))
        elif lang == 'en':
            await message.answer("Juz number: " + str(juzNum))

    if st_ayah + 10 > len(arabic):  # 148
        lt_ayah = len(arabic)
    else:
        lt_ayah = st_ayah + 9
        rem_ayahs = 10
    for i in range(st_ayah - 1, lt_ayah):
        caption, audio, ayah_num = making_msg(i, arabic, transliteration, translation, translation_ru, translation_en,
                                              lang)
        if len(caption) > 4096:
            firstpart, secondpart = caption[:len(caption) // 2], caption[len(caption) // 2:]
            await bot.send_audio(chat_id=message.chat.id, audio=audio, caption=ayah_num)
            await message.answer(text=firstpart)
            await message.answer(text=secondpart)
        elif len(caption) > 1024:
            await bot.send_audio(chat_id=message.chat.id, audio=audio, caption=ayah_num)
            await message.answer(text=caption)
        else:
            await bot.send_audio(chat_id=message.chat.id, audio=audio, caption=caption)

    if lt_ayah + 10 > len(arabic):
        rem_ayahs = len(arabic) - st_ayah - 9

    if lt_ayah == len(arabic):
        end_juz = {"uzl": "Juz oxiriga yetdingiz. Pastdagilardan birini tanlang!",
            "uzk": "Жуз охирига етдингиз. Пастдагилардан бирини танланг!",
            "ru": "Вы дошли до конца жузи. Выберите один ниже!",
            "en": "You've reached the end of this juz. Please choose one of the options below!"}
        await message.answer(text=end_juz[lang], reply_markup=kb_endOfJuz(lang))
        await states_for_Quran.choosing_end_juz.set()
    else:
        ch_bel = {"uzl": "Pastdagilardan birini tanlang!", "uzk": "Пастдагилардан бирини танланг!",
            "ru": "Выберите один ниже!", "en": "Please choose one of the options below!"}
        await message.answer(text=ch_bel[lang], reply_markup=kb_juz_option_to_continue(rem_ayahs, lang))
    async with state.proxy() as data:
        data['latest-ayah-juz'] = lt_ayah


@dp.message_handler(state=states_for_Quran.juz)
async def juz_cmd(message: types.Message, state: FSMContext):
    lang = db_users.get_user_language(id=message.chat.id)[0]

    if message.text.isdigit() == False:
        en_num = {"uzl": "Iltimos raqam kiriting!", "uzk": "Илтимос рақам киритинг!",
            "ru": "Пожалуйста, введите номер!", "en": "Please, enter number!"}
        await message.answer(en_num[lang])
    else:
        num = int(message.text)
    if num > 30 or num < 1:
        en_num_limit = {"uzl": "Iltimos 1 va 30 orasida bo'lgan raqam kiriting!",
            "uzk": "Илтимос 1 ва 30 орасида бўлган рақам киритинг!", "ru": "Пожалуйста, введите число от 1 до 30!",
            "en": "Please, enter a number between 1 and 30"}
        await message.answer(en_num_limit[lang])
    else:
        async with state.proxy() as data:
            data['juz-number'] = int(message.text)
        await send_ayahs(message, state)
