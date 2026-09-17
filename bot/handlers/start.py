from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from bot.keyboards.inline import get_language_keyboard, get_main_menu_keyboard
from bot.services.i18n import _
from bot.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, lang: str):
    # Always show language selection on start
    await message.answer(
        _("welcome", lang),
        reply_markup=get_language_keyboard()
    )


@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User):
    new_lang = callback.data.split("_")[1]

    # Update user language in database
    user.language = new_lang
    await session.commit()

    await callback.message.edit_text(
        _("language_selected", new_lang),
        reply_markup=get_main_menu_keyboard(new_lang)
    )
    await callback.answer()


@router.callback_query(F.data == "menu_language")
async def process_language_menu(callback: CallbackQuery, lang: str):
    await callback.message.edit_text(
        _("welcome", lang),
        reply_markup=get_language_keyboard()
    )
    await callback.answer()
