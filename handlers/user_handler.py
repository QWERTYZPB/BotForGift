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
    


    



@router.callback_query(F.data == 'check_subscr')
async def second_start(cb: CallbackQuery):
    controllers_id = [user.user_id for user in await req.get_controlers()]
    
    if cb.from_user.id in config.ADMIN_IDS:
        role = "admin"
    elif cb.from_user.id in controllers_id:
        role = "controller"
    else:
        role = "user"

    
    
    try:
        start_message = await cb.message.edit_text(lexicon.START_TEXT, disable_web_page_preview=True, reply_markup=user_kb.user_start())
    except:
        start_message = await cb.message.answer(lexicon.START_TEXT, disable_web_page_preview=True, reply_markup=user_kb.user_start())
    
    await add_user(       #Добавляем нового пользователя при старте бота
        user_id=cb.from_user.id,
        username=cb.from_user.username,
        full_name=cb.from_user.full_name,
        role=role,
        start_message_id=start_message.message_id
    )



@router.callback_query(F.data.startswith('enterance_'))
async def check_enterance(cb: CallbackQuery):
    data = cb.data.split('_')
    vibor = data[1]
    user_id = int(data[2])
    action_id = data[3]



    if vibor == 'confirm':
        action = await get_promotion_by_id(action_id)
        user = await get_user_by_id(user_id)

        await cb.answer('Готово! Пользователь отмечен', show_alert=True)
        await cb.message.delete()

        # await update_user(user_id=cb.from_user.id, events_ids=','.join(user_events))
        await Update_promotion(
            id=action.id,
            enter_count=action.enter_count+1,
            enter_users_ids=str(user.user_id)+","
            
            )
        return
    await cb.message.delete()
    await cb.answer('Отмена прохода', show_alert=True)





@router.callback_query(F.data=="about")
async def about(callback: CallbackQuery):
    await callback.message.answer(lexicon.INFO_ABOUT, reply_markup=user_kb.back_to_mainmenu())


@router.callback_query(F.data=="myQr")
async def handle_my_qrs(cb: CallbackQuery):
    user = await get_user_by_id(cb.from_user.id)

    try:
        user_qrs = [await get_promotion_by_id(pr_id) for pr_id in user.events_ids.split(',')]
    except:
        await cb.message.answer('Что-то пошло не так, попробуйте нажать /start')
    while None in user_qrs:
        user_qrs.remove(None)
    
    user_qrs = [action for action in user_qrs if action.active]
    
    await update_user(
        user_id=cb.from_user.id, 
        events_ids=','.join([str(i.id) for i in user_qrs])
    )

    if len(user_qrs) == 0:
        await cb.answer('Вы еще не зарегестрированны ни на одно мероприятие!', show_alert=True)
        return


    try:
        await cb.message.edit_text("Выберите акцию:", reply_markup= user_kb.show_user_qr_names(user_qrs))
    except:
        await cb.message.answer("Выберите акцию:", reply_markup= user_kb.show_user_qr_names(user_qrs))


@router.callback_query(F.data.startswith('seeQr_'))
async def see_qr(cb: CallbackQuery):
    await cb.answer('')
    await utils.delete_messages(cb=cb, message_ids=[cb.message.message_id-j for j in range(12)])

    action_id = cb.data.split('_')[-1]

    action = await get_promotion_by_id(action_id)

    prepared_qr = await utils.generate_qrcode(
        payload= await create_start_link(
            bot=cb.bot,
            payload=str(cb.from_user.id)+f'_{action.id}',
            encode=True
        )
    )
    await cb.message.answer_photo(
        photo=prepared_qr,
        caption='Покажите ваш QR при входе.\n\nДанный QR-код сохранен к вам во вкладку "Мои QR"',
        reply_markup=user_kb.back_to_mainmenu()
        )






