"""
Worker configuration.
"""
import os

from pydantic import BaseSettings
from pydantic import RedisDsn

from infrastructure.common.config import BaseConfig

# YouTube
OUT_DIR = os.path.join("/tmp", "posts")  # noqa


class WorkerSettings(BaseSettings):
    celery_result_backend: RedisDsn
    celery_broker_url: RedisDsn

    class Config(BaseConfig):
        pass
