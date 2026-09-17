from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from bot.database.models import User, Settings, Transaction, Listing, Gift
from bot.services.i18n import _
from config import config
from aiogram.fsm.state import StatesGroup, State

router = Router()


class AdminStates(StatesGroup):
    waiting_for_commission = State()


def is_admin(tg_id: int) -> bool:
    return tg_id in config.admin_ids


def get_admin_keyboard(lang: str) -> InlineKeyboardMarkup:
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_(
                "btn_admin_stats",
                lang),
            callback_data="admin_stats"))
    builder.row(
        InlineKeyboardButton(
            text=_(
                "btn_admin_commission",
                lang),
            callback_data="admin_commission"))
    return builder.as_markup()


@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(callback: CallbackQuery, user: User, lang: str):
    if not is_admin(user.tg_id):
        await callback.answer(_("admin_not_authorized", lang), show_alert=True)
        return

    await callback.message.edit_text(_("admin_panel_title", lang), reply_markup=get_admin_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def show_admin_stats(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):
    if not is_admin(user.tg_id):
        return

    # Total users
    users_count = await session.scalar(select(func.count(User.id)))
    # Total gifts
    gifts_count = await session.scalar(select(func.count(Gift.id)))
    # Active listings
    listings_count = await session.scalar(select(func.count(Listing.id)).where(Listing.is_active))
    # Completed transactions
    tx_count = await session.scalar(select(func.count(Transaction.id)).where(Transaction.status == "completed"))
    # Language stats
    lang_stats_result = await session.execute(select(User.language, func.count(User.id)).group_by(User.language))
    lang_stats = "\n".join(
        [f"  {l}: {count}" for l, count in lang_stats_result.all()])

    text = _("admin_stats_text", lang,
             users=users_count,
             gifts=gifts_count,
             listings=listings_count,
             txs=tx_count,
             lang_stats=lang_stats)

    await callback.message.edit_text(text, reply_markup=get_admin_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "admin_commission")
async def start_commission_change(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        user: User,
        lang: str):
    if not is_admin(user.tg_id):
        return

    settings = await session.scalar(select(Settings))
    current_commission = settings.commission_percent if settings else 5.0

    await state.set_state(AdminStates.waiting_for_commission)
    await callback.message.answer(_("admin_current_commission", lang, commission=current_commission))
    await callback.answer()


@router.message(AdminStates.waiting_for_commission)
async def process_commission_change(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
        user: User,
        lang: str):
    if not is_admin(user.tg_id):
        return

    try:
        new_commission = float(message.text)
        if not (0 <= new_commission <= 100):
            raise ValueError
    except ValueError:
        await message.answer(_("admin_invalid_commission", lang))
        return

    settings = await session.scalar(select(Settings))
    if not settings:
        settings = Settings(commission_percent=new_commission)
        session.add(settings)
    else:
        settings.commission_percent = new_commission

    await session.commit()
    await message.answer(_("admin_commission_updated", lang, commission=new_commission))
    await state.clear()
