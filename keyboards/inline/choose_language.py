from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

create_choosing_language_kb = InlineKeyboardMarkup(row_width=2)
create_choosing_language_kb.insert(InlineKeyboardButton(text="O'zbekcha🇺🇿", callback_data='uzl'))
create_choosing_language_kb.insert(InlineKeyboardButton(text="Ўзбекча🇺🇿", callback_data='uzk'))
create_choosing_language_kb.insert(InlineKeyboardButton(text='Русский🇷🇺', callback_data='ru'))
create_choosing_language_kb.insert(InlineKeyboardButton(text='English🇬🇧', callback_data='en'))
