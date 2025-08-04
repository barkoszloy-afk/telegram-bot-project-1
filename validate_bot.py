#!/usr/bin/env python3
# validate_bot.py - Финальная валидация готовности бота

import sys
import subprocess
import json
from datetime import datetime

def run_comprehensive_test():
    """Запускает комплексное тестирование"""
    print("🔍 Запуск комплексного тестирования...")
    try:
        result = subprocess.run([sys.executable, 'comprehensive_test.py'], 
                              capture_output=True, text=True, timeout=120)
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)

def check_bot_structure():
    """Проверяет структуру бота"""
    print("📁 Проверка структуры проекта...")
    
    required_structure = {
        'files': [
            'main_bot_railway.py',
            'config.py',
            'requirements.txt',
            'Dockerfile',
            'Procfile',
            '.env.example',
            'README.md'
        ],
        'directories': [
            'handlers',
            'utils',
            'tests',
            '.github/workflows'
        ]
    }
    
    missing = []
    import os
    
    for file in required_structure['files']:
        if not os.path.exists(file):
            missing.append(f"Файл: {file}")
    
    for directory in required_structure['directories']:
        if not os.path.exists(directory):
            missing.append(f"Директория: {directory}")
    
    if missing:
        print(f"❌ Отсутствуют: {', '.join(missing)}")
        return False
    else:
        print("✅ Структура проекта корректна")
        return True

def validate_configuration():
    """Проверяет конфигурацию"""
    print("⚙️ Проверка конфигурации...")
    
    try:
        from config import validate_config, BOT_TOKEN, ADMIN_ID
        validate_config()
        
        # Проверяем, что это не тестовый токен в продакшене
        if BOT_TOKEN and 'TEST' in BOT_TOKEN:
            print("⚠️ Используется тестовый токен")
            return False
        
        print("✅ Конфигурация валидна")
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_core_functionality():
    """Тестирует основную функциональность"""
    print("🧪 Тестирование основной функциональности...")
    
    try:
        # Тест импортов
        from handlers.admin import admin_command
        from handlers.reactions import handle_reaction
        from utils.keyboards import create_main_menu_keyboard
        from utils.database import Database
        
        # Тест создания клавиатуры
        keyboard = create_main_menu_keyboard()
        assert hasattr(keyboard, 'inline_keyboard')
        
        # Тест базы данных
        db = Database()
        assert hasattr(db, 'add_reaction')
        
        print("✅ Основная функциональность работает")
        return True
    except Exception as e:
        print(f"❌ Ошибка функциональности: {e}")
        return False

def check_deployment_readiness():
    """Проверяет готовность к развертыванию"""
    print("🚀 Проверка готовности к развертыванию...")
    
    checks = []
    
    # Проверка Railway конфигурации
    import os
    if os.path.exists('railway.json'):
        checks.append("✅ Railway конфигурация")
    else:
        checks.append("❌ Отсутствует railway.json")
    
    # Проверка Docker
    if os.path.exists('Dockerfile'):
        checks.append("✅ Docker конфигурация")
    else:
        checks.append("❌ Отсутствует Dockerfile")
    
    # Проверка Procfile
    if os.path.exists('Procfile'):
        checks.append("✅ Procfile для деплоя")
    else:
        checks.append("❌ Отсутствует Procfile")
    
    # Проверка CI/CD
    if os.path.exists('.github/workflows/ci.yml'):
        checks.append("✅ CI/CD pipeline")
    else:
        checks.append("❌ Отсутствует CI/CD")
    
    for check in checks:
        print(f"   {check}")
    
    failed_checks = [c for c in checks if c.startswith("❌")]
    return len(failed_checks) == 0

def generate_validation_report():
    """Генерирует отчет валидации"""
    print("\n" + "="*60)
    print("📋 ФИНАЛЬНЫЙ ОТЧЕТ ВАЛИДАЦИИ")
    print("="*60)
    
    # Запускаем все проверки
    results = {}
    
    # Comprehensive test
    comp_success, comp_details = run_comprehensive_test()
    results['comprehensive_test'] = (comp_success, comp_details if not comp_success else "")
    
    # Structure check
    struct_success = check_bot_structure()
    results['structure_check'] = (struct_success, "")
    
    # Configuration
    config_success = validate_configuration()
    results['configuration'] = (config_success, "")
    
    # Functionality
    func_success = test_core_functionality()
    results['functionality'] = (func_success, "")
    
    # Deployment
    deploy_success = check_deployment_readiness()
    results['deployment'] = (deploy_success, "")
    
    passed = 0
    total = len(results)
    
    for test_name, (success, details) in results.items():
        if success:
            passed += 1
            print(f"✅ {test_name}: ПРОЙДЕН")
        else:
            print(f"❌ {test_name}: ПРОВАЛЕН")
            if details:
                print(f"   └─ {details}")
    
    success_rate = passed / total
    
    print(f"\n📊 Результаты валидации:")
    print(f"   Всего проверок: {total}")
    print(f"   Пройдено: {passed}")
    print(f"   Успешность: {success_rate:.1%}")
    
    # Определяем статус готовности
    if success_rate >= 0.9:
        status = "🟢 ГОТОВ К РАЗВЕРТЫВАНИЮ"
        recommendation = "Бот готов к развертыванию в продакшен"
    elif success_rate >= 0.7:
        status = "🟡 ЧАСТИЧНО ГОТОВ"
        recommendation = "Требуются минорные исправления"
    else:
        status = "🔴 НЕ ГОТОВ"
        recommendation = "Требуются серьезные исправления"
    
    print(f"\n🎯 Статус: {status}")
    print(f"💡 Рекомендация: {recommendation}")
    
    # Сохраняем отчет
    report = {
        'timestamp': datetime.now().isoformat(),
        'validation_results': results,
        'summary': {
            'total_checks': total,
            'passed_checks': passed,
            'success_rate': success_rate,
            'status': status,
            'recommendation': recommendation
        }
    }
    
    with open('validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Детальный отчет сохранен в: validation_report.json")
    
    return success_rate >= 0.8

def main():
    """Основная функция"""
    print("🚀 ФИНАЛЬНАЯ ВАЛИДАЦИЯ TELEGRAM БОТА")
    print("="*60)
    
    try:
        success = generate_validation_report()
        
        if success:
            print("\n🎉 ВАЛИДАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
            print("✅ Бот готов к использованию")
            sys.exit(0)
        else:
            print("\n⚠️ ВАЛИДАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ")
            print("❌ Требуются дополнительные исправления")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Валидация прервана пользователем")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Критическая ошибка валидации: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()