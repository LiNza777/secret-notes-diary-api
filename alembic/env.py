import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from config import settings
from models import Base

config = context.config

# 1. Настраиваем логирование Alembic
if config.config_file_name:
    fileConfig(config.config_file_name)

# 2. Передаем метаданные моделей
target_metadata = Base.metadata

# 3. В первую очередь берем ВНУТРЕННИЙ DATABASE_URL
db_url = (
    os.getenv("DATABASE_URL")
    or os.getenv("DATABASE_PUBLIC_URL")
    or str(settings.DATABASE_URL)
)

# 4. Приводим к синхронному виду для Alembic
if "+asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# 5. Экранируем '%' и передаем в конфигурацию
config.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))


def run_migrations_offline() -> None:
    """Запуск миграций в офлайн-режиме (генерация SQL-скрипта)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме (подключение к базе)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
