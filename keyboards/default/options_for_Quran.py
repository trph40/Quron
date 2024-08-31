from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram import types

async def options_to_read(lang, message: types.Message):

    Juz = {
        'uzl': "Juzlar",
        'uzk': "Жузлар",
        'ru': "Жузи",
        'en': "Juzs"
    }
    Surah = {
        'uzl': "Suralar",
        'uzk': "Суралар",
        'ru': "Суры",
        'en': "Surahs"
    }
    Page = {
        'uzl': "Varaqlar",
        'uzk': "Варақлар",
        'ru': "Страницы",
        'en': "Pages"
    }
    text = {
        'uzl': "Davom etish uchun pastdagi tugmalardan birini tanlang!",
        'uzk': "Давом этиш учун пастдаги тугмалардан бирини танланг!",
        'ru': "Выберите одну из кнопок ниже, чтобы продолжить!",
        'en': "Press a button below to continue!"
    }
    manzil = {
        'uzl': "Manzillar",
        'uzk': "Манзилы",
        'ru': "Манзилы",
        'en': "Manzils"
    }
    options_to_read = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder=text[lang], one_time_keyboard=True)
    options_to_read.add(KeyboardButton(text=Juz[lang]), KeyboardButton(text=Surah[lang]), KeyboardButton(text=Page[lang]),KeyboardButton(text=manzil[lang]))
    return options_to_read
