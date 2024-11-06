"""
Post cache state manager.
"""
import abc
import enum


class PostCacheState(enum.Enum):
    """
    Post cache states.
    """

    NONE = "NONE"
    DOWNLOADED = "DOWNLOADED"
    DOWNLOADING = "DOWNLOADING"


class BasePostStateCache(abc.ABC):
    """
    Base class that declares getting and setting cache state.
    """

    @abc.abstractmethod
    def _set_msg_id(self, post_id: str, msg_id: int) -> None:
        ...

    @abc.abstractmethod
    def _set_chat_id(self, post_id: str, chat_id: int) -> None:
        ...

    @abc.abstractmethod
    def _set_state(self, post_id: str, new_state: PostCacheState) -> None:
        ...

    @abc.abstractmethod
    def _set_files(self, post_id: str, files: list[str]) -> None:
        ...

    @abc.abstractmethod
    def _get_state(self, post_id: str) -> PostCacheState:
        ...

    @abc.abstractmethod
    def _get_msg_id(self, post_id: str) -> int | None:
        ...

    @abc.abstractmethod
    def _get_chat_id(self, post_id: str) -> int | None:
        ...

    @abc.abstractmethod
    def _get_files(self, post_id: str) -> list[str]:
        ...

    @abc.abstractmethod
    def _delete_state(self, post_id: str):
        ...

    @abc.abstractmethod
    def _delete_files(self, post_id: str):
        ...

    @abc.abstractmethod
    def _delete_msg_id(self, post_id: str):
        ...

    @abc.abstractmethod
    def _delete_chat_id(self, post_id: str):
        ...

    def set_msg_info(self, post_id: str, chat_id: int, msg_id: int) -> None:
        self._set_msg_id(post_id, msg_id)
        self._set_chat_id(post_id, chat_id)

    def set_state(self, post_id: str, new_state: PostCacheState) -> None:
        self._set_state(post_id, new_state)

    def set_files(self, post_id: str, files: list[str]) -> None:
        self._set_files(post_id, files)

    def get(
        self, post_id: str
    ) -> tuple[PostCacheState | None, list[str], tuple[int | None, int | None]]:
        """
        Get post cache state.

        :param post_id:
        :return: State, files, chat ID, message ID
        """

        state = self._get_state(post_id)
        msg_id = self._get_msg_id(post_id)
        chat_id = self._get_chat_id(post_id)
        files = self._get_files(post_id)

        return state, files, (chat_id, msg_id)

    def clear(self, post_id: str):
        """
        Clear post cache state.

        :param post_id:
        :return:
        """

        self._delete_state(post_id)
        self._delete_msg_id(post_id)
        self._delete_files(post_id)
        self._delete_chat_id(post_id)
