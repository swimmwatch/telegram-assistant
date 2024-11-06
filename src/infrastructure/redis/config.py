"""
Redis service configuration.
"""
from pydantic import BaseSettings

from infrastructure.common.config import BaseConfig
from infrastructure.common.config import RunLevelMixin


class RedisSettings(RunLevelMixin, BaseSettings):
    host: str
    db: int

    @property
    def url(self):
        return f"redis://{self.host}/{self.db}"

    class Config(BaseConfig):
        env_prefix = "redis_"
