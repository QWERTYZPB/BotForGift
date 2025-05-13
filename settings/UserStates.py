from aiogram.fsm.state import StatesGroup, State

class EditEventState(StatesGroup):
    event_id = State()
    inp = State()
    photo = State()


class AddChannel(StatesGroup):
    
    channel_id = State()





class AddEvent(StatesGroup):

    name = State()
    description = State()
    channel_event_ids=State()
    win_count = State()
    end_date = State()