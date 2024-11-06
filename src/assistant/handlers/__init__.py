"""
Implemented Command handlers.
"""
from assistant.commands.handler import ExplicitCommandHandlerWrapper
from assistant.handlers.download_post import InstagramPostDownloadCommandHandler
from assistant.handlers.download_post import YouTubeShortVideoDownloadCommandHandler

from ..commands.process import AsyncCommandHandlerProcessor
from .about_me import about_me_command
from .all import all_command
from .convert_music import reply_convert_music_command
from .download_post import reply_download_post_command
from .hello import hello_command

_COMMANDS = [
    YouTubeShortVideoDownloadCommandHandler(),
    InstagramPostDownloadCommandHandler(),
    ExplicitCommandHandlerWrapper(hello_command),
    ExplicitCommandHandlerWrapper(about_me_command),
    ExplicitCommandHandlerWrapper(all_command),
    ExplicitCommandHandlerWrapper(reply_download_post_command),
    ExplicitCommandHandlerWrapper(reply_convert_music_command),
]
command_processor = AsyncCommandHandlerProcessor(_COMMANDS)

__all__ = [
    "command_processor",
]
