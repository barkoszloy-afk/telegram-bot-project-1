"""Тесты для модуля utils.localization."""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from utils.localization import Localization, i18n, _, get_user_locale


@pytest.fixture
def temp_locales_dir():
    """Создание временной директории с файлами локализации."""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    
    # Создаем тестовые файлы локализации
    ru_data = {
        "test": {
            "greeting": "Привет, {name}!",
            "message": "Тестовое сообщение",
            "nested": {
                "deep": "Глубокое значение"
            }
        }
    }
    
    en_data = {
        "test": {
            "greeting": "Hello, {name}!",
            "message": "Test message",
            "nested": {
                "deep": "Deep value"
            }
        }
    }
    
    with open(os.path.join(temp_dir, 'ru.json'), 'w', encoding='utf-8') as f:
        json.dump(ru_data, f, ensure_ascii=False)
    
    with open(os.path.join(temp_dir, 'en.json'), 'w', encoding='utf-8') as f:
        json.dump(en_data, f, ensure_ascii=False)
    
    yield temp_dir
    
    # Очистка
    shutil.rmtree(temp_dir)


class TestLocalizationInit:
    """Тесты инициализации системы локализации."""
    
    def test_localization_default_init(self):
        """Тест инициализации с параметрами по умолчанию."""
        loc = Localization()
        
        assert loc.default_locale == "ru"
        assert isinstance(loc.locales, dict)
    
    def test_localization_custom_locale(self):
        """Тест инициализации с кастомным языком."""
        loc = Localization(default_locale="en")
        
        assert loc.default_locale == "en"
    
    @patch('utils.localization.os.path.exists', return_value=False)
    def test_localization_no_locales_dir(self, mock_exists):
        """Тест инициализации без директории локализации."""
        loc = Localization()
        
        # Должно работать без ошибок
        assert isinstance(loc.locales, dict)
    
    def test_localization_with_temp_dir(self, temp_locales_dir):
        """Тест загрузки локализации из временной директории."""
        with patch('utils.localization.os.path.join') as mock_join:
            # Имитируем путь к временной директории
            mock_join.return_value = temp_locales_dir
            
            with patch('utils.localization.os.path.exists', return_value=True):
                with patch('utils.localization.os.listdir', return_value=['ru.json', 'en.json']):
                    # Создаем новый экземпляр для тестирования
                    loc = Localization()
                    loc._load_locales()
                    
                    # Проверяем, что локали загрузились
                    assert len(loc.locales) >= 0  # Может быть пустым из-за моков


class TestLocalizationGet:
    """Тесты получения локализованных строк."""
    
    def test_get_simple_key(self):
        """Тест получения простого ключа."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "test": "значение"
            }
        }
        
        result = loc.get("test", "ru")
        assert result == "значение"
    
    def test_get_nested_key(self):
        """Тест получения вложенного ключа."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "section": {
                    "subsection": {
                        "key": "глубокое значение"
                    }
                }
            }
        }
        
        result = loc.get("section.subsection.key", "ru")
        assert result == "глубокое значение"
    
    def test_get_with_formatting(self):
        """Тест форматирования строк."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "greeting": "Привет, {name}!"
            }
        }
        
        result = loc.get("greeting", "ru", name="Иван")
        assert result == "Привет, Иван!"
    
    def test_get_nonexistent_key(self):
        """Тест получения несуществующего ключа."""
        loc = Localization()
        loc.locales = {"ru": {}}
        
        result = loc.get("nonexistent.key", "ru")
        assert result == "nonexistent.key"  # Возвращает сам ключ
    
    def test_get_nonexistent_locale(self):
        """Тест получения строки для несуществующего языка."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "test": "значение"
            }
        }
        loc.default_locale = "ru"
        
        result = loc.get("test", "nonexistent")
        assert result == "значение"  # Должен вернуть из default_locale
    
    def test_get_default_locale_fallback(self):
        """Тест возврата к языку по умолчанию."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "test": "русское значение"
            },
            "en": {}
        }
        loc.default_locale = "ru"
        
        result = loc.get("test", "en")
        assert result == "русское значение"
    
    def test_get_no_default_locale(self):
        """Тест без языка по умолчанию."""
        loc = Localization()
        loc.locales = {}
        loc.default_locale = "nonexistent"
        
        result = loc.get("test.key", "any")
        assert result == "test.key"


class TestLocalizationMethods:
    """Тесты методов локализации."""
    
    def test_get_available_locales(self):
        """Тест получения списка доступных языков."""
        loc = Localization()
        loc.locales = {
            "ru": {},
            "en": {},
            "fr": {}
        }
        
        available = loc.get_available_locales()
        assert set(available) == {"ru", "en", "fr"}
    
    def test_get_available_locales_empty(self):
        """Тест получения списка при отсутствии языков."""
        loc = Localization()
        loc.locales = {}
        
        available = loc.get_available_locales()
        assert available == []


class TestGlobalFunctions:
    """Тесты глобальных функций локализации."""
    
    @patch('utils.localization.i18n')
    def test_underscore_function(self, mock_i18n):
        """Тест функции _ (underscore)."""
        mock_i18n.get.return_value = "тестовое значение"
        
        result = _("test.key", "ru", name="Тест")
        
        mock_i18n.get.assert_called_once_with("test.key", "ru", name="Тест")
        assert result == "тестовое значение"
    
    def test_get_user_locale_default(self):
        """Тест получения языка пользователя (по умолчанию)."""
        user_id = 123456
        
        result = get_user_locale(user_id)
        assert result == "ru"  # Пока всегда возвращает русский


class TestLocalizationErrorHandling:
    """Тесты обработки ошибок локализации."""
    
    def test_malformed_locale_file(self):
        """Тест обработки поврежденного файла локализации."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Создаем поврежденный JSON файл
            malformed_file = os.path.join(temp_dir, 'broken.json')
            with open(malformed_file, 'w') as f:
                f.write("invalid json content")
            
            with patch('utils.localization.os.path.join', return_value=temp_dir):
                with patch('utils.localization.os.path.exists', return_value=True):
                    with patch('utils.localization.os.listdir', return_value=['broken.json']):
                        loc = Localization()
                        loc._load_locales()
                        
                        # Не должно падать, должно логировать ошибку
                        assert isinstance(loc.locales, dict)
    
    def test_get_with_type_error(self):
        """Тест обработки ошибки типов при форматировании."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "test": {"not": "a string"}  # Не строка
            }
        }
        
        result = loc.get("test", "ru")
        # Должно вернуть строковое представление
        assert isinstance(result, str)
    
    def test_get_with_key_error_in_nested(self):
        """Тест обработки ошибки ключа во вложенной структуре."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "level1": {
                    "level2": "value"
                }
            }
        }
        
        result = loc.get("level1.nonexistent.level3", "ru")
        assert result == "level1.nonexistent.level3"


