"""
Download post command handler.
"""
from loguru import logger
from telethon.errors import MessageNotModifiedError

from assistant.commands.handler import ExplicitCommand
from assistant.commands.request import CommandRequest
from assistant.tasks import download_and_send_post
from post.adapters import InstagramPost
from post.adapters import YouTubeShortVideo
from post.exceptions import PostTooLarge
from post.exceptions import PostUnavailable
from utils.common.patterns import AsyncChainOfResponsibility
from utils.instagram.url import extract_instagram_link
from utils.youtube.url import extract_youtube_link


class YouTubeShortVideoDownloadCommandHandler(AsyncChainOfResponsibility):
    async def process_request(self, request: CommandRequest) -> bool:
        if request.text is None:
            return False

        link = extract_youtube_link(request.text)
        if not link:
            return False

        try:
            _ = YouTubeShortVideo(link)
        except (PostTooLarge, PostUnavailable):
            return False

        # remove web page preview
        if not request.event.message.is_reply:
            try:
                # space for avoid MessageNotModifiedError
                await request.event.message.edit(request.text + " ", link_preview=False)
            except MessageNotModifiedError:
                logger.warning("link preview was not hidden.")

        post = YouTubeShortVideo(link)
        download_and_send_post.delay(request.event.message.chat_id, post.id)
        logger.info(f"downloading YouTube short video post: {link}")

        return True


class InstagramPostDownloadCommandHandler(AsyncChainOfResponsibility):
    async def process_request(self, request: CommandRequest) -> bool:
        if request.text is None:
            return False

        link = extract_instagram_link(request.text)
        if not link:
            return False

        # remove web page preview
        if not request.event.message.is_reply:
            try:
                # space for avoid MessageNotModifiedError
                await request.event.message.edit(request.text + " ", link_preview=False)
            except MessageNotModifiedError:
                logger.warning("link preview was not hidden.")

        post = InstagramPost(link)
        download_and_send_post.delay(request.event.message.chat_id, post.id)
        logger.info(f"downloading Instagram post: {link}")

        return True


reply_download_post_command = ExplicitCommand(name="d")
reply_download_post_command.on_reply(
    [
        YouTubeShortVideoDownloadCommandHandler(),
        InstagramPostDownloadCommandHandler(),
    ]
)
