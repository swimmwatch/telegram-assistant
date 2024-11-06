"""
API dependencies.
"""
from infrastructure.db.client import AsyncDatabase
from infrastructure.db.client import Database
from infrastructure.db.config import DatabaseSettings


def get_db():
    # TODO: add return typing
    settings = DatabaseSettings()
    return Database(settings.url).session


async def get_async_db():
    # TODO: add return typing
    settings = DatabaseSettings()
    return AsyncDatabase(settings.url).session
