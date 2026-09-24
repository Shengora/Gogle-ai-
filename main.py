import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from bot.middlewares.db_i18n import DatabaseAndI18nMiddleware


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    if not config.bot_token or config.bot_token == "YOUR_BOT_TOKEN":
        logging.error("BOT_TOKEN is not set properly in .env")
        return

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # Register Middlewares
    dp.update.middleware(DatabaseAndI18nMiddleware())

    # Register Routers
    from bot.handlers.start import router as start_router
    from bot.handlers.market import router as market_router
    from bot.handlers.admin import router as admin_router
    from bot.handlers.payments import router as payments_router
    from bot.handlers.wallet import router as wallet_router
    from bot.handlers.inventory import router as inventory_router

    dp.include_router(start_router)
    dp.include_router(wallet_router)
    dp.include_router(inventory_router)
    dp.include_router(market_router)
    dp.include_router(admin_router)
    dp.include_router(payments_router)

    logging.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
