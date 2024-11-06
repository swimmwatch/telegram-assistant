import grpc
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from assistant.assistant_pb2 import AuthMethod
from assistant.assistant_pb2 import SendAuthorizationRequest
from assistant.assistant_pb2 import SendCheckAuthorizationRequest
from assistant.grpc_.client import AssistantAsyncGrpcClient
from bot.container import TelegramBotContainer
from bot.keyboards import get_auth_methods_keyboard
from bot.permissions import registered
from bot.templates import render_error
from core import models
from utils.python_telegram_bot.response import send_response


@registered
@inject
async def handle_login_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    current_user: models.User,
    assistant_grpc_client: AssistantAsyncGrpcClient = Provide[
        TelegramBotContainer.assistant_grpc_client
    ],
):
    if not update.effective_user:
        return

    request = SendCheckAuthorizationRequest(tg_user_id=update.effective_user.id)
    response = await assistant_grpc_client.stub.is_authorized(request)
    is_authorized = response.value
    if is_authorized:
        await send_response(
            update,
            context,
            render_error("You are authorized."),
        )
        return

    await send_response(
        update,
        context,
        "Choose authorization method:",
        keyboard=get_auth_methods_keyboard(),
    )


@registered
@inject
async def auth_method_qr_code_cb(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    current_user: models.User,
    assistant_grpc_client: AssistantAsyncGrpcClient = Provide[
        TelegramBotContainer.assistant_grpc_client
    ],
):
    user = update.effective_user
    if not user:
        return

    query = update.callback_query
    if not query:
        return

    await query.edit_message_text("Authorizing using QR code method...")

    request = SendAuthorizationRequest(
        tg_user_id=user.id,
        auth_method=AuthMethod.QR_CODE,
    )
    try:
        await assistant_grpc_client.stub.authorize_user(request)
    except grpc.RpcError as err:
        status_code = err.code()
        detail_msg = err.details()
        match status_code:
            case (grpc.StatusCode.ALREADY_EXISTS, grpc.StatusCode.CANCELLED):
                await query.edit_message_text(detail_msg)
            case _:
                logger.error(detail_msg)
                await query.edit_message_text("Something went wrong. Try later.")


@registered
@inject
async def auth_method_phone_cb(
    update: Update,
    _: ContextTypes.DEFAULT_TYPE,
    assistant_grpc_client: AssistantAsyncGrpcClient = Provide[
        TelegramBotContainer.assistant_grpc_client
    ],
):
    user = update.effective_user
    if not user:
        return

    query = update.callback_query
    if not query:
        return

    await query.edit_message_text("Authorizing using phone method...")

    request = SendAuthorizationRequest(
        tg_user_id=user.id,
        auth_method=AuthMethod.PHONE,
    )
    try:
        await assistant_grpc_client.stub.authorize_user(request)
    except grpc.RpcError as err:
        status_code = err.code()
        detail_msg = err.details()
        match status_code:
            case grpc.StatusCode.ALREADY_EXISTS:
                await query.edit_message_text(detail_msg)
            case _:
                logger.error(detail_msg)
                await query.edit_message_text("Something went wrong. Try later.")
