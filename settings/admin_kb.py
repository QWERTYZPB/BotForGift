from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_enterance(user_id, action_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить",callback_data=f"enterance_confirm_{user_id}_{action_id}")],
        [InlineKeyboardButton(text="Отменить", callback_data=f"enterance_cancel_{user_id}_{action_id}")]
    ])

def confirm_send_post():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить",callback_data=f"post_confirm")],
        [InlineKeyboardButton(text="Отменить", callback_data=f"post_cncl")]
    ])



def admin_start():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Акции",callback_data="admin_promotions")],
        [InlineKeyboardButton(text="Афиша",callback_data="admin_afisha")],
        [InlineKeyboardButton(text="Ланч",callback_data="admin_launch")],
        [InlineKeyboardButton(text="Персонал",callback_data="personal")],
        [InlineKeyboardButton(text="Рассылка", callback_data="mailing")]
    ])


def admin_afisha_and_launch(_type: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Медиа", callback_data=f"ALedit_{_type}_media")],
        [InlineKeyboardButton(text="Описание", callback_data=f"ALedit_{_type}_text")],
        [InlineKeyboardButton(text="Очистить", callback_data=f"ALedit_{_type}_clear")],
        [InlineKeyboardButton(text="Назад", callback_data="admin_back")]
    ])


def admin_back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="admin_back")]
    ])

def admin_back_to_al(type_):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=f"admin_{type_}")]
    ])

def action_qr_request():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Акция без выдачи QR", callback_data="NotQrAction")],
        [InlineKeyboardButton(text="Назад", callback_data="admin_back")]
    ])
    

def admin_promotions_keyb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить", callback_data="add"), InlineKeyboardButton(text="Редактировать", callback_data="edit")],
        [InlineKeyboardButton(text="Статистика", callback_data="statistics")]
    ])

def category_list():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Картинг", callback_data="category_karting"),
         InlineKeyboardButton(text="Ресторан", callback_data="category_restoraunt")],
        [InlineKeyboardButton(text="Караоке", callback_data="category_caraoke"),
         InlineKeyboardButton(text="Боулинг", callback_data="category_bowling")],
        [
         InlineKeyboardButton(text="Танцевальные выходные", callback_data="category_dancing"), 
         InlineKeyboardButton(text="Банкеты и ДР", callback_data="category_banket")
         ]
    ])

def add_promotion_final():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить", callback_data="finish_add"),InlineKeyboardButton(text="Отменить", callback_data="cancel_add")]
    ])

def skip_photo():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_photo")]
    ])


def admin_promotions_kb_edit(promotion_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Описание", callback_data=f"PromotionEdit_description_{promotion_id}")],
        [InlineKeyboardButton(text="Фотография", callback_data=f"PromotionEdit_photo_{promotion_id}")],
        [InlineKeyboardButton(text="Срок проведения акции", callback_data=f"PromotionEdit_lasting_{promotion_id}")],
        [InlineKeyboardButton(text="Лимит выдачи QR", callback_data=f"PromotionEdit_QRnumber_{promotion_id}")],
        [InlineKeyboardButton(text="Отправить в архив", callback_data=f"PromotionEdit_archive_{promotion_id}")],
        [InlineKeyboardButton(text="Удалить акцию", callback_data=f"PromotionEdit_delete_{promotion_id}")],
        [InlineKeyboardButton(text="Подтвердить", callback_data=f"PromotionEdit_confirm_{promotion_id}")],
    ])

def admin_return():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Вернуться в меню", callback_data="category_return_to_menu")]
    ])






def promotions_type():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Активные", callback_data="status_active"), InlineKeyboardButton(text="Архивные", callback_data="status_archived")]
    ])







def admin_start_promotion_button(next_promotion, len_promotion, status):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"1/{len_promotion}", callback_data="q"), 
            InlineKeyboardButton(text="➡️", callback_data=f"Admnavigation_forward_{next_promotion}_{status}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"admin_back")
        
        ]
    ])

def admin_middle_promotion_button(next_promotion, len_promotion, back_promotion, current_promotion_number, status):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"Admnavigation_back_{back_promotion}_{status}"),
            InlineKeyboardButton(text=f"{current_promotion_number}/{len_promotion}", callback_data="q"),
            InlineKeyboardButton(text="➡️", callback_data=f"Admnavigation_forward_{next_promotion}_{status}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"admin_back")
        ]
    ])

def admin_end_promotion_button(len_promotion, back_promotion, status):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"Admnavigation_back_{back_promotion}_{status}"), 
            InlineKeyboardButton(text=f"{len_promotion}/{len_promotion}", callback_data="q")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"admin_back")
        ]
    ])






def start_promotion_button_a(next_promotion, len_promotion):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать", callback_data=f"promotion_edit_{next_promotion-1}")],
        [InlineKeyboardButton(text=f"1/{len_promotion}", callback_data="q"), InlineKeyboardButton(text="➡️", callback_data=f"a_navigation_forward_{next_promotion}")],
     [
            InlineKeyboardButton(text="Назад", callback_data=f"admin_back")
        
        ]
     ])

def middle_promotion_button_a(next_promotion, len_promotion, back_promotion, current_promotion_number):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать", callback_data=f"promotion_edit_{current_promotion_number}")],
        [InlineKeyboardButton(text="⬅️", callback_data=f"a_navigation_back_{back_promotion}"), InlineKeyboardButton(text=f"{current_promotion_number}/{len_promotion}", callback_data="q"), InlineKeyboardButton(text="➡️", callback_data=f"a_navigation_forward_{next_promotion}")],
    [
            InlineKeyboardButton(text="Назад", callback_data=f"admin_back")
        
        ]
    ])

def end_promotion_button_a(len_promotion, back_promotion):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Редактировать", callback_data=f"promotion_edit_{back_promotion+1}")],
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"a_navigation_back_{back_promotion}"),
            InlineKeyboardButton(text=f"{len_promotion}/{len_promotion}", callback_data="q")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=f"admin_back")
        
        ]
    ])

