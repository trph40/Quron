from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from states.states_for_Quran import states_for_Quran

async def going_back_to_Quran_options(lang):
    back = {
        "uzl": "Ortga⬅️",
        "uzk": "Ортга⬅️",
        "ru": "Назад⬅️",
        "en": "Go back⬅️️"
    }
    return InlineKeyboardButton(text=back[lang], callback_data='choose-Quran-reading-options')

