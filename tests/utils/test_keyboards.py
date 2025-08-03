"""Тесты для модуля utils.keyboards."""

import pytest
from unittest.mock import patch
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from utils.keyboards import (
    create_main_menu_keyboard,
    get_main_menu_keyboard,
    remove_reply_keyboard,
)


class TestMainMenuKeyboard:
    """Тесты для главной клавиатуры меню."""
    
    def test_create_main_menu_keyboard_structure(self):
        """Тест структуры главной клавиатуры."""
        keyboard = create_main_menu_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3  # 3 ряда кнопок
        
        # Первый ряд: 2 кнопки
        assert len(keyboard.inline_keyboard[0]) == 2
        
        # Второй ряд: 2 кнопки  
        assert len(keyboard.inline_keyboard[1]) == 2
        
        # Третий ряд: 1 кнопка
        assert len(keyboard.inline_keyboard[2]) == 1
    
    def test_main_menu_keyboard_buttons(self):
        """Тест содержимого кнопок главного меню."""
        keyboard = create_main_menu_keyboard()
        
        # Собираем все кнопки в плоский список
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)
        
        assert len(all_buttons) == 5  # Всего 5 кнопок
        
        # Проверяем, что все кнопки имеют правильные callback_data
        callback_data = [button.callback_data for button in all_buttons]
        expected_callbacks = [
            "category_motivation",
            "category_esoteric", 
            "category_development",
            "category_health",
            "category_relationships"
        ]
        
        for expected in expected_callbacks:
            assert expected in callback_data
    
    def test_main_menu_keyboard_text_content(self):
        """Тест текстового содержимого кнопок."""
        keyboard = create_main_menu_keyboard()
        
        # Собираем весь текст кнопок
        button_texts = []
        for row in keyboard.inline_keyboard:
            for button in row:
                button_texts.append(button.text)
        
        # Проверяем наличие ключевых слов
        all_text = " ".join(button_texts)
        assert "Мотивация" in all_text
        assert "Эзотерика" in all_text
        assert "Развитие" in all_text
        assert "Здоровье" in all_text
        assert "Отношения" in all_text
    
    def test_get_main_menu_keyboard_compatibility(self):
        """Тест совместимости get_main_menu_keyboard с create_main_menu_keyboard."""
        keyboard1 = create_main_menu_keyboard()
        keyboard2 = get_main_menu_keyboard()
        
        # Оба должны возвращать InlineKeyboardMarkup
        assert isinstance(keyboard1, InlineKeyboardMarkup)
        assert isinstance(keyboard2, InlineKeyboardMarkup)
        
        # Структура должна быть похожей
        assert len(keyboard1.inline_keyboard) == len(keyboard2.inline_keyboard)


class TestRemoveReplyKeyboard:
    """Тесты для функции удаления reply клавиатуры."""
    
    def test_remove_reply_keyboard_returns_correct_type(self):
        """Тест возвращаемого типа."""
        result = remove_reply_keyboard()
        
        assert isinstance(result, ReplyKeyboardRemove)
        assert result.remove_keyboard is True


class TestKeyboardValidation:
    """Тесты для валидации клавиатур."""
    
    def test_keyboard_button_limits(self):
        """Тест ограничений Telegram на кнопки."""
        keyboard = create_main_menu_keyboard()
        
        # Проверяем, что не превышаем лимиты Telegram
        for row in keyboard.inline_keyboard:
            assert len(row) <= 8, "Слишком много кнопок в ряду"
            
            for button in row:
                assert len(button.text) <= 64, "Текст кнопки слишком длинный"
                # Безопасная проверка callback_data
                if button.callback_data is not None:
                    assert len(str(button.callback_data)) <= 64, "Callback_data слишком длинный"


class TestKeyboardEmojis:
    """Тесты для эмодзи в клавиатурах."""
    
    def test_main_menu_has_emojis(self):
        """Тест наличия эмодзи в главном меню."""
        keyboard = create_main_menu_keyboard()
        
        all_text = ""
        for row in keyboard.inline_keyboard:
            for button in row:
                all_text += button.text
        
        # Проверяем наличие различных эмодзи
        emoji_chars = ["💫", "🔮", "🎯", "🌟", "💝", "✨", "🎉", "❤️", "🔥"]
        has_emoji = any(emoji in all_text for emoji in emoji_chars)
        assert has_emoji, "В главном меню должны быть эмодзи"


