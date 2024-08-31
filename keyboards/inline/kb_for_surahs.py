from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



another_surah = {
    "uzl": "Boshqa sura",
    "uzk": "Бошқа сура",
    "ru": "Другая сура",
    "en": "Another surah"
}
main_menu = {
    "uzl": "Asosiy menu",
    "uzk": "Асосий меню",
    "ru": "Главное меню",
    "en": "Main menu"
}

back = {
    "uzl": "Ortga⬅️",
    "uzk": "Ортга⬅️",
    "ru": "Назад⬅️",
    "en": "Go back⬅️️"
}

async def getting_list_of_surahs(lang):
    text = {
        "uzl": "Suralar ro'yhatini olish!",
        "uzk": "Суралар рўйҳатини олиш!",
        "ru": "Получить список суры!",
        "en": "Get the list of surahs"
    }
    ikb = InlineKeyboardMarkup()
    ikb.insert(InlineKeyboardButton(text=text[lang], callback_data="list-of-surahs"))
    ikb.insert(InlineKeyboardButton(text=back[lang], callback_data='go-back'))
    ikb.insert(InlineKeyboardButton(text=main_menu[lang] + "🏠", callback_data='main-menu'))
    return ikb


def kb_surah_option_to_continue(ayah, lang):
    next_10_ayahs = {
        "uzl": f"Keyingi {ayah} ta oyatlar",
        "uzk": f"Кейинги {ayah} та оятлар",
        "ru": f"Следующие {ayah} аяти",
        "en": f"Next {ayah} ayahs"
    }

    next_ayah = {
        "uzl": "Keyingi oyat",
        "uzk": "Кейинги оят",
        "ru": "Следующий аят",
        "en": "Next ayah"
    }

    next_ayahs = InlineKeyboardMarkup(row_width=2)
    if ayah != 1:
        next_ayahs.insert(InlineKeyboardButton(text=next_10_ayahs[lang], callback_data="next-10-ayahs"))
    next_ayahs.insert(InlineKeyboardButton(text=next_ayah[lang], callback_data="next-ayah"))
    next_ayahs.insert(InlineKeyboardButton(text=another_surah[lang], callback_data="another-surah"))
    next_ayahs.insert(InlineKeyboardButton(text=main_menu[lang] + "🏠", callback_data="main-menu"))
    return next_ayahs


def ten_ayahs(surah_num, array, lang):
    if 10 > array[surah_num]:
        ayah = array[surah_num]
    else:
        ayah = 10
    next_10_ayahs = {
        "uzl": f"{ayah} ta oyatlarni olish",
        "uzk": f"{ayah} та оятлар",
        "ru": f"Следующие {ayah} аяти",
        "en": f"Next {ayah} ayahs"
    }
    full_surah_uz = {
        "uzl": f"O'zbekcha audio!",
        "uzk": f"Ўзбекча аудио!",

    }
    full_surah_ar = {
        "uzl": f"Arabcha audio!",
        "uzk": f"Арабча аудио!",
        "ru": f"Aрабское аудио!",
        "en": f"Audio in arabic!"
    }

    kb = InlineKeyboardMarkup(row_width=1).insert(InlineKeyboardButton(text=next_10_ayahs[lang], callback_data="next-10-ayahs")).insert(InlineKeyboardButton(text=full_surah_ar[lang], callback_data='full-surah-audio'))
    if lang == 'uzl' or lang == 'uzk':
        kb.insert(InlineKeyboardButton(text=full_surah_uz[lang], callback_data='full-surah-audio-uz'))
    return kb


async def end_surah(lang):
    end_surah = InlineKeyboardMarkup(row_width=1)
    end_surah.insert(InlineKeyboardButton(text=str(another_surah[lang]), callback_data="another-surah"))
    end_surah.insert(InlineKeyboardButton(text=str(main_menu[lang]) + "🏠", callback_data="main-menu"))
    return end_surah
