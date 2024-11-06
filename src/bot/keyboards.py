"""
Telegram Bot keyboards.
"""
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from . import callbacks


def get_auth_methods_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "QR Code", callback_data=callbacks.AUTH_METHODS_QR_CODE
                )
            ],
            [InlineKeyboardButton("Phone", callback_data=callbacks.AUTH_METHODS_PHONE)],
        ]
    )
