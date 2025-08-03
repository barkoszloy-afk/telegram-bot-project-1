#!/usr/bin/env python3
"""
🚀 Мгновенный автодеплой - как было раньше!
Без всяких сложностей, просто запускаем бота
"""

import os
import subprocess
import sys
import json
import time
from datetime import datetime

def print_step(msg):
    print(f"🔵 {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def run_cmd(cmd, silent=False):
    """Запуск команды"""
    if not silent:
        print(f"📝 {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if not silent and result.stdout:
            print(result.stdout.strip())
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def instant_deploy():
    print("🚀 МГНОВЕННЫЙ АВТОДЕПЛОЙ")
    print("=" * 50)
    
    # Проверяем что мы в правильной папке
    if not os.path.exists("main_bot_railway.py"):
        print_error("Файл main_bot_railway.py не найден!")
        return False
    
    print_step("Коммитим и пушим изменения...")
    
    # Добавляем все файлы
    run_cmd("git add .", silent=True)
    
    # Коммитим с временной меткой
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_cmd(f'git commit -m "🚀 Auto deploy {timestamp}"', silent=True)
    
    # Пушим
    success, out, err = run_cmd("git push origin main", silent=True)
    if success:
        print_success("Код отправлен в GitHub!")
    else:
        print_error("Ошибка отправки в GitHub")
    
    print_step("Создаем файлы конфигурации...")
    
    # Создаем .env.example если его нет
    if not os.path.exists(".env.example"):
        with open(".env.example", "w") as f:
            f.write("""# Скопируйте в .env и заполните
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
CHANNEL_ID=your_channel_id_here
PORT=8000
""")
    
    # Создаем простой Dockerfile
    with open("Dockerfile", "w") as f:
        f.write("""FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main_bot_railway.py"]
""")
    
    # Создаем docker-compose.yml
    with open("docker-compose.yml", "w") as f:
        f.write("""version: '3.8'
services:
  bot:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    restart: unless-stopped
""")
    
    print_success("Файлы созданы!")
    
    # Проверяем Docker
    docker_ok, _, _ = run_cmd("docker --version", silent=True)
    
    if docker_ok:
        print_step("🐳 Docker найден! Запускаем локально...")
        
        # Проверяем .env файл
        if not os.path.exists(".env"):
            print("📝 Создайте файл .env со следующими данными:")
            print("BOT_TOKEN=ваш_токен_от_BotFather")
            print("ADMIN_ID=ваш_telegram_id")
            print("CHANNEL_ID=id_канала")
            print("PORT=8000")
            print()
            
            # Создаем пример .env
            with open(".env", "w") as f:
                f.write("BOT_TOKEN=ЗАМЕНИТЕ_НА_ВАШ_ТОКЕН\n")
                f.write("ADMIN_ID=ЗАМЕНИТЕ_НА_ВАШ_ID\n")
                f.write("CHANNEL_ID=\n")
                f.write("PORT=8000\n")
            
            print("✅ Файл .env создан! Отредактируйте его и запустите снова")
            return True
        
        # Останавливаем предыдущие контейнеры
        run_cmd("docker-compose down", silent=True)
        
        # Собираем и запускаем
        print_step("Собираем Docker образ...")
        build_ok, _, _ = run_cmd("docker build -t telegram-bot .")
        
        if build_ok:
            print_step("Запускаем контейнер...")
            up_ok, _, _ = run_cmd("docker-compose up -d")
            
            if up_ok:
                print_success("🎉 БОТ ЗАПУЩЕН!")
                print()
                print("🌐 Проверьте: http://localhost:8000/health")
                print("📋 Логи: docker-compose logs -f")
                print("🛑 Остановка: docker-compose down")
                return True
            else:
                print_error("Ошибка запуска контейнера")
        else:
            print_error("Ошибка сборки образа")
    
    else:
        print_step("Docker не найден. Показываю облачные варианты...")
    
    print()
    print("☁️ ОБЛАЧНЫЙ ДЕПЛОЙ:")
    print("=" * 30)
    print()
    
    print("🟣 HEROKU (рекомендуется):")
    print("1. Идите на https://dashboard.heroku.com/new-app")
    print("2. Создайте приложение")  
    print("3. Deploy → GitHub → barkoszloy-afk/telegram-bot-project-1")
    print("4. Settings → Config Vars → добавьте:")
    print("   BOT_TOKEN, ADMIN_ID, CHANNEL_ID, PORT=8000")
    print("5. Deploy Branch")
    print()
    
    print("🟦 RAILWAY:")
    print("1. Идите на https://railway.app")
    print("2. New Project → GitHub → telegram-bot-project-1")
    print("3. Settings → Environment → добавьте переменные")
    print("4. Автодеплой!")
    print()
    
    print("🟢 RENDER:")
    print("1. Идите на https://render.com")
    print("2. New → Web Service → GitHub")
    print("3. Выберите репозиторий")
    print("4. Environment → добавьте переменные")
    print()
    
    print("📱 КАК ПОЛУЧИТЬ ДАННЫЕ:")
    print("BOT_TOKEN: @BotFather → /newbot")
    print("ADMIN_ID: @userinfobot")
    print("CHANNEL_ID: добавьте бота в канал как админа")
    print()
    
    print_success("🎯 Готово! Выберите любую платформу и деплойте!")
    
    # Финальный коммит
    run_cmd("git add .", silent=True)
    run_cmd('git commit -m "🐳 Add Docker and cloud deployment configs"', silent=True)
    run_cmd("git push origin main", silent=True)
    
    return True

if __name__ == "__main__":
    print("⚡ МГНОВЕННЫЙ ДЕПЛОЙ БЕЗ ВСЯКИХ СЛОЖНОСТЕЙ!")
    print()
    
    success = instant_deploy()
    
    if success:
        print()
        print("🎉 ВСЁ ГОТОВО!")
        print("Ваш бот готов к работе!")
    else:
        print("❌ Что-то пошло не так")
        sys.exit(1)
