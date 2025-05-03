from aiogram import Router, F, types
from aiogram.filters import CommandStart, CommandObject


import logging as lg
from settings import user_kb, lexicon
from settings.lexicon import categ_dict
from database.req import add_user
from database import req
import config

from config import ADMIN_IDS
from aiogram.utils.deep_linking import decode_payload











router=Router()

@router.message(CommandStart())
async def start_bot(message: types.Message, command: CommandObject):

    start_message = await message.answer(lexicon.START_TEXT, disable_web_page_preview=True, reply_markup=user_kb.user_start())

    await add_user(       #Добавляем нового пользователя при старте бота
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        
    )
    


    
