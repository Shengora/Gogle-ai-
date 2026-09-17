import redis.asyncio as redis
from pytonconnect import TonConnect
from pytonconnect.storage import IStorage
from config import config


class RedisStorage(IStorage):
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.redis = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            decode_responses=True)

    def _get_key(self, key: str) -> str:
        return f"tonconnect_{self.chat_id}_{key}"

    async def set_item(self, key: str, value: str):
        await self.redis.set(self._get_key(key), value)

    async def get_item(self, key: str, default_value: str = None) -> str:
        value = await self.redis.get(self._get_key(key))
        return value if value is not None else default_value

    async def remove_item(self, key: str):
        await self.redis.delete(self._get_key(key))


class TonConnectService:
    def __init__(self):
        self.manifest_url = config.manifest_url

    def get_connector(self, chat_id: int) -> TonConnect:
        storage = RedisStorage(chat_id)
        return TonConnect(manifest_url=self.manifest_url, storage=storage)
