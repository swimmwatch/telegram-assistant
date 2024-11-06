import contextlib
import os
import typing
from pathlib import Path

import alembic
import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import drop_database

from infrastructure.db.config import DatabaseSettings
from utils.factory import FactoryType
from utils.sqlalchemy.types import AsyncSessionFactory
from utils.sqlalchemy.types import AsyncSessionGenerator
from utils.sqlalchemy.types import SessionFactory
from utils.sqlalchemy.types import SessionGenerator


def _upgrade_head(settings: DatabaseSettings, rootdir: str) -> None:
    """
    Upgrade the test database to head.

    :param settings: Database settings
    :param rootdir: Root project directory
    """
    config = alembic.config.Config()
    alembic_folder = Path(rootdir) / Path("src") / Path("migrations")
    config.set_main_option("script_location", str(alembic_folder))
    config.set_main_option("sqlalchemy.url", settings.url)

    # heads means all migrations from all branches (in case there are split branches)
    alembic.command.upgrade(config, "heads")


@pytest.fixture(scope="session")
def db_engine(request) -> typing.Generator[sa.Engine, None, None]:
    os.environ["DB_NAME"] = "test"  # override default database
    settings = DatabaseSettings()

    if not database_exists(settings.url):
        create_database(settings.url)

    engine = sa.create_engine(settings.url, echo=settings.debug)

    _upgrade_head(settings, request.config.rootdir)

    try:
        yield engine
    finally:
        drop_database(settings.url)


@pytest.fixture()
def alembic_engine(db_engine: sa.Engine) -> sa.Engine:
    """
    Override "alembic_engine" fixture of "pytest-alembic" package.

    Check: https://pytest-alembic.readthedocs.io/en/latest/api.html#pytest_alembic.plugin.fixtures.alembic_engine  # noqa: E501

    :param db_engine: SQLAlchemy Engine instance
    :return: SQLAlchemy Engine instance
    """
    return db_engine


@pytest.fixture()
def db_session(db_engine: sa.Engine) -> SessionGenerator:
    connection = db_engine.connect()
    transaction = connection.begin()
    test_local_session = orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=connection,
        class_=orm.Session,
    )
    session = test_local_session()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()  # rollback to the savepoint
        connection.close()


@pytest.fixture()
def db_session_maker(db_session: orm.Session) -> SessionFactory:
    def session_maker() -> SessionGenerator:
        yield db_session

    return contextlib.contextmanager(session_maker)


@pytest.fixture()
def instance(db_session: orm.Session) -> typing.Callable:
    """
    SQLAlchemy model instance factory.

    :param db_session: SQLAlchemy session
    :return: Model instance
    """

    def make(*args):
        db_session.add_all(args)
        db_session.commit()
        return args

    return make


@pytest.fixture()
def db_factory(instance: typing.Callable) -> typing.Callable:
    """
    Uses FactoryMaker for creating database instances.
    """

    def make(factory_maker: FactoryType | None):
        if factory_maker is None:
            return

        data = factory_maker.make()
        if isinstance(data, typing.Iterable):
            return instance(*data)
        else:
            obj = instance(data)
            return obj[0]

    return make


@pytest.fixture(scope="session")
def async_db_engine(request) -> typing.Generator[AsyncEngine, None, None]:
    os.environ["DB_NAME"] = "async_test"  # override default database
    settings = DatabaseSettings()

    if not database_exists(settings.url):
        create_database(settings.url)

    engine = create_async_engine(settings.url, echo=settings.debug)

    _upgrade_head(settings, request.config.rootdir)

    try:
        yield engine
    finally:
        drop_database(settings.url)


@pytest_asyncio.fixture()
async def async_db_session(async_db_engine: AsyncEngine) -> AsyncSessionGenerator:
    connection = await async_db_engine.connect()
    transaction = await connection.begin()
    test_local_session = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=connection,
        class_=AsyncSession,
    )
    session = test_local_session()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()  # rollback to the savepoint
        await connection.close()


@pytest.fixture()
def async_db_session_maker(async_db_session: AsyncSession) -> AsyncSessionFactory:
    @contextlib.asynccontextmanager
    async def session_maker() -> AsyncSessionGenerator:
        yield async_db_session

    return session_maker


@pytest.fixture()
def async_instance(async_db_session: AsyncSession) -> typing.Callable:
    """
    SQLAlchemy model instance factory.

    :param async_db_session: SQLAlchemy session
    :return: Model instance
    """

    async def make(*args):
        async_db_session.add_all(args)
        await async_db_session.commit()
        return args

    return make


@pytest.fixture()
def async_db_factory(async_instance: typing.Callable) -> typing.Callable:
    """
    Uses FactoryMaker for creating database instances.
    """

    async def make(factory_maker: FactoryType | None):
        if factory_maker is None:
            return

        data = factory_maker.make()
        if isinstance(data, typing.Iterable):
            return await async_instance(*data)
        else:
            obj = await async_instance(data)
            return obj[0]

    return make
