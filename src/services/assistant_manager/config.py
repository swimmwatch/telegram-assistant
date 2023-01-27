"""
Assistant manager configuration.
"""
from pydantic import BaseSettings, SecretStr


class AssistantManagerSettings(BaseSettings):
    my_telegram_id: int = 0
    telegram_api_token: SecretStr

    assistant_manager_grpc_addr: str


assistant_manager_settings = AssistantManagerSettings()