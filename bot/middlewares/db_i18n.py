from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from bot.database.session import async_session_maker
from bot.database.models import User
from sqlalchemy import select


class DatabaseAndI18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        user_tg_id = None
        username = None

        if isinstance(event, Message) and event.from_user:
            user_tg_id = event.from_user.id
            username = event.from_user.username
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_tg_id = event.from_user.id
            username = event.from_user.username

        if user_tg_id:
            async with async_session_maker() as session:
                result = await session.execute(select(User).where(User.tg_id == user_tg_id))
                user = result.scalar_one_or_none()

                if not user:
                    user = User(
                        tg_id=user_tg_id,
                        username=username,
                        language="en")
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)

                data["session"] = session
                data["user"] = user
                data["lang"] = user.language

                return await handler(event, data)

        return await handler(event, data)
