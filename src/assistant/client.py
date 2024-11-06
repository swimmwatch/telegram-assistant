"""
Assistant.
"""
import os
import typing

from telethon import TelegramClient
from telethon import events
from telethon.sessions import Session
from telethon.sessions import StringSession
from telethon.tl.custom import QRLogin
from telethon.tl.types import Message
from telethon.tl.types import User as TelethonUser

from assistant.commands.request import CommandRequest
from assistant.grpc_.exceptions import ClientAlreadyInitiated
from assistant.grpc_.exceptions import ClientIsNotInitiated
from assistant.handlers import command_processor


class AssistantClient:
    def __init__(self, api_id: str, api_hash: str):
        self._api_id = api_id
        self._api_hash = api_hash
        self.telegram_client: TelegramClient | None = None

    async def log_out(self) -> bool:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        # TODO: handle case if telegram client is not exists
        status = await self.telegram_client.log_out()
        if status:
            self.telegram_client = None
        return status

    def make(self, session: Session) -> None:
        if self.telegram_client:
            raise ClientAlreadyInitiated

        # TODO: handle case if telegram client exists
        self.telegram_client = TelegramClient(
            session=session,
            api_id=self._api_id,
            api_hash=self._api_hash,
        )

    async def connect(self) -> None:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        await self.telegram_client.connect()

    async def get_me(self) -> TelethonUser:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return await self.telegram_client.get_me()

    def get_session(self) -> str:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return StringSession.save(self.telegram_client.session)

    def _add_handlers(self):
        """
        Add Telegram handlers.
        """
        if not self.telegram_client:
            raise ClientIsNotInitiated

        @self.telegram_client.on(events.NewMessage(outgoing=True))
        async def handle_new_own_message(event: events.NewMessage.Event):
            request = CommandRequest(event)
            await command_processor.handle(request)

    async def is_authorized(self) -> bool:
        if self.telegram_client:
            return await self.telegram_client.is_user_authorized()
        return False

    async def send_text(
        self, chat_id, text, disable_notification: bool = False
    ) -> Message:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return await self.telegram_client.send_message(
            chat_id,
            message=text,
            silent=disable_notification,
        )

    async def authorize_2fa_password(self, password: str) -> TelethonUser:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return await self.telegram_client.sign_in(password=password)

    async def qr_login(self) -> QRLogin:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return await self.telegram_client.qr_login()

    async def send_file(
        self,
        chat_id: int,
        files: typing.Sequence[os.PathLike] | os.PathLike,
        *,
        caption: str,
        disable_notification: bool,
    ) -> typing.Sequence[Message] | Message:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return await self.telegram_client.send_file(
            chat_id,
            files,
            caption=caption,
            silent=disable_notification,
        )

    async def forward_messages(
        self,
        chat_id: int,
        messages: list[int],
        from_chat_id: int,
        disable_notification: bool,
    ) -> typing.Sequence[Message]:
        if not self.telegram_client:
            raise ClientIsNotInitiated

        return await self.telegram_client.forward_messages(
            chat_id,
            messages,
            from_chat_id,
            silent=disable_notification,
        )

    async def init(self):
        """
        Assistant initialization.
        """
        self._add_handlers()
