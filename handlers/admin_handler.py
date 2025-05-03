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
import pytz





router=Router()
router.message.middleware(AlbumMiddleware())


class PromotionState(StatesGroup):
    category = State()
    name = State()
    lasting = State()
    QRs_number = State()
    description = State()
    photo = State()

class Mailing(StatesGroup):
    waiting_for_post=State()



class EditLa(StatesGroup):
    edit_media = State()
    edit_text = State()





@router.message(Command("apanel"), AdminProtect())
async def admin_panel(message: Message, bot: Bot):
    start_admin_message = await message.answer("Приветсвенное сообщение для администратора", reply_markup=admin_kb.admin_start())
    await add_user(
        user_id=message.from_user.id,
        start_message_id=start_admin_message.message_id
    )


@router.callback_query(F.data=="a_return_to_menu")
@router.callback_query(F.data=="back_to_admin")
@router.callback_query(F.data=="admin_back")
async def return_to_menu(callback: CallbackQuery, state: FSMContext):

    try:
        await state.clear()
    except:
        pass

    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])


    await callback.answer()
    try:
        start_admin_message  = await callback.message.edit_text("Приветсвенное сообщение для администратора", reply_markup=admin_kb.admin_start())
    except:
        
        start_admin_message = await callback.message.answer("Приветсвенное сообщение для администратора", reply_markup=admin_kb.admin_start())

    await add_user(
        user_id=callback.from_user.id
    )






@router.callback_query(F.data.startswith("admin_"))
async def admin_promotions(callback: CallbackQuery):
    action = callback.data.split('_')[-1]

    if action == 'promotions':
        await callback.message.edit_text("Выберите раздел", reply_markup=admin_kb.admin_promotions_keyb())
        return
    
    await callback.message.edit_text("Выберите что изменить", reply_markup=admin_kb.admin_afisha_and_launch(_type=action))


@router.callback_query(F.data.startswith('ALedit_'))
async def edit_al(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split('_')
    type_ = data[1]
    action = data[-1]

    await state.update_data(type_=type_, action=action)

    if action == 'media': 
        await cb.message.edit_text('Пришлите медиа одним сообщением:')
        await state.set_state(EditLa.edit_media)
    elif action == 'text':
        await cb.message.edit_text('Пришлите текст:', reply_markup=admin_kb.admin_back())
        
        await state.set_state(EditLa.edit_text)
    elif action == 'clear':
        if type_ == "afisha":
            utils.clear_in_afisha()
        else:
            utils.clear_in_launch()
        
        await cb.message.edit_text('Готово!', reply_markup=admin_kb.admin_back())






@router.message(EditLa.edit_media, F.photo)
@router.message(EditLa.edit_media, F.video)
async def add_promotion_6(message: Message, state: FSMContext, album: list=None):
    data = await state.get_data()
    type_ = data['type_']
    media_files_ids = []

    if album:
        count_photos = len(album)
        await message.reply(f"всего {count_photos} медиа файлов")

        for idx, msg in enumerate(album):

            if msg.photo:
                media_files_ids.append("p!"+str(msg.photo[-1].file_id))
            elif msg.video:
                media_files_ids.append("v!"+str(msg.video.file_id))
            else:
                continue
            
    else:
        if message.photo:
                media = types.InputMediaPhoto(media=message.photo[-1].file_id)
                media_files_ids.append("p!"+str(message.photo[-1].file_id))
        elif message.video:
            media = types.InputMediaVideo(media=message.video.file_id)
            media_files_ids.append("v!"+str(message.video.file_id))


    if type_ == 'afisha':
        utils.edit_media_in_afisha(media=media_files_ids)

    elif type_ == 'launch':
        utils.edit_media_in_launch(media=media_files_ids)
    
    await message.answer('Данные обновленны!', reply_markup=admin_kb.admin_back_to_al(data['type_']))


@router.message(EditLa.edit_text, F.text)
async def add_promotion_6(message: Message, state: FSMContext, album: list=None):
    data = await state.get_data()
    type_ = data['type_']
    
    text = message.text

    if type_ == 'afisha':
        utils.edit_text_in_afisha(text=text)

    elif type_ == 'launch':
        utils.edit_text_in_launch(text=text)
    

        
    await message.answer('Данные обновленны!', reply_markup=admin_kb.admin_back_to_al(data['type_']))











@router.callback_query(F.data=="add")
async def add_promotion_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])

    try:
        await callback.message.edit_text("Выберите категорию для добавления акции", reply_markup=admin_kb.category_list())
    except:
        await callback.message.answer("Выберите категорию для добавления акции", reply_markup=admin_kb.category_list())


