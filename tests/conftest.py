import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import fakeredis
import redis_client

from main import app
from data_base import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def mock_redis():
    fake_redis_instance = fakeredis.FakeRedis(decode_responses=True)
    redis_client.redis_client = fake_redis_instance
    yield fake_redis_instance
    fake_redis_instance.flushall()

@pytest.fixture(scope="function")
def db_session():
    """Создает свежие таблицы перед тестом и чистит их после."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Подменяет реальную БД на тестовую сессию (dependency_overrides)
    и возвращает экземпляр TestClient.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    """ Переопределяем зависимость get_db в FastAPI """
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    """ Сбрасываем переопределения после выполнения теста""" 
    app.dependency_overrides.clear()