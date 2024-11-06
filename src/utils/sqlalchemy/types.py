"""
SQLAlchemy typing utilities.
"""
import typing

from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession

SessionFactory = typing.Callable[..., typing.ContextManager[orm.Session]]
AsyncSessionFactory = typing.Callable[..., typing.AsyncContextManager[AsyncSession]]
SessionGenerator = typing.Generator[orm.Session, None, None]
AsyncSessionGenerator = typing.AsyncGenerator[AsyncSession, None]
