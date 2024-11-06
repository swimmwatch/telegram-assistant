from redis import Redis

from post.cache.base import BasePostStateCache
from post.cache.base import PostCacheState


class RedisPostStateCache(BasePostStateCache):
    """
    Implementation of post cache manager for Redis.
    """

    STATE_KEY_PATTERN = "state:%s"
    FILES_KEY_PATTERN = "files:%s"
    MSG_KEY_PATTERN = "msg:%s"
    CHAT_KEY_PATTERN = "chat:%s"

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    def _set_msg_id(self, post_id: str, msg_id: int):
        key = self.MSG_KEY_PATTERN % post_id
        self.redis_client.set(key, msg_id)

    def _set_chat_id(self, post_id: str, chat_id: int):
        key = self.CHAT_KEY_PATTERN % post_id
        self.redis_client.set(key, chat_id)

    def _set_state(self, post_id: str, new_state: PostCacheState) -> None:
        key = self.STATE_KEY_PATTERN % post_id
        self.redis_client.set(key, new_state.value)

    def _set_files(self, post_id: str, files: list[str]) -> None:
        key = self.FILES_KEY_PATTERN % post_id
        self.redis_client.lpush(key, *files)

    def _get_state(self, post_id: str) -> PostCacheState:
        state = PostCacheState.NONE
        state_key = self.STATE_KEY_PATTERN % post_id
        state_str = self.redis_client.get(state_key)
        if state_str:
            dec_state_str = state_str.decode()
            state = PostCacheState[dec_state_str]
        return state

    def _get_msg_id(self, post_id: str) -> int | None:
        msg_id = None
        msg_id_key = self.MSG_KEY_PATTERN % post_id
        msg_id_str = self.redis_client.get(msg_id_key)
        if msg_id_str:
            dec_msg_id_str = msg_id_str.decode()
            msg_id = int(dec_msg_id_str)
        return msg_id

    def _get_chat_id(self, post_id: str) -> int | None:
        chat_id = None
        chat_id_key = self.CHAT_KEY_PATTERN % post_id
        chat_id_str = self.redis_client.get(chat_id_key)
        if chat_id_str:
            dec_chat_id_str = chat_id_str.decode()
            chat_id = int(dec_chat_id_str)
        return chat_id

    def _get_files(self, post_id: str) -> list[str]:
        files_key = self.FILES_KEY_PATTERN % post_id
        files = self.redis_client.lrange(files_key, 0, -1)
        files = [file if not isinstance(file, bytes) else file.decode() for file in files]
        return files

    def _delete_state(self, post_id: str):
        state_key = self.STATE_KEY_PATTERN % post_id
        self.redis_client.delete(state_key)

    def _delete_files(self, post_id: str):
        files_key = self.FILES_KEY_PATTERN % post_id
        self.redis_client.delete(files_key)

    def _delete_msg_id(self, post_id: str):
        msg_id_key = self.MSG_KEY_PATTERN % post_id
        self.redis_client.delete(msg_id_key)

    def _delete_chat_id(self, post_id: str):
        chat_id_key = self.CHAT_KEY_PATTERN % post_id
        self.redis_client.delete(chat_id_key)
