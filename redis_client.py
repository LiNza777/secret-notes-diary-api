import os
import redis.asyncio as redis

from config import settings

# 1. Проверяем наличие готовой строки подключения REDIS_URL (из settings или env)
redis_url = getattr(settings, "REDIS_URL", None) or os.getenv("REDIS_URL")

# 2. Если REDIS_URL не передана, собираем URI вручную (с учетом пароля)
if not redis_url:
    password = getattr(settings, "REDIS_PASSWORD", None) or os.getenv("REDIS_PASSWORD")
    auth = f":{password}@" if password else ""
    redis_url = f"redis://{auth}{settings.REDIS_HOST}:{settings.REDIS_PORT}"

# 3. Инициализируем асинхронный клиент через from_url
redis_client = redis.from_url(redis_url, decode_responses=True)


async def save_refresh_token(
    user_id: str, refresh_token: str, expire_seconds: int = 604800
) -> None:
    """Сохраняет refresh-токен пользователя с TTL (по умолчанию 7 дней)."""
    key = f"refresh_token:{user_id}"
    await redis_client.set(name=key, value=refresh_token, ex=expire_seconds)


async def is_refresh_token_valid(user_id: str, refresh_token: str) -> bool:
    """Проверяет, совпадает ли присланный токен с тем, что лежит в Redis."""
    key = f"refresh_token:{user_id}"
    saved_token = await redis_client.get(key)
    return saved_token == refresh_token


async def revoke_refresh_token(user_id: str) -> None:
    """Удаляет токен из Redis (сброс сессии / logout)."""
    key = f"refresh_token:{user_id}"
    await redis_client.delete(key)