@router.callback_query(F.data=="karting")
async def kartingg(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer(lexicon.KARTING_TEXT, disable_web_page_preview=True, reply_markup= user_kb.karting())
    # try:
    #     await callback.message.edit_text(lexicon.KARTING_TEXT, reply_markup= user_kb.karting())
    # except Exception:

    # await callback.message.answer('Меню')
    
@router.callback_query(F.data=="restoran")
async def restoran(callback: CallbackQuery):
    await callback.answer('')
    
    await callback.message.answer(lexicon.RESTORAN_TEXT, disable_web_page_preview=True, reply_markup= user_kb.restoraunt())
    # try:
    #     await callback.message.edit_text(lexicon.RESTORAN_TEXT, disable_web_page_preview=True, reply_markup=user_kb.restoraunt())
    # except:


    
@router.callback_query(F.data=="caraoke")
async def caraoke(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    # try:
    #     await callback.message.edit_text(
    #         text=lexicon.KARAOKE_TEXT,
    #         reply_markup=user_kb.caraoke()
    #     )
    # except:
    await callback.message.answer(
        text=lexicon.KARAOKE_TEXT,
        reply_markup=user_kb.caraoke()
    )

@router.callback_query(F.data=="bowling")
async def bowling(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    await callback.message.answer(lexicon.BOULING_TEXT, reply_markup=user_kb.bowling())


@router.callback_query(F.data=="dancing")
async def bowling(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    await callback.message.answer(lexicon.DANCE_TEXT, reply_markup=user_kb.dance_kb())

@router.callback_query(F.data=="banket")
async def bowling(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    await callback.message.answer(lexicon.BANKET_TEXT, reply_markup=user_kb.dr_kb())




@router.callback_query(F.data=="back_to_mainmenu")
async def back_to_mainmenu(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    
    try:await state.clear()
    except:pass

    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(1)])

    # await callback.answer()
    await add_user(
        user_id=callback.from_user.id
    )
    await callback.message.answer(lexicon.START_TEXT, disable_web_page_preview=True,  reply_markup=user_kb.user_start())



@router.callback_query(F.data.startswith("back_to_category_menu_"))
async def back_to_category_menu(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    category_type = (callback.data.split("_")[-1])
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])
    lg.info(f"BACK TO {category_type}")
    if category_type == "karting" or category_type == "k":
        await utils.try_to_edit_else_answer(cb=callback, text=lexicon.KARTING_TEXT, markup=user_kb.karting())
    elif category_type == "restoran" or category_type == "r":
        await utils.try_to_edit_else_answer(cb=callback, text=lexicon.RESTORAN_TEXT, markup=user_kb.restoraunt())
    elif category_type == "caraoke" or category_type == "c":
        await utils.try_to_edit_else_answer(cb=callback, text=lexicon.KARAOKE_TEXT, markup=user_kb.caraoke())
    elif category_type == "bowling" or category_type == "b":
        await utils.try_to_edit_else_answer(cb=callback, text=lexicon.BOULING_TEXT, markup=user_kb.bowling())
    elif category_type == "dancing" or category_type == "da":
        await utils.try_to_edit_else_answer(cb=callback, text=lexicon.DANCE_TEXT, markup=user_kb.dance_kb())
    elif category_type == "banket" or category_type == "dr":
        await utils.try_to_edit_else_answer(cb=callback, text=lexicon.BANKET_TEXT, markup=user_kb.dr_kb())




@router.callback_query(F.data.startswith("events_"))
async def user_promotions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    category = callback.data.split('_')[-1]

    lg.info(f"NAVIGATING FOR CATEGORY: {category}")

    promotions = await get_promotions()
    # print(category)
    promotions = [promotion for promotion in promotions if promotion.category == categ_dict[category] and promotion.active]
    # print(promotions)
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(5)])
    await state.update_data(category=categ_dict[category])
    try:
        start_promotion=promotions[0]
    except IndexError:
        lg.error(f"NAVIGATING ERROR FOR CATEGORY: {category}:{categ_dict[category]} CATEGORIES: {promotions}")

        await callback.message.answer("Нет акций в этой категории", reply_markup=user_kb.back_to_mainmenu())
        return
    
    caption = f'Название: {start_promotion.name}\n\nОписание:\n{start_promotion.description}'
    if not start_promotion.photo_id == 'skip':
        await callback.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    # photo=start_promotion.photo_id,
                    media=utils.create_media_group_for_actions(start_promotion.photo_id.split(';'), caption=caption)
                    
                )
        await callback.message.answer('-'*20, reply_markup=user_kb.start_promotion_button(
            1, 
            len_promotion=len(promotions), 
            category=category,
            action_id=start_promotion.id,
            qr_active=start_promotion.qr_active
            ))
    else:
        await callback.message.answer(text=caption, reply_markup=user_kb.start_promotion_button(
            1, 
            len_promotion=len(promotions), 
            category=category,
            action_id=start_promotion.id,
            qr_active=start_promotion.qr_active
            ))
    
    
