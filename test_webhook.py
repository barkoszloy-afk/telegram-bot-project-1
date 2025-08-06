#!/usr/bin/env python3
"""
Тест прямой отправки webhook сообщения
"""

import requests
import json

def test_webhook():
    """Тестируем webhook напрямую"""
    webhook_url = "https://telegram-bot-project-1-production.up.railway.app/webhook/8382591665:AAFxyatJLj5O67weu26eV_NmCo6M60Jojrw"
    
    # Тестовое обновление
    test_update = {
        "update_id": 999999999,
        "message": {
            "message_id": 123,
            "date": 1691289600,
            "chat": {
                "id": 5157876264,
                "type": "private",
                "username": "testuser",
                "first_name": "Test"
            },
            "from": {
                "id": 5157876264,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
                "language_code": "ru"
            },
            "text": "/start"
        }
    }
    
    try:
        print("🧪 Отправляем тестовое обновление на webhook...")
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
            print("❌ Ошибка обработки webhook")
            
    except Exception as e:
        print(f"❌ Ошибка отправки на webhook: {e}")

if __name__ == "__main__":
    test_webhook()