@router.callback_query(F.data.startswith("category_"))
async def add_promotion_prom(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    
    category = callback.data.split('_')[-1]
    
    await state.update_data(category=category)
    
    try:
        await callback.message.edit_text("Пришлите срок действия акции в днях", reply_markup=admin_kb.admin_back())
    except:
        await callback.message.answer("Пришлите срок действия акции в днях", reply_markup=admin_kb.admin_back())

    await state.set_state(PromotionState.lasting)

@router.message(PromotionState.lasting)
async def add_promotion_3(message: Message, state: FSMContext):
    try:
        if not message.text.isdigit():
            await message.answer("Введите число!", reply_markup=admin_kb.admin_back())
            return
        
        await state.update_data(lasting=message.text)
        await state.set_state(PromotionState.name)
        await message.answer("Введите название акции", reply_markup=admin_kb.admin_back())
    except:
        await message.answer('Что-то пошло не так, попробуйте снова /apanel')

@router.message(PromotionState.name)
async def add_promotion_3_1(message: Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await state.set_state(PromotionState.QRs_number)
        await message.answer("Пришлите количество QR для выдачи", reply_markup=admin_kb.action_qr_request())
    except:
        await message.answer('Что-то пошло не так, попробуйте снова /apanel')

@router.callback_query(F.data == 'NotQrAction')
async def notQr(cb: CallbackQuery, state: FSMContext):
    try:
        await state.update_data(qr_active=False, QRs_number=0)
        await state.set_state(PromotionState.description)
        try:
            await cb.message.edit_text("Пришлите описание акции", reply_markup=admin_kb.admin_back())
        except:
            await cb.message.answer("Пришлите описание акции", reply_markup=admin_kb.admin_back())
    except:
        await cb.message.answer('Что-то пошло не так, попробуйте снова /apanel')



@router.message(PromotionState.QRs_number)
async def add_promotion_4(message: Message, state: FSMContext):
    try:
        if not message.text.isdigit():
            await message.answer("Введите число!", reply_markup=admin_kb.admin_back())
            return
        
        await state.update_data(
            QRs_number=message.text,
            qr_active=True
            )
        await state.set_state(PromotionState.description)
        await message.answer("Пришлите описание акции", reply_markup=admin_kb.admin_back())
    except:
        await message.answer('Что-то пошло не так, попробуйте снова /apanel')


@router.message(PromotionState.description)
async def add_promotion_5(message: Message, state: FSMContext):
    try:
        await state.update_data(description=message.text)
        await state.set_state(PromotionState.photo)
        await message.answer("Прикрепите медиа акции", reply_markup=admin_kb.skip_photo())
    except:
        await message.answer('Что-то пошло не так, попробуйте снова /apanel')


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
    
    data=await state.get_data()
    caption = f'Название: {data["name"]}\n\nкатегория: {data["category"]}\nСрок действия: {data["lasting"]}\nКоличество QR: {data["QRs_number"]}\nОписание: {data["description"]}'
    await message.bot.send_media_group(
                chat_id=message.from_user.id,
                media=utils.create_media_group_for_actions(media_files_ids, caption=caption)
            )
    await message.answer('-'*20, reply_markup=admin_kb.add_promotion_final())







    # except Exception as e:
    #     lg.error(f"ERROR WHILE GETTING ACTION PHOTOS (ADMIN): {e}")
        # await message.answer(f"Ошибка, что-то пошло не так, попробуйте еще раз", reply_markup=admin_kb.admin_back())


# @router.message(PromotionState.photo)
# async def add_promotion_6(message: Message, state: FSMContext):
#     await state.update_data(photo=message.photo[-1].file_id)
#     data=await state.get_data()
#     caption = f'Название: {start_promotion.name}\n\nкатегория: {data["category"]}\nСрок действия: {data["lasting"]}\nКоличество QR: {data["QRs_number"]}\nОписание: {data["description"]}'
#     await message.answer_photo(
#                 photo=data["photo"],
#                 caption=caption,
#                 reply_markup=admin_kb.add_promotion_final()
#             )
    
@router.callback_query(F.data=="skip_photo")
async def skip_photo_finish(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data=await state.get_data()
    await state.update_data(photo="skip")
    caption = f'Название: {data["name"]}\n\nкатегория: {data["category"]}\nСрок действия: {data["lasting"]}\nКоличество QR: {data["QRs_number"]}\nОписание: {data["description"]}'
    await callback.message.answer(caption, reply_markup=admin_kb.add_promotion_final())

@router.callback_query(F.data=="finish_add")
async def finish_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # promotion_id = str(uuid.uuid4())
    prmtns = await get_promotions()
    if len(prmtns) > 0:
        pr_max_id = max([i.id for i in prmtns])
    else:
        pr_max_id=0
    try:
        await Add_promotion(
                            id=pr_max_id+1,
                            category=data["category"],
                            name=data['name'],
                            ended_at=datetime.now(pytz.timezone('Asia/Omsk')) + timedelta(days=int(data["lasting"])), 
                            max_reg=data["QRs_number"], 
                            description=data["description"], 
                            photo_id=data["photo"],
                            active=True,
                            qr_active=data['qr_active']
                            )
    except Exception as e:
        lg.error(f"Error while adding promotion: {e}")
        await callback.answer("Ошибка при добавлении акции, попробуйте снова", show_alert=True)
        await state.clear()
        return
    await callback.answer("")
    await callback.message.answer("Акция успешно добавлена", reply_markup=admin_kb.admin_back())
    await state.clear()


@router.callback_query(F.data=="cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])
    await callback.message.answer("Отмена добавления акции", reply_markup=admin_kb.admin_back())
    await state.clear()


@router.callback_query(F.data=="statistics")
async def statistics(callback: CallbackQuery):
    await callback.message.edit_text("Выберите тип акций", reply_markup=admin_kb.promotions_type())






#Функция кнопки "Статус"
@router.callback_query(F.data.startswith("status_"))
async def active(callback: CallbackQuery, bot: Bot):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])

    type_of_operation=str(callback.data.split("_")[-1])
    promotions: list[Promotion] = []

    promotions_old = await get_promotions()

    for promotion in promotions_old:
        if type_of_operation=="active":
            if promotion.active:
                promotions.append(promotion)
        elif type_of_operation=="archived":
            if not promotion.active:
                promotions.append(promotion)
    
    try:
        start_promotion=promotions[0]
    except:
        await callback.message.answer("Нет акций данного статуса", reply_markup=admin_kb.admin_back())
        return
    
    await callback.answer()
    caption = f"Название: {start_promotion.name}\n"\
                    f"Описание: {start_promotion.description}\n"\
                    f'Акция активна до: {start_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\n'\
                    f"Количество QR: {start_promotion.max_reg}\n"\
                    f"Пользователей зарегистрировано: {start_promotion.reg_count}\n"\
                    f"Кол-во пользователей воспользовавшийхся QR: {start_promotion.enter_count}"
    
    if start_promotion.photo_id == 'skip':
        await callback.message.answer(
                text=caption,
                reply_markup=admin_kb.admin_start_promotion_button(1, len_promotion=len(promotions), status=type_of_operation)
            )
        
    else:
        await callback.bot.send_media_group(
                chat_id=callback.from_user.id,
                media=utils.create_media_group_for_actions(start_promotion.photo_id.split(';'), caption=caption)
                
            )
        await callback.message.answer('-'*20, reply_markup=admin_kb.admin_start_promotion_button(1, len_promotion=len(promotions), status=type_of_operation))
    
@router.callback_query(F.data.startswith("Admnavigation_"))
async def navigation(callback: CallbackQuery):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])

    promotions_old=await get_promotions() #cписок товаров 
    promotions = []
    
    data = callback.data.split("_")
    action=data[1] #Действие "вперёд" или "назад"
    promotion_index=int(data[2]) #индекс текущего товара
    status = data[-1]


    for promotion in promotions_old:
        if status=="active":
            if promotion.active:
                promotions.append(promotion)
        elif status=="archived":
            if not promotion.active:
                promotions.append(promotion)
    
    try:
        start_promotion=promotions[0] #стартовый товар
    except:
        await callback.answer('На данный момент, тут ничего нет')
        return
    

    if action=="forward":

        if promotion_index==len(promotions)-1: #Проверка на выход на последний товар
            try:
                current_promotion=promotions[promotion_index]
            except:
                await callback.answer('Конец списка!', show_alert=True)
                return
            

            caption =   f"Название: {current_promotion.name}\n"\
                        f"Описание: {current_promotion.description}\n"\
                        f'Акция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\n'\
                        f"Количество QR: {current_promotion.max_reg}\n"\
                        f"Пользователей зарегистрировано: {current_promotion.reg_count}\n"\
                        f"Кол-во пользователей воспользовавшийхся QR: {current_promotion.enter_count}"
            if current_promotion.photo_id == 'skip':
                
                await callback.message.answer(
                        text=caption,
                        reply_markup=admin_kb.admin_end_promotion_button(
                            len_promotion=len(promotions),
                            back_promotion=promotion_index-1,
                            status=status
                        ))
                return
            else:
                await callback.bot.send_media_group(
                        # photo=current_promotion.photo_id,
                        chat_id=callback.from_user.id,

                        media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'), caption=caption)
                        
                        )
                await callback.message.answer('-'*20, reply_markup=admin_kb.admin_end_promotion_button(
                            len_promotion=len(promotions),
                            back_promotion=promotion_index-1,
                            status=status))
                return
        
        try:
            current_promotion=promotions[promotion_index]
        except IndexError:
            await callback.answer('Конец списка', show_alert=True)
            return
        
        caption =   f"Название: {current_promotion.name}\n"\
                    f"Описание: {current_promotion.description}\n"\
                    f'Акция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\n'\
                    f"Количество QR: {current_promotion.max_reg}\n"\
                    f"Пользователей зарегистрировано: {current_promotion.reg_count}\n"\
                    f"Кол-во пользователей воспользовавшийхся QR: {current_promotion.enter_count}"
        
        if current_promotion.photo_id == 'skip':
            await callback.message.answer(
                    text=caption,
                    reply_markup=admin_kb.admin_middle_promotion_button(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1, #Потому что индекс товаров начинается с 0, а номер первого товара 1
                        status=status
                    )
                )
        else:
            await callback.bot.send_media_group(
                chat_id=callback.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
                # photo=current_promotion.photo_id,
                
            )
            await callback.message.answer('-'*20, reply_markup=admin_kb.admin_middle_promotion_button(
                    next_promotion=promotion_index+1,
                    len_promotion=len(promotions),
                    back_promotion=promotion_index-1,
                    current_promotion_number=promotion_index+1, #Потому что индекс товаров начинается с 0, а номер первого товара 1
                    status=status
                ))
        return



    elif action=="back":

        if promotion_index<1: #Проверка на выход на первый товар
            caption =   f"Название: {start_promotion.name}\n"\
                        f"Описание: {start_promotion.description}\n"\
                        f'Акция активна до: {start_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\n'\
                        f"Количество QR: {start_promotion.max_reg}\n"\
                        f"Пользователей зарегистрировано: {start_promotion.reg_count}\n"\
                        f"Кол-во пользователей воспользовавшийхся QR: {start_promotion.enter_count}"
            
            if start_promotion.photo_id == 'skip':
                await callback.message.answer(
                    text=caption,
                    reply_markup=admin_kb.admin_start_promotion_button(1, len_promotion=len(promotions),
                            status=status)
                )
            else:
                await callback.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    media=utils.create_media_group_for_actions(start_promotion.photo_id.split(';'),caption=caption)
                    
                )

                await callback.message.answer('-'*20, reply_markup=admin_kb.admin_start_promotion_button(1, len_promotion=len(promotions),
                            status=status))
            return
         
        current_promotion=promotions[promotion_index]
        caption =   f"Название: {current_promotion.name}\n"\
                    f"Описание: {current_promotion.description}\n"\
                    f'Акция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\n'\
                    f"Количество QR: {current_promotion.max_reg}\n"\
                    f"Пользователей зарегистрировано: {start_promotion.reg_count}\n"\
                    f"Кол-во пользователей воспользовавшийхся QR: {start_promotion.enter_count}"
        if current_promotion.photo_id == 'skip':
            await callback.message.answer(
                text=caption,
                reply_markup=admin_kb.admin_middle_promotion_button(
                    next_promotion=promotion_index+1,
                    len_promotion=len(promotions),
                    back_promotion=promotion_index-1,
                    current_promotion_number=promotion_index+1,
                    status=status
                )
            )
        
        else:
            await callback.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=callback.from_user.id,

                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'), caption=caption)
                )
            await callback.message.answer('-'*20, reply_markup=admin_kb.admin_middle_promotion_button(
                    next_promotion=promotion_index+1,
                    len_promotion=len(promotions),
                    back_promotion=promotion_index-1,
                    current_promotion_number=promotion_index+1,
                    status=status
            ))
        


