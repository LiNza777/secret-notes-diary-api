import logging
import traceback

from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from alembic import command
from config import settings
from limiter import limiter
from routers_auth import auth_router
from routers_notes import notes_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)


def run_migrations():
    """Запуск миграций Alembic перед стартом сервера."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def lifespan(app: FastAPI):
    logger.info("Применяем миграции базы данных...")
    run_migrations()
    logger.info("Миграции успешно применены!")
    yield


app = FastAPI(
    title="Secret Notes API",
    description="API для безопасного дневника с JWT-авторизацией",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RedisError)
async def redis_error_handler(request: Request, exc: RedisError):
    logger.error(f"{request.url.path} - RedisError (503): {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={"detail": "Сервис временно недоступен, попробуйте позже"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"{request.url.path} - Unhandled Exception (500): {exc}", exc_info=True
    )
    if settings.DEBUG:
        content = {
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc().splitlines(),
        }
    else:
        content = {"detail": "Внутренняя ошибка сервера"}
    return JSONResponse(status_code=500, content=content)


app.include_router(auth_router)
app.include_router(notes_router)


@app.get("/", tags=["Root"])
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "API работает успешно!",
        "docs": "Перейди по адресу /docs, чтобы протестировать эндпоинты",
    }
