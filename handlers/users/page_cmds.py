import requests as req
from aiogram.dispatcher import FSMContext
from aiogram.types import callback_query
from keyboards.default.List_of_books_kb import list_of_books
from states.language_state import Language
from utils.misc.transliterate import transliterate
from loader import dp, bot, db_users
from aiogram import types
from keyboards.inline.kb_for_page import end_page
from states.states_for_Quran import states_for_Quran
from handlers.users.Quran import quran_cmd
lang = ''


async def get_data(page_num):
    arabic_arr = req.get(f"http://api.alquran.cloud/v1/page/{page_num}").json()['data']['ayahs']
    transliteration_arr = req.get(f"http://api.alquran.cloud/v1/page/{page_num}/en.transliteration").json()['data'][
        'ayahs']
    translation_uz_arr = req.get(f"http://api.alquran.cloud/v1/page/{page_num}/uz.sodik").json()['data']['ayahs']
    translation_ru_arr = req.get(f"http://api.alquran.cloud/v1/page/{page_num}/ru.porokhova").json()['data']['ayahs']
    translation_en_arr = req.get(f"http://api.alquran.cloud/v1/page/{page_num}/en.asad").json()['data']['ayahs']
    return arabic_arr, transliteration_arr, translation_uz_arr, translation_ru_arr, translation_en_arr


async def make_message_with_audio(num, arabic_arr, transliteration_arr, translation_uz_arr, translation_ru_arr,
                                  translation_en_arr, ):
    global lang
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
        text = NumInSurah + arabicVer + lit_version + "\n" + translationF

    audioURl = f"https://cdn.islamic.network/quran/audio/128/ar.alafasy/{arabic_arr[num]['number']}.mp3"
    return audioURl, text, NumInSurah


async def send_ayahs_in_pages(message: types.Message, state: FSMContext, page_num):
    arabic_arr, transliteration_arr, translation_uz_arr, translation_ru_arr, translation_en_arr = await get_data(page_num)
    for ayah_num in range(0, len(arabic_arr)):
        audioURL, text, numberInSurah = await make_message_with_audio(ayah_num, arabic_arr, transliteration_arr, translation_uz_arr,
                                                 translation_ru_arr,
                                                 translation_en_arr)
        if len(text)> 4096:
            firstpart, secondpart = text[:len(text) // 2], text[len(text) // 2:]
            await bot.send_audio(chat_id=message.chat.id, audio=audioURL, caption=numberInSurah)
            await message.answer(text=firstpart)
            await message.answer(text=secondpart)
        elif len(text) > 1024:
            await bot.send_audio(chat_id=message.chat.id, audio=audioURL, caption=numberInSurah)
            await message.answer(text=text)
        else:
            await bot.send_audio(chat_id=message.chat.id, audio=audioURL, caption=text)
    end_page_msg = {
        "uzl": "Varaq oxiriga yetdingiz. Pastdagilardan birini tanlang!",
        "uzk": "Bарақ охирига етдингиз. Пастдагилардан бирини танланг!",
        "ru": "Вы дошли до конца этой страницы. Выберите один ниже!",
        "en": "You've reached the end of this page. Please choose one of the options below!"
    }
    end_book_msg = {
        "uzl":"Kitob oxiriga yetdingiz! Pastdagilardan birini tanlang!",
        "uzl":"Китоб охирига етдингиз! Пастдагилардан бирини танланг!",
        "ru":"Вы добрались до конца книги! Выберите один ниже!",
        "en":"You have reached the end. Please choose one of the options below!"
    }
    if page_num == 604:
        await message.answer(text=end_book_msg[lang], reply_markup=end_page(lang, page_num))
    else:
        await message.answer(text=end_page_msg[lang], reply_markup=end_page(lang, page_num))
    await states_for_Quran.choosing_end_page.set()


@dp.message_handler(state=states_for_Quran.page)
async def check_number(message: types.Message, state: FSMContext):
    global lang
    lang = db_users.get_user_language(id=message.chat.id)[0]

    if message.text.isdigit() == False:
        en_num = {
            "uzl": "Iltimos raqam kiriting!",
            "uzk": "Илтимос рақам киритинг!",
            "ru": "Пожалуйста, введите номер!",
            "en": "Please, enter number!"
        }
        await message.answer(en_num[lang])
    else:
        page_num = int(message.text)
    if page_num > 604 or page_num < 1:
        en_num_limit = {
            "uzl": "Iltimos 1 va 604 orasida bo'lgan raqam kiriting!",
            "uzk": "Илтимос 1 ва 604 орасида бўлган рақам киритинг!",
            "ru": "Пожалуйста, введите число от 1 до 604!",
            "en": "Please, enter a number between 1 and 604, inclusively!"
        }
        await message.answer(en_num_limit[lang])
    else:
        async with state.proxy() as data:
            data['page-num'] = page_num
        await send_ayahs_in_pages(message, state, page_num)


@dp.callback_query_handler(state=states_for_Quran.page)
async def page_callbacks(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'main-menu':
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)




@dp.callback_query_handler(state=states_for_Quran.choosing_end_page)
async def callbacks_for_page(call: callback_query.CallbackQuery, state: FSMContext):
    if call.data == 'next-page':
        await call.message.delete()
        async with state.proxy() as data:
            page_num = data['page-num']
        page_num += 1
        await send_ayahs_in_pages(call.message, state, page_num)
    elif call.data == 'another-page':
        await call.message.delete()
        text = {
            'uzl': "Varaq raqamini kiriting!",
            'uzk': "Варақ рақамини киритинг!",
            'ru': "Введите номер страницы!",
            'en': "Enter the page number"
        }
        await call.message.answer(text=text[lang])
        await states_for_Quran.page.set()

    elif call.data == "main-menu":
        await call.message.delete()
        await Language.Choosing_book.set()
        await quran_cmd(call.message, state)

