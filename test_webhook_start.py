#!/usr/bin/env python3
"""
Симуляция webhook запроса для тестирования
"""

import requests
import json
from config import BOT_TOKEN

def test_webhook_directly():
    """Тестируем webhook напрямую с симуляцией /start команды"""
    
    webhook_url = f"https://telegram-bot-project-1-production.up.railway.app/webhook/{BOT_TOKEN}"
    
    # Симуляция /start команды от пользователя
    test_update = {
        "update_id": 999999,
        "message": {
            "message_id": 9999,
            "from": {
                "id": 345470935,  # ADMIN_ID
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 345470935,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1735776000,
            "text": "/start",
            "entities": [
                {
                    "offset": 0,
                    "length": 6,
                    "type": "bot_command"
                }
            ]
        }
    }
    
    print("🧪 ТЕСТ WEBHOOK ENDPOINT")
    print("=" * 40)
    print(f"📡 URL: {webhook_url}")
    print(f"📨 Отправляем /start команду...")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_update,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook обработал запрос успешно!")
        else:
            print(f"❌ Ошибка webhook: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка при отправке запроса: {e}")

if __name__ == "__main__":
    test_webhook_directly()
