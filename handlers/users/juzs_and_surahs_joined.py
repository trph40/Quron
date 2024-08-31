# from loader import dp
# from aiogram.dispatcher.filters import BoundFilter
# from aiogram.dispatcher import FSMContext
# from aiogram.types import callback_query, CallbackQuery
# from states.states_for_Quran import states_for_Quran
# from .Quran import quran_cmd
#
#
#
#
# # class MyDataFilter(BoundFilter):
# #     key = 'mydata'
# #     def __init__(self, mydata):
# #         self.mydata = mydata
# #
# #
# #     async def check(self, callback_query: CallbackQuery) -> bool:
# #         return callback_query.data.startswith(f'{self.key}:{self.mydata}')
# #
# #
#
#
# @dp.callback_query_handler(lambda call: callback_query.CallbackQuery.data(data="choose-Quran-reading-options"))
# # @dp.callback_query_handler(CallbackQuery.data == "choose-Quran-reading-options", state=states_for_Quran.juz)
# async def go_back_cmd(call: callback_query, state: FSMContext):
#     await quran_cmd(call.message, state)
