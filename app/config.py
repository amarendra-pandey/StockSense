from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StockSense"
    environment: str = "development"
    debug: bool = False
    database_url: str = "postgresql+psycopg://localhost:5432/stocksense"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
