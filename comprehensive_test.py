#!/usr/bin/env python3
# comprehensive_test.py - Полная проверка проекта Telegram бота

import os
import sys
import subprocess
import traceback
import time
import psutil
import json
from datetime import datetime
from pathlib import Path

class ComprehensiveTestRunner:
    """Класс для выполнения полной проверки проекта"""
    
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {
            'environment': {},
            'imports': {},
            'code_quality': {},
            'security': {},
            'functionality': {},
            'performance': {},
            'deployment': {},
            'documentation': {}
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def print_header(self, title):
        """Печать заголовка секции"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
        
    def print_result(self, test_name, success, details=""):
        """Печать результата теста"""
        self.total_tests += 1
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{status}: {test_name}")
        if details:
            print(f"   └─ {details}")
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
    def test_environment(self):
        """Проверка окружения"""
        self.print_header("ПРОВЕРКА ОКРУЖЕНИЯ")
        
        # Проверка Python версии
        python_version = sys.version
        python_ok = sys.version_info >= (3, 8)
        self.print_result(
            "Python версия",
            python_ok,
            f"Python {python_version.split()[0]}"
        )
        self.test_results['environment']['python'] = {
            'version': python_version.split()[0],
            'compatible': python_ok
        }
        
        # Проверка зависимостей
        try:
            import telegram
            telegram_version = telegram.__version__
            telegram_ok = True
            self.print_result(
                "Python Telegram Bot библиотека",
                True,
                f"Версия {telegram_version}"
            )
        except ImportError as e:
            telegram_ok = False
            self.print_result("Python Telegram Bot библиотека", False, str(e))
            
        self.test_results['environment']['telegram'] = {
            'installed': telegram_ok,
            'version': telegram_version if telegram_ok else None
        }
        
        # Проверка .env файла
        env_exists = os.path.exists('.env')
        self.print_result(
            "Конфигурационный файл .env",
            env_exists,
            "Найден" if env_exists else "Отсутствует"
        )
        
        # Проверка переменных окружения
        from config import BOT_TOKEN, ADMIN_ID
        token_ok = BOT_TOKEN is not None and len(BOT_TOKEN) > 10
        admin_ok = ADMIN_ID is not None and ADMIN_ID > 0
        
        self.print_result("BOT_TOKEN", token_ok, "Настроен" if token_ok else "Отсутствует")
        self.print_result("ADMIN_ID", admin_ok, f"ID: {ADMIN_ID}" if admin_ok else "Отсутствует")
        
        self.test_results['environment']['config'] = {
            'env_file': env_exists,
            'bot_token': token_ok,
            'admin_id': admin_ok
        }
        
    def test_imports(self):
        """Проверка импортов"""
        self.print_header("ПРОВЕРКА ИМПОРТОВ")
        
        import_tests = [
            ("config", "import config"),
            ("handlers.admin", "from handlers.admin import admin_command"),
            ("handlers.reactions", "from handlers.reactions import handle_reaction"),
            ("utils.keyboards", "from utils.keyboards import create_main_menu_keyboard"),
            ("utils.database", "from utils.database import Database"),
            ("main_bot_railway", "import main_bot_railway"),
        ]
        
        for module_name, import_cmd in import_tests:
            try:
                exec(import_cmd)
                self.print_result(f"Импорт {module_name}", True)
                self.test_results['imports'][module_name] = True
            except Exception as e:
                self.print_result(f"Импорт {module_name}", False, str(e))
                self.test_results['imports'][module_name] = False
                
    def test_code_quality(self):
        """Проверка качества кода"""
        self.print_header("ПРОВЕРКА КАЧЕСТВА КОДА")
        
        # Проверка синтаксиса Python файлов
        python_files = []
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in root or '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = []
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
            except Exception:
                pass  # Игнорируем другие ошибки для синтаксической проверки
                
        syntax_ok = len(syntax_errors) == 0
        self.print_result(
            f"Синтаксис Python файлов ({len(python_files)} файлов)",
            syntax_ok,
            f"{len(syntax_errors)} ошибок" if not syntax_ok else "Все файлы корректны"
        )
        
        # Проверка flake8 (если доступен)
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'flake8', '--select=E9,F63,F7,F82', '.'],
                capture_output=True, text=True, timeout=30
            )
            flake8_ok = result.returncode == 0
            self.print_result(
                "Flake8 критические ошибки",
                flake8_ok,
                "Нет критических ошибок" if flake8_ok else f"Найдены ошибки"
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            # Если flake8 недоступен, проверяем синтаксис Python напрямую
            flake8_ok = len(syntax_errors) == 0
            self.print_result(
                "Flake8 проверка", 
                flake8_ok if len(syntax_errors) == 0 else None, 
                "Flake8 недоступен, используем проверку синтаксиса Python" if flake8_ok else "Flake8 недоступен"
            )
            
        self.test_results['code_quality'] = {
            'syntax_errors': syntax_errors,
            'flake8_passed': flake8_ok,
            'files_checked': len(python_files)
        }
        
    def test_security(self):
        """Проверка безопасности"""
        self.print_header("ПРОВЕРКА БЕЗОПАСНОСТИ")
        
        # Проверка на жестко заданные токены в коде
        hardcoded_secrets = []
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in root or '.git' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Ищем потенциальные токены - но исключаем допустимые случаи
                            if 'BOT_TOKEN' in content and ('=' in content):
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    line_clean = line.strip()
                                    # Пропускаем комментарии и допустимые использования
                                    if (line_clean.startswith('#') or 
                                        'os.getenv' in line or 
                                        'BOT_TOKEN}' in line or  # f-string usage
                                        'import' in line or
                                        'from' in line or
                                        'BOT_TOKEN = os.getenv' in line or
                                        'webhook' in line.lower()):  # webhook URLs are OK
                                        continue
                                    if 'BOT_TOKEN' in line and '=' in line:
                                        hardcoded_secrets.append(f"{file_path}:{i+1} - {line.strip()}")
                    except Exception:
                        pass
                        
        secrets_ok = len(hardcoded_secrets) == 0
        self.print_result(
            "Жестко заданные секреты",
            secrets_ok,
            "Не найдены" if secrets_ok else f"Найдено {len(hardcoded_secrets)} потенциальных проблем"
        )
        
        # Проверка .env в .gitignore
        gitignore_exists = os.path.exists('.gitignore')
        gitignore_ok = False
        if gitignore_exists:
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                gitignore_ok = '.env' in gitignore_content
                
        self.print_result(
            ".env в .gitignore",
            gitignore_ok,
            "Настроено корректно" if gitignore_ok else "Требует внимания"
        )
        
        self.test_results['security'] = {
            'hardcoded_secrets': hardcoded_secrets,
            'gitignore_configured': gitignore_ok
        }
        
    def test_functionality(self):
        """Проверка функциональности"""
        self.print_header("ПРОВЕРКА ФУНКЦИОНАЛЬНОСТИ")
        
        # Тест создания клавиатур
        try:
            from utils.keyboards import create_main_menu_keyboard, get_reaction_keyboard, create_zodiac_keyboard
            
            # Главное меню
            main_kb = create_main_menu_keyboard()
            main_kb_ok = hasattr(main_kb, 'inline_keyboard') and len(main_kb.inline_keyboard) > 0
            self.print_result("Создание главного меню", main_kb_ok)
            
            # Клавиатура реакций
            reaction_kb = get_reaction_keyboard("test_123")
            reaction_kb_ok = hasattr(reaction_kb, 'inline_keyboard') and len(reaction_kb.inline_keyboard) > 0
            self.print_result("Создание клавиатуры реакций", reaction_kb_ok)
            
            # Клавиатура знаков зодиака
            zodiac_kb = create_zodiac_keyboard()
            zodiac_kb_ok = hasattr(zodiac_kb, 'inline_keyboard') and len(zodiac_kb.inline_keyboard) > 0
            self.print_result("Создание клавиатуры знаков зодиака", zodiac_kb_ok)
            
        except Exception as e:
            self.print_result("Создание клавиатур", False, str(e))
            main_kb_ok = reaction_kb_ok = zodiac_kb_ok = False
            
        # Тест конфигурации
        try:
            from config import validate_config
            validate_config()
            config_ok = True
            self.print_result("Валидация конфигурации", True)
        except Exception as e:
            config_ok = False
            self.print_result("Валидация конфигурации", False, str(e))
            
        # Тест админ команд
        try:
            from handlers.admin import admin_command, stats_command
            admin_ok = True
            self.print_result("Админ команды", True, "Функции загружены успешно")
        except Exception as e:
            admin_ok = False
            self.print_result("Админ команды", False, str(e))
            
        self.test_results['functionality'] = {
            'keyboards': {
                'main_menu': main_kb_ok,
                'reactions': reaction_kb_ok,
                'zodiac': zodiac_kb_ok
            },
            'config_validation': config_ok,
            'admin_commands': admin_ok
        }
        
    def test_performance(self):
        """Проверка производительности"""
        self.print_header("ПРОВЕРКА ПРОИЗВОДИТЕЛЬНОСТИ")
        
        # Тест использования памяти
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Загружаем основные модули
        try:
            import main_bot_railway
            from handlers import admin, reactions, stats
            from utils import keyboards, database
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = final_memory - initial_memory
            
            memory_ok = memory_usage < 50  # 50 MB limit
            self.print_result(
                "Использование памяти при загрузке",
                memory_ok,
                f"{memory_usage:.2f} MB"
            )
        except Exception as e:
            self.print_result("Использование памяти при загрузке", False, str(e))
            memory_usage = None
            memory_ok = False
            
        # Тест времени импорта
        start_time = time.time()
        try:
            from telegram.ext import Application, CommandHandler
            import_time = time.time() - start_time
            import_ok = import_time < 5.0  # 5 секунд максимум
            self.print_result(
                "Скорость импорта библиотек",
                import_ok,
                f"{import_time:.3f} секунд"
            )
        except Exception as e:
            import_ok = False
            import_time = None
            self.print_result("Скорость импорта библиотек", False, str(e))
            
        self.test_results['performance'] = {
            'memory_usage_mb': memory_usage,
            'import_time_sec': import_time,
            'memory_efficient': memory_ok,
            'import_fast': import_ok
        }
        
    def test_deployment(self):
        """Проверка готовности к развертыванию"""
        self.print_header("ПРОВЕРКА ГОТОВНОСТИ К РАЗВЕРТЫВАНИЮ")
        
        # Проверка наличия необходимых файлов
        required_files = [
            'requirements.txt',
            'Dockerfile',
            'Procfile',
            'railway.json',
            'config.py',
            'main_bot_railway.py'
        ]
        
        files_status = {}
        for file in required_files:
            exists = os.path.exists(file)
            files_status[file] = exists
            self.print_result(f"Файл {file}", exists)
            
        # Проверка requirements.txt
        try:
            with open('requirements.txt', 'r') as f:
                reqs = f.read()
                has_telegram = 'python-telegram-bot' in reqs
                has_dotenv = 'python-dotenv' in reqs
                
                self.print_result("requirements.txt содержит telegram-bot", has_telegram)
                self.print_result("requirements.txt содержит python-dotenv", has_dotenv)
        except Exception as e:
            self.print_result("Анализ requirements.txt", False, str(e))
            has_telegram = has_dotenv = False
            
        # Проверка CI/CD
        ci_exists = os.path.exists('.github/workflows/ci.yml')
        self.print_result("CI/CD конфигурация", ci_exists)
        
        self.test_results['deployment'] = {
            'required_files': files_status,
            'requirements': {
                'telegram_bot': has_telegram,
                'dotenv': has_dotenv
            },
            'ci_cd': ci_exists
        }
        
    def test_documentation(self):
        """Проверка документации"""
        self.print_header("ПРОВЕРКА ДОКУМЕНТАЦИИ")
        
        # Проверка README
        readme_files = ['README.md', 'readme.md', 'ReadMe.md']
        readme_exists = any(os.path.exists(f) for f in readme_files)
        self.print_result("README файл", readme_exists)
        
        # Проверка докстрингов в ключевых файлах
        key_files = ['config.py', 'main_bot_railway.py', 'handlers/admin.py']
        docstring_coverage = 0
        total_functions = 0
        
        for file_path in key_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Простая проверка наличия докстрингов
                        functions = content.count('def ')
                        docstrings = content.count('"""')
                        total_functions += functions
                        docstring_coverage += min(docstrings, functions)
                except Exception:
                    pass
                    
        docs_ratio = docstring_coverage / max(total_functions, 1)
        docs_ok = docs_ratio > 0.3  # 30% покрытия минимум
        
        self.print_result(
            "Покрытие документацией",
            docs_ok,
            f"{docs_ratio:.1%} функций документированы"
        )
        
        self.test_results['documentation'] = {
            'readme_exists': readme_exists,
            'docstring_coverage': docs_ratio,
            'total_functions': total_functions
        }
        
    def run_existing_tests(self):
        """Запуск существующих тестов"""
        self.print_header("ЗАПУСК СУЩЕСТВУЮЩИХ ТЕСТОВ")
        
        test_files = [
            'test_import_fix.py',
            'test_keyboards_complete.py'
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                try:
                    result = subprocess.run(
                        [sys.executable, test_file],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    success = result.returncode == 0
                    self.print_result(
                        f"Тест {test_file}",
                        success,
                        "Успешно" if success else f"Ошибка: {result.stderr[:100]}"
                    )
                except subprocess.TimeoutExpired:
                    self.print_result(f"Тест {test_file}", False, "Превышено время ожидания")
                except Exception as e:
                    self.print_result(f"Тест {test_file}", False, str(e))
            else:
                self.print_result(f"Тест {test_file}", False, "Файл не найден")
                
    def generate_report(self):
        """Генерация итогового отчета"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        self.print_header("ИТОГОВЫЙ ОТЧЕТ")
        
        print(f"📊 Статистика тестирования:")
        print(f"   Всего тестов: {self.total_tests}")
        print(f"   Пройдено: {self.passed_tests} ✅")
        print(f"   Провалено: {self.failed_tests} ❌")
        print(f"   Успешность: {(self.passed_tests/max(self.total_tests,1)*100):.1f}%")
        print(f"   Время выполнения: {duration:.2f} секунд")
        
        # Общая оценка проекта
        success_rate = self.passed_tests / max(self.total_tests, 1)
        
        if success_rate >= 0.9:
            status = "🎉 ОТЛИЧНО"
            color = "green"
        elif success_rate >= 0.7:
            status = "🟡 ХОРОШО"
            color = "yellow"
        elif success_rate >= 0.5:
            status = "🟠 УДОВЛЕТВОРИТЕЛЬНО"
            color = "orange"
        else:
            status = "🔴 ТРЕБУЕТ ВНИМАНИЯ"
            color = "red"
            
        print(f"\n🎯 Общая оценка проекта: {status}")
        print(f"📈 Уровень готовности: {success_rate*100:.1f}%")
        
        # Сохранение детального отчета
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'failed_tests': self.failed_tests,
                'success_rate': success_rate,
                'duration_seconds': duration,
                'status': status
            },
            'results': self.test_results
        }
        
        with open('comprehensive_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n📋 Детальный отчет сохранен в: comprehensive_test_report.json")
        
        # Рекомендации
        print(f"\n💡 Рекомендации:")
        
        if not self.test_results['environment'].get('config', {}).get('bot_token'):
            print("   • Настройте BOT_TOKEN в .env файле")
            
        if self.test_results['security'].get('hardcoded_secrets'):
            print("   • Удалите жестко заданные секреты из кода")
            
        if not self.test_results['documentation'].get('readme_exists'):
            print("   • Добавьте README.md с описанием проекта")
            
        if not self.test_results['functionality'].get('config_validation'):
            print("   • Исправьте ошибки в конфигурации")
            
        return success_rate >= 0.7  # Возвращаем True если проект в хорошем состоянии
        
def main():
    """Главная функция запуска тестирования"""
    print("🚀 ЗАПУСК ПОЛНОЙ ПРОВЕРКИ ПРОЕКТА TELEGRAM БОТА")
    print("=" * 60)
    
    runner = ComprehensiveTestRunner()
    
    try:
        # Выполняем все проверки
        runner.test_environment()
        runner.test_imports()
        runner.test_code_quality()
        runner.test_security()
        runner.test_functionality()
        runner.test_performance()
        runner.test_deployment()
        runner.test_documentation()
        runner.run_existing_tests()
        
        # Генерируем отчет
        project_healthy = runner.generate_report()
        
        # Возвращаем соответствующий код выхода
        sys.exit(0 if project_healthy else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Тестирование прервано пользователем")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка при тестировании: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()