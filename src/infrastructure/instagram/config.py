"""
Instagram service configuration.
"""
from pydantic import BaseSettings
from pydantic import SecretStr

from infrastructure.common.config import BaseConfig


class InstagramSettings(BaseSettings):
    login: str
    password: SecretStr

    proxy: str

    class Config(BaseConfig):
        env_prefix = "inst_"
