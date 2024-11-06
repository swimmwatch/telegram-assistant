"""
gRPC Assistant server.
"""
import asyncio
import typing

import qrcode
from google.protobuf.empty_pb2 import Empty
from grpc import StatusCode
from PIL.Image import Image
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.tl.custom import QRLogin
from telethon.tl.types import User as TelethonUser

from assistant.assistant_pb2 import AuthMethod
from assistant.assistant_pb2 import BooleanValue
from assistant.assistant_pb2 import MessageResponse
from assistant.assistant_pb2 import SendTextRequest
from assistant.assistant_pb2_grpc import AssistantServicer
from assistant.client import AssistantClient
from bot.bot_pb2 import SendPhotoRequest
from bot.grpc_.client import TelegramBotAsyncGrpcClient
from core.dal import UserAsyncDAL
from infrastructure.assistant.config import AssistantSettings
from utils.img.base64 import Base64Image
from utils.sqlalchemy.types import AsyncSessionFactory


class AsyncAssistantService(AssistantServicer):
    def __init__(
        self,
        bot_grpc_client: TelegramBotAsyncGrpcClient,
        session_factory: AsyncSessionFactory,
    ) -> None:
        super().__init__()

        self._accounts: dict[int, AssistantClient] = {}
        self._bot_grpc_client = bot_grpc_client

        self._session_factory = session_factory

        self._settings = AssistantSettings()

    def _get_client(self, tg_user_id: int) -> AssistantClient:
        if tg_user_id in self._accounts:
            return self._accounts[tg_user_id]
        else:
            client = AssistantClient(
                self._settings.api_id.get_secret_value(),
                self._settings.api_hash.get_secret_value(),
            )
            self._accounts[tg_user_id] = client
            return client

    async def send_text(self, request, context):
        # TODO: handle errors
        message = await self._get_client(request.tg_user_id).send_text(
            request.chat_id,
            request.text,
            request.disable_notification,
        )
        return MessageResponse(
            id=message.id,
            chat_id=request.chat_id,
            # can_be_forwarded=message.can_be_forwarded
        )

    async def send_video(self, request, context):
        # TODO: handle errors
        message = await self._get_client(request.tg_user_id).send_file(
            request.chat_id,
            request.video_path,
            caption=request.caption,
            disable_notification=request.disable_notification,
        )

        if isinstance(message, typing.Sequence):
            message = message[0]

        return MessageResponse(
            id=message.id,
            chat_id=request.chat_id,
            # can_be_forwarded=message.can_be_forwarded
        )

    async def send_files(self, request, context):
        # TODO: handle errors
        messages = await self._get_client(request.tg_user_id).send_file(
            request.chat_id,
            list(request.files),
            caption=request.caption,
            disable_notification=request.disable_notification,
        )
        return MessageResponse(
            id=messages[0].id,
            chat_id=request.chat_id,
            # can_be_forwarded=result_msg.can_be_forwarded
        )

    async def forward_messages(self, request, context):
        # TODO: handle errors
        await self._get_client(request.tg_user_id).forward_messages(
            request.chat_id,
            list(request.message_ids),
            request.from_chat_id,
            request.disable_notification,
        )
        return Empty()

    async def is_authorized(self, request, context):
        is_authorized = await self._get_client(request.tg_user_id).is_authorized()
        return BooleanValue(value=is_authorized)

    def _create_login_qr_code(self, qr_login: QRLogin) -> Image:
        return qrcode.make(qr_login.url)

    async def _send_qr_code(self, chat_id: int, img: Image) -> None:
        base64_img = Base64Image.encode(img)
        req = SendPhotoRequest(
            chat_id=chat_id,
            caption="Please login using this QR code.",
            base64_img=base64_img,
        )
        await self._bot_grpc_client.stub.send_photo(req)

    async def _authorize_qr_login(self, tg_user_id: int) -> TelethonUser:
        client = self._get_client(tg_user_id)
        qr_login = await client.qr_login()
        user: TelethonUser | None = None
        attempts = 1
        while not user:
            if attempts > 3:
                break

            img = self._create_login_qr_code(qr_login)
            await self._send_qr_code(tg_user_id, img)
            try:
                user = await qr_login.wait(self._settings.qr_login_timeout)
            except SessionPasswordNeededError:
                # raise err
                user = await client.authorize_2fa_password("1136i love richard1136")
            except asyncio.TimeoutError:
                await qr_login.recreate()
                attempts += 1
        return user

    async def _authorize_user(
        self,
        tg_user_id: int,
        auth_method: AuthMethod,
    ) -> TelethonUser:
        user_repo = UserAsyncDAL(self._session_factory)
        client = self._get_client(tg_user_id)

        current_user = user_repo.filter(tg_id=tg_user_id)
        user = await current_user.first()

        # TODO: Handle session decryption/encryption
        session = StringSession(user.session)
        client.make(session)
        await client.connect()

        is_authorized = await client.is_authorized()
        if not is_authorized:
            match auth_method:
                case AuthMethod.QR_CODE:
                    user = await self._authorize_qr_login(tg_user_id)
                case AuthMethod.PHONE:
                    pass
                case _:
                    pass
        else:
            user = await client.get_me()

        # Save new Telegram session for current user
        if user:
            session = client.get_session()
            await current_user.update(session=session)

        return user

    async def _send_success_msg(self, chat_id: int, username: str):
        req = SendTextRequest(
            chat_id=chat_id,
            text=f"{username}, authorized successful!",
        )
        await self._bot_grpc_client.stub.send_text(req)

    async def authorize_user(self, request, context):
        telegram_user: TelethonUser | None = None
        client = self._get_client(request.tg_user_id)
        is_authorized = await client.is_authorized()
        if not is_authorized:
            try:
                # TODO: handle unknown authorization method
                telegram_user = await self._authorize_user(
                    request.tg_user_id,
                    request.auth_method,
                )
            except SessionPasswordNeededError:
                # Handle case if you need to pass two factor password
                detail_msg = "Cannot authorize. Need pass two factory password."
                context.set_details(detail_msg)
                context.set_code(StatusCode.CANCELLED)

            if not telegram_user:
                detail_msg = "Cannot authorize. Try later."
                context.set_code(StatusCode.CANCELLED)
                context.set_details(detail_msg)
            else:
                await client.init()
                await self._send_success_msg(request.tg_user_id, telegram_user.username)
        else:
            detail_msg = "You are already logged in."
            context.set_code(StatusCode.ALREADY_EXISTS)
            context.set_details(detail_msg)

        return Empty()

    async def logout_user(self, request, context):
        client = self._get_client(request.tg_user_id)
        is_authorized = await client.is_authorized()
        if is_authorized:
            status = await client.log_out()

            if not status:
                detail_msg = "Something wrong with logout."
                context.set_code(StatusCode.CANCELLED)
                context.set_details(detail_msg)
        else:
            detail_msg = "You are not authorized."
            context.set_code(StatusCode.UNAUTHENTICATED)
            context.set_details(detail_msg)

        return Empty()
