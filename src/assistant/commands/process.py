"""
Command processors.
"""
import typing

from assistant.commands.request import CommandRequest
from utils.common.patterns import AsyncChainOfResponsibility


class AsyncCommandHandlerProcessor:
    """
    Aggregate async command handlers and process request.
    """

    def __init__(self, commands: typing.Sequence[AsyncChainOfResponsibility]) -> None:
        self._commands = commands

    async def handle(self, request: CommandRequest) -> None:
        """
        Handle command request.

        :param request: Command request
        """
        for command in self._commands:
            handled = await command.process_request(request)
            if handled:
                break


class CommandHandlerProcessor:
    """
    Aggregate command handlers and process request.
    """

    def __init__(self, commands: typing.Sequence[AsyncChainOfResponsibility]) -> None:
        self._commands = commands

    def handle(self, request: CommandRequest) -> None:
        """
        Handle command request.

        :param request: Command request
        """
        for command in self._commands:
            handled = command.process_request(request)
            if handled:
                break
