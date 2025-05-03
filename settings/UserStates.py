from aiogram.fsm.state import StatesGroup, State


class Promotion(StatesGroup):
    category = State()
    lasting = State()
    QRs_number = State()
    description = State()
    photo = State()

class Mailing(StatesGroup):
    waiting_for_post=State()

class Description_edit(StatesGroup):
    description_edit=State()

class Lasting_edit(StatesGroup):
    lasting_edit=State()

class QRs_number_edit(StatesGroup):
    QRs_number_edit=State()

class Photo_edit(StatesGroup):
    photo_edit=State()

class Archive_edit(StatesGroup):
    archive_edit=State()
    




class Booking(StatesGroup):
    name=State()
    phone=State()
    age=State() # child
    count_members = State()
    format_=State()
    date=State()
    msg=State()




class BookingRestoran(StatesGroup):
    name=State()
    phone=State()
    date=State()
    msg=State()


class BookingDance(StatesGroup):
    name=State()
    phone=State()
    date=State()
    msg=State()
    format_ = State()

class BookingKarting(StatesGroup):
    name=State()
    phone=State()
    age=State() # child
    date=State()
    msg=State()


class BookingBouling(StatesGroup):
    name=State()
    phone=State()
    date=State()
    msg=State()


class BookingKaraoke(StatesGroup):
    name=State()
    phone=State()
    date=State()
    msg=State()


class BookingBanket(StatesGroup):
    name=State()
    phone=State()
    date=State()
    format_=State()
    msg=State()



