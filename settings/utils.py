import random
from PIL import Image, ImageDraw, ImageFont
from aiogram import types, Bot
from settings import user_kb

from io import BytesIO

default_color_red = 228
default_color_green = 150
default_color_blue = 150

async def generate_random_string(length):
    random_string = ""
    for i in range(0,length):
        random_string = random_string + random.choice('1234567890ABCDEFGHIJKLMNOPQRSTUVQXYZ')
    return random_string

async def draw_random_ellipse(draw):
    a = random.randrange(10, 300, 1)
    b = random.randrange(10, 275, 1)
    c = a + random.randrange(10, 90, 1)
    d = b + random.randrange(10, 90, 1)
    draw.ellipse((a,b,c,d), fill=(default_color_red + random.randrange(-100,100,1), 
                                  default_color_green + random.randrange(-100,100,1), 
                                  default_color_blue + random.randrange(-100,100,1), 255), 
                                  outline = "black")

async def generate_captcha():
    '''
    Generate a captcha
    :return: A tuple (image, captcha string encoded in the image)
    '''
    captcha_string = await generate_random_string(5)

    captcha_image = Image.new("RGBA", (400, 200), (default_color_red,default_color_green,default_color_blue))
    draw = ImageDraw.Draw(captcha_image, "RGBA")
    for i in range(1,20):
        await draw_random_ellipse(draw)

    fontStyle = ImageFont.truetype("Aaargh.ttf", 48)     # font must be in the same folder as the .py file. 

    # Arbitrary starting co-ordinates for the text we will write
    x = 10 + random.randrange(0, 100, 1)
    y = 79 + random.randrange(-10, 10, 1)
    for letter in captcha_string:
        draw.text((x, y), letter, (0,0,0),font=fontStyle)    # Write in black
        x = x + 35
        y = y +  random.randrange(-10, 10, 1)
    
    return (captcha_image, captcha_string)  # return a heterogeneous tuple










async def send_captcha_2user(message: types.Message | types.CallbackQuery, bot: Bot):
    captcha_img, captcha_str = await generate_captcha()

    buffer = BytesIO()
    captcha_img.save(buffer, format='PNG')
    buffer.seek(0)

    input_file = types.BufferedInputFile(buffer.read(), filename='image.png')
    if isinstance(message, types.Message):
        await bot.send_photo(photo=input_file, 
                            chat_id=message.from_user.id,
                            caption='❌ Пройдите капчу!',
                            reply_markup=await user_kb.create_captcha_kb(captcha_str))
    else:
        await bot.send_photo(photo=input_file, 
                            chat_id=message.message.chat.id,
                            caption='❌ Пройдите капчу!',
                            reply_markup=await user_kb.create_captcha_kb(captcha_str))