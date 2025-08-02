#!/usr/bin/env python3
"""
Тест отправки сообщения через Railway webhook
"""

import json

# Создаем простую Flask функцию для тестирования отправки
test_message_data = {
    "chat_id": 345470935,
    "text": "🧪 Тест отправки сообщения с Railway\n\nЕсли вы видите это сообщение, значит бот может отправлять сообщения!"
}

print("📤 Тестовые данные для отправки сообщения:")
print(json.dumps(test_message_data, indent=2, ensure_ascii=False))
print("\n🌐 URL для отправки:")
print("https://api.telegram.org/bot8382591665:AAFxyatJLj5O67weu26eV_NmCo6M60Jojrw/sendMessage")
