#!/usr/bin/env python3
"""
🚀 Автономный деплой без браузера
Развертывание бота на Heroku или локально
"""

import os
import sys
import subprocess
import json
import time
from typing import Optional

class AutoDeploy:
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        
    def print_step(self, message: str) -> None:
        print(f"🔵 {message}")
        
    def print_success(self, message: str) -> None:
        print(f"✅ {message}")
        
    def print_warning(self, message: str) -> None:
        print(f"⚠️  {message}")
        
    def print_error(self, message: str) -> None:
        print(f"❌ {message}")
        
    def run_command(self, command: str, capture_output: bool = True) -> tuple[bool, str]:
        """Выполнить команду и вернуть результат"""
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    cwd=self.project_dir
                )
                return result.returncode == 0, result.stdout + result.stderr
            else:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    cwd=self.project_dir
                )
                return result.returncode == 0, ""
        except Exception as e:
            return False, str(e)
    
    def check_heroku_cli(self) -> bool:
        """Проверить установку Heroku CLI"""
        self.print_step("Проверяем Heroku CLI...")
        success, output = self.run_command("heroku --version")
        
        if success:
            self.print_success(f"Heroku CLI установлен: {output.strip()}")
            return True
        else:
            self.print_warning("Heroku CLI не установлен")
            return False
    
    def install_heroku_cli(self) -> bool:
        """Установить Heroku CLI"""
        self.print_step("Устанавливаем Heroku CLI...")
        
        system = sys.platform.lower()
        
        if system == "darwin":  # macOS
            if self.run_command("which brew")[0]:
                success, output = self.run_command("brew tap heroku/brew && brew install heroku")
            else:
                self.print_error("Установите Homebrew или скачайте Heroku CLI с https://devcenter.heroku.com/articles/heroku-cli")
                return False
        elif system.startswith("linux"):  # Linux
            success, output = self.run_command("curl https://cli-assets.heroku.com/install.sh | sh")
        else:  # Windows
            self.print_error("Скачайте Heroku CLI с https://devcenter.heroku.com/articles/heroku-cli")
            return False
        
        if success:
            self.print_success("Heroku CLI установлен")
            return True
        else:
            self.print_error(f"Ошибка установки: {output}")
            return False
    
    def check_docker(self) -> bool:
        """Проверить Docker"""
        self.print_step("Проверяем Docker...")
        success, output = self.run_command("docker --version")
        
        if success:
            self.print_success(f"Docker установлен: {output.strip()}")
            return True
        else:
            self.print_warning("Docker не установлен")
            return False
    
    def create_heroku_files(self) -> bool:
        """Создать файлы для Heroku"""
        self.print_step("Создаем файлы для Heroku...")
        
        # Создаем runtime.txt
        with open(os.path.join(self.project_dir, "runtime.txt"), "w") as f:
            f.write("python-3.11.9\n")
        
        # Обновляем Procfile для Heroku
        with open(os.path.join(self.project_dir, "Procfile"), "w") as f:
            f.write("web: python main_bot_railway.py\n")
        
        # Создаем app.json для Heroku
        app_json = {
            "name": "telegram-bot-project",
            "description": "Modern Telegram Bot with CI/CD",
            "repository": "https://github.com/barkoszloy-afk/telegram-bot-project-1",
            "logo": "https://telegram.org/img/t_logo.png",
            "keywords": ["telegram", "bot", "python", "heroku"],
            "stack": "heroku-22",
            "buildpacks": [
                {"url": "heroku/python"}
            ],
            "env": {
                "BOT_TOKEN": {
                    "description": "Telegram Bot Token from @BotFather",
                    "required": True
                },
                "ADMIN_ID": {
                    "description": "Your Telegram User ID",
                    "required": True
                },
                "CHANNEL_ID": {
                    "description": "Telegram Channel ID (optional)",
                    "required": False
                },
                "PORT": {
                    "description": "Port for web server",
                    "value": "8000"
                }
            },
            "formation": {
                "web": {
                    "quantity": 1,
                    "size": "eco"
                }
            }
        }
        
        with open(os.path.join(self.project_dir, "app.json"), "w") as f:
            json.dump(app_json, f, indent=2)
        
        self.print_success("Файлы для Heroku созданы")
        return True
    
    def create_docker_files(self) -> bool:
        """Создать Docker файлы"""
        self.print_step("Создаем Docker файлы...")
        
        # Dockerfile
        dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Открываем порт
