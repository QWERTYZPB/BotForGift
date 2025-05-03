from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database import models





def user_start():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
         InlineKeyboardButton(text="Картинг", callback_data="karting"), 
         InlineKeyboardButton(text="Ресторан&Терраса ", callback_data="restoran")],
        [
         InlineKeyboardButton(text="Караоке-холл", callback_data="caraoke"), 
         InlineKeyboardButton(text="Боулинг", callback_data="bowling")],
        [InlineKeyboardButton(text="Танцевальные выходные", callback_data="dancing")], 
        [InlineKeyboardButton(text="Банкеты и ДР", callback_data="banket")],
        [InlineKeyboardButton(text="О нас", callback_data="about")],
        [InlineKeyboardButton(text="Мои QR", callback_data="myQr")]
    ])


def subscribe_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
          InlineKeyboardButton(text="Подписаться на канал", url="https://t.me/MishkinMishkinOmsk"),
          InlineKeyboardButton(text="👍 Проверить подписку", callback_data="check_subscr")
        ]
    ])



def show_user_qr_names(user_actions: list[models.Promotion]):
    buttns = []
    
    for action in user_actions:
        buttns.append([InlineKeyboardButton(text=action.name, callback_data=f'seeQr_{action.id}')])
    buttns.append([InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")])
    return InlineKeyboardMarkup(inline_keyboard=buttns)




def karting():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Цены", callback_data="cost_k")],
        [InlineKeyboardButton(text="Аренда", callback_data="bron_k")],
        [InlineKeyboardButton(text="Акции", callback_data="events_k")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])
#  (на вынос 10%)
def restoraunt():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Бизнес-ланч", callback_data="buisness-launch")],
        [InlineKeyboardButton(text="Меню", callback_data="cost_r")],
        [InlineKeyboardButton(text="Бронь", callback_data="bron_r")],
        [InlineKeyboardButton(text="Акции", callback_data="events_r")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])

def caraoke():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Меню", callback_data="cost_c")],
        [InlineKeyboardButton(text="Бронь", callback_data="bron_c")],
        [InlineKeyboardButton(text="Акции", callback_data="events_c")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])

def bowling():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Цены", callback_data="cost_b")],
        [InlineKeyboardButton(text="Бронь", callback_data="bron_b")],
        [InlineKeyboardButton(text="Акции", callback_data="events_b")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])


def dance_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Афиша", callback_data="afisha")],
        [InlineKeyboardButton(text="Бронь", callback_data="bron_da")],
        [InlineKeyboardButton(text="Акции", callback_data="events_da")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])


def dr_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Меню", callback_data="cost_dr")],
        [InlineKeyboardButton(text="Бронь", callback_data="bron_dr")],
        [InlineKeyboardButton(text="Акции", callback_data="events_dr")],
        
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])

def start_promotion_button(next_promotion, len_promotion, category, action_id, qr_active: bool):
    list_kb = []
    list_kb.append(
        [
            InlineKeyboardButton(text=f"1/{len_promotion}", callback_data="q"), 
            InlineKeyboardButton(text="➡️", callback_data=f"navigation_forward_{next_promotion}")
        ]
    )
    if qr_active:
        list_kb.append(
            [
            InlineKeyboardButton(text="Получить QR-код!", callback_data=f"getQr_{category}_{action_id}") if qr_active else '',
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_category_menu_{category}")
            ]
        )
    else:
        list_kb.append(
            [
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_category_menu_{category}")
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=list_kb)

def middle_promotion_button(
        next_promotion, 
        len_promotion, 
        back_promotion, 
        current_promotion_number, 
        category, action_id,
        qr_active: bool
        ):
    
    
    list_kb = []
    list_kb.append(
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"navigation_back_{back_promotion}"),
            InlineKeyboardButton(text=f"{current_promotion_number}/{len_promotion}", callback_data="q"),
            InlineKeyboardButton(text="➡️", callback_data=f"navigation_forward_{next_promotion}")
        ]
    )
    if qr_active: 
        list_kb.append([
            InlineKeyboardButton(text="Получить QR-код!", callback_data=f"getQr_{category}_{action_id}"),
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_category_menu_{category}")
        ])
    else:
        list_kb.append([
            InlineKeyboardButton(text="Назад", callback_data=f"back_to_category_menu_{category}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=list_kb)

def end_promotion_button(len_promotion, back_promotion, category, action_id, qr_active: bool):
    list_kb=[]
    list_kb.append(
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"navigation_back_{back_promotion}"), 
            InlineKeyboardButton(text=f"{len_promotion}/{len_promotion}", callback_data="q")
        ]
    )
    if qr_active:
        list_kb.append(
            [
                InlineKeyboardButton(text="Получить QR-код!", callback_data=f"getQr_{category}_{action_id}"),
                InlineKeyboardButton(text="Назад", callback_data=f"back_to_category_menu_{category}")
            ]
        )
    else:
        list_kb.append(
            [
                InlineKeyboardButton(text="Назад", callback_data=f"back_to_category_menu_{category}")
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=list_kb)



def back_karting():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_category_menu_karting")]
    ])

def back_caraoke():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_category_menu_caraoke")]
    ])

def back_restaraunt():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_category_menu_restoran")]
    ])

def back_bowling():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_category_menu_bowling")]
    ])

def back_dancing():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_category_menu_dancing")]
    ])
def back_dr():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_category_menu_banket")]
    ])



def back_to_mainmenu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_mainmenu")]
    ])




def confirm_booking():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data=f"booking_confirm")],
        [InlineKeyboardButton(text="Отменить", callback_data=f"booking_cancel")]
    ])



def request_contact_button():
    return ReplyKeyboardBuilder().row(
        KeyboardButton(text='☎️ Отправить номер', request_contact=True)
    ).as_markup(resize_keyboard=True)