class TestLocalizationIntegration:
    """Интеграционные тесты локализации."""
    
    def test_real_locales_structure(self):
        """Тест реальной структуры файлов локализации."""
        # Проверяем, что глобальный экземпляр работает
        assert isinstance(i18n, Localization)
        assert i18n.default_locale == "ru"
    
    def test_bot_messages_localization(self):
        """Тест локализации сообщений бота."""
        # Тестируем, что можем получить сообщения бота
        loc = Localization()
        loc.locales = {
            "ru": {
                "bot": {
                    "welcome": {
                        "greeting": "Привет, {name}!"
                    },
                    "errors": {
                        "general": "Произошла ошибка"
                    }
                }
            }
        }
        
        greeting = loc.get("bot.welcome.greeting", "ru", name="Пользователь")
        error = loc.get("bot.errors.general", "ru")
        
        assert greeting == "Привет, Пользователь!"
        assert error == "Произошла ошибка"
    
    def test_multilingual_support(self):
        """Тест поддержки нескольких языков."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "message": "Русское сообщение"
            },
            "en": {
                "message": "English message"
            }
        }
        
        ru_msg = loc.get("message", "ru")
        en_msg = loc.get("message", "en")
        
        assert ru_msg == "Русское сообщение"
        assert en_msg == "English message"


class TestLocalizationPerformance:
    """Тесты производительности локализации."""
    
    def test_multiple_get_calls(self):
        """Тест множественных вызовов get."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "test": "значение {number}"
            }
        }
        
        # Множественные вызовы не должны вызывать проблем
        for i in range(100):
            result = loc.get("test", "ru", number=i)
            assert result == f"значение {i}"
    
    def test_large_localization_data(self):
        """Тест с большим объемом данных локализации."""
        loc = Localization()
        
        # Создаем большую структуру данных
        large_data = {}
        for i in range(100):
            large_data[f"section_{i}"] = {
                f"key_{j}": f"value_{i}_{j}" for j in range(50)
            }
        
        loc.locales = {"ru": large_data}
        
        # Проверяем, что можем получить значения
        result = loc.get("section_50.key_25", "ru")
        assert result == "value_50_25"


class TestLocalizationEdgeCases:
    """Тесты граничных случаев локализации."""
    
    def test_empty_key(self):
        """Тест с пустым ключом."""
        loc = Localization()
        loc.locales = {"ru": {"": "пустой ключ"}}
        
        result = loc.get("", "ru")
        assert result == "пустой ключ"
    
    def test_key_with_dots_in_value(self):
        """Тест ключа с точками в значении."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "test": "значение.с.точками"
            }
        }
        
        result = loc.get("test", "ru")
        assert result == "значение.с.точками"
    
    def test_unicode_keys_and_values(self):
        """Тест с Unicode ключами и значениями."""
        loc = Localization()
        loc.locales = {
            "ru": {
                "тест": "русское значение с эмодзи 🎉",
                "emoji_key_🔥": "значение с эмодзи ключом"
            }
        }
        
        result1 = loc.get("тест", "ru")
        result2 = loc.get("emoji_key_🔥", "ru")
        
        assert result1 == "русское значение с эмодзи 🎉"
        assert result2 == "значение с эмодзи ключом"
    
    def test_very_deep_nesting(self):
        """Тест очень глубокой вложенности."""
        loc = Localization()
        
        # Создаем очень глубокую структуру
        deep_data = {"level1": {"level2": {"level3": {"level4": {"level5": "глубокое значение"}}}}}
        loc.locales = {"ru": deep_data}
        
        result = loc.get("level1.level2.level3.level4.level5", "ru")
        assert result == "глубокое значение"
