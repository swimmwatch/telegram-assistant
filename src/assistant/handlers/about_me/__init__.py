"""
"About me" command handler.
"""
from assistant.commands.handler import ExplicitCommand
from assistant.commands.request import CommandRequest
from assistant.commands.types import ParsedArguments
from assistant.handlers.about_me.models import GameScopeValues
from assistant.handlers.about_me.models import TypeProfiles
from assistant.handlers.about_me.models import WorkScopeValues
from assistant.handlers.about_me.models import game_info_dict
from assistant.handlers.about_me.models import work_info_dict
from assistant.templates import render_template_

about_me_command = (
    ExplicitCommand(name="me")
    .add_arg(name="type", cls=TypeProfiles)
    .add_arg(name="scope", cls=str)
)


@about_me_command.on(lambda args: args["type"] is TypeProfiles.WORK)
async def handle_output_work_profile(args: ParsedArguments, request: CommandRequest):
    scope_value = None
    if args["scope"]:
        scope_value = WorkScopeValues(args["scope"])
        exist_item = scope_value in work_info_dict

        if not exist_item:
            # TODO: handle error through Telegram bot
            return

    data = {
        "title": "My business card",
        "data": work_info_dict,
        "scope": scope_value,
    }
    message = render_template_("card.html", data)
    await request.event.client.send_message(
        request.event.message.chat_id, message, parse_mode="html", silent=True
    )


@about_me_command.on(lambda args: args["type"] is TypeProfiles.GAME)
async def handle_output_game_profile(args: ParsedArguments, request: CommandRequest):
    scope_value = None
    if args["scope"]:
        scope_value = GameScopeValues(args["scope"])
        exist_item = scope_value in game_info_dict

        if not exist_item:
            # TODO: handle error through Telegram bot
            return

    data = {
        "title": "\N{VIDEO GAME} My game profiles \N{VIDEO GAME}",
        "data": game_info_dict,
        "scope": scope_value,
    }
    message = render_template_("card.html", data)
    await request.event.client.send_message(
        request.event.message.chat_id, message, parse_mode="html", silent=True
    )