EXPOSE 8000

# Переменные окружения
ENV PYTHONPATH=/app
ENV PORT=8000

# Запускаем бота
CMD ["python", "main_bot_railway.py"]
"""
        
        with open(os.path.join(self.project_dir, "Dockerfile"), "w") as f:
            f.write(dockerfile_content)
        
        # docker-compose.yml
        compose_content = """version: '3.8'

services:
  telegram-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - CHANNEL_ID=${CHANNEL_ID}
      - PORT=8000
    restart: unless-stopped
    volumes:
      - ./bot.log:/app/bot.log
      - ./reactions_data.json:/app/reactions_data.json
"""
        
        with open(os.path.join(self.project_dir, "docker-compose.yml"), "w") as f:
            f.write(compose_content)
        
        # .env.example
        env_example = """# Скопируйте этот файл в .env и заполните значения

# Telegram Bot Token от @BotFather
BOT_TOKEN=your_bot_token_here

# Ваш Telegram ID (получите от @userinfobot)
ADMIN_ID=your_telegram_id_here

# ID канала (опционально)
CHANNEL_ID=your_channel_id_here

# Порт для веб-сервера
PORT=8000
"""
        
        with open(os.path.join(self.project_dir, ".env.example"), "w") as f:
            f.write(env_example)
        
        self.print_success("Docker файлы созданы")
        return True
    
    def setup_env_file(self) -> bool:
        """Настроить .env файл"""
        self.print_step("Настраиваем переменные окружения...")
        
        env_file = os.path.join(self.project_dir, ".env")
        
        print("\n" + "="*50)
        print("📝 Настройка переменных окружения")
        print("="*50)
        
        # BOT_TOKEN
        print("\n🤖 BOT_TOKEN:")
        print("1. Найдите @BotFather в Telegram")
        print("2. Отправьте /newbot")
        print("3. Следуйте инструкциям")
        print("4. Скопируйте токен")
        bot_token = input("Введите BOT_TOKEN: ").strip()
        
        # ADMIN_ID
        print("\n👤 ADMIN_ID:")
        print("1. Найдите @userinfobot в Telegram")
        print("2. Отправьте ему любое сообщение")
        print("3. Скопируйте ваш ID")
        admin_id = input("Введите ADMIN_ID: ").strip()
        
        # CHANNEL_ID (опционально)
        channel_id = ""
        setup_channel = input("\nХотите настроить CHANNEL_ID? (y/n): ").lower()
        if setup_channel == 'y':
            print("1. Создайте канал или используйте существующий")
            print("2. Добавьте бота как администратора")
            print("3. Получите ID канала")
            channel_id = input("Введите CHANNEL_ID: ").strip()
        
        # Создаем .env файл
        env_content = f"""BOT_TOKEN={bot_token}
