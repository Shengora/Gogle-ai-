import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from bot.database.models import User
from bot.services.i18n import _
from bot.services.tonconnect_client import TonConnectService
from pytonconnect.exceptions import UserRejectsError
from pytonconnect import TonConnect

router = Router()


async def connection_polling(
        connector: TonConnect,
        chat_id: int,
        user_tg_id: int,
        bot,
        session_maker):
    try:
        # Wait for the user to approve the connection
        for _ in range(60):  # poll for roughly 60 seconds
            await asyncio.sleep(1)
            if connector.connected:
                break

        if connector.connected:
            wallet_address = connector.account.address
            # Save to database
            async with session_maker() as session:
                user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
                if user:
                    # Store as raw user-friendly address string (simplified)
                    user.wallet_address = wallet_address
                    await session.commit()

                # Fetch lang to answer correctly
                lang = user.language if user else "en"
                await bot.send_message(chat_id, _("wallet_connected", lang, address=wallet_address))
        else:
            # Polling timeout, could notify user
            pass
    except UserRejectsError:
        # User rejected the connection
        pass
    except Exception as e:
        # Generic error
        print(f"Error in polling: {e}")


@router.callback_query(F.data == "menu_wallet")
async def process_wallet_menu(
        callback: CallbackQuery,
        session: AsyncSession,
        user: User,
        lang: str):
    tc_service = TonConnectService()
    connector = tc_service.get_connector(callback.from_user.id)

    # Restore connection if exists
    is_connected = await connector.restore_connection()

    if is_connected:
        await callback.message.edit_text(
            _("wallet_connected", lang, address=connector.account.address)
        )
        return

    # Generate connection link/QR
    wallets_list = connector.get_wallets()

    # Generate generic universal link
    generated_url = await connector.connect(wallets_list)

    text = _("connect_wallet_msg", lang) + \
        f"\n\n[Connect Wallet]({generated_url})"

    await callback.message.edit_text(text, parse_mode="Markdown", disable_web_page_preview=True)

    # Start polling task in background
    from bot.database.session import async_session_maker
    asyncio.create_task(
        connection_polling(
            connector,
            callback.message.chat.id,
            user.tg_id,
            callback.bot,
            async_session_maker))

    await callback.answer()