@router.callback_query(F.data.startswith("navigation_"))
async def navigation(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    try:
        data = await state.get_data()
        if 'category' in data.keys():
            
            category = data['category']
        else:
            await callback.message.answer('Данные устарели, зайдите заново', reply_markup=user_kb.back_to_mainmenu())
            return
    except:
        await callback.message.answer('Данные устарели, зайдите заново', reply_markup=user_kb.back_to_mainmenu())
        return

    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])
    # await callback.message.delete()

    promotions=await get_promotions() #cписок товаров 
    promotions = [pr for pr in promotions if pr.category == category and pr.active]

    try:
        start_promotion=promotions[0] #стартовый товар
    except IndexError:
        await callback.answer("Нет акций в этой категории или конец списка")
        return
    data = callback.data.split("_")
    action=data[1] #Действие "вперёд" или "назад"
    
    promotion_index=int(data[-1]) #индекс текущего товара

    if action=="forward":

        if promotion_index==len(promotions)-1: #Проверка на выход на последний товар
            current_promotion=promotions[promotion_index]
            caption = f'Название: {current_promotion.name}\n\nОписание:\n{current_promotion.description}'
            if current_promotion.photo_id =='skip':
                await callback.message.answer(caption, reply_markup=user_kb.end_promotion_button(
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        category=category,
                        action_id=current_promotion.id,
                        qr_active=current_promotion.qr_active

                        )
                    )
                
            else:
                await callback.bot.send_media_group(
                        chat_id=callback.from_user.id,
                        # photo=current_promotion.photo_id,
                        media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'), caption=caption)
                        
                        )
                await callback.message.answer('-'*20, reply_markup=user_kb.end_promotion_button(
                    len_promotion=len(promotions),
                    back_promotion=promotion_index-1,
                    category=category,
                    action_id=current_promotion.id,
                    qr_active=current_promotion.qr_active

                    ))
            return
        
        try:
            current_promotion=promotions[promotion_index]
        except IndexError:
            await callback.message.answer("Нет акций в этой категории", reply_markup=user_kb.back_to_mainmenu())
            return
        

        caption = f'Название: {current_promotion.name}\n\nОписание:\n{current_promotion.description}'
        if current_promotion.photo_id == 'skip':
            await callback.message.answer(caption, reply_markup=user_kb.middle_promotion_button(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1, #Потому что индекс товаров начинается с 0, а номер первого товара 1,
                        category=category,
                        action_id=current_promotion.id,
                        qr_active=current_promotion.qr_active
                    )
                    )
        else:
            await callback.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    # photo=current_promotion.photo_id,
                    media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
                    
                )
            await callback.message.answer('-'*20, reply_markup=user_kb.middle_promotion_button(
                next_promotion=promotion_index+1,
                len_promotion=len(promotions),
                back_promotion=promotion_index-1,
                current_promotion_number=promotion_index+1, #Потому что индекс товаров начинается с 0, а номер первого товара 1,
                category=category,
                action_id=current_promotion.id,
                qr_active=current_promotion.qr_active

            ))
        
    elif action=="back":

        if promotion_index<1: #Проверка на выход на первый товар
            caption =f'Название: {start_promotion.name}\n\nОписание:\n{start_promotion.description}'
            if start_promotion.photo_id == 'skip':
                await callback.message.answer(caption, reply_markup=user_kb.start_promotion_button(
                    1,
                    len_promotion=len(promotions)),
                    category=category,
                    action_id=start_promotion.id,
                    qr_active=start_promotion.qr_active
                    )
            else:
                await callback.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    # photo=start_promotion.photo_id,
                    media=utils.create_media_group_for_actions(start_promotion.photo_id.split(';'),caption=caption)
                )

                await callback.message.answer('-'*20, reply_markup=user_kb.start_promotion_button(
                    1,
                    len_promotion=len(promotions),
                    category=category,
                    action_id=start_promotion.id,
                    qr_active=start_promotion.qr_active
                    ))
            return
        
        try:
            current_promotion=promotions[promotion_index]
        except IndexError:
            await callback.message.answer("Нет акций в этой категории", reply_markup=user_kb.back_to_mainmenu())
            return
        
        caption = f'Название: {current_promotion.name}\n\nОписание:\n{current_promotion.description}'
        if current_promotion.photo_id =='skip':
            await callback.message.answer(caption, reply_markup=user_kb.middle_promotion_button(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1,
                        category=category,
                        action_id=current_promotion.id,
                        qr_active=current_promotion.qr_active

                    )
                    )
        else:
            await callback.bot.send_media_group(
                    chat_id=callback.from_user.id,
                    # photo=current_promotion.photo_id,
                    media=utils.create_media_group_for_actions(current_promotion.photo_id.split(';'),caption=caption)
                )
            await callback.message.answer('-'*20, reply_markup=user_kb.middle_promotion_button(
                        next_promotion=promotion_index+1,
                        len_promotion=len(promotions),
                        back_promotion=promotion_index-1,
                        current_promotion_number=promotion_index+1,
                        category=category,
                        action_id=current_promotion.id,
                        qr_active=current_promotion.qr_active

                    ))
            






