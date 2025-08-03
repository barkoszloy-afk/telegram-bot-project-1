"""Тесты для модуля handlers.reactions."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, Message, User, Chat
from telegram.ext import ContextTypes

from handlers.reactions import (
    handle_reaction_callback,
)


@pytest.fixture
def user():
    """Создание пользователя."""
    return User(
        id=123456789,
        first_name="TestUser",
        is_bot=False,
        username="test_user"
    )


@pytest.fixture
def channel_chat():
    """Создание канального чата."""
    return Chat(id=-100123456789, type=Chat.CHANNEL)


@pytest.fixture
def private_chat():
    """Создание приватного чата.""" 
    return Chat(id=123456789, type=Chat.PRIVATE)


@pytest.fixture
def channel_message(user, channel_chat):
    """Создание сообщения в канале."""
    return Message(
        message_id=100,
        date=datetime.now(),
        chat=channel_chat,
        from_user=user,
        text="Тестовое сообщение в канале"
    )


@pytest.fixture 
def context():
    """Создание контекста бота."""
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)


class TestReactionCallbacks:
    """Тесты для обработки реакций."""
    
    @pytest.mark.asyncio
    async def test_valid_reaction_callback(self, user, channel_message, context):
        """Тест валидной реакции."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_like_post123"
        callback_query.message = channel_message
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        with patch('handlers.reactions.reactions_db') as mock_db:
            with patch('handlers.reactions.REACTION_NAMES', ['like', 'love', 'fire']):
                with patch('handlers.reactions.REACTION_MESSAGES', 
                          {'like': ['Спасибо за лайк!']}):
                    
                    mock_db.add_user_reaction.return_value = None  # Новая реакция
                    
                    await handle_reaction_callback(update, context)
                    
                    # Проверяем, что реакция была добавлена
                    mock_db.add_user_reaction.assert_called_once_with(
                        str(user.id), 'like', 'post123'
                    )
                    callback_query.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_duplicate_reaction(self, user, channel_message, context):
        """Тест повторной реакции."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_love_post456"
        callback_query.message = channel_message
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        with patch('handlers.reactions.reactions_db') as mock_db:
            with patch('handlers.reactions.REACTION_NAMES', ['like', 'love', 'fire']):
                
                mock_db.add_user_reaction.return_value = 'love'  # Уже была реакция
                
                await handle_reaction_callback(update, context)
                
                # Проверяем сообщение о дублировании
                callback_query.answer.assert_called_once()
                call_args = callback_query.answer.call_args
                assert "уже поставили" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_invalid_reaction_format(self, user, context):
        """Тест неверного формата данных реакции."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "invalid_format"
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        # Функция должна просто вернуться без ошибок
        await handle_reaction_callback(update, context)
    
    @pytest.mark.asyncio
    async def test_unknown_reaction_type(self, user, channel_message, context):
        """Тест неизвестного типа реакции."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_unknown_post123"
        callback_query.message = channel_message
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        with patch('handlers.reactions.REACTION_NAMES', ['like', 'love', 'fire']):
            # Должна обработаться как неизвестная реакция
            await handle_reaction_callback(update, context)
    
    @pytest.mark.asyncio
    async def test_no_user_id(self, channel_message, context):
        """Тест реакции без пользователя."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_like_post123"
        callback_query.message = channel_message
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = None
        
        # Функция должна просто вернуться без ошибок
        await handle_reaction_callback(update, context)
    
    @pytest.mark.asyncio
    async def test_malformed_callback_data(self, user, context):
        """Тест некорректных данных callback."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_like"  # Отсутствует post_id
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        # Функция должна обработать ошибку без исключений
        await handle_reaction_callback(update, context)
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, user, channel_message, context):
        """Тест обработки ошибок базы данных."""
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_like_post123"
        callback_query.message = channel_message
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        with patch('handlers.reactions.reactions_db') as mock_db:
            with patch('handlers.reactions.REACTION_NAMES', ['like', 'love', 'fire']):
                
                # Симулируем ошибку базы данных
                mock_db.add_user_reaction.side_effect = Exception("DB Error")
                
                # Не должно вызывать необработанных исключений
                await handle_reaction_callback(update, context)


class TestReactionData:
    """Тесты для валидации данных реакций."""
    
    def test_reaction_names_exist(self):
        """Тест существования списка названий реакций."""
        from config import REACTION_NAMES
        
        assert isinstance(REACTION_NAMES, list), "REACTION_NAMES должен быть списком"
        assert len(REACTION_NAMES) > 0, "Список реакций не должен быть пустым"
        
        for reaction in REACTION_NAMES:
            assert isinstance(reaction, str), "Название реакции должно быть строкой"
            assert len(reaction) > 0, "Название реакции не должно быть пустым"
    
    def test_reaction_messages_exist(self):
        """Тест существования сообщений реакций."""
        from config import REACTION_MESSAGES
        
        assert isinstance(REACTION_MESSAGES, dict), "REACTION_MESSAGES должен быть словарем"
        assert len(REACTION_MESSAGES) > 0, "Словарь сообщений не должен быть пустым"
        
        for reaction, messages in REACTION_MESSAGES.items():
            assert isinstance(reaction, str), "Ключ должен быть строкой"
            assert isinstance(messages, list), "Значение должно быть списком"
            assert len(messages) > 0, f"Список сообщений для {reaction} не должен быть пустым"
            
            for message in messages:
                assert isinstance(message, str), "Сообщение должно быть строкой"
                assert len(message) > 0, "Сообщение не должно быть пустым"


class TestReactionIntegration:
    """Интеграционные тесты для реакций."""
    
    @pytest.mark.asyncio
    async def test_reaction_workflow_channel(self, user, context):
        """Тест полного workflow реакции в канале."""
        # Создаем сообщение в канале
        channel_chat = Chat(id=-100123456789, type=Chat.CHANNEL)
        channel_message = Message(
            message_id=100,
            date=datetime.now(),
            chat=channel_chat,
            from_user=user,
            text="Пост в канале"
        )
        
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_fire_daily_post_001"
        callback_query.message = channel_message
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        with patch('handlers.reactions.reactions_db') as mock_db:
            with patch('handlers.reactions.REACTION_NAMES', ['like', 'love', 'fire']):
                with patch('handlers.reactions.REACTION_MESSAGES', 
                          {'fire': ['Огонь! 🔥']}):
                    
                    mock_db.add_user_reaction.return_value = None
                    
                    await handle_reaction_callback(update, context)
                    
                    # Проверяем правильность обработки
                    mock_db.add_user_reaction.assert_called_once_with(
                        str(user.id), 'fire', 'daily_post_001'
                    )
                    callback_query.answer.assert_called_once()
    
    @pytest.mark.asyncio 
    async def test_reaction_workflow_private(self, user, context):
        """Тест workflow реакции в приватном чате."""
        private_chat = Chat(id=user.id, type=Chat.PRIVATE)
        private_message = Message(
            message_id=101,
            date=datetime.now(),
            chat=private_chat,
            from_user=user,
            text="Сообщение в личке"
        )
        
        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.data = "react_love_personal_message_42"
        callback_query.message = private_message
        callback_query.answer = AsyncMock()
        
        update = MagicMock(spec=Update)
        update.callback_query = callback_query
        update.effective_user = user
        
        with patch('handlers.reactions.reactions_db') as mock_db:
            with patch('handlers.reactions.REACTION_NAMES', ['like', 'love', 'fire']):
                with patch('handlers.reactions.REACTION_MESSAGES', 
                          {'love': ['Спасибо! ❤️']}):
                    
                    mock_db.add_user_reaction.return_value = None
                    
                    await handle_reaction_callback(update, context)
                    
                    # Проверяем обработку в приватном чате
                    mock_db.add_user_reaction.assert_called_once_with(
                        str(user.id), 'love', 'personal_message_42'
                    )
