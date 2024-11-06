"""
Command handler request.
"""
from dataclasses import dataclass

from telethon import events
from telethon.tl.types import Message


@dataclass
class CommandRequest:
    """
    Command request data.
    """

    event: events.NewMessage.Event

    @property
    def text(self) -> str | None:
        """
        Return text from Telegram message if it is contained.

        :return: Text from Telegram message
        """
        return self.event.message.message

    @property
    def message(self) -> Message:
        """
        Return message.

        :return: Telegram message
        """
        return self.event.message
