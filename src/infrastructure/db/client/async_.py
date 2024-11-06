"""
Async database client.
"""
import asyncio
import contextlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_scoped_session
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from utils.sqlalchemy.types import AsyncSessionGenerator


class AsyncDatabase:
    def __init__(self, db_url: str, echo: bool = True) -> None:
        self._engine = create_async_engine(db_url, echo=echo)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
            asyncio.current_task,
        )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncSessionGenerator:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
