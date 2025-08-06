#!/usr/bin/env python3
"""
Тест ChatGPT функциональности бота
"""

import asyncio
import sys
import os

# Добавим путь к проекту
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

from utils.openai_client import ChatGPTClient

async def test_chatgpt_functionality():
    """Тестируем функциональность ChatGPT"""
    print("🧪 Тестирование ChatGPT функциональности...")
    
    try:
        # Создаем клиент
        client = ChatGPTClient()
        
        # Тестируем базовую отправку сообщения
        print("📝 Тест 1: Отправка базового сообщения...")
        test_user_id = 12345
        response = await client.chat_completion("Привет! Как дела?", test_user_id)
        
        if response:
            print(f"✅ Ответ получен: {response[:100]}...")
        else:
            print("❌ Ответ не получен")
            
        # Тестируем генерацию гороскопа
        print("🔮 Тест 2: Генерация гороскопа...")
        horoscope = await client.generate_horoscope("leo", test_user_id)
        
        if horoscope:
            print(f"✅ Гороскоп сгенерирован: {horoscope[:100]}...")
        else:
            print("❌ Гороскоп не сгенерирован")
            
        # Тестируем утреннее сообщение
        print("🌅 Тест 3: Утреннее сообщение...")
        morning = await client.generate_morning_message(test_user_id)
        
        if morning:
            print(f"✅ Утреннее сообщение: {morning[:100]}...")
        else:
            print("❌ Утреннее сообщение не сгенерировано")
            
        print("🏁 Тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_chatgpt_functionality())
