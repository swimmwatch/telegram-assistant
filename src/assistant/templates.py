"""
Assistant service template utilities.
"""
import typing

from infrastructure.assistant.config import AssistantSettings
from utils.telegram.templates import render_template


def render_template_(template_name: str, data: dict[str, typing.Any] | None = None) -> str:
    settings = AssistantSettings()
    return render_template(settings.template_dir, template_name, data)


def render_error(content: str) -> str:
    return render_template_("error/inline.html", {"content": content})