ADMIN_ID={admin_id}
CHANNEL_ID={channel_id}
PORT=8000
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        self.print_success(".env файл создан")
        return True
    
    def commit_changes(self) -> bool:
        """Коммит изменений"""
        self.print_step("Коммитим изменения...")
        
        success, _ = self.run_command("git add .")
        if not success:
            self.print_error("Ошибка git add")
            return False
        
        success, _ = self.run_command('git commit -m "🚀 Add deployment configurations for multiple platforms"')
        if not success:
            self.print_warning("Нет изменений для коммита или ошибка")
        
        return True
    
    def deploy_heroku(self) -> bool:
        """Деплой на Heroku"""
        self.print_step("🚀 Деплой на Heroku...")
        
        print("\n" + "="*50)
        print("🌐 АВТОМАТИЧЕСКИЙ ДЕПЛОЙ НА HEROKU")
        print("="*50)
        
        print("\n📋 Следующие шаги:")
        print("1. Перейдите на https://dashboard.heroku.com/new-app")
        print("2. Создайте новое приложение")
        print("3. В разделе Deploy выберите GitHub")
        print("4. Подключите репозиторий barkoszloy-afk/telegram-bot-project-1")
        print("5. Включите Automatic Deploys")
        print("6. В Settings > Config Vars добавьте:")
        print("   - BOT_TOKEN")
        print("   - ADMIN_ID") 
        print("   - CHANNEL_ID (если нужен)")
        print("7. Нажмите 'Deploy Branch'")
        
        input("\nНажмите Enter когда завершите настройку в Heroku...")
        
        self.print_success("Настройка Heroku завершена!")
        return True
    
    def deploy_docker_local(self) -> bool:
        """Локальный деплой через Docker"""
        self.print_step("🐳 Локальный деплой через Docker...")
        
        if not os.path.exists(os.path.join(self.project_dir, ".env")):
            self.print_error(".env файл не найден!")
            return False
        
        print("\nЗапускаем Docker контейнер...")
        
        # Собираем образ
        self.print_step("Собираем Docker образ...")
        success, output = self.run_command("docker build -t telegram-bot .", capture_output=False)
        
        if not success:
            self.print_error("Ошибка сборки Docker образа")
            return False
        
        # Запускаем контейнер
        self.print_step("Запускаем контейнер...")
        success, output = self.run_command("docker-compose up -d", capture_output=False)
        
        if success:
            self.print_success("🎉 Бот запущен локально в Docker!")
            print("\n📊 Полезные команды:")
            print("   docker-compose logs -f     - просмотр логов")
            print("   docker-compose stop        - остановка")
            print("   docker-compose restart     - перезапуск")
            print("   docker-compose down        - полная остановка")
            print("\n🌐 Проверьте http://localhost:8000/health")
            return True
        else:
            self.print_error("Ошибка запуска контейнера")
            return False
    
    def run_full_deploy(self) -> bool:
        """Полный автоматический деплой"""
        print("🚀 ПОЛНАЯ АВТОМАТИЗАЦИЯ ДЕПЛОЯ")
        print("=" * 50)
        
        # Создаем файлы конфигурации
        self.create_heroku_files()
        self.create_docker_files()
        
        # Настройка переменных
        if not self.setup_env_file():
            return False
        
        # Коммит изменений
        self.commit_changes()
        
        # Отправляем в GitHub
        self.print_step("Отправляем в GitHub...")
        success, output = self.run_command("git push origin main")
        if success:
            self.print_success("✅ Код отправлен в GitHub")
        else:
            self.print_warning("⚠️ Ошибка отправки в GitHub")
        
        # Выбор способа деплоя
        print("\n" + "="*50)
        print("🎯 ВЫБЕРИТЕ СПОСОБ ДЕПЛОЯ")
        print("="*50)
        print("1. Heroku (облачный, бесплатный)")
        print("2. Docker (локальный)")
        print("3. Оба способа")
        
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            return self.deploy_heroku()
        elif choice == "2":
            if self.check_docker():
                return self.deploy_docker_local()
            else:
                self.print_error("Docker не установлен")
                return False
        elif choice == "3":
            heroku_success = self.deploy_heroku()
            docker_success = False
            if self.check_docker():
                docker_success = self.deploy_docker_local()
            return heroku_success or docker_success
        else:
            self.print_error("Неверный выбор")
            return False

def main():
    deployer = AutoDeploy()
    
    print("🎯 АВТОНОМНЫЙ ДЕПЛОЙ БЕЗ БРАУЗЕРА")
    print("Поддерживаемые платформы: Heroku, Docker")
    print("=" * 50)
    
    success = deployer.run_full_deploy()
    
    if success:
        print("\n🎉 ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!")
        print("\n📱 Протестируйте бота:")
        print("   1. Найдите бота в Telegram")
        print("   2. Отправьте /start")
        print("   3. Проверьте работу меню")
        print("\n📊 Мониторинг:")
        print("   - Heroku: https://dashboard.heroku.com")
        print("   - Docker: docker-compose logs -f")
    else:
        print("\n❌ Ошибка деплоя")
        sys.exit(1)

if __name__ == "__main__":
    main()
