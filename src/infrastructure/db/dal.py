"""
SQLAlchemy Data Access Layer.
"""
import abc
import typing

import sqlalchemy as sa
from sqlalchemy.sql.dml import ReturningDelete
from sqlalchemy.sql.dml import ReturningUpdate

from infrastructure.db.base import Base
from utils.sqlalchemy.types import AsyncSessionFactory
from utils.sqlalchemy.types import SessionFactory

T = typing.TypeVar("T", bound=Base)


class BaseSqlAlchemyDAL(abc.ABC):
    class Config:
        model: type

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self._base_query = sa.select(self.Config.model)  # type: ignore

    @classmethod
    def _update(cls, instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        return instance

    @property
    def pk(self) -> str | None:
        meta = sa.inspect(self.Config.model)  # type: ignore
        if not meta:
            return None

        return meta.primary_key[0].name

    def base(self, query: sa.Select) -> "BaseSqlAlchemyDAL":
        self._base_query = query
        return self

    def query(self) -> sa.Select:
        return self._base_query

    def filter(self, **kwargs) -> "BaseSqlAlchemyDAL":
        self._base_query = self._base_query.filter_by(**kwargs)
        return self

    def where(self, *args) -> "BaseSqlAlchemyDAL":
        self._base_query = self._base_query.where(*args)
        return self

    def order_by(self, *args) -> "BaseSqlAlchemyDAL":
        self._base_query = self._base_query.order_by(*args)
        return self

    def group_by(self, *args) -> "BaseSqlAlchemyDAL":
        self._base_query = self._base_query.group_by(*args)
        return self

    def join(self, *args) -> "BaseSqlAlchemyDAL":
        self._base_query = self._base_query.join(*args)
        return self

    def _delete_stmt(self) -> ReturningDelete:
        return (
            sa.delete(self.Config.model)
            .where(self._base_query.whereclause)  # type: ignore
            .returning(self.Config.model)
        )

    def _update_stmt(self, **kwargs) -> ReturningUpdate:
        """
        Returns UPDATE statement with WHERE condition.

        :param kwargs: Condition parameters.
        """
        return (
            sa.update(self.Config.model)
            .values(**kwargs)
            .where(self._base_query.whereclause)  # type: ignore
            .returning(self.Config.model)
        )

    def _reset_query(self):
        self._base_query = sa.select(self.Config.model)

    @abc.abstractmethod
    def first(self):
        ...

    @abc.abstractmethod
    def all(self):
        ...

    @abc.abstractmethod
    def create_one(self, **kwargs):
        ...

    @abc.abstractmethod
    def update_instance(self, instance, **kwargs):
        ...

    @abc.abstractmethod
    def update_or_create(self, **kwargs) -> typing.Callable:
        ...

    @abc.abstractmethod
    def delete(self):
        ...

    @abc.abstractmethod
    def update(self, **kwargs):
        ...


class SqlAlchemyDAL(BaseSqlAlchemyDAL, typing.Generic[T]):
    session_factory: SessionFactory

    def update(self, **kwargs) -> sa.Result:
        with self.session_factory() as session:
            # TODO: refactor using base query
            stmt = self._update_stmt(**kwargs)
            res = session.execute(stmt)
            self._reset_query()
            return res

    def delete(self) -> sa.Result:
        with self.session_factory() as session:
            stmt = self._delete_stmt()
            res = session.execute(stmt)
            self._reset_query()
            return res

    def first(self) -> T | None:
        with self.session_factory() as session:
            instance = session.execute(self._base_query).scalar_one_or_none()
            self._reset_query()
            return instance

    def all(self) -> sa.ScalarResult[T]:
        with self.session_factory() as session:
            instances = session.execute(self._base_query).scalars()
            self._reset_query()
            return instances

    def create_one(self, **kwargs):
        with self.session_factory() as session:
            instance = self.Config.model(**kwargs)
            session.add(instance)
            session.commit()
            self._reset_query()
            return instance

    def update_instance(self, instance, **kwargs):
        with self.session_factory() as session:
            updated_instance = self._update(instance, **kwargs)
            session.commit()
            self._reset_query()
            return updated_instance

    def update_or_create(self, **kwargs) -> typing.Callable:
        def update(**inner_kwargs):
            instance = self.filter(**kwargs).first()

            if not instance:
                params = {**kwargs, **inner_kwargs}
                if self.pk and self.pk in params:
                    params.pop(self.pk)
                return self.create_one(**params)

            instance = self.update_instance(instance, **inner_kwargs)

            return instance

        return update


class SqlAlchemyAsyncDAL(BaseSqlAlchemyDAL):
    session_factory: AsyncSessionFactory

    async def update(self, **kwargs) -> sa.Result:
        async with self.session_factory() as session:
            # TODO: refactor using base query
            stmt = self._update_stmt(**kwargs)
            res = await session.execute(stmt)
            await session.commit()
            self._reset_query()
            return res

    async def delete(self) -> sa.Result:
        async with self.session_factory() as session:
            stmt = self._delete_stmt()
            cursor = await session.execute(stmt)
            self._reset_query()
            return cursor

    async def first(self) -> T | None:
        async with self.session_factory() as session:
            cursor = await session.execute(self._base_query)
            self._reset_query()
            return cursor.scalar_one_or_none()

    async def all(self) -> sa.ScalarResult:
        async with self.session_factory() as session:
            cursor = await session.execute(self._base_query)
            self._reset_query()
            return cursor.scalars()

    async def create_one(self, **kwargs):
        async with self.session_factory() as session:
            instance = self.Config.model(**kwargs)
            session.add(instance)
            await session.commit()
            self._reset_query()
            return instance

    async def update_instance(self, instance, **kwargs):
        async with self.session_factory() as session:
            updated_instance = self._update(instance, **kwargs)
            await session.commit()
            self._reset_query()
            return updated_instance

    def update_or_create(self, **kwargs) -> typing.Callable:
        async def update(**inner_kwargs):
            instance = await self.filter(**kwargs).first()

            if not instance:
                params = {**kwargs, **inner_kwargs}
                if self.pk and self.pk in params:
                    params.pop(self.pk)
                return await self.create_one(**params)

            instance = await self.update_instance(instance, **inner_kwargs)

            return instance

        return update
