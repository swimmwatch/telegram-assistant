from typing import Protocol

from assistant.assistant_pb2 import MessageResponse
from assistant.grpc_.client import AssistantGrpcClient


class SupportsTelegramSending(Protocol):
    """
    Declares sending process to Telegram
    """

    def send(
        self, client: AssistantGrpcClient, tg_user_id: int, **kwargs
    ) -> MessageResponse:
        """
        Send data as Telegram message.

        :param client: Telegram gRPC client
        :param tg_user_id: Telegram user ID (sender)
        :param kwargs: Any arguments
        :return: Message response
        """
        ...
