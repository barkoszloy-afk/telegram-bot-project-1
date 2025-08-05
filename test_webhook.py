"""Tests related to webhook availability for python-telegram-bot."""

from telegram.ext._updater import WEBHOOKS_AVAILABLE


def test_webhook_extras_installed() -> None:
    """Ensure that the python-telegram-bot webhooks extras are installed."""
    assert WEBHOOKS_AVAILABLE, (
        "python-telegram-bot[webhooks] must be installed in production environments"
    )
