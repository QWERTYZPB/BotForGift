from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram import Bot


import logging as lg
from settings import user_kb, lexicon, files, utils, UserStates, admin_kb
from settings.lexicon import categ_dict
from database.req import add_user, get_promotions, get_promotion_by_id, update_user, Update_promotion, get_user_by_id
from database import req
import config

from config import ADMIN_IDS
from aiogram.utils.deep_linking import create_start_link, decode_payload











router=Router()

@router.message(CommandStart())
async def start_bot(message: Message, command: CommandObject):
    if message.chat.type != 'private':
        return
    
    controllers_id = [user.user_id for user in await req.get_controlers()]
    
    if command.args:
        if message.from_user.id in config.ADMIN_IDS or message.from_user.id in controllers_id:
            
            data=decode_payload(command.args)
            
            try:
                user_id, action_id = data.split('_')
            except Exception as e:
                await message.answer('Что-то пошло не так!')
                lg.error(f"SOMETHING WRONG WITH SCAN QR USER-{user_id}, ACTION-{action_id}, err:{e}")
            
            user = await get_user_by_id(int(user_id))
            action = await get_promotion_by_id(action_id)

            if str(user.user_id) in action.enter_users_ids.split(','):
                await message.answer(f'Данный пользователь уже воспользовался акцией ({action.name})')
            else:
                await message.answer(f'Подтвердите вход:\n\nПользователь - {user.full_name}\nМероприятие - {action.name}', reply_markup=admin_kb.confirm_enterance(user_id, action_id))
            
            return
    
    
    if message.from_user.id in config.ADMIN_IDS:
        role = "admin"
    elif message.from_user.id in controllers_id:
        role = "controller"
    else:
        role = "user"

    start_message = await message.answer(lexicon.START_TEXT, disable_web_page_preview=True, reply_markup=user_kb.user_start())

    await add_user(       #Добавляем нового пользователя при старте бота
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        role=role,
        start_message_id=start_message.message_id
    )
    


    
