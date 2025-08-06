#!/usr/bin/env python3
"""
Тест отправки сообщения через webhook симуляцию
"""

import requests
import json
from config import BOT_TOKEN

def test_webhook_with_direct_response():
    """Тестируем webhook с ожиданием прямого ответа"""
    
    webhook_url = f"https://telegram-bot-project-1-production.up.railway.app/webhook/{BOT_TOKEN}"
    
    # Симуляция /test команды - она должна отправить ответ
    test_update = {
        "update_id": 999998,
        "message": {
            "message_id": 9998,
            "from": {
                "id": 345470935,  # ADMIN_ID
                "is_bot": False,
                "first_name": "TestUser",
                "username": "testuser"
            },
            "chat": {
                "id": 345470935,
                "first_name": "TestUser",
                "username": "testuser", 
                "type": "private"
            },
            "date": 1735776000,
            "text": "/test",
            "entities": [
                {
                    "offset": 0,
                    "length": 5,
                    "type": "bot_command"
                }
            ]
        }
    }
    
    print("🧪 ТЕСТ WEBHOOK С КОМАНДОЙ /test")
    print("=" * 40)
    print(f"📡 URL: {webhook_url}")
    print(f"📨 Отправляем /test команду...")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_update,
            headers={'Content-Type': 'application/json'},
            timeout=30  # Увеличенный timeout для обработки
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        print(f"⏱️ Время ответа: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            print("✅ Webhook обработал запрос успешно!")
            print("📱 Проверьте Telegram - должно прийти сообщение с результатом /test")
        else:
            print(f"❌ Ошибка webhook: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")

if __name__ == "__main__":
    test_webhook_with_direct_response()
