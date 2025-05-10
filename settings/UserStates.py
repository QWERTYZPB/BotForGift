from aiogram.fsm.state import StatesGroup, State

class EditEventState(StatesGroup):
    event_id = State()
    inp = State()
    photo = State()


class AddChannel(StatesGroup):
    
    channel_id = State()