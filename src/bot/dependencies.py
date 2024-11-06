from infrastructure.db.client.async_ import AsyncDatabase
from infrastructure.db.config import DatabaseSettings


def get_async_db() -> AsyncDatabase:
    settings = DatabaseSettings()
    db = AsyncDatabase(settings.url)
    return db
