#!/usr/bin/env python3
"""
Быстрый тест основных функций бота
"""

import asyncio
import sys
import os
from datetime import datetime

# Добавим путь к проекту
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

from config import BOT_TOKEN
import requests

def test_health_endpoint():
    """Тест health endpoint"""
    print("🏥 Тестирование health endpoint...")
    try:
        response = requests.get("https://telegram-bot-project-1-production.up.railway.app/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint работает: {data}")
            return True
        else:
            print(f"❌ Health endpoint вернул код: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка health endpoint: {e}")
        return False

def test_telegram_webhook():
    """Тест Telegram webhook"""
    print("📡 Проверка webhook...")
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                webhook_info = data['result']
                webhook_url = webhook_info.get('url', '')
                if 'railway.app' in webhook_url:
                    print(f"✅ Webhook настроен правильно: {webhook_url}")
                    return True
                else:
                    print(f"⚠️ Webhook URL: {webhook_url}")
                    return False
            else:
                print(f"❌ Telegram API ошибка: {data}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка webhook проверки: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 БЫСТРЫЙ ТЕСТ БОТА")
    print(f"🕒 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = []
    
    # Тест 1: Health endpoint
    results.append(test_health_endpoint())
    print()
    
    # Тест 2: Webhook
    results.append(test_telegram_webhook())
    print()
    
    # Итоги
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Пройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты ПРОЙДЕНЫ! Бот готов к работе!")
    else:
        print("⚠️ Некоторые тесты не прошли. Требуется проверка.")
    
    print()
    print("🔍 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:")
    print("- Для тестирования ChatGPT нужна активная квота OpenAI")
    print("- Отправьте боту /start для проверки интерфейса")
    print("- Команда /chatgpt покажет меню AI функций")

if __name__ == "__main__":
    main()
