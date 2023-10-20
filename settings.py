"""Setting parser for the bot."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class with settings."""

    bot_token: str

    # loads from .env
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
