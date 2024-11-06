"""
Python Telegram Bot response utilities.
"""
import typing

from telegram import Chat
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from utils.python_telegram_bot.types import KeyboardType


async def send_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: KeyboardType | None = None,
) -> None:
    """
    Send text response.

    :param update: Update from Telegram Bot API
    :param context: Context from Python Telegram Bot
    :param response: Message content
    :param keyboard: Telegram Bot keyboard
    """
    await context.bot.send_message(
        chat_id=_get_chat_id(update),
        disable_web_page_preview=True,
        text=response,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


def _get_chat_id(update: Update) -> int:
    """
    Extract chat ID from Telegram Bot API update.

    :param update: Update from Telegram Bot API
    :return: Chat ID
    """
    return typing.cast(Chat, update.effective_chat).id
