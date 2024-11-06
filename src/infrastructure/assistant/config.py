"""
Telegram assistant configuration.
"""
from pathlib import Path

from pydantic import BaseSettings
from pydantic import SecretStr

from infrastructure.common.config import BaseConfig
from infrastructure.common.config import RunLevelMixin

BASE_DIR = Path(__file__).resolve().parent


class AssistantSettings(RunLevelMixin, BaseSettings):
    api_id: SecretStr
    api_hash: SecretStr
    grpc_addr: str

    template_dir: Path = BASE_DIR / "templates"

    qr_login_timeout: float = 60.0

    class Config(BaseConfig):
        env_prefix = "assistant_"