class TestKeyboardIntegration:
    """Интеграционные тесты для клавиатур."""
    
    def test_keyboard_consistency(self):
        """Тест согласованности между различными клавиатурами."""
        main_keyboard1 = create_main_menu_keyboard()
        main_keyboard2 = get_main_menu_keyboard()
        
        # Проверяем, что все клавиатуры имеют корректную структуру
        keyboards = [main_keyboard1, main_keyboard2]
        
        for keyboard in keyboards:
            assert isinstance(keyboard, InlineKeyboardMarkup)
            assert len(keyboard.inline_keyboard) > 0
            
            for row in keyboard.inline_keyboard:
                assert len(row) > 0, "Пустой ряд кнопок"
                
                for button in row:
                    assert isinstance(button, InlineKeyboardButton)
                    assert button.text is not None
                    assert button.callback_data is not None


class TestKeyboardEdgeCases:
    """Тесты для граничных случаев клавиатур."""
    
    def test_keyboard_serialization(self):
        """Тест сериализации клавиатур."""
        keyboards = [
            create_main_menu_keyboard(),
            get_main_menu_keyboard()
        ]
        
        for keyboard in keyboards:
            # Проверяем, что клавиатура может быть сериализована в JSON
            try:
                keyboard_dict = keyboard.to_dict()
                assert isinstance(keyboard_dict, dict)
                assert "inline_keyboard" in keyboard_dict
            except Exception as e:
                pytest.fail(f"Ошибка сериализации клавиатуры: {e}")


class TestKeyboardAccessibility:
    """Тесты для доступности клавиатур."""
    
    def test_button_text_readability(self):
        """Тест читаемости текста кнопок."""
        keyboard = create_main_menu_keyboard()
        
        for row in keyboard.inline_keyboard:
            for button in row:
                # Проверяем, что текст содержит буквы (не только эмодзи)
                text_without_emoji = ''.join(char for char in button.text if char.isalpha())
                assert len(text_without_emoji.strip()) > 0, f"Кнопка '{button.text}' содержит только эмодзи"
                
                # Проверяем, что текст не слишком короткий
                assert len(button.text.strip()) >= 2, f"Слишком короткий текст кнопки: '{button.text}'"
    
    def test_callback_data_uniqueness(self):
        """Тест уникальности callback_data."""
        keyboards = [
            create_main_menu_keyboard(),
            get_main_menu_keyboard()
        ]
        
        for keyboard in keyboards:
            callback_data_list = []
            for row in keyboard.inline_keyboard:
                for button in row:
                    if button.callback_data is not None:
                        callback_data_list.append(str(button.callback_data))
            
            # Проверяем уникальность в рамках одной клавиатуры
            assert len(callback_data_list) == len(set(callback_data_list)), "Найдены дублирующиеся callback_data"


class TestKeyboardParameters:
    """Тесты для параметров клавиатур."""
    
    def test_main_menu_keyboard_parameters(self):
        """Тест параметров главной клавиатуры."""
        keyboard = create_main_menu_keyboard()
        
        # Проверяем базовые параметры
        assert hasattr(keyboard, 'inline_keyboard')
        assert isinstance(keyboard.inline_keyboard, (list, tuple))
        
        # Проверяем, что каждая кнопка имеет необходимые атрибуты
        for row in keyboard.inline_keyboard:
            for button in row:
                assert hasattr(button, 'text')
                assert hasattr(button, 'callback_data')
                assert button.text is not None
                assert button.callback_data is not None
    
    def test_remove_reply_keyboard_parameters(self):
        """Тест параметров ReplyKeyboardRemove."""
        keyboard_remove = remove_reply_keyboard()
        
        assert hasattr(keyboard_remove, 'remove_keyboard')
        assert keyboard_remove.remove_keyboard is True
        
        # Проверяем, что можно сериализовать
        remove_dict = keyboard_remove.to_dict()
        assert isinstance(remove_dict, dict)
        assert remove_dict.get('remove_keyboard') is True
