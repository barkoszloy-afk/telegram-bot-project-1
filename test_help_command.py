import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

import main_bot_railway


@pytest.mark.asyncio
async def test_help_command_sends_help_text(monkeypatch):
    """help_command should reply with help information."""
    monkeypatch.setattr(main_bot_railway, "update_stats", lambda *a, **k: None)

    mock_reply = AsyncMock()
    message = SimpleNamespace(reply_text=mock_reply)
    user = SimpleNamespace(id=1)
    update = SimpleNamespace(message=message, effective_user=user)
    context = SimpleNamespace()

    await main_bot_railway.help_command(update, context)

    mock_reply.assert_awaited_once()
    sent_text = mock_reply.call_args[0][0]
    assert "Справка по боту" in sent_text
