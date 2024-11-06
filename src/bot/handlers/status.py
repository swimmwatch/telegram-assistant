from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from telegram import Update
from telegram.ext import ContextTypes

from assistant.assistant_pb2 import SendCheckAuthorizationRequest
from assistant.grpc_.client import AssistantAsyncGrpcClient
from bot.container import TelegramBotContainer
from bot.permissions import registered
from core import models


@registered
@inject
async def handle_status_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    current_user: models.User,
    assistant_grpc_client: AssistantAsyncGrpcClient = Provide[
        TelegramBotContainer.assistant_grpc_client
    ],
) -> None:
    if not update.effective_user:
        return

    request = SendCheckAuthorizationRequest(tg_user_id=update.effective_user.id)
    response = await assistant_grpc_client.stub.is_authorized(request)
    is_authorized = response.value
    if is_authorized:
        await update.message.reply_text("You are authorized.")  # type: ignore
    else:
        await update.message.reply_text("You are not authorized.")  # type: ignore
