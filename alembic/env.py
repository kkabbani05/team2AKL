import os
import sys
from logging.config import fileConfig

from alembic import context

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.app.database import engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations() -> None:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Offline migrations not supported")
else:
    run_migrations()