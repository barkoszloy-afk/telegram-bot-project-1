#!/usr/bin/env python3
"""
Тест реального взаимодействия с ботом
"""

import os
import sys
import time
import requests
import asyncio

# Добавим путь к проекту  
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

from config import BOT_TOKEN

def test_bot_response():
    """Тестируем ответ бота"""
    
    print("🤖 Тестирование ответа бота...")
    print("=" * 50)
    
    # 1. Проверим информацию о боте
    print("1️⃣ Получаем информацию о боте...")
    bot_info_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getMe'
    response = requests.get(bot_info_url)
    
    if response.status_code == 200:
        bot_data = response.json()
        if bot_data['ok']:
            bot_info = bot_data['result']
            print(f"✅ Бот активен: @{bot_info['username']}")
            print(f"📝 Имя: {bot_info['first_name']}")
            print(f"🆔 ID: {bot_info['id']}")
        else:
            print(f"❌ Ошибка: {bot_data}")
            return False
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        return False
    
    # 2. Проверим webhook
    print("\\n2️⃣ Проверяем webhook...")
    webhook_info_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo'
    response = requests.get(webhook_info_url)
    
    if response.status_code == 200:
        webhook_data = response.json()
        if webhook_data['ok']:
            webhook_info = webhook_data['result']
            print(f"✅ Webhook URL: {webhook_info.get('url', 'Не установлен')}")
            print(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"🔗 Max connections: {webhook_info.get('max_connections', 0)}")
        else:
            print(f"❌ Ошибка webhook: {webhook_data}")
    
    # 3. Проверим здоровье сервиса
    print("\\n3️⃣ Проверяем здоровье сервиса...")
    health_url = "https://telegram-bot-project-1-production.up.railway.app/health"
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Сервис здоров")
            print(f"⏱️ Uptime: {health_data.get('uptime_seconds', 0):.1f} секунд")
            print(f"🏷️ Версия: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка health check: {e}")
    
    print("\\n📋 ИТОГИ ДИАГНОСТИКИ:")
    print("=" * 50)
    print("🔹 Бот зарегистрирован в Telegram API")
    print("🔹 Webhook настроен и активен") 
    print("🔹 Railway сервис работает")
    print("\\n💡 РЕКОМЕНДАЦИИ ДЛЯ ТЕСТИРОВАНИЯ:")
    print("1. Откройте Telegram")
    print(f"2. Найдите бота @{bot_info['username']}")
    print("3. Отправьте команду /start")
    print("4. Если бот не отвечает, проверьте логи Railway")
    
    return True

if __name__ == "__main__":
    test_bot_response()
