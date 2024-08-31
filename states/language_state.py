from aiogram.dispatcher.filters.state import StatesGroup, State


class Language(StatesGroup):
    Choosing_language = State()
    Choosing_book = State()
