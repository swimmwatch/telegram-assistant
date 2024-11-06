import os
from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from moviepy.video.io.VideoFileClip import VideoFileClip

from assistant.assistant_pb2 import ForwardMessagesRequest
from assistant.assistant_pb2 import SendFilesRequest
from post.adapters import Post
from post.cache.base import PostCacheState
from post.exceptions import PostNonDownloadable
from post.exceptions import PostTooLarge
from post.exceptions import PostUnavailable
from worker.config import OUT_DIR
from worker.container import WorkerContainer

logger = get_task_logger(__name__)


@shared_task
@inject
def convert_video_to_audio(
    tg_user_id: int,
    chat_id: int,
    video_path: str,
    assistant_grpc_client=Provide[WorkerContainer.assistant_grpc_client],
) -> None:
    """
    Convert Video from Telegram message into audio and send it to `chat_id`.

    :param tg_user_id: Telegram User ID
    :param chat_id: Chat ID
    :param video_path: Video file path
    :param assistant_grpc_client: Assistant gRPC client instance.
    """
    filename, ext = os.path.splitext(video_path)
    clip = VideoFileClip(video_path)
    audio_path = f"{filename}.mp3"
    clip.audio.write_audiofile(audio_path)

    request = SendFilesRequest(
        tg_user_id=tg_user_id,
        caption="",
        chat_id=chat_id,
        files=[audio_path],
        disable_notification=True,
    )
    # TODO: handle errors
    assistant_grpc_client.stub.send_files(request)
    logger.debug(f"message with audio file was sent to {chat_id=}")

    # TODO: remove video and audio after sending


@shared_task
@inject
def clear_cached_post(
    post_id: str,
    files: list[str],
    post_state_cache=Provide[WorkerContainer.post_cache_state],
):
    """Clear cached post"""
    post = Post.from_post_id(post_id)
    post_state_cache.clear(post.id)
    post.clear(*files)


@shared_task
@inject
def download_and_send_post(
    tg_user_id: int,
    chat_id: int,
    post_id: str,
    post_state_cache=Provide[WorkerContainer.post_cache_state],
    assistant_grpc_client=Provide[WorkerContainer.assistant_grpc_client],
):
    try:
        post = Post.from_post_id(post_id)
    except (PostUnavailable, PostTooLarge) as err:
        logger.info(err.message)
        return

    state, files, (from_chat_id, msg_id) = post_state_cache.get(post.id)
    if state is PostCacheState.NONE:
        try:
            post_state_cache.set_state(post.id, PostCacheState.DOWNLOADING)
            files = post.download(OUT_DIR)
        except PostNonDownloadable as err:
            post_state_cache.set_state(post.id, PostCacheState.NONE)
            logger.warning(err.message)
            return
        except Exception as err:
            post_state_cache.set_state(post.id, PostCacheState.NONE)
            logger.error(err)
            return

        post_state_cache.set_state(post.id, PostCacheState.DOWNLOADED)
        post_state_cache.set_files(post.id, files)
    elif state is PostCacheState.DOWNLOADED:
        request = ForwardMessagesRequest(
            tg_user_id=tg_user_id,
            from_chat_id=from_chat_id,
            chat_id=chat_id,
            message_ids=[msg_id],
            disable_notification=True,
        )
        assistant_grpc_client.stub.forward_messages(request)
        logger.debug(
            f"message with post files was forwarded from {from_chat_id=} to {chat_id=}"
        )
        return

    files = [file if not isinstance(file, bytes) else file.decode() for file in files]
    msg = post.send(
        assistant_grpc_client,
        tg_user_id=tg_user_id,
        files=files,
        chat_id=chat_id,
        disable_notification=True,
    )
    logger.debug(f"message with post files was sent to {chat_id=}")

    post_state_cache.set_msg_info(post.id, msg.chat_id, msg.id)
    logger.debug(f"cached sent message information {post.id=}")

    # create task for clearing cached post
    release_date = datetime.now() + post.ttl
    clear_cached_post.apply_async((post.id, files), eta=release_date)
