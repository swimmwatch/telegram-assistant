"""
Assistant entrypoint.
"""
from grpc import aio
from loguru import logger

from assistant import assistant_pb2_grpc
from assistant.client import AssistantClient
from assistant.grpc_.server import AsyncAssistantService
from bot.grpc_.client import TelegramBotAsyncGrpcClient
from utils.sqlalchemy.types import AsyncSessionFactory


class AssistantEntrypoint:
    def __init__(
        self,
        grpc_addr: str,
        assistant_client: AssistantClient,
        bot_grpc_client: TelegramBotAsyncGrpcClient,
        session_factory: AsyncSessionFactory,
    ) -> None:
        self._grpc_addr = grpc_addr
        self._assistant = assistant_client
        self._bot_grpc_client = bot_grpc_client

        self._session_factory = session_factory

    async def _run_grpc_server(self) -> None:
        """
        Run gRPC server.
        """

        server = aio.server()
        service = AsyncAssistantService(
            # self._assistant,
            self._bot_grpc_client,
            self._session_factory,
        )
        assistant_pb2_grpc.add_AssistantServicer_to_server(service, server)

        # TODO: use secure port for production
        server.add_insecure_port(self._grpc_addr)

        logger.info(f"starting gRPC server on {self._grpc_addr}...")
        await server.start()
        logger.info("gRPC server was started.")

        await server.wait_for_termination()

    async def run(self) -> None:
        """
        Run assistant service.
        """

        await self._run_grpc_server()
