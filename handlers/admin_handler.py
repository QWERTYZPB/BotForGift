from aiogram import Router, F, Bot, types
from aiogram.filters import Command

from middlewares.filters import AdminProtect
from settings import utils, admin_kb

from middlewares.MiddleWares import AlbumMiddleware

from config import ADMIN_IDS


from datetime import timedelta, datetime
import logging as lg





router=Router()
router.message.middleware(AlbumMiddleware())





@router.message(Command("apanel"), AdminProtect())
async def admin_panel(message: types.Message, bot: Bot):
    await message.answer("Приветсвенное сообщение для администратора", reply_markup=admin_kb.admin_start())









'''
@router.message(PromotionState.photo, F.photo)
@router.message(PromotionState.photo, F.video)
@router.message(PromotionState.photo, F.text)
async def add_promotion_6(message: Message, state: FSMContext, album: list=None):
    # await state.update_data(photo=message.photo[-1].file_id)
    data=await state.get_data()
    caption = f'Название: {data["name"]}\n\nкатегория: {data["category"]}\nСрок действия: {data["lasting"]}\nКоличество QR: {data["QRs_number"]}\nОписание: {data["description"]}'
    # try:
    media_group = []
    media_files_ids = []
    if album:
        count_photos = len(album)
        await message.reply(f"всего {count_photos} медиа файлов")
    # print(message.media_group_id)
        for idx, msg in enumerate(album):
            # print(msg)
            # await message.answer_photo(msg.file_id)
            
            if msg.photo:
                media = types.InputMediaPhoto(media=msg.photo[-1].file_id)
                media_files_ids.append("p!"+str(msg.photo[-1].file_id))
            elif msg.video:
                media = types.InputMediaVideo(media=msg.video.file_id)
                media_files_ids.append("v!"+str(msg.video.file_id))
            else:
                continue
            
            if idx == 0:
                media.caption = msg.caption
            
            media_group.append(media)
        
        # await message.bot.send_media_group(
        #     chat_id=message.from_user.id,
        #     caption=caption,
        #     media=media_group)
    else:
        if message.photo:
                media = types.InputMediaPhoto(media=message.photo[-1].file_id)
                media_files_ids.append("p!"+str(message.photo[-1].file_id))
        elif message.video:
            media = types.InputMediaVideo(media=message.video.file_id)
            media_files_ids.append("v!"+str(message.video.file_id))

        
    
    await state.update_data(photo=';'.join(media_files_ids))
    

'''

