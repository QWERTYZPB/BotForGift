from aiogram import Router, F, Bot, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramForbiddenError

from middlewares.filters import AdminProtect
from settings import utils, admin_kb
from database.req import Add_promotion, get_promotions, Update_promotion, Delete_promotion, add_user, get_users_role
from database.models import Promotion
from settings.UserStates import Description_edit, Lasting_edit, QRs_number_edit, Photo_edit, Archive_edit

from middlewares.MiddleWares import AlbumMiddleware

from config import ADMIN_IDS


from datetime import timedelta, datetime
import logging as lg




router=Router()
router.message.middleware(AlbumMiddleware())






@router.message(Command("apanel"), AdminProtect())
async def admin_panel(message: Message, bot: Bot):
    start_admin_message = await message.answer("Приветсвенное сообщение для администратора", reply_markup=admin_kb.admin_start())
    await add_user(
        user_id=message.from_user.id,
        start_message_id=start_admin_message.message_id
    )
