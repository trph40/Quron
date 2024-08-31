import asyncio
import sqlite3
from typing import List, Union
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from data.config import  BOT_TOKEN
bot = Bot(token=BOT_TOKEN)  # Place your token here
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]

# Initialize SQLite database connection
db = sqlite3.connect('./data/surahs_file_id.db')
cursor = db.cursor()
try:
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Audio_ar (
        surah_num INTEGER PRIMARY KEY,
        file_id TEXT)''')
except:
    pass
db.commit()



class statesfornow(StatesGroup):
    Start = State()
    Writing = State()





@dp.message_handler(commands=['write_database_ar'], state='*')
async def starting_function_to_write_database_uz(message: types.Message):
    await message.answer("send the beginning number")
    await statesfornow.Start.set()


@dp.message_handler(state=statesfornow.Start)
async def getting_the_starting_number(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
         data['num']= int(message.text)
        await message.answer("send the media files")
        await statesfornow.Writing.set()
    else:
        await message.answer("send a number")

@dp.message_handler(is_media_group=True, content_types=types.ContentType.AUDIO, state=statesfornow.Writing)
async def handle_albums(message: types.Message, album: List[types.Message], state: FSMContext):
    print("started handling albums")
    async with state.proxy() as data:
        number = data['num']
    """This handler will receive a complete album of any type."""
    media_group = types.MediaGroup()
    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id
        print(number)
        print(file_id)
        cursor.execute("INSERT INTO Audio_ar (surah_num, file_id) VALUES (?, ?)", (number, file_id))
        db.commit()

        try:
            # We can also add a caption to each file by specifying `"caption": "text"`
            media_group.attach({"media": file_id, "type": obj.content_type})
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")
        number +=1

    await message.answer("send more or send /cancel to cancel the process")
    async with state.proxy() as data:
        data['num'] = number


@dp.message_handler(commands=['cancel'], state='*')
async def cancelling_process(message: types.Message, state: FSMContext):
    await state.finish()
    db.close()
    await message.answer("Finished")


if __name__ == "__main__":
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, skip_updates=True)
