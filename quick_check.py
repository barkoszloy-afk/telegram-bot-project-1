#!/usr/bin/env python3
# quick_check.py - Быстрая проверка статуса проекта

import os
import sys

def quick_status():
    """Быстрая проверка статуса проекта"""
    print("🚀 БЫСТРАЯ ПРОВЕРКА СТАТУСА TELEGRAM БОТА")
    print("=" * 50)
    
    # Проверка основных файлов
    essential_files = [
        ('main_bot_railway.py', 'Основной файл бота'),
        ('config.py', 'Конфигурация'),
        ('requirements.txt', 'Зависимости'),
        ('.env', 'Переменные окружения'),
        ('Dockerfile', 'Docker конфигурация'),
        ('Procfile', 'Procfile для деплоя')
    ]
    
    print("\n📁 Основные файлы:")
    missing_files = 0
    for file, description in essential_files:
        if os.path.exists(file):
            print(f"   ✅ {file} - {description}")
        else:
            print(f"   ❌ {file} - {description} (ОТСУТСТВУЕТ)")
            missing_files += 1
    
    # Проверка директорий
    essential_dirs = [
        ('handlers', 'Обработчики команд'),
        ('utils', 'Утилиты'),
        ('tests', 'Тесты')
    ]
    
    print("\n📂 Основные директории:")
    missing_dirs = 0
    for dir_name, description in essential_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/ - {description}")
        else:
            print(f"   ❌ {dir_name}/ - {description} (ОТСУТСТВУЕТ)")
            missing_dirs += 1
    
    # Проверка импортов
    print("\n🔧 Проверка импортов:")
    import_success = 0
    total_imports = 0
    
    imports_to_check = [
        ('config', 'Конфигурация'),
        ('utils.keyboards', 'Клавиатуры'),
        ('handlers.admin', 'Админ команды')
    ]
    
    for module, description in imports_to_check:
        total_imports += 1
        try:
            __import__(module)
            print(f"   ✅ {module} - {description}")
            import_success += 1
        except ImportError as e:
            print(f"   ❌ {module} - {description} (ОШИБКА: {e})")
    
    # Проверка конфигурации
    print("\n⚙️ Конфигурация:")
    config_issues = 0
    
    try:
        from config import BOT_TOKEN, ADMIN_ID
        
        if BOT_TOKEN:
            if 'TEST' in BOT_TOKEN:
                print("   ⚠️ BOT_TOKEN - Используется тестовый токен")
            else:
                print("   ✅ BOT_TOKEN - Настроен")
        else:
            print("   ❌ BOT_TOKEN - Не настроен")
            config_issues += 1
            
        if ADMIN_ID and ADMIN_ID > 0:
            print("   ✅ ADMIN_ID - Настроен")
        else:
            print("   ❌ ADMIN_ID - Не настроен")
            config_issues += 1
    except Exception as e:
        print(f"   ❌ Ошибка загрузки конфигурации: {e}")
        config_issues += 1
    
    # Итоговая оценка
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ ОЦЕНКА:")
    
    total_issues = missing_files + missing_dirs + (total_imports - import_success) + config_issues
    
    if total_issues == 0:
        status = "🟢 ОТЛИЧНО"
        message = "Проект готов к использованию!"
    elif total_issues <= 2:
        status = "🟡 ХОРОШО"  
        message = "Минорные проблемы, требуют внимания"
    else:
        status = "🔴 ТРЕБУЕТ ИСПРАВЛЕНИЙ"
        message = "Серьезные проблемы, требуют исправления"
    
    print(f"   Статус: {status}")
    print(f"   Проблем найдено: {total_issues}")
    print(f"   {message}")
    
    if total_issues == 0:
        print("\n🎉 Для полной проверки запустите: python comprehensive_test.py")
    else:
        print("\n🔧 Для детальной диагностики запустите: python comprehensive_test.py")
    
    return total_issues == 0

if __name__ == "__main__":
    try:
        success = quick_status()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Проверка прервана")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Ошибка: {e}")
        sys.exit(3)