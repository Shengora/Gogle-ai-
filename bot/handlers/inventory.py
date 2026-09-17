from bot.database.models import WithdrawalRequest
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.database.models import User, Gift, Listing
from bot.services.i18n import _
from bot.keyboards.market import get_inventory_item_keyboard
from bot.services.tonapi_client import TonAPIClient
from config import config

router = Router()


@router.callback_query(F.data.startswith("menu_inventory"))
async def show_inventory(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):
    if not user.wallet_address:
        await callback.answer(_("not_connected", lang), show_alert=True)
        return

    parts = callback.data.split("_")
    page = int(parts[2]) if len(parts) > 2 else 1
    items_per_page = 5

    if page == 1:
        await callback.message.edit_text("Fetching your NFTs, please wait...")
    else:
        await callback.message.delete()

    # Fetch real NFTs
    client = TonAPIClient(config.tonapi_key)
    nft_data = await client.get_account_nfts(user.wallet_address)

    if not nft_data:
        await callback.message.edit_text(_("inventory_empty", lang))
        return

    total_items = len(nft_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_data = nft_data[start_idx:end_idx]

    for i, item in enumerate(page_data):
        nft_address = item.get("address")
        name = item.get("metadata", {}).get("name", "Unknown NFT")
        image_url = item.get("previews", [{}])[0].get("url")

        text = f"{name}"

        # Add pagination buttons to the last item on the page
        is_last_item = (i == len(page_data) - 1)
        markup = get_inventory_item_keyboard(
            nft_address,
            lang,
            page=page,
            total_pages=total_pages if is_last_item else None)

        if image_url:
            await callback.message.answer_photo(
                photo=image_url,
                caption=text,
                reply_markup=markup
            )
        else:
            await callback.message.answer(
                text,
                reply_markup=markup
            )

    if page == 1 and callback.message.text == "Fetching your NFTs, please wait...":
        await callback.message.delete()

    await callback.answer()


@router.callback_query(F.data == "menu_my_nfts")
async def show_my_db_nfts(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):

    # These are the NFTs the user successfully purchased and currently owns in the bot's DB (master wallet)
    result = await session.execute(
        select(Gift).where(Gift.owner_id == user.id)
    )
    gifts = result.scalars().all()

    if not gifts:
        await callback.message.edit_text("You don't own any DB NFTs to withdraw.", show_alert=True)
        return

    await callback.message.delete()
    for gift in gifts:
        # Check if it's currently listed for sale
        existing_listing = await session.execute(
            select(Listing).where(Listing.gift_id ==
                                  gift.id, Listing.is_active)
        )
        if existing_listing.first():
            continue  # Don't show NFTs currently on active sale for withdrawal

        text = f"{gift.name}"
        if gift.model:
            text += f"\nModel: {gift.model}"

        from bot.keyboards.market import get_my_nft_item_keyboard
        markup = get_my_nft_item_keyboard(gift.id, lang)

        if gift.image_url:
            await callback.message.answer_photo(
                photo=gift.image_url,
                caption=text,
                reply_markup=markup
            )
        else:
            await callback.message.answer(
                text,
                reply_markup=markup
            )
    await callback.answer()


@router.callback_query(F.data.startswith("withdraw_"))
async def process_withdraw(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):

    gift_id = int(callback.data.split("_")[1])

    if not user.wallet_address:
        await callback.answer(_("not_connected", lang), show_alert=True)
        return

    gift = await session.scalar(select(Gift).where(Gift.id == gift_id, Gift.owner_id == user.id))
    if not gift:
        await callback.answer("Gift not found or you don't own it.", show_alert=True)
        return

    # Check if there is already a pending withdrawal
    existing = await session.scalar(
        select(WithdrawalRequest).where(WithdrawalRequest.gift_id ==
                                        gift.id, WithdrawalRequest.status == "pending")
    )
    if existing:
        await callback.answer("Withdrawal is already pending for this NFT.", show_alert=True)
        return

    # Create withdrawal request
    req = WithdrawalRequest(
        user_id=user.id,
        gift_id=gift.id,
        target_address=user.wallet_address,
        status="pending"
    )
    session.add(req)
    await session.commit()

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Withdrawal request created! An admin will process it shortly.")
    await callback.answer()


@router.callback_query(F.data == "menu_balance")
async def show_balance(callback: CallbackQuery, user: User, lang: str):
    wallet_str = user.wallet_address if user.wallet_address else _(
        "not_connected", lang)
    await callback.message.edit_text(
        _("balance_info", lang, ton=user.balance_ton,
          stars=user.balance_stars, wallet=wallet_str)
    )
    await callback.answer()


@router.callback_query(F.data == "menu_sales")
async def show_sales(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):
    result = await session.execute(
        select(Listing, Gift).join(Gift).where(
            Listing.seller_id == user.id, Listing.is_active)
    )
    listings = result.all()

    if not listings:
        await callback.message.edit_text("You have no active sales.")
        return

    await callback.message.delete()
    for listing, gift in listings:
        text = f"Listed: {gift.name} for {listing.price} {listing.currency}"
        await callback.message.answer(text)
    await callback.answer()
