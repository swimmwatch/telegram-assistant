import functools
import typing

from telegram import Update
from telegram.ext import ContextTypes

from bot.dependencies import get_async_db
from bot.templates import render_template_
from core import models
from core.dal import UserAsyncDAL
from utils.python_telegram_bot.response import send_response

AuthorizedHandler = typing.Callable[
    [Update, ContextTypes.DEFAULT_TYPE, models.User], typing.Awaitable[None]
]


def registered(handler: AuthorizedHandler):
    """
    Authorized Telegram handler.
    """

    @functools.wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        if not telegram_user:
            return

        db = get_async_db()
        user_repo = UserAsyncDAL(db.session)
        current_user = await user_repo.filter(tg_id=telegram_user.id).first()

        if current_user:
            await handler(
                update,
                context,
                current_user,
            )
        else:
            await send_response(
                update,
                context,
                response=render_template_("errors/unregistered.html"),
            )

    return wrapped


def unregistered(handler: typing.Callable):
    @functools.wraps(handler)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return

        tg_user_id = update.effective_user.id

        db = get_async_db()
        user_repo = UserAsyncDAL(db.session)
        current_user = await user_repo.filter(tg_id=tg_user_id).first()

        if current_user:
            await send_response(
                update,
                context,
                response=render_template_("errors/already_registered.html"),
            )
        else:
            await handler(update, context)

    return wrapped
