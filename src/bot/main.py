"""
Assistant manager entrypoint.
"""
from bot.container import TelegramBotContainer
from bot.entrypoint import TelegramBotEntrypoint
from infrastructure.bot.config import TelegramBotSettings


def main():
    container = TelegramBotContainer()
    container.wire(
        modules=[__name__],
        packages=["services.bot.handlers"],
    )
    telegram_bot_settings = TelegramBotSettings()

    telegram_bot_entrypoint = TelegramBotEntrypoint(
        telegram_bot_settings.grpc_addr,
        telegram_bot_settings.token.get_secret_value(),
    )
    telegram_bot_entrypoint.run()


if __name__ == "__main__":
    main()
