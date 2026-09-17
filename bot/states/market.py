from aiogram.fsm.state import StatesGroup, State


class SellGiftState(StatesGroup):
    waiting_for_price = State()
