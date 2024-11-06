from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.container import TelegramBotContainer
from bot.permissions import unregistered
from bot.templates import render_template_
from core.dal.dal import UserAsyncDAL


@unregistered
@inject
async def handle_start(
    update: Update,
    _: ContextTypes.DEFAULT_TYPE,
    user_repo: UserAsyncDAL = Provide[TelegramBotContainer.user_repo],
):
    if not update.effective_user:
        return

    if not update.message:
        return

    await user_repo.create_one(tg_id=update.effective_user.id)

    message = render_template_("hello.html", {"user": update.effective_user})
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)
