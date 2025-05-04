from logging.config import fileConfig
import os
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Импортируем базу и engine из models
from models import Base, engine

# Alembic config
config = context.config

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем Alembic метаданные моделей
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Миграции в offline-режиме."""
    url = os.getenv("DATABASE_URL")  # напрямую из .env
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Миграции в online-режиме."""
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
