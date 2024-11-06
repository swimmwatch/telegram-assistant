"""
Hello command handler.
"""
from assistant.commands.handler import ExplicitCommand
from assistant.commands.request import CommandRequest
from assistant.commands.types import ParsedArguments
from assistant.templates import render_template_

hello_command = ExplicitCommand(name="hello")


@hello_command.on()
async def handle_welcome_output(_: ParsedArguments, request: CommandRequest):
    project_link = "https://github.com/swimmwatch/my-telegram-assistant"
    message = render_template_("hello.html", {"project_link": project_link})
    await request.event.client.send_message(
        request.event.message.chat_id, message, parse_mode="html"
    )
