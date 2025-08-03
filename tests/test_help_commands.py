"""Тесты для команд help и instructions."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from main_bot_railway import help_command, instructions_command, setup_bot_commands


class TestHelpCommand:
    """Тесты для команды /help."""
    
    @pytest.mark.asyncio
    async def test_help_command_success(self):
        """Тест успешного выполнения команды /help."""
        # Создаем мок объекты
        update = MagicMock()
        context = MagicMock()
        message = MagicMock()
        user = MagicMock()
        
        # Настраиваем мок объекты
        update.effective_user = user
        user.id = 12345
        update.message = message
        message.reply_text = AsyncMock()
        
        # Выполняем команду
        await help_command(update, context)
        
        # Проверяем, что ответ был отправлен
        message.reply_text.assert_called_once()
        call_args = message.reply_text.call_args[0][0]
        
        # Проверяем содержание справки
        assert "🤖 Справка по боту" in call_args
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/instructions" in call_args
    
    @pytest.mark.asyncio
    async def test_help_command_no_message(self):
        """Тест команды /help без message объекта."""
        update = MagicMock()
        context = MagicMock()
        user = MagicMock()
        
        update.effective_user = user
        user.id = 12345
        update.message = None  # Нет message
        
        # Должно завершиться без ошибок
        await help_command(update, context)


class TestInstructionsCommand:
    """Тесты для команды /instructions."""
    
    @pytest.mark.asyncio
    async def test_instructions_command_success(self):
        """Тест успешного выполнения команды /instructions."""
        # Создаем мок объекты
        update = MagicMock()
        context = MagicMock()
        message = MagicMock()
        user = MagicMock()
        
        # Настраиваем мок объекты
        update.effective_user = user
        user.id = 12345
        update.message = message
        message.reply_text = AsyncMock()
        
        # Выполняем команду
        await instructions_command(update, context)
        
        # Проверяем, что ответ был отправлен
        message.reply_text.assert_called_once()
        call_args = message.reply_text.call_args[0][0]
        
        # Проверяем содержание инструкций
        assert "📚 Подробные инструкции" in call_args
        assert "🚀 Начало работы" in call_args
        assert "🎯 Категории" in call_args
        assert "💫 Мотивация" in call_args
        assert "🔮 Эзотерика" in call_args
    
    @pytest.mark.asyncio
    async def test_instructions_command_no_message(self):
        """Тест команды /instructions без message объекта."""
        update = MagicMock()
        context = MagicMock()
        user = MagicMock()
        
        update.effective_user = user
        user.id = 12345
        update.message = None  # Нет message
        
        # Должно завершиться без ошибок
        await instructions_command(update, context)


class TestSetupBotCommands:
    """Тесты для установки команд бота."""
    
    @pytest.mark.asyncio
    async def test_setup_bot_commands_success(self):
        """Тест успешной установки команд."""
        # Создаем мок application
        application = MagicMock()
        bot = MagicMock()
        application.bot = bot
        bot.set_my_commands = AsyncMock()
        bot.get_my_commands = AsyncMock()
        
        # Мок команд для get_my_commands
        mock_command = MagicMock()
        mock_command.command = "start"
        mock_command.description = "Главное меню с категориями"
        bot.get_my_commands.return_value = [mock_command]
        
        # Выполняем установку команд
        await setup_bot_commands(application)
        
        # Проверяем, что set_my_commands был вызван
        bot.set_my_commands.assert_called_once()
        call_args = bot.set_my_commands.call_args[0][0]
        
        # Проверяем, что переданы правильные команды
        assert len(call_args) == 3
        commands = {cmd.command: cmd.description for cmd in call_args}
        assert "start" in commands
        assert "help" in commands
        assert "instructions" in commands
    
    @pytest.mark.asyncio
    async def test_setup_bot_commands_error(self):
        """Тест обработки ошибок при установке команд."""
        # Создаем мок application с ошибкой
        application = MagicMock()
        bot = MagicMock()
        application.bot = bot
        bot.set_my_commands = AsyncMock(side_effect=Exception("API Error"))
        
        # Должно завершиться без исключений (ошибка логируется)
        await setup_bot_commands(application)
        
        # Проверяем, что set_my_commands был вызван
        bot.set_my_commands.assert_called_once()


class TestCommandsIntegration:
    """Интеграционные тесты команд."""
    
    @pytest.mark.asyncio
    async def test_all_commands_have_different_content(self):
        """Тест, что команды возвращают разный контент."""
        # Мок объекты
        update = MagicMock()
        context = MagicMock()
        message = MagicMock()
        user = MagicMock()
        
        update.effective_user = user
        user.id = 12345
        update.message = message
        message.reply_text = AsyncMock()
        
        # Тестируем help
        await help_command(update, context)
        help_content = message.reply_text.call_args[0][0]
        
        # Сбрасываем мок
        message.reply_text.reset_mock()
        
        # Тестируем instructions
        await instructions_command(update, context)
        instructions_content = message.reply_text.call_args[0][0]
        
        # Проверяем, что контент разный
        assert help_content != instructions_content
        assert "Справка" in help_content
        assert "инструкции" in instructions_content
        
        # Проверяем уникальные элементы
        assert "Быстрый старт" in help_content
        assert "Начало работы" in instructions_content
