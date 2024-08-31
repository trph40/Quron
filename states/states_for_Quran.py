from aiogram.dispatcher.filters.state import StatesGroup, State



class states_for_Quran(StatesGroup):
    option = State()

    surah = State()
    ayah = State()
    choosing_end_surah = State()

    juz = State()
    choosing_end_juz = State()

    page = State()
    choosing_end_page = State()