@router.callback_query(F.data=="mailing")
async def mailing_1(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Пришлите пост для рассылки", reply_markup=admin_kb.admin_back())
    await state.set_state(Mailing.waiting_for_post)


@router.message(Mailing.waiting_for_post, F.photo)
@router.message(Mailing.waiting_for_post, F.video)
@router.message(Mailing.waiting_for_post, F.text)
async def mailing_2(message: Message, state: FSMContext, album: list=None):
    # try:
        media_group = []
        media_for_preview_list = []
        if album:
            count_photos = len(album)
            await message.reply(f"всего {count_photos} медиа файлов")
            # print(message.media_group_id)
            for idx, msg in enumerate(album):
                # print(msg)
                # await message.answer_photo(msg.file_id)
                
                if msg.photo:
                    media_for_preview =types.InputMediaPhoto(media=msg.photo[-1].file_id)
                    media = "p!"+msg.photo[-1].file_id
                elif msg.video:
                    media_for_preview =types.InputMediaVideo(media=msg.video.file_id)
                    media = "v!"+msg.video.file_id
                else:
                    continue
                
                if idx == 0:
                    caption = msg.caption or None
                    media_for_preview.caption = msg.caption
                
                media_group.append(media)
                media_for_preview_list.append(media_for_preview)
            
            await message.bot.send_media_group(chat_id=message.from_user.id, media=media_for_preview_list)
            await state.update_data(
                    media_ids=media_group,
                    text=caption,
                    isOnlyText=0
                )

        else:
            isOnlyText = 1
            if message.photo:
                await state.update_data(media_ids="p!"+message.photo[-1].file_id, text=None)
                if message.caption:
                    await state.update_data(text=message.caption)
                    # print('caption')
                    await message.answer_photo(photo=message.photo[-1].file_id, caption=message.caption)
                    isOnlyText = 0
                else:
                    await message.answer_photo(photo=message.photo[-1].file_id)

                # print('photo')

            if message.video:
                await state.update_data(media_ids="v!"+message.video.file_id, text=None)
                if message.caption:
                    # print('caption')
                    await state.update_data(text=message.caption)
                    isOnlyText = 0
                    await message.answer_video(video=message.video.file_id, caption=message.caption)
                else:
                    await message.answer_video(video=message.video.file_id)
                
                # print('video')

            if message.text:
                await state.update_data(text=message.text)
                await state.update_data(media_ids="")
                isOnlyText = 1
                # print('text')
                await message.answer(message.text)

            await state.update_data(isOnlyText=isOnlyText)

    
        await message.answer('Подтвердите отправку поста ВСЕМ пользователям', reply_markup=admin_kb.confirm_send_post())
        

    
    # except Exception as e:
    #     lg.error(f"ERROR WHILE RESENDING POST: {e}")
    #     await message.answer(f"Ошибка, что-то пошло не так, попробуйте еще раз", reply_markup=admin_kb.admin_back())



@router.callback_query(F.data.startswith('post_'))
async def handle_post(cb: CallbackQuery, state: FSMContext):
    confirm = cb.data.split('_')[-1]
    await cb.answer()

    try:
        data = await state.get_data()
        media_ids = data['media_ids']
        text = data['text']
        try:
            isOnlyText = data['isOnlyText']
        except:
            isOnlyText = 0
    except:
        await cb.message.edit_text('Запрос устарел!', reply_markup=admin_kb.admin_back())
        return
    
    await state.clear()
    
    if confirm == 'confirm':
        users = await get_users_role('user')

        if media_ids == '' and isOnlyText:
            for user in users:
                try:
                    await cb.bot.send_message(
                        chat_id=user.user_id,
                        text=text
                    )
                except TelegramForbiddenError:
                    continue

                
        elif len(media_ids)>0:
            if type(media_ids) == list:
                media_group = utils.create_media_group_for_actions(
                    list_media_id=media_ids,
                    caption=text
                    )
            else:
                media_group = utils.create_media_group_for_actions(
                    list_media_id=[media_ids],
                    caption=text
                    )

            for user in users:
                await cb.bot.send_media_group(
                    chat_id=user.user_id, 
                    media=media_group,
                )
                
        await cb.message.edit_text("Пост переслан всем пользователям успешно!", reply_markup=admin_kb.admin_back())
    else:
        await cb.message.edit_text("Отмена рассылки!", reply_markup=admin_kb.admin_back())


@router.callback_query(F.data=="edit")
async def edit_promotion(callback: CallbackQuery, state: FSMContext):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])

    promotions = []
    promotions_old = await get_promotions()
    for promotion in promotions_old:
            if promotion.active:
                promotions.append(promotion)

    start_promotion=promotions[0]
    await callback.answer()
    caption = f'Название: {start_promotion.name}\n\nОписание: {start_promotion.description}\nАкция активна до: {start_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {start_promotion.max_reg}'
    if not start_promotion.photo_id == 'skip':
        await callback.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    # photo=start_promotion.photo_id,
                    media=utils.create_media_group_for_actions(start_promotion.photo_id.split(';'), caption=caption)
            )
        await callback.message.answer('-'*20, reply_markup=admin_kb.start_promotion_button_a(1, len_promotion=len(promotions)))
    else:
         await callback.message.answer(
                    text=caption,
                    reply_markup=admin_kb.start_promotion_button_a(1, len_promotion=len(promotions)
                                                                   )
                                                                )
    


