"""
Assistant entrypoint service.
"""
import asyncio
import logging

from assistant.container import AssistantContainer


async def main():
    assistant_container = AssistantContainer()
    assistant_container.wire(modules=[__name__])

    assistant_entrypoint = assistant_container.assistant_entrypoint()

    await assistant_entrypoint.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
