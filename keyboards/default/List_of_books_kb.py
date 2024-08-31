from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def list_of_books(lang) -> object:

    Quran = {
        'uzl': "Qur`oni Karim",
        'uzk': "Қурони Карим",
        'ru': "Коран",
        'en': "Quran"
    }

    Hadith = {
        "uzl": "Sahih hadislar",
        "uzk": "Саҳиҳ ҳадислар",
        "ru": "Xадисы",
        "en": "Hadiths"
    }

    placeholder = {
        "uzl": "Yuqorilardan birini tanlang!",
        "uzk": "Юқорилардан бирини танланг!",
        "ru": "Выберите один из вышеперечисленных!",
        "en": "Choose one of the options!"
    }

    books_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   input_field_placeholder=placeholder[lang],
                                   row_width=2,
                                   keyboard=[
                                       [
                                           KeyboardButton(text=Quran[lang]),
                                           KeyboardButton(text=Hadith[lang])
                                       ]
                                   ])
    return books_kb
