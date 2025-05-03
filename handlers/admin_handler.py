from aiogram import Router, F, Bot, types
from aiogram.filters import Command

from middlewares.filters import AdminProtect
from settings import utils, admin_kb

from middlewares.MiddleWares import AlbumMiddleware

from config import ADMIN_IDS


import logging as lg




router=Router()
router.message.middleware(AlbumMiddleware())






@router.message(Command("apanel"), AdminProtect())
async def admin_panel(message: types.Message):
    start_admin_message = await message.answer("Приветсвенное сообщение для администратора", reply_markup=admin_kb.admin_start())
    # await add_user(
    #     user_id=message.from_user.id,
    #     start_message_id=start_admin_message.message_id
    # )
