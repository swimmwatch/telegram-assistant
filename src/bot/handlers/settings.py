from dependency_injector.wiring import inject
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import Update
from telegram import WebAppInfo
from telegram.ext import ContextTypes

from bot.permissions import registered
from core import models
from infrastructure.bot.config import TelegramBotSettings


@registered
@inject
async def handle_settings_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    current_user: models.User,
) -> None:
    settings = TelegramBotSettings()
    web_app_info = WebAppInfo(url=settings.webapp_url)
    keyboard = [
        [
            InlineKeyboardButton("Open assistant settings", web_app=web_app_info),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = update.message
    if message:
        await message.reply_text(
            "Please press the button below to setup assistant settings via the WebApp.",
            reply_markup=reply_markup,
        )
