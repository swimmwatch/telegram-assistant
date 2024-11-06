"""
Command decorators.
"""
import functools

from assistant.commands.request import CommandRequest
from assistant.commands.types import ExplicitCommandHandler
from assistant.commands.types import ParsedArguments


def serve_only_replied_request(func: ExplicitCommandHandler) -> ExplicitCommandHandler:
    """
    Decorate explicit command handler for handling only replied requests.

    :param func: Explicit command handler
    :return: Wrapped explicit command handler
    """

    @functools.wraps(func)
    async def wrapper(args: ParsedArguments, request: CommandRequest):
        if request.event.is_reply:
            await func(args, request)

    return wrapper


def serve_only_group_messages(func: ExplicitCommandHandler) -> ExplicitCommandHandler:
    """
    Decorate explicit command handler for handling messages only from group.

    :param func: Explicit command handler
    :return: Wrapped explicit command handler
    """

    @functools.wraps(func)
    async def wrapper(args: ParsedArguments, request: CommandRequest):
        if request.event.message.is_group:
            await func(args, request)

    return wrapper
