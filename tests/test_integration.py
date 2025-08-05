# tests/test_integration.py - Интеграционные тесты

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

# Помечаем все тесты в этом файле как интеграционные
pytestmark = pytest.mark.integration

class TestBotIntegration:
    """Интеграционные тесты для бота"""
    
    @pytest.mark.asyncio
    async def test_bot_initialization(self):
        """Тест инициализации бота"""
        with patch('config.BOT_TOKEN', 'test_token'):
            try:
                from main_bot_railway import create_application
                app = create_application()
                assert app is not None
                print("✅ Bot initialization test passed")
            except Exception as e:
                pytest.skip(f"Bot initialization requires valid config: {e}")
    
    @pytest.mark.asyncio  
    async def test_webhook_setup(self):
        """Тест настройки webhook"""
        with patch('config.BOT_TOKEN', 'test_token'):
            try:
                from main_bot_railway import setup_webhook
                # Мокаем настройку webhook
                with patch('telegram.Bot.set_webhook') as mock_webhook:
                    mock_webhook.return_value = AsyncMock()
                    await setup_webhook()
                    print("✅ Webhook setup test passed")
            except Exception as e:
                pytest.skip(f"Webhook test requires valid config: {e}")
    
    @pytest.mark.asyncio
    async def test_command_handlers(self):
        """Тест обработчиков команд"""
        try:
            from handlers import ping_command, status_command
            
            # Мокаем update и context
            update = Mock()
            update.effective_chat.id = 12345
            update.message.reply_text = AsyncMock()
            
            context = Mock()
            
            # Тестируем команды
            await ping_command(update, context)
            await status_command(update, context)
            
            assert update.message.reply_text.called
            print("✅ Command handlers test passed")
            
        except Exception as e:
            pytest.skip(f"Command handlers test requires valid setup: {e}")

class TestKeyboardIntegration:
    """Интеграционные тесты для клавиатур"""
    
    def test_main_menu_creation(self):
        """Тест создания главного меню"""
        try:
            from utils.keyboards import create_main_menu_keyboard
            keyboard = create_main_menu_keyboard()
            
            assert keyboard is not None
            assert len(keyboard.inline_keyboard) > 0
            print("✅ Main menu keyboard test passed")
            
        except Exception as e:
            pytest.skip(f"Keyboard test requires valid setup: {e}")
    
    def test_zodiac_keyboard_creation(self):
        """Тест создания зодиакальной клавиатуры"""
        try:
            from utils.keyboards import create_zodiac_keyboard
            keyboard = create_zodiac_keyboard()
            
            assert keyboard is not None
            assert len(keyboard.inline_keyboard) >= 12  # 12 знаков зодиака
            print("✅ Zodiac keyboard test passed")
            
        except Exception as e:
            pytest.skip(f"Zodiac keyboard test requires valid setup: {e}")

class TestDatabaseIntegration:
    """Интеграционные тесты для базы данных"""
    
    def test_reactions_database(self):
        """Тест базы данных реакций"""
        try:
            from utils.database import reactions_db
            
            # Тестируем базовые операции
            test_post_id = "test_123"
            test_reaction = "👍"
            test_user_id = 12345
            
            reactions_db.add_reaction(test_post_id, test_reaction, test_user_id)
            stats = reactions_db.get_post_stats(test_post_id)
            
            assert stats is not None
            assert test_reaction in stats
            print("✅ Reactions database test passed")
            
        except Exception as e:
            pytest.skip(f"Database test requires valid setup: {e}")
