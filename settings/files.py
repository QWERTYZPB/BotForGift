from aiogram.types import FSInputFile

from settings import utils
import config






static_folder = 'static'

# karting1 = FSInputFile(path=static_folder+'/karting.jpg', filename="karting.jpg")
# karting2 = FSInputFile(path=static_folder+'/karting2.jpg', filename="karting2.jpg")
# karting3 = FSInputFile(path=static_folder+'/karting3.jpg', filename="karting3.jpg")
# karting4 = FSInputFile(path=static_folder+'/karting4.jpg', filename="karting4.jpg")

# karting_group = utils.create_media_group([karting1, karting2, karting3, karting4])

# restoran2 = FSInputFile(path=static_folder+'/restoran2.jpg', filename="restoran2.jpg")
# restoran_child_menu = FSInputFile(path=static_folder+'/child_menu.pdf', filename="child_menu.pdf")
# restoran_main_menu = FSInputFile(path=static_folder+'/main_menu.pdf', filename='main_menu.pdf')
# restoran_bar_menu = FSInputFile(path=static_folder+'/bar_menu.pdf', filename='bar_menu.pdf')
# karaoke = FSInputFile(path=static_folder+'/karaoke.jpg', filename="karaoke.jpg")

restoran_document_group = utils.create_media_group_static(
    list_media=[
        config.BAR_CARD_ID,
        config.CHILD_MENU_ID,
        config.OSNOVNOE_MENU_ID
    ],
    media_type='doc'
)

karting_images_group = utils.create_media_group_static(
    list_media=[
        config.KARTING_IMAGE_1,
        config.KARTING_IMAGE_2,
        config.KARTING_IMAGE_3,
        config.KARTING_IMAGE_4
    ]
)


# test_afisha_media_group = utils.create_media_group_with_caption(
#     [
#         config.TEST_AFISHA1,
#         config.TEST_AFISHA2
#     ],
#     caption='''
# Расписание <b>MISHKIN SHOW</b> на апрель🥂

# Каждую пятницу и субботу наш ресторан превращается в танцевальный центр ночи города Омска✨

# <b>MISHKIN SHOW</b> — это живой вокал и инструментал с 20:00, сменяемый самыми популярными группами города О, чередующиеся с диджей-сетами и МС: свет, звук, бармен-шоу, перформанс от официантов, ночной картинг и изысканный бар.'''
# )

# test_bisness_launch = utils.create_media_group_with_caption(
#     [
#         config.TEST_BISNESS_LAUNCH1,
#         config.TEST_BISNESS_LAUNCH2
#     ],
#     caption='''
# ▪️Доставка бизнес-ланча в будние дни с 11:00 до 23:00

# <a href="https://www.mishkinomsk.ru/page-delivery">ССЫЛКА</a>

# ▪️Скидка на самовывоз заказов по бизнес-ланчу — 20%
# '''
# )