from aiogram import Router, F, types
from aiogram.filters import CommandStart, CommandObject

from aiogram.fsm.context import FSMContext

import logging as lg
from datetime import datetime

from settings import user_kb, lexicon, UserStates
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
            fullname=message.from_user.full_name
        )
    except Exception:
        lg.warning(f'FAILED TO ADD USER IN START u_id:{message.from_user.id}')
    


@router.callback_query(F.data == 'backMain')
async def backmain(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer('')

    try: await state.clear()
    except: pass
    
    await cb.message.answer(
            lexicon.START_TEXT, 
            reply_markup=user_kb.main_reply()
        )






@router.message(F.text == "Розыгрыши")
async def raffle(message: types.Message):
    user = await req.get_user(message.from_user.id)

    if user:
        user_raffles = user.event_ids
        if user_raffles:
            await message.answer('<b>Вот ваши розыгрыши:</b>',
                                reply_markup=await user_kb.create_user_raffles(user_raffles.split(',')))


        elif user_raffles == None or user_raffles == '':
            await message.answer('<b>У вас нет розыгрышей!</b>', reply_markup=user_kb.back_to_menu())



@router.callback_query(F.data.startswith('user_event_'))
async def user_event(cb: types.CallbackQuery):

    await cb.answer('')

    action = cb.data.split('_')[-2]
    event_id = int(cb.data.split('_')[-1])


    if action == 'show':
        event = await req.get_event(event_id)
        if event:
            user_count = 0
            win_count = None
            raffle_data = None

            if event.user_event_ids:
                user_count = len(event.user_event_ids.split(','))
            
            win_count = event.win_count
            raffle_data = event.end_date.strftime("%d.%m.%Y, %H:%M")

            if event.media:
                await cb.message.answer_photo(
                    photo=event.media,
                    caption=lexicon.EVENT_TEXT.format(
                    name=event.name,
                    description=event.description or '',
                    users_count=user_count,
                    win_count=win_count,
                    raffle_date=raffle_data
                    ),
                    reply_markup=await user_kb.show_event_kb(event.id)
                )
            else:
                await cb.message.answer(text=lexicon.EVENT_TEXT.format(
                    name=event.name,
                    description=event.description or '',
                    users_count=user_count,
                    win_count=win_count,
                    raffle_date=raffle_data
                ),
                    reply_markup=await user_kb.show_event_kb(event.id)
                )
        else:
            await cb.message.answer('Что-то пошло не так...', reply_markup=user_kb.back_to_menu())


@router.callback_query(F.data.startswith('edit_event_'))
async def edit_event(cb: types.CallbackQuery, state: FSMContext):
    await cb.answer('')

    action = cb.data.split('_')[-2]
    event_id = int(cb.data.split('_')[-1])

    await state.update_data(
        event_id=event_id,
        action = action
    )    


    if action == 'name':
        await cb.message.answer(
            text='Введите новое наименование розыргрыша:',
            reply_markup=user_kb.back_to_menu()
        )
        
        await state.set_state(UserStates.EditEventState.inp)
    
    elif action == 'media':
        await cb.message.answer(
            text='Пришлите новую фотку для розыгрыша:',
            reply_markup=user_kb.back_to_menu()
        )
        await state.set_state(UserStates.EditEventState.photo)

    
    elif action == 'description':
        await cb.message.answer(
            text='Введите новое описание розыргрыша:',
            reply_markup=user_kb.back_to_menu()
        )
        await state.set_state(UserStates.EditEventState.inp)
    
    elif action == 'wins':
        await cb.message.answer(
            text='Введите новое кол-во призовых мест розыргрыша:',
            reply_markup=user_kb.back_to_menu()
        )
        await state.set_state(UserStates.EditEventState.inp)
    
    elif action == 'channels':
        user_channels = (await req.get_user(cb.from_user.id)).channel_ids
        if not user_channels or user_channels == '':
            user_channels = []
        else:
            user_channels = user_channels.split(',')
        
        await cb.message.answer(
            text='Выберите канал,\n\n<b>ВНИМАНИЕ: Бот должен иметь права администатора в вашем Канале/Чате чтобы проверять наличие пользователя</b>',
            reply_markup=await user_kb.show_user_channels(user_channels, event_id)
        )
    
    elif action == 'date':
        await cb.message.answer(
            text=f'Введите новую дату окончания розыргрыша:\n\nФормат: <b>{datetime.now().strftime("%d.%m.%Y %H:%M")}</b>',
            reply_markup=user_kb.back_to_menu()
        )
        await state.set_state(UserStates.EditEventState.inp)
    



@router.message(UserStates.EditEventState.inp)
async def edit_input(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if 'event_id' not in data.keys() or 'action' not in data.keys():
        await message.answer('Данные устарели!', reply_markup=user_kb.back_to_menu())

    action = data['action']
    event_id = int(data['event_id'])


    if action == 'name':
        await req.update_event(
            event_id=event_id,
            name=message.text
        )
        
        await message.answer('Данные обновлены!', reply_markup=user_kb.back_to_event(event_id))

    elif action == 'description':
        await req.update_event(
            event_id=event_id,
            description=message.text
        )
    
        await message.answer('Данные обновлены!', reply_markup=user_kb.back_to_event(event_id))
    
    elif action == 'wins':
        await req.update_event(
            event_id=event_id,
            win_count=message.text
        )
    
        await message.answer('Данные обновлены!', reply_markup=user_kb.back_to_event(event_id))
    
    elif action == 'date':
        try:
            time = datetime.strptime(message.text, '%d.%m.%Y %H:%M')
        except:
            await message.answer(f'Неверный формат!\n\n Пример: {datetime.now().strftime("%d.%m.%Y %H:%M")}\n\nВведите еще раз:',
                                 reply_markup=user_kb.back_to_event(event_id))
            return
        

        await req.update_event(
            event_id=event_id,
            end_date=time
        )
    
        await message.answer('Данные обновлены!', reply_markup=user_kb.back_to_event(event_id))
    

    await state.clear()




@router.message(UserStates.EditEventState.photo)
async def handle_edit_photo(message: types.Message, state: FSMContext):
    if message.photo:
        data = await state.get_data()
        event_id = int(data['event_id'])

        photo_id = message.photo[-1].file_id

        await req.update_event(
            event_id=event_id,
            media=photo_id
        )

        await message.answer('Данные обновлены!', reply_markup=user_kb.back_to_event(event_id))
        await state.clear()
    else:
        await message.answer('Пришлите только одно фото!', reply_markup=user_kb.back_to_event(event_id))


@router.callback_query(F.data.startswith('channel_disable_'))
async def change_event_channel(cb: types.CallbackQuery, state: FSMContext):
    data = cb.data.split('_')

    event_id = int(data[-2])
    channel_id = data[-1]

    event = await req.get_event(event_id)
    channel = await req.get_channel(int(channel_id))
    user_channels = (await req.get_user(cb.from_user.id)).channel_ids
    if not user_channels or user_channels == '':
        user_channels = []
    else:
        user_channels = user_channels.split(',')

    if event.channel_event_ids:
        event_channels = event.channel_event_ids.split(',')
        event_channels.remove(channel_id)
        event_channels = ','.join(event_channels)

        channel_events = channel.root_event_ids.split(',')
        channel_events.remove(str(event_id))
        channel_events = ','.join(channel_events)

        
        await req.update_event(event_id=event_id, channel_event_ids=event_channels)
        await req.update_channel(channel_id=int(channel_id), 
                                 root_event_ids=channel_events
                                 )

    try:
        await cb.message.edit_text(
            text='Выберите канал,\n\n<b>ВНИМАНИЕ: Бот должен иметь права администатора в вашем Канале/Чате чтобы проверять наличие пользователя</b>',
            reply_markup=await user_kb.show_user_channels(user_channels, event_id)
        )
    except:
        await cb.message.edit_text('Успешно обновленно!', reply_markup=user_kb.back_to_event(event_id))



@router.callback_query(F.data.startswith('channel_enable_'))
async def change_event_channel(cb: types.CallbackQuery, state: FSMContext):
    data = cb.data.split('_')

    event_id = int(data[-2])
    channel_id = data[-1]

    event = await req.get_event(event_id)
    channel = await req.get_channel(int(channel_id))
    user_channels = (await req.get_user(cb.from_user.id)).channel_ids
    if not user_channels or user_channels == '':
        user_channels = []
    else:
        user_channels = user_channels.split(',')

    if event.channel_event_ids:
        event_channels = event.channel_event_ids + ',' + channel_id
    else:
        event_channels = channel_id

    if channel.root_event_ids:
        channel_root_event_ids = channel.root_event_ids + ',' + str(event_id)
    else:
        channel_root_event_ids = str(event_id)


    await req.update_event(event_id=event_id, channel_event_ids=event_channels)
    await req.update_channel(channel_id=int(channel_id), 
                                root_event_ids=channel_root_event_ids
                                )
    try:
        await cb.message.edit_text(
            text='Выберите канал,\n\n<b>ВНИМАНИЕ: Бот должен иметь права администатора в вашем Канале/Чате чтобы проверять наличие пользователя</b>',
            reply_markup=await user_kb.show_user_channels(user_channels, event_id)
        )
    except:
        await cb.message.edit_text('Успешно обновленно!', reply_markup=user_kb.back_to_event(event_id))






@router.callback_query(F.data.startswith('send_'))
async def send_post(cb: types.CallbackQuery):
    event_id = cb.data.split('_')[-1]
    
    try:
        await cb.message.edit_text('Вы уверены что хотите разослать розыгрыш по всем каналам/чатам?',
                               reply_markup=user_kb.confirm_send(event_id))
    except:
        await cb.message.answer('Вы уверены что хотите разослать розыгрыш по всем каналам/чатам?',
                               reply_markup=user_kb.confirm_send(event_id))
    


@router.callback_query(F.data.startswith('confirm_send_'))
async def confirm_sending(cb: types.CallbackQuery, bot: config.Bot):
    await cb.answer()
    event_id = cb.data.split('_')[-1]
    
    event = await req.get_event(int(event_id))

    if not event.channel_event_ids or event.channel_event_ids == '':
        await cb.message.answer('Нету активных каналов!', reply_markup=user_kb.back_to_event(event_id))
        return
    

    for channel_id in event.channel_event_ids.split(','):

        # try:
            user_count = 0
            win_count = None
            raffle_data = None
            message: types.Message = None
            if event.user_event_ids:
                user_count = len(event.user_event_ids.split(','))
            
            win_count = event.win_count
            raffle_data = event.end_date.strftime("%d.%m.%Y, %H:%M")


            if event.media:
                message = await bot.send_photo(
                    chat_id=channel_id,
                    photo=event.media,
                    caption=lexicon.EVENT_TEXT.format(
                    name=event.name,
                    description=event.description or '',
                    users_count=user_count,
                    win_count=win_count,
                    raffle_date=raffle_data
                    ),
                    reply_markup= user_kb.show_event_web_kb(event.id)
                )
            else:
                message = await bot.send_message(
                    chat_id=channel_id,
                    text=lexicon.EVENT_TEXT.format(
                    name=event.name,
                    description=event.description or '',
                    users_count=user_count,
                    win_count=win_count,
                    raffle_date=raffle_data
                    ),
                    reply_markup= user_kb.show_event_web_kb(event.id)
                )
            if message:
                event_message_ids = ''
                if not event.message_ids:
                    event_message_ids = channel_id+":"+str(message.message_id)
                elif not event.message_ids  == '' :
                    event_message_ids += channel_id+":"+str(message.message_id)
                else:
                    event_message_ids = ','.join(list(set(event_message_ids.split(',').append(channel_id+":"+str(message.message_id)))))

                await req.update_event(
                    event_id=int(event_id),
                    message_ids=event_message_ids
                )


        # except Exception as e:
        #     print(e)











""" CHANNEL ADD """


@router.callback_query(F.data.startswith('user_channel_add_'))
async def channel_add(cb: types.CallbackQuery, state: FSMContext):

    event_id = int(cb.data.split('_')[-1])

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # TODO: ПОЙМАТЬ ID ЧАТА С КЛАВИАТУРЫ КАК В MAIN MENU
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # await state.update_data(event_id=event_id)

    # await cb.message.answer('Перешлите сообш')