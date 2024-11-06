"""
Post exceptions.
"""


class BasePostException(Exception):
    """Base post exception class"""

    def __init__(self, url: str, message: str):
        self.url = url
        super().__init__(message)


class PostUnavailable(BasePostException):
    def __init__(self, url: str):
        self.message = f'Post with "{url}" is unavailable'
        super().__init__(url, self.message)


class PostNonDownloadable(BasePostException):
    def __init__(self, url: str):
        self.message = f'Post with "{url}" is non downloadable'
        super().__init__(url, self.message)


class PostTooLarge(BasePostException):
    def __init__(self, url: str):
        self.message = f'Post with "{url}" is too large'
        super().__init__(url, self.message)
