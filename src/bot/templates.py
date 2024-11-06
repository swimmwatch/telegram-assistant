"""
Assistant service template utilities.
"""
import typing

from infrastructure.bot.config import TelegramBotSettings
from utils.telegram.templates import render_template


def render_template_(template_name: str, data: dict[str, typing.Any] | None = None) -> str:
    settings = TelegramBotSettings()
    return render_template(settings.template_dir, template_name, data)


def render_error(message: str) -> str:
    return render_template_("errors/inline.html", {"content": message})
