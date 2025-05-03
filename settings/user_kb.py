from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat
)

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database import models





def main_reply():
    return ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text='Розыгрыши'),
                KeyboardButton(text='Новый розыгрыш'),
                KeyboardButton(text='Подписки')
            ],
            [
                KeyboardButton(text='Добавить группу', request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=False)),
                KeyboardButton(text='Добавить Канал', request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=True))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="По ком получим ID?"
    )