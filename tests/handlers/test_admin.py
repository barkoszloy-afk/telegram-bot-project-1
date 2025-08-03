"""Тесты для модуля handlers.admin."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, Message, User, Chat
from telegram.ext import ContextTypes

from handlers.admin import (
    handle_admin_command,
    handle_admin_callback,
    show_statistics,
    preview_morning_post,
    preview_horoscope_post,
    preview_evening_post,
    publish_post_to_channel,
)
from utils.exceptions import AccessDeniedException, PostingException


@pytest.fixture
def admin_user():
    """Создание пользователя-администратора."""
    return User(
        id=123456789,  # Должен совпадать с ADMIN_ID в конфиге
        first_name="Admin",
        is_bot=False,
        username="admin_user"
    )


@pytest.fixture
def regular_user():
    """Создание обычного пользователя."""
    return User(
        id=987654321,
        first_name="User",
        is_bot=False,
        username="regular_user"
    )


@pytest.fixture
def private_chat():
    """Создание приватного чата."""
    return Chat(id=-100123456789, type=Chat.PRIVATE)


@pytest.fixture
def admin_message(admin_user, private_chat):
    """Создание сообщения от администратора."""
    return Message(
        message_id=1,
        date=datetime.now(),
        chat=private_chat,
        from_user=admin_user,
        text="/admin"
    )


@pytest.fixture
def regular_message(regular_user, private_chat):
    """Создание сообщения от обычного пользователя."""
    return Message(
        message_id=2,
        date=datetime.now(),
        chat=private_chat,
        from_user=regular_user,
        text="/admin"
    )


@pytest.fixture
def admin_update(admin_user, admin_message):
    """Создание Update от администратора."""
    update = MagicMock(spec=Update)
    update.effective_user = admin_user
    update.message = admin_message
    update.callback_query = None
    return update


@pytest.fixture
def regular_update(regular_user, regular_message):
    """Создание Update от обычного пользователя."""
    update = MagicMock(spec=Update)
    update.effective_user = regular_user
    update.message = regular_message
    update.callback_query = None
    return update


@pytest.fixture
def admin_callback_update(admin_user):
    """Создание callback Update от администратора."""
    callback_query = MagicMock(spec=CallbackQuery)
    callback_query.data = "admin_stats"
    callback_query.answer = AsyncMock()
    callback_query.edit_message_text = AsyncMock()
    
    update = MagicMock(spec=Update)
    update.effective_user = admin_user
    update.callback_query = callback_query
    update.message = None
    return update


@pytest.fixture
def context():
    """Создание контекста бота."""
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)


class TestAdminCommands:
    """Тесты для админских команд."""
    
    @pytest.mark.asyncio
    async def test_admin_command_success(self, admin_update, context):
        """Тест успешного выполнения команды /admin администратором."""
        admin_update.message.reply_text = AsyncMock()
        
        with patch('handlers.admin.ADMIN_ID', 123456789):
            with patch('handlers.admin.create_admin_menu_keyboard') as mock_keyboard:
                mock_keyboard.return_value = MagicMock()
                
                await handle_admin_command(admin_update, context)
                
                admin_update.message.reply_text.assert_called_once()
                args = admin_update.message.reply_text.call_args
                assert "Админ-панель" in args[0][0]
    
    @pytest.mark.asyncio
    async def test_admin_command_access_denied(self, regular_update, context):
        """Тест отказа в доступе для обычного пользователя."""
        regular_update.message.reply_text = AsyncMock()
        
        with patch('handlers.admin.ADMIN_ID', 123456789):
            await handle_admin_command(regular_update, context)
            
            regular_update.message.reply_text.assert_called_once_with(
                "❌ У вас нет прав администратора"
            )
    
    @pytest.mark.asyncio
    async def test_admin_command_no_user(self, context):
        """Тест команды без пользователя."""
        update = MagicMock(spec=Update)
        update.effective_user = None
        update.message = MagicMock()
        
        # Не должно вызывать исключений
        await handle_admin_command(update, context)
    
    @pytest.mark.asyncio
    async def test_admin_command_no_message(self, admin_user, context):
        """Тест команды без сообщения."""
        update = MagicMock(spec=Update)
        update.effective_user = admin_user
        update.message = None
        
        # Не должно вызывать исключений
        await handle_admin_command(update, context)


class TestAdminCallbacks:
    """Тесты для callback-обработчиков админки."""
    
    @pytest.mark.asyncio
    async def test_admin_stats_callback(self, admin_callback_update, context):
        """Тест callback для статистики."""
        with patch('handlers.admin.ADMIN_ID', 123456789):
            with patch('handlers.admin.show_statistics') as mock_stats:
                mock_stats.return_value = AsyncMock()
                
                await handle_admin_callback(admin_callback_update, context)
                
                admin_callback_update.callback_query.answer.assert_called_once()
                mock_stats.assert_called_once_with(
                    admin_callback_update.callback_query, context
                )
    
    @pytest.mark.asyncio
    async def test_admin_callback_access_denied(self, regular_user, context):
        """Тест отказа в доступе в callback."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "admin_stats"
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.effective_user = regular_user
        update.callback_query = callback_query
        
        with patch('handlers.admin.ADMIN_ID', 123456789):
            await handle_admin_callback(update, context)
            
            callback_query.edit_message_text.assert_called_once_with(
                "❌ У вас нет прав администратора"
            )
    
    @pytest.mark.asyncio
    async def test_morning_post_callback(self, admin_user, context):
        """Тест callback для утреннего поста."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "admin_morning"
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.effective_user = admin_user
        update.callback_query = callback_query
        
        with patch('handlers.admin.ADMIN_ID', 123456789):
            with patch('handlers.admin.preview_morning_post') as mock_preview:
                await handle_admin_callback(update, context)
                
                mock_preview.assert_called_once_with(callback_query, context)


class TestStatistics:
    """Тесты для статистики."""
    
    @pytest.mark.asyncio
    async def test_show_statistics_with_data(self, context):
        """Тест показа статистики с данными."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = AsyncMock()
        
        mock_stats = {
            'total_users': 100,
            'total_posts': 50,
            'total_reactions': 250
        }
        
        with patch('handlers.admin.reactions_db') as mock_db:
            mock_db.get_stats.return_value = mock_stats
            
            await show_statistics(callback_query, context)
            
            callback_query.edit_message_text.assert_called_once()
            args = callback_query.edit_message_text.call_args[0][0]
            assert "100" in args  # total_users
            assert "50" in args   # total_posts
            assert "250" in args  # total_reactions
    
    @pytest.mark.asyncio 
    async def test_show_statistics_no_data(self, context):
        """Тест показа статистики без данных."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = AsyncMock()
        
        with patch('handlers.admin.reactions_db') as mock_db:
            mock_db.get_stats.return_value = {}
            
            await show_statistics(callback_query, context)
            
            callback_query.edit_message_text.assert_called_once()
            args = callback_query.edit_message_text.call_args[0][0]
            assert "Нет данных" in args


class TestPostPreviews:
    """Тесты для предпросмотра постов."""
    
    @pytest.mark.asyncio
    async def test_preview_morning_post(self, context):
        """Тест предпросмотра утреннего поста."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = AsyncMock()
        
        with patch('handlers.admin.create_admin_post_keyboard') as mock_keyboard:
            with patch('random.choice') as mock_choice:
                mock_choice.return_value = "Тестовое утреннее сообщение"
                mock_keyboard.return_value = MagicMock()
                
                await preview_morning_post(callback_query, context)
                
                callback_query.edit_message_text.assert_called_once()
                args = callback_query.edit_message_text.call_args
                assert "Предпросмотр утреннего поста" in args[0][0]
                assert "Тестовое утреннее сообщение" in args[0][0]
    
    @pytest.mark.asyncio
    async def test_preview_horoscope_post(self, context):
        """Тест предпросмотра гороскопа."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = AsyncMock()
        
        with patch('handlers.admin.create_admin_post_keyboard') as mock_keyboard:
            with patch('handlers.admin.ZODIAC_MESSAGES', ["Тест гороскоп"]):
                mock_keyboard.return_value = MagicMock()
                
                await preview_horoscope_post(callback_query, context)
                
                callback_query.edit_message_text.assert_called_once()
                args = callback_query.edit_message_text.call_args
                assert "Предпросмотр гороскопа" in args[0][0]


class TestPostSending:
    """Тесты для отправки постов."""
    
    @pytest.mark.asyncio
    async def test_publish_post_success(self, context):
        """Тест успешной публикации поста."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = AsyncMock()
        
        with patch('handlers.admin.context.bot') as mock_bot:
            mock_bot.send_message = AsyncMock()
            with patch('handlers.admin.CHANNEL_ID', -100123456789):
                with patch('random.choice') as mock_choice:
                    mock_choice.return_value = "Утренний пост"
                    
                    await publish_post_to_channel(callback_query, context)
                    
                    callback_query.edit_message_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_publish_post_failure(self, context):
        """Тест ошибки при публикации поста."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = AsyncMock()
        
        with patch('handlers.admin.context.bot') as mock_bot:
            mock_bot.send_message = AsyncMock(side_effect=Exception("Network error"))
            with patch('handlers.admin.CHANNEL_ID', -100123456789):
                
                await publish_post_to_channel(callback_query, context)
                
                # Должно показать ошибку
                callback_query.edit_message_text.assert_called()
                args = callback_query.edit_message_text.call_args[0][0]
                assert "Ошибка" in args


class TestPostValidation:
    """Тесты для валидации постов."""
    
    def test_zodiac_post_content(self):
        """Тест валидности контента гороскопов."""
        from config import ZODIAC_MESSAGES
        
        assert len(ZODIAC_MESSAGES) > 0, "Список гороскопов не должен быть пустым"
        
        for message in ZODIAC_MESSAGES:
            assert isinstance(message, str), "Гороскоп должен быть строкой"
            assert len(message) > 0, "Гороскоп не должен быть пустым"
            assert len(message) <= 4096, "Гороскоп не должен превышать лимит Telegram"
    
    def test_evening_post_content(self):
        """Тест валидности контента вечерних постов."""
        from config import EVENING_MESSAGES
        
        assert len(EVENING_MESSAGES) > 0, "Список вечерних сообщений не должен быть пустым"
        
        for message in EVENING_MESSAGES:
            assert isinstance(message, str), "Сообщение должно быть строкой"
            assert len(message) > 0, "Сообщение не должно быть пустым"
            assert len(message) <= 4096, "Сообщение не должно превышать лимит Telegram"
