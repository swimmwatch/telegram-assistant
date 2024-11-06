"""
Worker DI container.
"""
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from redis import Redis

from assistant.grpc_.client import AssistantGrpcClient
from infrastructure.assistant.config import AssistantSettings
from infrastructure.redis.config import RedisSettings
from post.cache.redis import RedisPostStateCache
from worker.config import WorkerSettings


class WorkerContainer(DeclarativeContainer):
    worker_settings = WorkerSettings()
    redis_settings = RedisSettings()
    assistant_settings = AssistantSettings()

    assistant_grpc_client = providers.Factory(
        AssistantGrpcClient,
        addr=assistant_settings.grpc_addr,
    )
    redis_client = providers.Singleton(
        Redis.from_url,
        url=redis_settings.url,
    )
    post_cache_state: providers.Singleton[RedisPostStateCache] = providers.Singleton(
        RedisPostStateCache,
        redis_client=redis_client,
    )
