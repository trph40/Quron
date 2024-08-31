from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

next_page = {
    "uzl": "Keyingi varaq",
    "uzk": "Кейинги варақ",
    "ru": "Следущая страница",
    "en": "Next page"
}
another_page = {
    "uzl": "Boshqa varaq",
    "uzk": "Бошка варак",
    "ru": "Другая страница",
    "en": "Another page"
}
main_menu = {
    "uzl": "Asosiy menu",
    "uzk": "Асосий меню",
    "ru": "Главное меню",
    "en": "Main menu"
}


def end_page(lang, page_num):
    kb = InlineKeyboardMarkup(row_width=2)
    if page_num != 604:
        kb.insert(InlineKeyboardButton(text=next_page[lang], callback_data="next-page"))
    kb.insert(InlineKeyboardButton(text=another_page[lang], callback_data="another-page"))
    kb.insert(InlineKeyboardButton(text=main_menu[lang] + "🏠", callback_data="main-menu"))
    return kb


def ikb_page_start(lang):
    kb = InlineKeyboardMarkup()
    kb.insert(InlineKeyboardButton(text=main_menu[lang] + "🏠", callback_data="main-menu"))
    return kb