"""  РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ ПО QR  """



@router.callback_query(F.data.startswith('getQr_'))
async def handle_get_qr(cb: CallbackQuery):
    await utils.delete_messages(cb=cb, message_ids=[cb.message.message_id-j for j in range(12)])

    data = cb.data.split('_')
    category = data[1]
    action_id = data[-1]

    action = await get_promotion_by_id(action_id)
    user = await get_user_by_id(cb.from_user.id)

    if action.reg_count >= action.max_reg:
        await cb.answer(text="К сожалению, регистрации по QR закончились!", show_alert=True)
        return
    try:
        if str(action.id) in user.events_ids.split(','):
            await cb.answer(text="Вы уже зарегистрированны!", show_alert=True)
            return
    except:
        await cb.message.answer('Что-то пошло не так, попробуйте нажать /start')


    prepared_qr = await utils.generate_qrcode(
        payload= await create_start_link(
            bot=cb.bot,
            payload=str(cb.from_user.id)+f'_{action.id}',
            encode=True
        )
    )
    await cb.message.answer_photo(
        photo=prepared_qr,
        caption="Покажите ваш QR при входе.",
        reply_markup=user_kb.back_to_mainmenu()
        )

    try:
        user_events = user.events_ids.split(',')
    except:
        await cb.message.answer('Что-то пошло не так, попробуйте нажать /start')

    user_events.append(str(action.id))

    if len(user_events)>1:
        user_events=','.join(user_events)
    else:
        user_events=str(action.id)+','

    await update_user(user_id=cb.from_user.id, events_ids=user_events)
    await Update_promotion(
        id=action.id,
        reg_count=action.reg_count+1
        
        )







''' БРОНЬ '''

@router.callback_query(F.data.startswith("bron_"))
async def booking(callback: CallbackQuery, state: FSMContext):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])
    await callback.answer()
    category = callback.data.split('_')[-1]
    await state.update_data(category=category)
    
    await state.set_state(UserStates.Booking.name)
    
    try:
        await callback.message.edit_text('Введите имя на бронь:', reply_markup=user_kb.back_to_mainmenu())
    except:
        await callback.message.answer('Введите имя на бронь:', reply_markup=user_kb.back_to_mainmenu())





