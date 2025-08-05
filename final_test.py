"""High level integration tests for the project.

The previous version of this file attempted to communicate with the
real Telegram API which makes automated testing unreliable.  The test
interacting with Telegram is now skipped by default while still
illustrating how such a check could be performed.  We also keep a simple
module import test to ensure that key parts of the project are
importable.
"""

import asyncio
import importlib

import pytest


@pytest.mark.skip(reason="Requires real Telegram credentials and network access")
def test_bot_functionality() -> None:
    """Placeholder test for interacting with Telegram's API."""
    from telegram import Bot
    from config import BOT_TOKEN, validate_config

    validate_config()
    if not BOT_TOKEN:
        pytest.fail("BOT_TOKEN not found")

    bot = Bot(token=BOT_TOKEN)
    bot_info = asyncio.get_event_loop().run_until_complete(bot.get_me())
    assert bot_info is not None
    asyncio.get_event_loop().run_until_complete(bot.get_my_commands())
    asyncio.get_event_loop().run_until_complete(bot.get_webhook_info())


def test_all_modules() -> None:
    """Ensure important project modules can be imported."""
    modules = [
        "config",
        "utils.keyboards",
        "utils.database",
        "handlers.admin",
        "handlers.reactions",
        "main_bot_railway",
    ]

    for module in modules:
        importlib.import_module(module)
