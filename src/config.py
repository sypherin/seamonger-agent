from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    shopify_store_domain: str = ""
    shopify_access_token: str = ""
    shopify_api_version: str = "2025-10"

    poll_interval_seconds: int = 300

    whatsapp_api_url: str = ""
    whatsapp_api_token: str = ""

    founder_phone: str = ""

    sqlite_path: str = "seamonger.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
