import grpc
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from assistant.assistant_pb2 import SendLogoutRequest
from assistant.grpc_.client import AssistantAsyncGrpcClient
from bot.container import TelegramBotContainer
from bot.permissions import registered
from bot.templates import render_error
from core import models
from utils.python_telegram_bot.response import send_response


@registered
@inject
async def handle_logout_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    current_user: models.User,
    assistant_grpc_client: AssistantAsyncGrpcClient = Provide[
        TelegramBotContainer.assistant_grpc_client
    ],
):
    if not update.effective_user:
        return

    request = SendLogoutRequest(tg_user_id=update.effective_user.id)
    try:
        await assistant_grpc_client.stub.logout_user(request)
    except grpc.RpcError as err:
        status_code = err.code()
        detail_msg = err.details()
        match status_code:
            case grpc.StatusCode.UNAUTHENTICATED:
                await send_response(
                    update,
                    context,
                    render_error(detail_msg),
                )
            case _:
                logger.error(detail_msg)
                await send_response(
                    update,
                    context,
                    render_error("Something went wrong."),
                )
    else:
        await update.message.reply_text("You logged out.")  # type: ignore
