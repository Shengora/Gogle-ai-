from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.i18n import _


def get_market_item_keyboard(
        listing_id: int,
        price: float,
        lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("buy_btn", lang, price=price),
            callback_data=f"buy_{listing_id}"
        )
    )
    return builder.as_markup()


def get_my_nft_item_keyboard(
        gift_id: int,
        lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="Withdraw NFT",
            callback_data=f"withdraw_{gift_id}"
        )
    )
    return builder.as_markup()


def get_inventory_item_keyboard(
        nft_address: str,
        lang: str,
        page: int = None,
        total_pages: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("sell_btn", lang),
            callback_data=f"sell_{nft_address}"
        )
    )

    if page is not None and total_pages is not None and total_pages > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=f"menu_inventory_{
                        page - 1}"))

        nav_buttons.append(
            InlineKeyboardButton(
                text=f"{page}/{total_pages}",
                callback_data="noop"))

        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"menu_inventory_{
                        page + 1}"))

        builder.row(*nav_buttons)

    return builder.as_markup()
