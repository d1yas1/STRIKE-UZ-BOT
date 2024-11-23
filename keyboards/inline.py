from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import callback_data

language_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek tili",callback_data="uzbek"),
            InlineKeyboardButton(text="🇷🇺 Русский язык",callback_data="russian"),
        ]
    ],
    resize_keyboard=True
)