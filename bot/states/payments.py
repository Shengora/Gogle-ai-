from aiogram.fsm.state import StatesGroup, State


class DepositTonState(StatesGroup):
    waiting_for_amount = State()


class DepositStarsState(StatesGroup):
    waiting_for_amount = State()
