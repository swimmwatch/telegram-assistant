"""
Basic class for social networks posts.
"""
import os
import typing
from abc import ABC
from abc import abstractmethod
from datetime import timedelta
from os import path
from urllib.parse import urlparse

import instagrapi
import pytube
from pytube import YouTube

from assistant.assistant_pb2 import MessageResponse
from assistant.assistant_pb2 import SendFilesRequest
from assistant.grpc_.client import AssistantGrpcClient
from infrastructure.instagram.config import InstagramSettings
from post.exceptions import PostNonDownloadable
from post.exceptions import PostTooLarge
from post.exceptions import PostUnavailable
from utils.telegram.protocols import SupportsTelegramSending


class Post(ABC, SupportsTelegramSending):
    _subclasses: dict[str, typing.Type["Post"]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._subclasses[cls.__name__] = cls

    @property
    @abstractmethod
    def id(self) -> str:
        """
        :return: Post ID
        """
        pass

    @abstractmethod
    def download(self, out_dir: str) -> typing.Sequence[str]:
        """Download post"""
        pass

    @property
    @abstractmethod
    def ttl(self) -> timedelta:
        """
        :return: Post TTL in cache
        """
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """
        :return: Post title
        """
        pass

    def clear(self, *args) -> None:
        for file in args:
            if path.exists(file):
                os.remove(file)

    @staticmethod
    @abstractmethod
    def init_from_id(post_id: str) -> "Post":
        """
        Create Post instances by post_id

        :param post_id: Post ID
        :return: Post instance
        """

    @classmethod
    def from_post_id(cls, post_id: str) -> "Post":
        class_name, id_ = post_id.split(":")
        return cls._subclasses[class_name].init_from_id(id_)


class YouTubeShortVideo(Post):
    YT_SHORT_VIDEO_TTL = timedelta(minutes=3)
    YT_SHORT_VIDEO_MAX_LEN = timedelta(minutes=3)

    def __init__(self, url: str):
        self.url = url

        try:
            self.yt = YouTube(self.url)
        except pytube.exceptions.VideoUnavailable:
            raise PostUnavailable(self.url)

        video_len = timedelta(seconds=self.yt.length)
        if video_len > self.YT_SHORT_VIDEO_MAX_LEN:
            raise PostTooLarge(url)

    @property
    def id(self) -> str:
        return f"{type(self).__name__}:{self.yt.video_id}"

    def download(self, out_dir: str) -> typing.Sequence[str]:
        """
        Download short YouTube video.

        :param out_dir: Output directory
        :return: Output filename
        """
        stream = self.yt.streams.get_highest_resolution()
        if stream is None:
            raise PostNonDownloadable(self.url)
        uniq_filename = f"{self.yt.title}.{stream.subtype}"
        out_filename = stream.download(out_dir, uniq_filename)
        return [out_filename]

    @property
    def ttl(self) -> timedelta:
        return self.YT_SHORT_VIDEO_TTL

    @property
    def title(self) -> str:
        return self.yt.title

    def send(
        self, client: AssistantGrpcClient, tg_user_id: int, **kwargs
    ) -> MessageResponse:
        req = SendFilesRequest(tg_user_id=tg_user_id, caption=self.title, **kwargs)
        return client.stub.send_files(req)

    @staticmethod
    def init_from_id(post_id: str) -> "YouTubeShortVideo":
        url = f"https://www.youtube.com/watch?v={post_id}"
        return YouTubeShortVideo(url)


class InstagramPost(Post):
    def __init__(self, url: str):
        self.url = url
        self.settings = InstagramSettings()

        # TODO: handle errors
        self.client = instagrapi.Client(proxy=self.settings.proxy, request_timeout=2)

        self._media_pk = self.client.media_pk_from_url(self.url)

    @property
    def id(self) -> str:
        parts = [p for p in urlparse(self.url).path.split("/") if p]
        return f"{type(self).__name__}:{parts.pop()}"

    def download(self, out_dir: str) -> typing.Sequence[str]:
        """
        Download Instagram video.

        :param out_dir: Output directory
        :return: Output filename
        """

        # TODO: handle errors
        self.client.login(self.settings.login, self.settings.password.get_secret_value())

        # TODO: handle errors
        media_info = self.client.media_info(self._media_pk)

        info = media_info.dict()
        media_type = info["media_type"]
        product_type = info["product_type"]
        match (media_type, product_type):
            case (1, "feed"):
                return [self.client.photo_download(self._media_pk, out_dir)]
            case (2, "feed") | (2, "clips"):
                return [self.client.video_download(self._media_pk, out_dir)]
            case (2, "igtv"):
                return [self.client.igtv_download(self._media_pk, out_dir)]
            case (8, _):
                return self.client.album_download(self._media_pk, out_dir)
            case _ as pair:
                raise AssertionError(f"Unhandled Instagram post downloading case: {pair}")

    @property
    def ttl(self) -> timedelta:
        return timedelta(minutes=3)

    @property
    def title(self) -> str:
        return "test"
        # return self._media.title or ""

    def send(
        self, client: AssistantGrpcClient, tg_user_id: int, **kwargs
    ) -> MessageResponse:
        req = SendFilesRequest(caption=self.title, tg_user_id=tg_user_id, **kwargs)
        return client.stub.send_files(req)

    @staticmethod
    def init_from_id(media_code: str) -> "InstagramPost":
        url = f"https://www.instagram.com/p/{media_code}/"
        return InstagramPost(url)


# class TikTokVideo(Post):
#     TT_VIDEO_TTL = timedelta(minutes=3)
#     TT_VIDEO_MAX_LEN = timedelta(minutes=3)
#
#     def __init__(self, url: str):
#         self.url = url
#
#         # TODO: check for available video
#         # TODO: add check for video size
#         self.tiktok_api = TikTokApi()
#         self.video = self.tiktok_api.video(url=self.url)
#
#     @property
#     def id(self) -> str:
#         return f'{type(self).__name__}:{self.video.id}'
#
#     def download(self, out_dir: str) -> str:
#         with self.tiktok_api:
#             video_data = self.video.bytes()
#             video_path = os.path.join(out_dir, self.id)
#             with open(video_path, "wb") as out_file:
#                 out_file.write(video_data)
#
#         return video_path
#
#     @property
#     def ttl(self) -> timedelta:
#         return self.TT_VIDEO_TTL
#
#     @property
#     def title(self) -> str:
#         # TODO: handle if something wrong
#         info = self.video.info()
#         return info['desc']
#
#     @staticmethod
#     def init_from_id(id_: str) -> 'Post':
#         url = f'https://www.tiktok.com/embed/video/{id_}'
#         return TikTokVideo(url)
