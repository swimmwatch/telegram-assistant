"""
Database configuration.
"""
from pydantic import BaseSettings
from pydantic import SecretStr

from infrastructure.common.config import BaseConfig
from infrastructure.common.config import RunLevelMixin


class DatabaseSettings(RunLevelMixin, BaseSettings):
    user: str
    password: SecretStr
    scheme: str = "postgresql+psycopg"
    host: str
    name: str
    debug: bool = True

    @property
    def url(self):
        """
        Returns database URL.
        """
        password = self.password.get_secret_value()
        return f"{self.scheme}://{self.user}:{password}@{self.host}/{self.name}"

    class Config(BaseConfig):
        env_prefix = "db_"
