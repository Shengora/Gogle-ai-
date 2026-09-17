from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.i18n import _


def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
    )
    return builder.as_markup()


def get_main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_(
                "btn_market",
                lang),
            callback_data="menu_market"),
        InlineKeyboardButton(
            text=_(
                "btn_inventory",
                lang),
            callback_data="menu_inventory"))
    builder.row(
        InlineKeyboardButton(
            text=_(
                "btn_sales",
                lang),
            callback_data="menu_sales"),
        InlineKeyboardButton(
            text=_(
                "btn_balance",
                lang),
            callback_data="menu_balance"))
    builder.row(
        InlineKeyboardButton(
            text="⭐️ Deposit Stars",
            callback_data="deposit_stars"),
        InlineKeyboardButton(
            text=_(
                "btn_wallet",
                lang),
            callback_data="menu_wallet"))
    builder.row(
        InlineKeyboardButton(
            text=_(
                "btn_language",
                lang),
            callback_data="menu_language"),
        InlineKeyboardButton(
            text=_(
                "btn_admin",
                lang),
            callback_data="admin_panel"))

    return builder.as_markup()
