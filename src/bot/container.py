"""
Assistant manager DI container.
"""
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from assistant.grpc_.client import AssistantAsyncGrpcClient
from core.dal import UserAsyncDAL
from infrastructure.assistant.config import AssistantSettings
from infrastructure.bot.config import TelegramBotSettings
from infrastructure.db.client.async_ import AsyncDatabase
from infrastructure.db.config import DatabaseSettings


class TelegramBotContainer(DeclarativeContainer):
    telegram_bot_settings = TelegramBotSettings()
    database_settings = DatabaseSettings()
    assistant_settings = AssistantSettings()

    assistant_grpc_client = providers.Singleton(
        AssistantAsyncGrpcClient,
        addr=assistant_settings.grpc_addr,
    )
    async_database = providers.Singleton(
        AsyncDatabase,
        db_url=database_settings.url,
    )
    user_repo: providers.Factory[UserAsyncDAL] = providers.Factory(
        UserAsyncDAL,
        session_factory=async_database.provided.session,
    )
