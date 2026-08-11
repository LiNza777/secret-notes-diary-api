import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import settings

storage_uri = getattr(settings, "REDIS_URL", None) or os.getenv("REDIS_URL")

# Если REDIS_URL нет, собираем URI вручную (с учетом пароля, если он есть)
if not storage_uri:
    password = getattr(settings, "REDIS_PASSWORD", None) or os.getenv("REDIS_PASSWORD")
    if password:
        storage_uri = f"redis://:{password}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    else:
        storage_uri = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
)