@router.callback_query(F.data.startswith("a_navigation_"))
async def navigation(callback: CallbackQuery):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])
    promotions = []
    promotions_old = await get_promotions()
    
    for promotion in promotions_old:
            if promotion.active:
                promotions.append(promotion)
 
    start_promotion=promotions[0] #стартовый товар
    data = callback.data.split("_")
    action=data[-2] #Действие "вперёд" или "назад"
    promotion_index=int(data[-1]) #индекс текущего товара

    if action=="forward":

        if promotion_index==len(promotions)-1: #Проверка на выход на последний товар
            current_promotion=promotions[promotion_index]
            caption = f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
            if current_promotion.photo_id == 'skip':
                await callback.message.answer(caption, reply_markup=admin_kb.end_promotion_button_a(
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1)
                        )
            else:
                await callback.bot.send_media_group(
                        # photo=current_promotion.photo_id,
                        chat_id=callback.from_user.id,
                        media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'), caption=caption)
                        
                        )
                await callback.message.answer('-'*20, reply_markup=admin_kb.end_promotion_button_a(
                    len_promotion=len(promotions),
                    back_promotion=promotion_index-1)
                    )
            return
        
        try:
            current_promotion=promotions[promotion_index]
        except:
            await callback.answer('Конец списка', show_alert=True)
            return
        caption = f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
        if current_promotion.photo_id == 'skip':
            await callback.message.answer(caption, reply_markup=admin_kb.middle_promotion_button_a(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1, #Потому что индекс товаров начинается с 0, а номер первого товара 1
                    )
                    )
        else:
            await callback.bot.send_media_group(
                    # photo=current_promotion.photo_id,
                    chat_id=callback.from_user.id,
                    media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
                    
                )
            await callback.message.answer('-'*20, reply_markup=admin_kb.middle_promotion_button_a(
                    next_promotion=promotion_index+1,
                    len_promotion=len(promotions),
                    back_promotion=promotion_index-1,
                    current_promotion_number=promotion_index+1, #Потому что индекс товаров начинается с 0, а номер первого товара 1
                )
            )
        
    elif action=="back":

        if promotion_index<1: #Проверка на выход на первый товар
            caption =f'Название: {start_promotion.name}\n\nОписание: {start_promotion.description}\nАкция активна до: {start_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {start_promotion.max_reg}'
            if start_promotion.photo_id == 'skip':
                await callback.message.answer(caption, reply_markup=admin_kb.start_promotion_button_a(1, len_promotion=len(promotions)))
            else:
                await callback.bot.send_media_group(
                    # photo=start_promotion.photo_id,
                    chat_id=callback.from_user.id,

                    media=utils.create_media_group_for_actions(start_promotion.photo_id.split(';'),caption=caption)
                )
                await callback.message.answer('-'*20, reply_markup=admin_kb.start_promotion_button_a(1, len_promotion=len(promotions)))
            return
         
        current_promotion=promotions[promotion_index]
        caption = f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
        if current_promotion.photo_id == 'skip':
            await callback.message.answer(caption, reply_markup=admin_kb.middle_promotion_button_a(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1,
                    )
                    )
        else:
            await callback.bot.send_media_group(
                    # photo=current_promotion.photo_id,
                    chat_id=callback.from_user.id,
                    media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
                )
            await callback.message.answer('-'*20, reply_markup=admin_kb.middle_promotion_button_a(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1,
                    )
                )
            



