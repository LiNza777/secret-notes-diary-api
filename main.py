import traceback
from contextlib import asynccontextmanager

from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from alembic import command
from limiter import limiter
from routers_auth import auth_router
from routers_notes import notes_router


def run_migrations():
    """Запуск миграций Alembic перед стартом сервера."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск миграций Alembic...")
    run_migrations()
    print("Миграции успешно применены!")
    yield


app = FastAPI(
    title="Secret Notes API",
    description="API для безопасного дневника с JWT-авторизацией",
    version="1.0.0",
    lifespan=lifespan,
)

# Настройка middleware, обработчиков ошибок и роутеров
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc().splitlines(),
        },
    )


app.include_router(auth_router)
app.include_router(notes_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "API работает успешно!",
        "docs": "Перейди по адресу /docs, чтобы протестировать эндпоинты",
    }
