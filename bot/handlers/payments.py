import hashlib
import json
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram import Bot

from bot.database.models import User
from bot.services.i18n import _

router = Router()


@router.callback_query(F.data == "deposit_stars")
async def process_deposit_stars(callback: CallbackQuery, bot: Bot, lang: str):
    prices = [LabeledPrice(label="50 Stars", amount=50)]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Deposit Stars",
        description="Add 50 Telegram Stars to your balance.",
        payload="deposit_50_stars",
        provider_token="",  # Empty string for Telegram Stars
        currency="XTR",
        prices=prices
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(
        message: Message,
        session: AsyncSession,
        user: User,
        lang: str):
    payment_info = message.successful_payment

    if payment_info.currency == "XTR":
        # amount is total amount in smallest units. For XTR 1 unit = 1 Star.
        amount = payment_info.total_amount
        user.balance_stars += amount
        await session.commit()
        await message.answer(f"Successfully deposited {amount} Stars!")
