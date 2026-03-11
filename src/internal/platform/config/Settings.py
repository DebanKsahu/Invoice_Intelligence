from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from internal.platform.config.DatabaseSettings import DatabaseSettings
from internal.platform.config.GoogleSettings import GoogleGeminiSettings, GoogleSettings
from internal.platform.config.LlmWhispererSettings import LlmWhispererSettings

BASE_DIR = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter=".",
        env_nested_max_split=3,
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )

    googleSettings: GoogleSettings = Field(alias="google_settings")
    databaseSettings: DatabaseSettings = Field(alias="database_settings")
    llmWhispererSettings: LlmWhispererSettings = Field(alias="llmwhisperer_settings")
    googleGeminiSettings: GoogleGeminiSettings = Field(alias="google_gemini_settings")
