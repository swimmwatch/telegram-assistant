"""
Download post command handler.
"""
from loguru import logger

from assistant.commands.handler import ExplicitCommand
from assistant.commands.request import CommandRequest
from assistant.tasks import convert_video_to_audio
from utils.common.patterns import AsyncChainOfResponsibility
from worker.config import OUT_DIR


class CovertVideoToMusicCommandHandler(AsyncChainOfResponsibility):
    async def process_request(self, request: CommandRequest) -> bool:
        message = request.message
        if message.video:
            # TODO: handle errors
            # TODO: change to right output directory
            video_path = await message.download_media(OUT_DIR)

            convert_video_to_audio.delay(chat_id=message.chat_id, video_path=video_path)
            logger.info("converting video to audio...")

            return True

        return False


reply_convert_music_command = ExplicitCommand(name="audio")
reply_convert_music_command.on_reply([CovertVideoToMusicCommandHandler()])
