from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.database.models import User, Gift, Listing, Settings, Transaction
from bot.services.i18n import _
from bot.keyboards.market import get_market_item_keyboard
from bot.services.tonapi_client import TonAPIClient
from bot.states.market import SellGiftState
from config import config

router = Router()


@router.callback_query(F.data == "menu_market")
async def show_market(
        callback: CallbackQuery,
        session: AsyncSession,
        lang: str):
    result = await session.execute(
        select(Listing, Gift).join(Gift).where(Listing.is_active).limit(10)
    )
    listings = result.all()

    if not listings:
        await callback.message.edit_text(_("market_empty", lang))
        return

    await callback.message.delete()
    for listing, gift in listings:
        text = f"💰 {listing.price} {listing.currency}\n{gift.name}"
        if gift.model:
            text += f"\nModel/Rarity: {gift.model}"

        markup = get_market_item_keyboard(listing.id, listing.price, lang)

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


@router.callback_query(F.data.startswith("sell_"))
async def start_sell(callback: CallbackQuery, state: FSMContext, lang: str):
    nft_address = callback.data.split("_")[1]
    await state.update_data(nft_address=nft_address)
    await state.set_state(SellGiftState.waiting_for_price)
    await callback.message.answer(_("enter_price", lang))
    await callback.answer()


@router.message(SellGiftState.waiting_for_price)
async def process_sell_price(
        message: Message,
        state: FSMContext,
        session: AsyncSession,
        user: User,
        lang: str):
    try:
        price = float(message.text)
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer(_("invalid_price", lang))
        return

    data = await state.get_data()
    nft_address = data["nft_address"]

    # 1. Check if it's already in our gifts table
    result = await session.execute(select(Gift).where(Gift.nft_address == nft_address))
    gift = result.scalar_one_or_none()

    # 2. If not, fetch it from TonAPI and save to DB (Import)
    if not gift:
        client = TonAPIClient(config.tonapi_key)
        item = await client.get_nft_item(nft_address)
        if not item:
            await message.answer("Error fetching NFT details from TonAPI.")
            await state.clear()
            return

        gift = Gift(
            owner_id=user.id,
            nft_address=nft_address,
            name=item.get("metadata", {}).get("name", "Unknown NFT"),
            image_url=item.get("previews", [{}])[0].get("url")
        )
        session.add(gift)
        await session.flush()  # flush to get gift.id

    # Check if already listed actively
    existing = await session.execute(
        select(Listing).where(Listing.gift_id == gift.id, Listing.is_active)
    )
    if existing.first():
        await message.answer(_("already_listed", lang))
        await state.clear()
        return

    listing = Listing(
        gift_id=gift.id,
        seller_id=user.id,
        price=price,
        currency="TON"
    )
    session.add(listing)
    await session.commit()

    await message.answer(_("listing_created", lang, price=price))
    await state.clear()


async def process_purchase(session: AsyncSession,
                           buyer: User, listing_id: int) -> tuple[bool, str]:
    result = await session.execute(
        select(Listing, Gift).join(Gift).where(Listing.id == listing_id, Listing.is_active)
    )
    row = result.first()

    if not row:
        return False, "Listing not found or already sold."

    listing, gift = row

    if buyer.balance_ton < listing.price:
        return False, "not_enough_balance"

    seller_result = await session.execute(select(User).where(User.id == listing.seller_id))
    seller = seller_result.scalar_one_or_none()

    if not seller:
        return False, "Seller not found."

    settings_result = await session.execute(select(Settings))
    settings = settings_result.scalar_one_or_none()
    commission_percent = settings.commission_percent if settings else 5.0

    commission_amount = listing.price * (commission_percent / 100)
    seller_receives = listing.price - commission_amount

    # Update balances (Escrow)
    buyer.balance_ton -= listing.price
    seller.balance_ton += seller_receives

    # Transfer DB ownership
    gift.owner_id = buyer.id

    # End listing
    listing.is_active = False

    tx = Transaction(
        listing_id=listing.id,
        buyer_id=buyer.id,
        seller_id=seller.id,
        price=listing.price,
        currency=listing.currency,
        commission_amount=commission_amount,
        status="completed"
    )

    session.add(tx)
    await session.commit()

    return True, gift.name


@router.callback_query(F.data.startswith("buy_"))
async def process_buy(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):
    listing_id = int(callback.data.split("_")[1])

    success, result_msg = await process_purchase(session, user, listing_id)

    if success:
        await callback.message.answer(_("purchase_successful", lang, name=result_msg))
    else:
        if result_msg == "not_enough_balance":
            await callback.answer(_("not_enough_balance", lang), show_alert=True)
        else:
            await callback.answer(result_msg, show_alert=True)

    await callback.message.delete()
