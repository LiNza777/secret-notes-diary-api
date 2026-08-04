import redis.asyncio as redis
from config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

async def save_refresh_token(user_id: str, refresh_token: str, expire_seconds: int = 604800) -> None:
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