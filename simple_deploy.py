#!/usr/bin/env python3
"""
🚀 Простой деплой бота с готовыми данными
"""

import os
import subprocess
import sys

def run_command(cmd):
    """Выполнить команду"""
    print(f"🔧 Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"⚠️ {result.stderr}")
    
    return result.returncode == 0

def main():
    print("🚀 Простой деплой Telegram Bot")
    print("=" * 40)
    
    # Проверяем наличие основных файлов
    if not os.path.exists("main_bot_railway.py"):
        print("❌ Файл main_bot_railway.py не найден!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ Файл requirements.txt не найден!")
        return False
    
    print("✅ Основные файлы найдены")
    
    # Проверяем Git статус
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        print("📝 Коммичу изменения...")
        run_command("git add .")
        run_command('git commit -m "🚀 Deploy update"')
    
    # Push в GitHub
    print("📤 Отправляю в GitHub...")
    if run_command("git push origin main"):
        print("✅ Успешно отправлено в GitHub")
    else:
        print("⚠️ Ошибка отправки в GitHub (не критично)")
    
    print("\n🎯 Следующие шаги для деплоя на Railway:")
    print("1. Перейдите на https://railway.app")
    print("2. Войдите через GitHub")
    print("3. Нажмите 'New Project'")
    print("4. Выберите 'Deploy from GitHub repo'")
    print("5. Найдите barkoszloy-afk/telegram-bot-project-1")
    print("6. Нажмите 'Deploy'")
    print("\n🔧 После создания проекта добавьте переменные:")
    print("   BOT_TOKEN=ваш_токен_от_BotFather")
    print("   ADMIN_ID=ваш_telegram_id")
    print("   CHANNEL_ID=id_канала")
    print("   PORT=8000")
    
    print("\n📱 Как получить данные:")
    print("   BOT_TOKEN: @BotFather -> /newbot")
    print("   ADMIN_ID: @userinfobot")
    print("   CHANNEL_ID: добавьте бота в канал как админа")
    
    print("\n✨ После настройки Railway автоматически развернет бота!")
    print("🌐 Получите URL в Railway Dashboard")
    print("❤️ Проверьте /health endpoint")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
