import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

import main_bot_railway


@pytest.mark.asyncio
async def test_start_command_shows_main_menu(monkeypatch):
    """start_command should call show_main_menu for valid updates."""
    mock_show_main_menu = AsyncMock()
    monkeypatch.setattr(main_bot_railway, "show_main_menu", mock_show_main_menu)
    monkeypatch.setattr(main_bot_railway, "update_stats", lambda *a, **k: None)

    user = SimpleNamespace(id=1, first_name="Tester", username="tester")
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message, effective_user=user)
    context = SimpleNamespace()

    await main_bot_railway.start_command(update, context)

    mock_show_main_menu.assert_awaited_once_with(update, context)
