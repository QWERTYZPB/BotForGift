from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    WebAppInfo
)


from typing import List

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from settings.utils import generate_random_string
from database import req
import datetime, random
import config



def main_reply():
    return ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text='Розыгрыши'),
                KeyboardButton(text='Новый розыгрыш'),
                # KeyboardButton(text='Подписки')
            ],
            [
                KeyboardButton(text='Добавить группу', request_chat=KeyboardButtonRequestChat(request_id=1, chat_is_channel=False)),
                KeyboardButton(text='Добавить Канал', request_chat=KeyboardButtonRequestChat(request_id=2, chat_is_channel=True))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие"
    )


def back_to_menu():
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='Назад', callback_data='backMain')
    ).as_markup()

async def create_user_raffles(events: List[str]):
    btns = []

    for id in events:
        try:
            event = await req.get_event(int(id))
            if event:
                btns.append(
                    InlineKeyboardButton(
                        text=event.name,
                        callback_data=f'user_event_show_{event.id}'
                    )
                )

        except:
            pass

    return InlineKeyboardBuilder().row(
        *btns,
        InlineKeyboardButton(text='Назад', callback_data='backMain'),
        width=2
    ).as_markup()


async def show_user_channels(channels, event_id):
    btns = []
    if len(channels)>0:
        for channel_id in channels:
            channel = await req.get_channel(int(channel_id))
            channel_text = channel.name
            channel_cb_data = f'channel_enable_{event_id}_{channel.id}'

            if channel.root_event_ids:
                if str(event_id) in channel.root_event_ids.split(','):
                    channel_text= channel.name + ' ✅'
                    channel_cb_data = f'channel_disable_{event_id}_{channel.id}'

            if channel:
                btns.append(InlineKeyboardButton(text=channel_text, callback_data=channel_cb_data))

        return InlineKeyboardBuilder().row(
            *btns,
            InlineKeyboardButton(text='Назад', callback_data=f'user_event_show_{event_id}'),
            width=2
        ).as_markup()
    
    return InlineKeyboardBuilder().row(
            InlineKeyboardButton(text='Назад', callback_data=f'user_event_show_{event_id}'),
            width=2
        ).as_markup()



async def show_event_kb(event_id: int, use_captha: bool = False, is_active: bool = True):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='Название', callback_data=f'edit_event_name_{event_id}'),
        InlineKeyboardButton(text='Медиа', callback_data=f'edit_event_media_{event_id}'),
        InlineKeyboardButton(text='Описание', callback_data=f'edit_event_description_{event_id}'),
        
        InlineKeyboardButton(text='Победители (кол-во)', callback_data=f'edit_event_wins_{event_id}'),
        InlineKeyboardButton(text='Каналы', callback_data=f'edit_event_channels_{event_id}'),
        InlineKeyboardButton(text='Дата', callback_data=f'edit_event_date_{event_id}'),

        InlineKeyboardButton(text='Рассылка', callback_data=f"send_{event_id}"),
        
        InlineKeyboardButton(text='Капча ✅', callback_data=f"captcha_disable_{event_id}") if use_captha else \
        InlineKeyboardButton(text='Капча ❌', callback_data=f"captcha_enable_{event_id}"),

        InlineKeyboardButton(text='Активно ✅', callback_data=f"activeEvent_disable_{event_id}") if is_active else \
        InlineKeyboardButton(text='Активно ❌', callback_data=f"activeEvent_enable_{event_id}"),
         

        InlineKeyboardButton(text='Назад', callback_data=f"backMain"),

        width=3
    ).as_markup()
    

def show_event_web_kb(url):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Учавствую', 
                    url=url
                    # WebAppInfo(url
                    )
            ]
        ]
        )


def show_event_results_web_kb(url):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Результаты', 
                    url=url
                    )
            ]
        ]
        )


def show_private_chat_web_app(event_id, event_end_date: datetime.datetime):
    btn = []
    
    if datetime.datetime.now() > event_end_date:
        btn = [
                InlineKeyboardButton(
                    text='Результаты', 
                    web_app=WebAppInfo(url=f'https://{config.HOST_URL}/?tgWebAppStartParam=eventId={event_id}&action=results')
                    )
            ]
    else:
        btn = [
                InlineKeyboardButton(
                    text='Учавствую', 
                    web_app=WebAppInfo(url=f'https://{config.HOST_URL}/?tgWebAppStartParam=eventId={event_id}&action=raffle')
                    )
            ]

    
    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            btn
        ]
    )



def confirm_send(event_id):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='✅ Да', callback_data=f'confirm_send_{event_id}'),
        InlineKeyboardButton(text='❌ Нет', callback_data=f'decline_send_{event_id}'),
        InlineKeyboardButton(text='Назад', callback_data=f'user_event_show_{event_id}'),
    ).as_markup()


def back_to_event(event_id):
    return InlineKeyboardBuilder().row(
        InlineKeyboardButton(text='Назад', callback_data=f'user_event_show_{event_id}'),
        
    ).as_markup()
















async def create_captcha_kb(right_answer: str):

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    buttns: list[InlineKeyboardButton] = [InlineKeyboardButton(text=await generate_random_string(5), callback_data='Captcha_False') for _ in range(2)]

    buttns.append(InlineKeyboardButton(text=right_answer, callback_data='Captcha_True'))
    
    random.shuffle(buttns)

    kb_builder.row(*buttns, width=3)
    buttns.clear()

    buttns.append(InlineKeyboardButton(text="🔁 Поменять капчу", callback_data='Change_Captcha'))
    kb_builder.row(*buttns, width=1)
    
    return kb_builder.as_markup()