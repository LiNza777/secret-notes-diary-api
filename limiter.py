import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings

# Достаем REDIS_URL из Pydantic settings или переменных окружения
storage_uri = getattr(settings, "REDIS_URL", None) or os.getenv("REDIS_URL")

# Если REDIS_URL нет, пытаемся собрать из HOST и PORT
if not storage_uri:
    host = getattr(settings, "REDIS_HOST", None) or os.getenv("REDIS_HOST")
    port = getattr(settings, "REDIS_PORT", None) or os.getenv("REDIS_PORT", 6379)
    password = getattr(settings, "REDIS_PASSWORD", None) or os.getenv("REDIS_PASSWORD")

    if host:
        if password:
            storage_uri = f"redis://:{password}@{host}:{port}"
        else:
            storage_uri = f"redis://{host}:{port}"

# ФОЛЛБЕК: Если URL не задан ИЛИ он указывает на localhost (когда Redis не запущен локально)
if not storage_uri or "localhost" in storage_uri:
    storage_uri = "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
)
