import pytest_asyncio
from typing import AsyncGenerator  
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport    
import pytest
import fakeredis.aioredis
from main import app
from data_base import get_db
from base import Base
from limiter import limiter

SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

limiter.enabled = False

@pytest.fixture(autouse=True)
async def mock_redis(monkeypatch):
    """Автоматически подменяет redis_client на in-memory хранилище для всех тестов."""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr("redis_client.redis_client", fake_redis)
    yield fake_redis
    await fake_redis.aclose()

engine_test = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    poolclass=StaticPool, 
)

async_session_maker = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Создает свежие таблицы перед тестом и чистит их после."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Подменяет реальную БД на тестовую сессию (dependency_overrides)
    и возвращает экземпляр TestClient.
    """
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    """ Переопределяем зависимость get_db в FastAPI """
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as test_client:
        yield test_client

    """ Сбрасываем переопределения после выполнения теста""" 
    app.dependency_overrides.clear()