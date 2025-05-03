import segno, io
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from database import req

import re, datetime, asyncio, json


def normalize_phone_number(phone_number):
    
    cleaned_number = re.sub(r'\D', '', phone_number)

    if not cleaned_number:
        return None

    if cleaned_number.startswith('00'):
        cleaned_number = cleaned_number[2:]
    elif cleaned_number.startswith('+'):
        cleaned_number = cleaned_number[1:]

    return cleaned_number 

def is_valid_phone(phone: str) -> bool:
    """
    Проверяет валидность номера телефона.
    Допустимые форматы: 79099696905, +79099696905, 89099696905.
    Возвращает True, если номер валиден, иначе False.
    """
    pattern = r'^(\+7|7|8)\d{10}$'
    return bool(re.fullmatch(pattern, phone))


def is_valid_datetime(input_str: str) -> bool:
    """
    Проверяет валидность даты и времени в строке формата:
    - дд.мм.гггг чч:мм
    - дд-мм-гггг чч:мм
    - дд/мм/гггг чч:мм
    """
    # Регулярное выражение для проверки структуры
    pattern = r"^(\d{2})([./-])(\d{2})\2(\d{4}) (\d{2}):(\d{2})$"
    match = re.match(pattern, input_str)
    if not match:
        return False

    # Извлечение компонентов
    day, sep, month, year, hour, minute = match.groups()
    day, month, year = int(day), int(month), int(year)
    hour, minute = int(hour), int(minute)

    # Проверка времени
    if not (0 <= hour < 24 and 0 <= minute < 60):
        return False

    # Проверка даты через datetime
    try:
        datetime.datetime(year=year, month=month, day=day)
        return True
    except ValueError:
        return False








async def generate_qrcode(payload: str, format: str = "PNG") -> types.BufferedInputFile:
    qrcode = segno.make_qr(content=payload, error="H")
    buffer = io.BytesIO()
    # qrcode.save('qr.png', kind=format, scale=10)

    with buffer as f:     
        qrcode.save(f, kind=format, scale=10)
        buffer.seek(0)
        
        return types.BufferedInputFile(buffer.read(), filename='image.png')




def create_media_group_static(list_media: list[str], media_type='photo'):
    '''
    media_type: photo, doc
    
    '''
    
    media_builder = MediaGroupBuilder()
    for media in list_media:
        if media_type == 'photo':
            media_builder.add_photo(media=media)

        if media_type == 'doc':
            media_builder.add_document(media=media)

    return media_builder.build()

def create_media_group_for_actions(list_media_id: list[str], caption: str):
    '''
    list_media: ["p!123-abcd", "v!321-abcd"]
    '''
    use_caption = True
    
    media_builder = MediaGroupBuilder()
    for media in list_media_id:
        media_type, file_id = media.split('!')
        
        if media_type == 'p':
            if use_caption:
                media_builder.add_photo(media=file_id, caption=caption)
                use_caption=False
            else:
                media_builder.add_photo(media=file_id)
            
        

        elif media_type == 'v':
            if use_caption:
                media_builder.add_video(media=file_id, caption=caption)
                use_caption=False
            else:        
                media_builder.add_video(media=file_id)


    return media_builder.build()



# not in use
def create_media_group_with_caption(list_media_id: list[str], caption: str):
    '''
    list_media: ["p!123-abcd", "v!321-abcd"]
    '''
    use_caption = True
    
    media_builder = MediaGroupBuilder()
    for media in list_media_id:
        media_type, file_id = media.split('!')
        
        if media_type == 'p':
            if use_caption:
                media_builder.add_photo(media=file_id, caption=caption)
                use_caption=False
            else:
                media_builder.add_photo(media=file_id)
            
        

        elif media_type == 'v':
            if use_caption:
                media_builder.add_video(media=file_id, caption=caption)
                use_caption=False
            else:        
                media_builder.add_video(media=file_id)


    return media_builder.build()

        


def create_media_group(list_media_id: list[str]):
    '''
    list_media: ["p!123-abcd", "v!321-abcd"]
    '''
    
    media_builder = MediaGroupBuilder()
    for media in list_media_id:
        if media:
            media_type, file_id = media.split('!')

            if media_type == 'p':
                media_builder.add_photo(media=file_id)

            elif media_type == 'v':        
                media_builder.add_video(media=file_id)


    return media_builder.build()




async def try_to_edit_else_answer(cb: types.CallbackQuery, text: str, markup: types.InlineKeyboardMarkup = None):
    try:
        await cb.message.edit_text(text=text, disable_web_page_preview=True, reply_markup=markup)
    except Exception as e:
        await cb.message.answer(text=text, disable_web_page_preview=True, reply_markup=markup)

async def delete_messages(cb: types.CallbackQuery, message_ids: list[int]):
    try:
        user_start_message_id = (await req.get_user_by_id(cb.from_user.id)).start_message_id
    except:
        pass
        return
    
    for message_id in message_ids:
        try:
            if message_id!=user_start_message_id:
                await cb.bot.delete_message(chat_id=cb.from_user.id, message_id=message_id)
            else:
                return
        except:
            return
            






def create_afisha_media_group():
    data = get_al_data()
    text, media = data['Afisha']['text'], data['Afisha']['media']

    if text == '' and len(media) > 0:
        return 'MediaNoCaption', create_media_group(media)
    
    elif len(text)>0 and len(media) > 0: 
        return 'MediaWithCaption', create_media_group_with_caption(media, text)
    
    elif len(text): 
        return 'OnlyText', text
    
    return [None]



def create_launch_media_group():
    data = get_al_data()
    text, media = data['Launch']['text'], data['Launch']['media']

    if text == '' and len(media) > 0:
        return 'MediaNoCaption', create_media_group(media)
    
    elif len(text)>0 and len(media) > 0: 
        return 'MediaWithCaption', create_media_group_with_caption(media, text)
    
    elif len(text): 
        return 'OnlyText', text
    
    return [None]


def get_al_data( path='settings/AfishaLaunch.json'):
    data = {}
    with open(path, 'r', encoding='utf-8') as fg:
        data = json.load(fp=fg)
        
    return data


def save_al_data(data, path='settings/AfishaLaunch.json'):
    with open(path, 'w', encoding='utf-8') as fs:
        data = json.dump(obj=data, fp=fs, indent=4)


def clear_in_afisha():
    data = get_al_data()

    data['Afisha']['media'].clear()
    data['Afisha']['text'] = ''
    
    save_al_data(data)


def clear_in_launch():
    data = get_al_data()

    data['Launch']['media'].clear()
    data['Launch']['text'] = ''
    
    save_al_data(data)




def edit_media_in_afisha(media: list[str]):
    data = get_al_data()

    data['Afisha']['media'].clear()
    
    data['Afisha']['media'].extend(media)

    save_al_data(data)


def edit_media_in_launch(media: list[str]):
    data = get_al_data()

    data['Launch']['media'].clear()
    
    data['Launch']['media'].extend(media)

    save_al_data(data)


def edit_text_in_afisha(text: str):
    data = get_al_data()

    data['Afisha']['text'] = text

    save_al_data(data)


def edit_text_in_launch(text: str):
    data = get_al_data()
    
    data['Launch']['text'] = text

    save_al_data(data)

