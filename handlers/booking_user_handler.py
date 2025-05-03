from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram import Bot

import logging as lg
import config
from settings import user_kb, lexicon, utils, UserStates
from settings.lexicon import categ_dict
from database.req import add_user, get_promotions









router=Router()



@router.message(UserStates.Booking.name)
async def bookingname(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('Отправьте только текст!')
        return
    
    await state.update_data(name=message.text)
    await message.answer('Введите телефон:', reply_markup=user_kb.back_to_mainmenu())
    
    await message.answer('Можете нажать на кнопку для отправки вашего номера', reply_markup=user_kb.request_contact_button())
    
    await state.set_state(UserStates.Booking.phone)


@router.message(UserStates.Booking.phone, F.text)
@router.message(UserStates.Booking.phone, F.contact)
async def bookingname(message: Message, state: FSMContext):
    
    if not message.contact:
        if not utils.is_valid_phone(message.text):
            await message.answer('Формат номера не верный!\nПример:+79091234567 / 79091234567 / 89091234567\n\nПопробуйте снова:', reply_markup=user_kb.back_to_mainmenu())
            return
        phone = message.text
    else:
        phone = message.contact.phone_number
    
    # fmsg = await message.answer('.')

    await state.update_data(phone=phone)
    await message.answer(
            text='Введите дату и время:'
            'Пример:\n'
            '- дд.мм.гггг чч:мм\n'
            '- дд-мм-гггг чч:мм\n'
            '- дд/мм/гггг чч:мм\n', 
        reply_markup=user_kb.ReplyKeyboardRemove())
    await state.set_state(UserStates.Booking.date)

@router.message(UserStates.Booking.date)
async def bookingname(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('Отправьте только текст!')
        return
    
    if not utils.is_valid_datetime(message.text):
        await message.answer(
            'Формат даты не верный!\n'
            'Пример:\n'
            '- дд.мм.гггг чч:мм\n'
            '- дд-мм-гггг чч:мм\n'
            '- дд/мм/гггг чч:мм\n\nПопробуйте снова:', 
            reply_markup=user_kb.back_to_mainmenu())
        return
    await state.update_data(date=message.text)
    # data = await state.get_data()

    # if data['category'] == 'dr' or data['category'] == 'k':
    #     await message.answer('Введите возраст детей:', reply_markup=user_kb.back_to_mainmenu())
    #     await state.set_state(UserStates.Booking.age)
    #     return

    await message.answer('Введите кол-во человек:', reply_markup=user_kb.back_to_mainmenu())
    await state.set_state(UserStates.Booking.count_members)



# @router.message(UserStates.Booking.age)
# async def bookingname(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         await message.answer(
#             'Введите число!'
#             '\n\nПопробуйте снова:', 
#             reply_markup=user_kb.back_to_mainmenu())
#         return
#     await state.update_data(age=message.text)
#     await message.answer('Введите кол-во человек:', reply_markup=user_kb.back_to_mainmenu())
#     await state.set_state(UserStates.Booking.count_members)



@router.message(UserStates.Booking.count_members)
async def bookingname(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('Отправьте только текст!')
        return
    
    if not message.text.isdigit():
        await message.answer(
            'Введите число!'
            '\n\nПопробуйте снова:', 
            reply_markup=user_kb.back_to_mainmenu())
        return
    await state.update_data(count_members=message.text)
    await message.answer('Введите ваши пожелания:', reply_markup=user_kb.back_to_mainmenu())
    await state.set_state(UserStates.Booking.msg)

@router.message(UserStates.Booking.msg)
async def bookingname(message: Message, state: FSMContext):
    if not message.text:
        await message.answer('Отправьте только текст!')
        return
    
    await state.update_data(msg=message.text)

    data = await state.get_data()
    try:
        msg =  data['msg']
    except:
        msg = message.text


    if data['category'] == 'dr' or data['category'] == 'k':

        text = lexicon.BOOKING_TEXT.format(
            lexicon.categ_dict_ru[data['category']],
            data['name'],
            data['phone'],
            data['date'],
            data['count_members'],
            msg,
        )     

    text = lexicon.BOOKING_TEXT.format(
        lexicon.categ_dict_ru[data['category']],
        data['name'],
        data['phone'],
        data['date'],
        data['count_members'],
        msg,
    )
    await state.update_data(text_to_send=text)
    
    await message.answer(text="Ваша заявка:\n" +text, reply_markup=user_kb.confirm_booking())













# Универсальная ф-ция подтверждения

@router.callback_query(F.data.startswith('booking_'))
async def send_or_not(cb: CallbackQuery, state: FSMContext):
    confirm = cb.data.split('_')[-1]
    try:
        text_to_send = (await state.get_data())['text_to_send']
        category = (await state.get_data())['category']
    except:
        await cb.message.answer('Заявка устарела, попробуйте снова!', reply_markup=user_kb.back_to_mainmenu())
        return
    
    
    if confirm == 'confirm':
        
        admin_text = f'Новая бронь!\nПользователь: <a href="{cb.from_user.url}">{cb.from_user.full_name}</a>\n' + text_to_send
        message_thread_id = None
        match category:
            case 'k':
                message_thread_id=config.CHAT_KARTING_THREAD_ID
            case 'r':
                message_thread_id=config.CHAT_RESTORAN_THREAD_ID
            case 'c':
                message_thread_id=config.CHAT_KARAOKE_THREAD_ID
            case 'b':
                message_thread_id=config.CHAT_BOWLING_THREAD_ID
            case 'da':
                message_thread_id=config.CHAT_DANCE_THREAD_ID
            case 'dr':
                message_thread_id=config.CHAT_BANKET_THREAD_ID
                
            case _:
                pass

        await cb.bot.send_message(
            chat_id=config.CHAT_TO_SEND_BOOKING,
            message_thread_id=message_thread_id,
            text=admin_text
            )
        

        try:
            await cb.message.edit_text('Сообщение отправлено администрации, с вами скоро свяжутся!', reply_markup= user_kb.back_to_mainmenu())
        except:
            await cb.message.answer('Сообщение отправлено администрации, с вами скоро свяжутся!', reply_markup= user_kb.back_to_mainmenu())

    else:
        await cb.message.answer('Отмена бронирования', reply_markup= user_kb.back_to_mainmenu() )

    await state.clear()

