"""
Assistant manager service entrypoint.
"""
import asyncio
from multiprocessing import Process

from grpc import aio
from loguru import logger
from telegram.ext import Application
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler

from bot import bot_pb2_grpc
from bot import handlers
from bot.grpc_.server import AsyncTelegramBotService


class TelegramBotEntrypoint:
    def __init__(
        self,
        grpc_addr: str,
        token: str,
    ):
        self._grpc_addr = grpc_addr
        self._app = Application.builder().token(token).build()
        self._bot = self._app.bot

    def _setup_bot_handlers(self):
        for pattern, handler in handlers.COMMAND_HANDLERS.items():
            self._app.add_handler(CommandHandler(pattern, handler))

        for pattern, handler in handlers.CALLBACK_QUERY_HANDLERS.items():
            self._app.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    def _run_bot(self):
        self._setup_bot_handlers()

        logger.info("launch bot")
        self._app.run_polling()

    async def _run_grpc_server(self):
        server = aio.server()
        service = AsyncTelegramBotService(self._bot)
        bot_pb2_grpc.add_TelegramBotServicer_to_server(service, server)
        server.add_insecure_port(self._grpc_addr)

        logger.info(f"starting gRPC server on {self._grpc_addr}...")
        await server.start()
        logger.info("gRPC was started.")

        await server.wait_for_termination()

    def _create_event_loop(self, task):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(task())
        return

    def run(self):
        """
        Run assistant manager service.
        """
        processes = (
            Process(target=self._create_event_loop, args=(self._run_grpc_server,)),
            Process(target=self._run_bot),
        )
        for process in processes:
            process.start()

        for process in processes:
            process.join()
