from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    language = State()

class AdminStates(StatesGroup):
    admin = State()
    file_id = State()
    post_text = State()