#!/usr/bin/env python3
# railway_test.py - Тест готовности для Railway
import os
import sys
import asyncio
from pathlib import Path

def test_environment_variables():
    """Проверка переменных окружения"""
    print("🔧 Проверка переменных окружения...")
    
    required_vars = ['BOT_TOKEN', 'ADMIN_ID', 'CHANNEL_ID']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: установлен")
        else:
            print(f"  ❌ {var}: НЕ УСТАНОВЛЕН")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        print("📋 Установите их в Railway Dashboard")
        return False
    
    print("✅ Все переменные окружения настроены")
    return True

def test_files():
    """Проверка необходимых файлов"""
    print("\n📁 Проверка файлов...")
    
    required_files = [
        'main_bot_railway.py',
        'config.py', 
        'requirements.txt',
        'railway.json',
        'handlers/admin.py',
        'handlers/reactions.py',
        'utils/database.py',
        'utils/keyboards.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}: НЕ НАЙДЕН")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все необходимые файлы на месте")
    return True

def test_imports():
    """Проверка импортов"""
    print("\n📦 Проверка зависимостей...")
    
    try:
        import telegram
        print("  ✅ python-telegram-bot")
    except ImportError:
        print("  ❌ python-telegram-bot: НЕ УСТАНОВЛЕН")
        return False
    
    try:
        import flask
        print("  ✅ flask")
    except ImportError:
        print("  ❌ flask: НЕ УСТАНОВЛЕН") 
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv")
    except ImportError:
        print("  ❌ python-dotenv: НЕ УСТАНОВЛЕН")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def test_config():
    """Проверка конфигурации"""
    print("\n⚙️ Проверка конфигурации...")
    
    try:
        # Попытка импорта конфигурации
        sys.path.append('.')
        from config import BOT_TOKEN, ADMIN_ID, validate_config
        
        validate_config()
        print("  ✅ Конфигурация валидна")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка конфигурации: {e}")
        return False

def test_railway_readiness():
    """Проверка готовности к Railway"""
    print("\n🚀 Проверка готовности к Railway...")
    
    # Проверка railway.json
    railway_config = Path('railway.json')
    if railway_config.exists():
        print("  ✅ railway.json существует")
    else:
        print("  ❌ railway.json не найден")
        return False
    
    # Проверка main_bot_railway.py
    railway_main = Path('main_bot_railway.py')
    if railway_main.exists():
        print("  ✅ main_bot_railway.py готов")
    else:
        print("  ❌ main_bot_railway.py не найден")
        return False
    
    # Проверка requirements.txt
    requirements = Path('requirements.txt')
    if requirements.exists():
        with open(requirements, 'r') as f:
            content = f.read()
            if 'flask' in content:
                print("  ✅ requirements.txt включает flask")
            else:
                print("  ❌ flask отсутствует в requirements.txt")
                return False
    
    print("✅ Готов к деплою на Railway")
    return True

def main():
    """Главная функция тестирования"""
    print("🤖 ТЕСТ ГОТОВНОСТИ К RAILWAY")
    print("=" * 40)
    
    tests = [
        test_files,
        test_imports, 
        test_environment_variables,
        test_config,
        test_railway_readiness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"✅ Пройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("🚀 Проект готов к деплою на Railway")
        print("\n📋 Следующие шаги:")
        print("1. Установите переменные окружения в Railway Dashboard")
        print("2. Подключите GitHub репозиторий к Railway")
        print("3. Запустите деплой")
        print("4. Проверьте логи в Railway")
        return True
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ!")
        print("🔧 Исправьте ошибки и запустите тест снова")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
