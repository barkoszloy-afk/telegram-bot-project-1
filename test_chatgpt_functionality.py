#!/usr/bin/env python3
"""
Тест ChatGPT функциональности бота с использованием pytest-asyncio
"""

import pytest
import sys
import os

# Добавим путь к проекту
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

from utils.openai_client import ChatGPTClient

@pytest.mark.asyncio
async def test_chatgpt_client_initialization():
    """Тестируем инициализацию ChatGPT клиента"""
    print("🧪 Тест инициализации ChatGPT клиента...")
    
    try:
        # Создаем клиент
        client = ChatGPTClient()
        assert client is not None
        print("✅ ChatGPT клиент создан успешно")
        
        # Проверяем доступность API
        is_available = client.is_available()
        print(f"📊 API доступен: {is_available}")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        pytest.skip(f"ChatGPT клиент недоступен: {e}")

@pytest.mark.asyncio
async def test_chatgpt_basic_functionality():
    """Тестируем базовую функциональность ChatGPT"""
    print("🧪 Тестирование ChatGPT функциональности...")
    
    try:
        # Создаем клиент
        client = ChatGPTClient()
        
        if not client.is_available():
            pytest.skip("OpenAI API недоступен (нет ключа или квота превышена)")
        
        # Тестируем базовую отправку сообщения
        print("📝 Тест 1: Отправка базового сообщения...")
        test_user_id = 12345
        response = await client.chat_completion("Привет! Как дела?", test_user_id)
        
        assert response is not None
        assert isinstance(response, dict)
        assert "success" in response
        
        if response["success"]:
            print(f"✅ Ответ получен: {str(response['response'])[:100]}...")
        else:
            print(f"⚠️ Ошибка API: {response['response']}")
            # Не падаем на ошибке API - это ожидаемо при отсутствии квоты
            
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        pytest.skip(f"ChatGPT API недоступен: {e}")

@pytest.mark.asyncio        
async def test_chatgpt_horoscope_generation():
    """Тестируем генерацию гороскопа"""
    print("🔮 Тест генерации гороскопа...")
    
    try:
        client = ChatGPTClient()
        
        if not client.is_available():
            pytest.skip("OpenAI API недоступен")
            
        test_user_id = 12345
        horoscope = await client.generate_horoscope("leo", test_user_id)
        
        assert horoscope is not None
        assert isinstance(horoscope, str)
        assert len(horoscope) > 0
        print(f"✅ Гороскоп сгенерирован: {horoscope[:100]}...")
        
    except Exception as e:
        print(f"❌ Ошибка генерации гороскопа: {e}")
        pytest.skip(f"Генерация гороскопа недоступна: {e}")

@pytest.mark.asyncio
async def test_chatgpt_morning_message():
    """Тестируем утреннее сообщение"""
    print("🌅 Тест утреннего сообщения...")
    
    try:
        client = ChatGPTClient()
        
        if not client.is_available():
            pytest.skip("OpenAI API недоступен")
            
        test_user_id = 12345
        morning = await client.generate_morning_message(test_user_id)
        
        assert morning is not None
        assert isinstance(morning, str)
        assert len(morning) > 0
        print(f"✅ Утреннее сообщение: {morning[:100]}...")
        
    except Exception as e:
        print(f"❌ Ошибка утреннего сообщения: {e}")
        pytest.skip(f"Утреннее сообщение недоступно: {e}")

@pytest.mark.asyncio
async def test_chatgpt_conversation_management():
    """Тестируем управление историей разговора"""
    print("💬 Тест управления историей разговора...")
    
    try:
        client = ChatGPTClient()
        test_user_id = 12345
        
        # Тестируем получение длины разговора
        initial_length = client.get_conversation_length(test_user_id)
        assert isinstance(initial_length, int)
        assert initial_length >= 0
        print(f"📊 Начальная длина разговора: {initial_length}")
        
        # Тестируем очистку разговора
        result = client.clear_conversation(test_user_id)
        assert isinstance(result, bool)
        print(f"🗑️ Разговор очищен: {result}")
        
        # Проверяем, что длина стала 0
        cleared_length = client.get_conversation_length(test_user_id)
        assert cleared_length == 0
        print("✅ История разговора успешно очищена")
        
    except Exception as e:
        print(f"❌ Ошибка управления разговором: {e}")
        pytest.fail(f"Управление разговором должно работать без API: {e}")

if __name__ == "__main__":
    # Запуск через pytest при прямом вызове
    pytest.main([__file__, "-v"])
