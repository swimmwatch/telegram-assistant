"""
Telegram template utilities.
"""
import re
import typing
from pathlib import Path

import emoji
import jinja2


def render_template(
    template_dir: Path,
    template_name: str,
    data: dict[str, typing.Any] | None = None,
) -> str:
    if data is None:
        data = {}
    template = _get_template_env(template_dir).get_template(template_name)
    rendered = template.render(**data).replace("\n", " ")
    rendered = rendered.replace("<br>", "\n")
    rendered = re.sub(" +", " ", rendered).replace(" .", ".").replace(" ,", ",")
    rendered = "\n".join(line.strip() for line in rendered.split("\n"))
    rendered = rendered.replace("{FOURPACES}", "    ")
    rendered = emoji.emojize(rendered)
    return rendered


def _get_template_env(telegram_dir: Path):
    if not getattr(_get_template_env, "template_env", None):
        template_loader = jinja2.FileSystemLoader(searchpath=telegram_dir)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )
        _get_template_env.template_env = env  # type: ignore

    return _get_template_env.template_env  # type: ignore
