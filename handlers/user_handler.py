from aiogram import Router, F, types
from aiogram.filters import CommandStart, CommandObject


import logging as lg
from settings import user_kb, lexicon
from database.req import add_user
from database import req
import config

from config import ADMIN_IDS
from aiogram.utils.deep_linking import decode_payload











router = Router()

@router.message(CommandStart())
async def start_bot(message: types.Message, command: CommandObject):

    await message.answer(
        lexicon.START_TEXT, 
        reply_markup=user_kb.main_reply()
    )


    try:
        await add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
        )
    except Exception:
        lg.warning(f'FAILED TO ADD USER IN START u_id:{message.from_user.id}')
    


    
