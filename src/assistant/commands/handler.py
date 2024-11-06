"""
Command handlers.
"""
import typing
from collections import deque

from loguru import logger
from telethon import events

from assistant.commands.decorators import serve_only_replied_request
from assistant.commands.process import AsyncCommandHandlerProcessor
from assistant.commands.request import CommandRequest
from assistant.commands.types import ExplicitCommandCondition
from assistant.commands.types import ExplicitCommandHandler
from assistant.commands.types import ParsedArguments
from utils.common.patterns import AsyncChainOfResponsibility


class ExplicitCommand:
    """
    Explicit command.
    """

    MAX_COMMAND_NAME_LEN = 16

    def __init__(self, name: str):
        """
        Create explicit command instance.

        :param name: Command name
        """
        if not name:
            raise ValueError("Command name must be not empty")

        if "\\" in name:
            raise ValueError(r'Command name must doesn\'t contain "\" character')

        if len(name) >= ExplicitCommand.MAX_COMMAND_NAME_LEN:
            raise ValueError(
                f"Command name length must be"
                f" less then {ExplicitCommand.MAX_COMMAND_NAME_LEN}"
            )

        if any(char.isdigit() for char in name):
            raise ValueError("Command name must doesn't contain digits")

        self._name = name
        self._args: dict[str, typing.Type] = {}
        self._handlers: typing.Deque[
            tuple[ExplicitCommandHandler, ExplicitCommandCondition | None]
        ] = deque()

    @property
    def name(self) -> str:
        """
        Command name property.
        """
        return self._name

    def _add_arg(self, name: str, cls: typing.Type) -> None:
        """
        Private method for adding command argument.

        :param name: Argument name
        :param cls: Value type
        """
        self._args[name] = cls

    def add_arg(self, name: str, cls: typing.Type) -> "ExplicitCommand":
        """
        Add command argument.

        :param name: Argument
        :param cls: Value type
        :return: Self
        """
        self._add_arg(name, cls)
        return self

    def _add_handler(
        self,
        func: ExplicitCommandHandler,
        condition: ExplicitCommandCondition | None,
    ) -> None:
        """
        Private method for adding explicit command handler.

        :param func: Explicit command handler
        :param condition: Explicit command condition predicate
        """
        self._handlers.append((func, condition))

    def on(
        self, condition: ExplicitCommandCondition | None = None
    ) -> typing.Callable[[ExplicitCommandHandler], None]:
        """
        Decorate explicit command handler.

        :param condition: Explicit command condition predicate
        :return: Decorated explicit command handler that calls if condition returns True
        """

        def wrapper(func: ExplicitCommandHandler) -> None:
            self._add_handler(func, condition)

        return wrapper

    def on_reply(self, command_handlers: list[AsyncChainOfResponsibility]) -> None:
        @self.on()
        @serve_only_replied_request
        async def handler(_: ParsedArguments, request: CommandRequest) -> None:
            replied_message = await request.event.message.get_reply_message()
            request = CommandRequest(events.NewMessage.Event(replied_message))
            processor = AsyncCommandHandlerProcessor(command_handlers)
            await processor.handle(request)

    async def emit(self, args: ParsedArguments, command_request: CommandRequest):
        """
        Emit handler with passed arguments and command request.

        :param args: Parsed command arguments
        :param command_request: Command request
        """
        for func, condition in self._handlers:
            if condition:
                if condition(args):
                    await func(args, command_request)
            else:
                await func(args, command_request)

    def parse(self, text: str) -> ParsedArguments | None:
        """
        Parse command arguments from text.

        :param text: Some text
        :return: Parsed command arguments
        """
        if not text:
            return None

        parts = text.split()
        actual_command_name = parts[0]
        expected_command_name = rf"\{self._name}"

        if (
            not text.startswith(expected_command_name)
            or actual_command_name != expected_command_name
        ):
            return None

        values = parts[1:]
        res = {arg_name: None for arg_name in self._args}
        try:
            for (arg_name, arg_type), arg_value in zip(self._args.items(), values):
                res[arg_name] = arg_type(arg_value)
        except ValueError:
            return None
        return res


class ExplicitCommandHandlerWrapper(AsyncChainOfResponsibility):
    """
    Handler wrapper for explicit commands.
    """

    def __init__(
        self,
        command: ExplicitCommand,
    ):
        self.command = command

    async def process_request(self, request: CommandRequest) -> bool:
        """
        Process explicit command request.

        :param request: Command request
        :return: Parsing status
        """
        if request.text is None:
            return False

        args = self.command.parse(request.text)

        if args is None:
            return False

        await self.command.emit(args, request)
        logger.info(f"handling {self.command.name} command")

        return True