@router.callback_query(F.data.startswith("promotion_edit"))
async def edit_promotion(callback: CallbackQuery, state: FSMContext):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])
    
    data = callback.data.split("_")
    promotion_id = str(data[-1])
    promotions = [i for i in await get_promotions() if i.active]
    promotion_id = int(data[-1])
    current_promotion=promotions[promotion_id]
    caption= f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
    
    
    if current_promotion.photo_id == 'skip':
        await callback.message.answer(
            text=caption,
            reply_markup=admin_kb.admin_promotions_kb_edit(promotion_id)
        )
    else:
        await callback.bot.send_media_group(
            # photo=current_promotion.photo_id,
            chat_id=callback.from_user.id,
            media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'), caption=caption)
            
        )
        await callback.message.answer('-'*20, reply_markup=admin_kb.admin_promotions_kb_edit(promotion_id))



@router.callback_query(F.data.startswith("PromotionEdit_"))
async def edit_promotion(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    promotion_id = int(data[-1])
    promotions = [i for i in await get_promotions() if i.active]
    edit_type=data[-2]
    try:
        current_promotion=promotions[promotion_id]
    except:
        await callback.answer('Конец списка', show_alert=True)
        return
    if edit_type == "description":
        await state.set_state(Description_edit.description_edit)
        await state.update_data(promotion_id=current_promotion.id)
        await state.update_data(ids=int(data[-1]))
        await callback.message.answer("Введите новое описание:", reply_markup=admin_kb.admin_back())
    elif edit_type == "lasting":
        await state.set_state(Lasting_edit.lasting_edit)
        await state.update_data(promotion_id=current_promotion.id)
        await state.update_data(ids=int(data[-1]))
        await callback.message.answer("Введите новое количество дней:", reply_markup=admin_kb.admin_back())
    elif edit_type == "QRnumber":
        await state.set_state(QRs_number_edit.QRs_number_edit)
        await state.update_data(promotion_id=current_promotion.id)
        await state.update_data(ids=int(data[-1]))
        await callback.message.answer("Введите новое количество QR:", reply_markup=admin_kb.admin_back())
    elif edit_type == "photo":
        await state.set_state(Photo_edit.photo_edit)
        await state.update_data(promotion_id=current_promotion.id)
        await state.update_data(ids=int(data[-1]))
        await callback.message.answer("Отправьте новое фото:", reply_markup=admin_kb.admin_back())

    elif edit_type== "archive":
        await state.set_state(Archive_edit.archive_edit)
        await state.update_data(promotion_id=current_promotion.id)
        data = await state.get_data()
        promotion_id = data['promotion_id']
        if "promotion_id" not in data.keys():
            await callback.message.answer("Данные устарели, попробуйте снова - /apanel")
            return
        try:
            await Update_promotion(id=promotion_id, active=0)
            await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(6)])
            await callback.message.answer("Акция помещена в архив", reply_markup=admin_kb.admin_back())
        except Exception as e:
            await callback.message.answer(f"Произошла ошибка при обновлении описания: {str(e)}", reply_markup=admin_kb.admin_back())
        await state.clear()

    elif edit_type=="delete":
        await state.set_state(Archive_edit.archive_edit)
        await state.update_data(promotion_id=current_promotion.id)
        data = await state.get_data()
        promotion_id = data['promotion_id']
        if "promotion_id" not in data.keys():
            await callback.message.answer("Данные устарели, попробуйте снова - /apanel", reply_markup=admin_kb.admin_back())
            return
        try:
            await Delete_promotion(id=promotion_id)
            await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(6)])
            await callback.message.answer("Акция успешно удалена", reply_markup=admin_kb.admin_back())
        except Exception as e:
            await callback.message.answer(f"Произошла ошибка при удалении акции: {str(e)}", reply_markup=admin_kb.admin_back())
        await state.clear()

    elif edit_type=="confirm":
        caption =f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}\n\nАкция обновлена'
        
        if current_promotion.photo_id == 'skip':
            await callback.message.answer(
                
                text=caption,
                reply_markup=admin_kb.admin_back()
            )
        else:
            await callback.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=callback.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
            )
            await callback.message.answer('-'*20, reply_markup=admin_kb.admin_back())
        


