#!/usr/bin/env python3
"""
🚀 Автоматический деплой на Railway через Python
Альтернатива bash скрипту для пользователей Windows
"""

import os
import sys
import subprocess
import json
import time
import requests
from typing import Optional, Dict, Any

class Colors:
    """ANSI цвета для красивого вывода"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m' 
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class AutoDeploy:
    """Класс для автоматического деплоя"""
    
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.railway_installed = False
        self.railway_logged_in = False
        
    def print_step(self, message: str) -> None:
        """Печать шага с красивым форматированием"""
        print(f"{Colors.BLUE}📋 {message}{Colors.NC}")
        
    def print_success(self, message: str) -> None:
        """Печать успеха"""
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
        
    def print_warning(self, message: str) -> None:
        """Печать предупреждения"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
        
    def print_error(self, message: str) -> None:
        """Печать ошибки"""
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        
    def run_command(self, command: str, capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Выполнение команды с обработкой ошибок"""
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    check=check,
                    cwd=self.project_dir
                )
            else:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    check=check,
                    cwd=self.project_dir
                )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                self.print_error(f"Ошибка выполнения команды: {command}")
                self.print_error(f"Код ошибки: {e.returncode}")
                if e.stderr:
                    self.print_error(f"Stderr: {e.stderr}")
                raise
            return e
    
    def check_railway_cli(self) -> bool:
        """Проверка установки Railway CLI"""
        self.print_step("Проверяем установку Railway CLI...")
        
        try:
            result = self.run_command("railway --version")
            self.railway_installed = True
            self.print_success(f"Railway CLI установлен: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Railway CLI не найден")
            return False
    
    def install_railway_cli(self) -> bool:
        """Установка Railway CLI"""
        self.print_step("Устанавливаем Railway CLI...")
        
        system = sys.platform.lower()
        
        try:
            if system == "win32":
                # Windows
                self.print_step("Скачиваем Railway CLI для Windows...")
                install_cmd = 'powershell -Command "iwr -useb https://railway.app/install.ps1 | iex"'
            elif system == "darwin":
                # macOS
                if self.run_command("which brew", check=False).returncode == 0:
                    install_cmd = "brew install railway"
                else:
                    install_cmd = "curl -fsSL https://railway.app/install.sh | sh"
            else:
                # Linux
                install_cmd = "curl -fsSL https://railway.app/install.sh | sh"
            
            result = self.run_command(install_cmd, capture_output=False)
            
            # Проверяем установку
            time.sleep(2)
            return self.check_railway_cli()
            
        except Exception as e:
            self.print_error(f"Ошибка установки Railway CLI: {e}")
            self.print_warning("Установите Railway CLI вручную: https://docs.railway.app/develop/cli")
            return False
    
    def check_railway_auth(self) -> bool:
        """Проверка авторизации в Railway"""
        self.print_step("Проверяем авторизацию в Railway...")
        
        try:
            result = self.run_command("railway whoami")
            self.railway_logged_in = True
            self.print_success(f"Авторизованы как: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Не авторизованы в Railway")
            return False
    
    def login_railway(self) -> bool:
        """Авторизация в Railway"""
        self.print_step("Авторизация в Railway...")
        self.print_warning("Сейчас откроется браузер для авторизации")
        
        input("Нажмите Enter для продолжения...")
        
        try:
            self.run_command("railway login", capture_output=False)
            return self.check_railway_auth()
        except Exception as e:
            self.print_error(f"Ошибка авторизации: {e}")
            return False
    
    def setup_project(self) -> bool:
        """Настройка проекта Railway"""
        self.print_step("Настраиваем проект Railway...")
        
        # Проверяем существующий проект
        try:
            result = self.run_command("railway status")
            self.print_success("Проект уже связан с Railway")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError:
            # Создаем новый проект
            self.print_step("Создаем новый проект...")
            
            try:
                self.run_command("railway project create telegram-bot-project", capture_output=False)
                self.run_command("railway link", capture_output=False)
                self.print_success("Проект создан и связан")
                return True
            except Exception as e:
                self.print_error(f"Ошибка создания проекта: {e}")
                return False
    
    def setup_environment_vars(self) -> bool:
        """Настройка переменных окружения"""
        self.print_step("Настраиваем переменные окружения...")
        
        # Показываем текущие переменные
        try:
            result = self.run_command("railway vars", check=False)
            if result.returncode == 0:
                print("Текущие переменные:")
                print(result.stdout)
        except:
            pass
        
        print("\n" + "="*50)
        print("📝 Настройка переменных окружения")
        print("="*50)
        
        setup = input("Хотите настроить переменные сейчас? (y/n): ").lower()
        
        if setup == 'y':
            # BOT_TOKEN
            print("\n🤖 BOT_TOKEN:")
            print("1. Напишите @BotFather в Telegram")
            print("2. Используйте /newbot")
            print("3. Скопируйте токен")
            bot_token = input("Введите BOT_TOKEN: ").strip()
            
            if bot_token:
                self.run_command(f'railway vars set BOT_TOKEN="{bot_token}"')
                self.print_success("BOT_TOKEN установлен")
            
            # ADMIN_ID
            print("\n👤 ADMIN_ID:")
            print("1. Напишите @userinfobot в Telegram")
            print("2. Скопируйте ваш ID")
            admin_id = input("Введите ADMIN_ID: ").strip()
            
            if admin_id:
                self.run_command(f'railway vars set ADMIN_ID="{admin_id}"')
                self.print_success("ADMIN_ID установлен")
            
            # CHANNEL_ID (опционально)
            channel_setup = input("\nХотите настроить CHANNEL_ID? (y/n): ").lower()
            if channel_setup == 'y':
                channel_id = input("Введите CHANNEL_ID: ").strip()
                if channel_id:
                    self.run_command(f'railway vars set CHANNEL_ID="{channel_id}"')
                    self.print_success("CHANNEL_ID установлен")
            
            # PORT
            self.run_command('railway vars set PORT="8000"')
            self.print_success("PORT установлен")
            
            return True
        else:
            self.print_warning("Не забудьте настроить переменные позже")
            return True
    
    def commit_and_push(self) -> bool:
        """Коммит и пуш изменений"""
        try:
            # Проверяем статус git
            result = self.run_command("git status --porcelain")
            
            if result.stdout.strip():
                self.print_step("Коммитим изменения...")
                self.run_command("git add .")
                commit_msg = f"🚀 Auto-deploy: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                self.run_command(f'git commit -m "{commit_msg}"')
                self.print_success("Изменения закоммичены")
            
            # Пушим в GitHub (если настроен)
            try:
                self.run_command("git remote get-url origin")
                self.print_step("Отправляем в GitHub...")
                self.run_command("git push origin main", check=False)
                self.print_success("Отправлено в GitHub")
            except:
                self.print_warning("GitHub remote не настроен или ошибка push")
            
            return True
            
        except Exception as e:
            self.print_warning(f"Ошибка работы с git: {e}")
            return True  # Не критическая ошибка
    
    def deploy_to_railway(self) -> bool:
        """Деплой в Railway"""
        self.print_step("🚀 Запускаем деплой в Railway...")
        
        try:
            self.run_command("railway up --detach", capture_output=False)
            self.print_success("Деплой запущен!")
            return True
        except Exception as e:
            self.print_error(f"Ошибка деплоя: {e}")
            return False
    
    def check_deployment_status(self) -> None:
        """Проверка статуса деплоя"""
        self.print_step("Проверяем статус деплоя...")
        
        # Ждем немного
        time.sleep(10)
        
        try:
            # Получаем URL проекта
            result = self.run_command("railway domain", check=False)
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'https://' in line:
                        url = line.strip()
                        self.print_success(f"🌐 Проект доступен: {url}")
                        
                        # Проверяем healthcheck
                        time.sleep(5)
                        try:
                            health_url = f"{url}/health"
                            response = requests.get(health_url, timeout=10)
                            
                            if response.status_code == 200:
                                self.print_success("✨ Бот успешно развернут и работает!")
                                
                                print(f"\n{Colors.CYAN}🎯 Полезные ссылки:{Colors.NC}")
                                print(f"   🌐 Основной URL: {url}")
                                print(f"   ❤️  Healthcheck: {health_url}")
                                print(f"   📋 Логи: {url}/logs")
                                print(f"   🏗️  Railway Dashboard: https://railway.app/dashboard")
                                
                                print(f"\n{Colors.PURPLE}📱 Тестирование бота:{Colors.NC}")
                                print("   1. Найдите вашего бота в Telegram")
                                print("   2. Отправьте /start")
                                print("   3. Проверьте работу меню")
                                
                            else:
                                self.print_warning("Healthcheck недоступен, но деплой завершен")
                                
                        except requests.RequestException:
                            self.print_warning("Не удалось проверить healthcheck")
                        
                        break
            else:
                # Показываем общий статус
                try:
                    result = self.run_command("railway status")
                    print(result.stdout)
                except:
                    pass
                    
                self.print_success("Деплой завершен! Проверьте Railway Dashboard")
                
        except Exception as e:
            self.print_warning(f"Ошибка проверки статуса: {e}")
    
    def print_helpful_commands(self) -> None:
        """Печать полезных команд"""
        print(f"\n{Colors.CYAN}📚 Полезные команды Railway:{Colors.NC}")
        print("   railway logs          - логи в реальном времени")
        print("   railway status        - статус проекта")
        print("   railway vars          - переменные окружения")
        print("   railway open          - открыть в браузере")
        print("   railway domain        - получить URL проекта")
        print("   railway restart       - перезапустить сервис")
    
    def run_full_deploy(self) -> bool:
        """Полный автоматический деплой"""
        print(f"{Colors.WHITE}🎯 Автоматический деплой Telegram Bot на Railway{Colors.NC}")
        print("=" * 60)
        
        # Проверяем, что мы в правильной директории
        if not os.path.exists(os.path.join(self.project_dir, "main_bot_railway.py")):
            self.print_error("Файл main_bot_railway.py не найден!")
            self.print_error("Убедитесь, что вы в правильной директории")
            return False
        
        # Шаг 1: Проверка/установка Railway CLI
        if not self.check_railway_cli():
            if not self.install_railway_cli():
                return False
        
        # Шаг 2: Авторизация
        if not self.check_railway_auth():
            if not self.login_railway():
                return False
        
        # Шаг 3: Настройка проекта
        if not self.setup_project():
            return False
        
        # Шаг 4: Переменные окружения
        if not self.setup_environment_vars():
            return False
        
        # Шаг 5: Git операции
        self.commit_and_push()
        
        # Шаг 6: Деплой
        if not self.deploy_to_railway():
            return False
        
        # Шаг 7: Проверка
        self.check_deployment_status()
        
        # Заключение
        print(f"\n{Colors.GREEN}🎉 Автоматический деплой завершен!{Colors.NC}")
        self.print_helpful_commands()
        
        return True
    
    def quick_deploy(self) -> bool:
        """Быстрый деплой без интерактивных вопросов"""
        print(f"{Colors.WHITE}⚡ Быстрый деплой...{Colors.NC}")
        
        # Проверки
        if not self.check_railway_cli():
            self.print_error("Railway CLI не установлен. Запустите полный деплой.")
            return False
        
        if not self.check_railway_auth():
            self.print_error("Не авторизованы в Railway. Запустите полный деплой.")
            return False
        
        # Быстрые операции
        self.commit_and_push()
        
        if self.deploy_to_railway():
            self.print_success("🎉 Быстрый деплой завершен!")
            
            # Показываем URL если возможно
            try:
                result = self.run_command("railway domain", check=False)
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if 'https://' in line:
                            url = line.strip()
                            print(f"🌐 URL: {url}")
                            print(f"❤️ Health: {url}/health")
                            break
            except:
                pass
            
            self.print_helpful_commands()
            return True
        
        return False

def main():
    """Главная функция"""
    deployer = AutoDeploy()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        success = deployer.quick_deploy()
    else:
        success = deployer.run_full_deploy()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()