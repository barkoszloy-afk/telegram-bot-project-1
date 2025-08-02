#!/usr/bin/env python3
"""
Тест webhook для Railway
"""

import requests
import json

def test_webhook():
    """Тестируем webhook endpoint"""
    webhook_url = "https://telegram-bot-project-1-production.up.railway.app/webhook/8382591665:AAFxyatJLj5O67weu26eV_NmCo6M60Jojrw"
    
    # Создаем тестовое сообщение /start
    test_data = {
        "update_id": 123456,
        "message": {
            "message_id": 1,
            "from": {
                "id": 345470935,
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
            "date": 1722624000,
            "text": "/start"
        }
    }
    
    print("🧪 Тестируем webhook endpoint...")
    print(f"📍 URL: {webhook_url}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Статус: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook отвечает успешно")
        else:
            print("❌ Webhook возвращает ошибку")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    test_webhook()