@router.message(Description_edit.description_edit)
async def description_edit(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    data = await state.get_data()
    promotion_id = data['promotion_id']
    
    if "promotion_id" not in data.keys():
        await message.answer("Данные устарели, попробуйте снова - /apanel")
        return

    try:
        await Update_promotion(id=promotion_id, description=description)
        # await message.answer("Описание успешно изменено.")
        
        promotions = [i for i in await get_promotions() if i.active]

        current_promotion=promotions[int(data["ids"])]
        caption= f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
        
        if current_promotion.photo_id == 'skip':
            await message.answer(
                
                text=caption,
                reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
            )
        else:
            await message.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=message.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
            )
            await message.answer('-'*20, reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"])))
            
    except Exception as e:
        await message.answer(f"Произошла ошибка при обновлении описания: {str(e)}", reply_markup=admin_kb.admin_back())

    await state.clear()


@router.message(Lasting_edit.lasting_edit)
async def lasting_edit(message: Message, state: FSMContext):
    lasting = message.text
    await state.update_data(ended_at=lasting)
    data = await state.get_data()
    promotion_id = data['promotion_id']
    
    if "promotion_id" not in data.keys():
        await message.answer("Данные устарели, попробуйте снова - /apanel")
        return

    try:
        await Update_promotion(id=promotion_id, ended_at=lasting)
        promotions = [i for i in await get_promotions() if i.active]

        current_promotion=promotions[int(data["ids"])]
        caption= f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}\n\n'
        
        if current_promotion.photo_id == 'skip':
            await message.answer(
                
                text=caption,
                reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
            )
        else:
            await message.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=message.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'), caption=caption)
            )

            await message.answer('-'*20, reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"])))
        
        # await message.answer_photo(
        #     photo=current_promotion.photo_id,
        #     caption=caption,
        #     reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
        # )
        # await message.answer("Количество дней успешно изменено.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при обновлении дней: {str(e)}")

    await state.clear()

@router.message(QRs_number_edit.QRs_number_edit)
async def QRnumber_edit(message: Message, state: FSMContext):
    QRnumber = message.text
    await state.update_data(QRnumber=QRnumber)
    data = await state.get_data()
    promotion_id = data['promotion_id']
    
    if "promotion_id" not in data.keys():
        await message.answer("Данные устарели, попробуйте снова - /apanel")
        return

    try:
        await Update_promotion(id=promotion_id, max_reg=QRnumber)
        promotions = [i for i in await get_promotions() if i.active]

        current_promotion=promotions[int(data["ids"])]
        caption= f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
        
        if current_promotion.photo_id == 'skip':
            await message.answer(
                
                text=caption,
                reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
            )
        else:
            await message.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=message.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
            )
            await message.answer('-'*20, reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"])))
         
    except Exception as e:
        await message.answer(f"Произошла ошибка при обновлении количества QR: {str(e)}")

    await state.clear()

@router.message(Photo_edit.photo_edit)
async def QRnumber_edit(message: Message, state: FSMContext):
    Photo = message.photo[-1].file_id
    await state.update_data(Photo=Photo)
    data = await state.get_data()
    promotion_id = data['promotion_id']
    
    if "promotion_id" not in data.keys():
        await message.answer("Данные устарели, попробуйте снова - /apanel")
        return

    try:
        await Update_promotion(id=promotion_id, photo=Photo)
        promotions = [i for i in await get_promotions() if i.active]
        current_promotion=promotions[int(data["ids"])]
        caption= f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
        if current_promotion.photo_id == 'skip':
            await message.answer(
                
                text=caption,
                reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
            )
        else:
            await message.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=message.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
            )
            await message.answer('-'*20, reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"])))

        # await message.answer_photo(
        #     photo=current_promotion.photo_id,
        #     caption=caption,
        #     reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
        # )
        # await message.answer("Фото успешно изменено.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при обновлении фото: {str(e)}")

    await state.clear()

@router.message(QRs_number_edit.QRs_number_edit)
async def QRnumber_edit(message: Message, state: FSMContext):
    QRnumber = message.text
    await state.update_data(QRnumber=QRnumber)
    data = await state.get_data()
    promotion_id = data['promotion_id']
    
    if "promotion_id" not in data.keys():
        await message.answer("Данные устарели, попробуйте снова - /apanel")
        return

    try:
        await Update_promotion(id=promotion_id, max_reg=QRnumber)
        promotions = [i for i in await get_promotions() if i.active]
        current_promotion=promotions[int(data["ids"])]
        caption= f'Название: {current_promotion.name}\n\nОписание: {current_promotion.description}\nАкция активна до: {current_promotion.ended_at.strftime("%d-%m-%Y %H:%M")}\nКоличество QR: {current_promotion.max_reg}'
        
        if current_promotion.photo_id == 'skip':
            await message.answer(
                
                text=caption,
                reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
            )
        else:
            await message.bot.send_media_group(
                # photo=current_promotion.photo_id,
                chat_id=message.from_user.id,
                media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
            )
            await message.answer('-'*20, reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"])))

        # await message.answer_photo(
        #     photo=current_promotion.photo_id,
        #     caption=caption,
        #     reply_markup=admin_kb.admin_promotions_kb_edit(int(data["ids"]))
        # )
        # await message.answer("Количество QR успешно изменено.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при обновлении количества QR: {str(e)}")

    await state.clear()
    