"""  ЦЕНЫ  """
@router.callback_query(F.data.startswith("cost_"))
async def booking(callback: CallbackQuery, state: FSMContext):
    await utils.delete_messages(cb=callback, message_ids=[callback.message.message_id-j for j in range(12)])

    await callback.answer()
    category = callback.data.split('_')[-1]
    await utils.delete_messages(
        cb=callback, 

        message_ids=[callback.message.message_id-j for j in range(6)]
        )
    match category:
        case 'k':
            await callback.bot.send_media_group(
                chat_id=callback.from_user.id,
                media=files.karting_images_group
            )
            await callback.message.answer('Вот наши цены', reply_markup=user_kb.back_karting())
        case 'r':
            await callback.bot.send_media_group(
                chat_id=callback.from_user.id,
                media=files.restoran_document_group
            )
            await callback.message.answer('Наши цены в меню', reply_markup=user_kb.back_restaraunt())
        case 'c':
            await callback.message.answer('Нет данных', reply_markup=user_kb.back_caraoke())            
        case 'b':
            await callback.message.answer_photo(photo=config.KARTING_IMAGE_1, caption='Наши цены',reply_markup=user_kb.back_bowling())
            # await callback.message.answer('Нет данных', reply_markup=user_kb.back_bowling())
        case 'da':
            await callback.message.answer('Нет данных', reply_markup=user_kb.back_dancing())
        case 'dr':
            await callback.bot.send_media_group(
                chat_id=callback.from_user.id,
                media=files.restoran_document_group
            )
            await callback.message.answer_photo(photo=config.FURSHET_MENU_IMAGE, reply_markup=user_kb.back_dr())
            # await callback.message.answer('Нет данных', reply_markup=user_kb.back_dr())
        case _:
            pass


@router.callback_query(F.data == 'afisha')
async def afisha(cb: CallbackQuery):
    try:
        await utils.delete_messages(cb=cb, message_ids=[cb.message.message_id-j for j in range(12)])
    except:
        pass
    
    data = utils.create_afisha_media_group()
    media_status = data[0]

    if media_status == 'MediaNoCaption':
        await cb.bot.send_media_group(chat_id=cb.from_user.id, media=data[-1])
        await cb.message.answer('-'*20, reply_markup=user_kb.back_dancing())

    elif media_status == 'MediaWithCaption':
        await cb.bot.send_media_group(chat_id=cb.from_user.id, media=data[-1])
        await cb.message.answer('-'*20, reply_markup=user_kb.back_dancing())
    
    elif media_status == 'OnlyText':
        await cb.message.answer(data[-1], reply_markup=user_kb.back_dancing())
    
    else:
        await cb.message.answer('На данный момент новых событий в афише нет!', reply_markup=user_kb.back_dancing())
        
    






@router.callback_query(F.data == 'buisness-launch')
async def afisha(cb: CallbackQuery):
    try:
        await utils.delete_messages(cb=cb, message_ids=[cb.message.message_id-j for j in range(12)])
    except:
        pass

    data = utils.create_launch_media_group()
    media_status = data[0]

    if media_status == 'MediaNoCaption':
        await cb.bot.send_media_group(chat_id=cb.from_user.id, media=data[-1])
        await cb.message.answer('-'*20, reply_markup=user_kb.back_restaraunt())

    elif media_status == 'MediaWithCaption':
        await cb.bot.send_media_group(chat_id=cb.from_user.id, media=data[-1])
        await cb.message.answer('-'*20, reply_markup=user_kb.back_restaraunt())
    
    elif media_status == 'OnlyText':
        await cb.message.answer(data[-1], reply_markup=user_kb.back_restaraunt())
    
    else:
        await cb.message.answer('На данный момент тут пусто!', reply_markup=user_kb.back_restaraunt())
        
    




# @router.message(F.document)
# async def handle_document(message: Message):
#     lg.info(message.document.file_id)


# @router.message(F.photo)
# async def handle_document(message: Message):
#     lg.info(message.photo[-1].file_id)
