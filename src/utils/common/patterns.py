"""
Common patterns.
"""
import abc
import typing


class Repository(typing.Protocol):
    """
    Repository protocol.
    """

    pass


class Factory(typing.Protocol):
    """Factory protocol."""

    pass


class ChainOfResponsibility(abc.ABC):
    """Chain Of Responsibility pattern"""

    @abc.abstractmethod
    def process_request(self, request) -> bool:
        pass


class AsyncChainOfResponsibility(abc.ABC):
    """Asynchronous Chain Of Responsibility pattern"""

    @abc.abstractmethod
    async def process_request(self, request) -> bool:
        pass
