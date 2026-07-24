from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Описываем переменные и их типы
    SECRET_KEY: str
    ALGORITHM: str = "HS256" # Дефолтное значение, если не найдет в .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str

    # Настройка для чтения из .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Создаем один глобальный объект настроек в RAM
settings = Settings()