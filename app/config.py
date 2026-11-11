import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CryoFlow"
    API_V1_STR: str = "/api/v1"

    # NASA Earthdata Credentials (нужны для скачивания продуктов через earthaccess)
    NASA_USERNAME: str | None = None
    NASA_PASSWORD: str | None = None

    # Путь к локальному кэшу растровых данных
    DATA_CACHE_DIR: str = os.path.join(os.getcwd(), "data_cache")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Убедимся, что директория для кэша существует
os.makedirs(settings.DATA_CACHE_DIR, exist_ok=True)