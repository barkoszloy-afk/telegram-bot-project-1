#!/usr/bin/env python3
"""
Отправка команды боту через Telegram API
"""

import os
import requests
import sys

# Добавим путь к проекту
sys.path.append('/Users/konstantinbaranov/Desktop/eto vse ty/telegram-bot-project-1')

from config import BOT_TOKEN

def send_start_command():
    """Отправляем команду /start боту"""
    
    # Получаем информацию о боте
    bot_info_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getMe'
    response = requests.get(bot_info_url)
    
    if response.status_code == 200:
        bot_data = response.json()
        if bot_data['ok']:
            bot_username = bot_data['result']['username']
            print(f"🤖 Найден бот: @{bot_username}")
        else:
            print(f"❌ Ошибка получения информации о боте: {bot_data}")
            return
    else:
        print(f"❌ HTTP ошибка: {response.status_code}")
        return
    
    print("ℹ️ Для тестирования:")
    print(f"1. Откройте Telegram")
    print(f"2. Найдите бота @{bot_username}")
    print(f"3. Отправьте команду /start")
    print(f"4. Проверьте, отвечает ли бот")
    
    # Попробуем получить последние обновления (если webhook отключен)
    try:
        updates_url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?limit=1&timeout=1'
        response = requests.get(updates_url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                print(f"📊 Статус обновлений: получено {len(data['result'])} обновлений")
            else:
                print(f"❓ Результат getUpdates: {data}")
        else:
            print(f"⚠️ Не удалось получить обновления (webhook активен)")
    except Exception as e:
        print(f"ℹ️ Webhook активен - это нормально: {e}")

if __name__ == "__main__":
    send_start_command()
