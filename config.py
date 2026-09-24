
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    bot_token: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "gift_market"
    redis_host: str = "localhost"
    redis_port: int = 6379
    admin_ids: List[int] = Field(default_factory=list)
    tonapi_key: str = ""
    manifest_url: str = ""
    master_wallet_address: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8")

    @field_validator('admin_ids', mode='before')
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                import json
                try:
                    return json.loads(v)
                except BaseException:
                    pass
            return [int(id_str.strip())
                    for id_str in v.split(',') if id_str.strip().isdigit()]
        return v

    @property
    def db_url(self) -> str:
        # Use sqlite for local development if DB_HOST is sqlite
        if self.db_host == "sqlite":
            return "sqlite+aiosqlite:///db.sqlite3"
        return f"postgresql+asyncpg://{
            self.db_user}:{
            self.db_password}@{
            self.db_host}:{
                self.db_port}/{
                    self.db_name}"


config = Settings()
