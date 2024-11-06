"""
Assistant manager gRPC server.
"""
from telegram import Bot

from bot.bot_pb2 import MessageResponse
from bot.bot_pb2 import SendPhotoRequest
from bot.bot_pb2_grpc import TelegramBotServicer
from utils.img.base64 import Base64Image


class AsyncTelegramBotService(TelegramBotServicer):
    def __init__(self, bot: Bot):
        super().__init__()

        self._bot = bot

    async def send_text(self, request, context):
        # TODO: handle errors
        result_msg = await self._bot.send_message(request.chat_id, text=request.text)
        return MessageResponse(
            id=result_msg.message_id,
            chat_id=request.chat_id,
            # can_be_forwarded=result_msg.can_be_forwarded
        )

    async def send_photo(self, request: SendPhotoRequest, context):
        # TODO: handle errors
        img_file = Base64Image.decode_file(request.base64_img)
        result_msg = await self._bot.send_photo(
            request.chat_id,
            img_file,
            caption=request.caption,
        )
        return MessageResponse(
            id=result_msg.message_id,
            chat_id=request.chat_id,
            # can_be_forwarded=result_msg.can_be_forwarded
        )
