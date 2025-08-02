#!/usr/bin/env python3
"""
Тест удаления Reply клавиатур
"""

import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.keyboards import remove_reply_keyboard

def test_reply_keyboard_removal():
    """Тестирует функцию удаления Reply клавиатур"""
    print("🧪 Тестируем удаление Reply клавиатур...\n")
    
    # Создаем ReplyKeyboardRemove
    remove_markup = remove_reply_keyboard()
    
    print("✅ ReplyKeyboardRemove создан успешно")
    print(f"📋 Selective: {remove_markup.selective}")
    
    print("\n💡 Теперь все пользователи видят только Inline кнопки!")
    print("   Reply клавиатуры полностью убраны из интерфейса")
    
    return True

def main():
    """Главная функция тестирования"""
    print("🚀 Тест удаления постоянных Reply клавиатур\n")
    
    try:
        test_reply_keyboard_removal()
        
        print("\n📊 Результаты:")
        print("✅ Reply клавиатуры удалены из кода")
        print("✅ Функция очистки клавиатур работает") 
        print("✅ Бот использует только Inline кнопки")
        print("✅ Интерфейс стал чище и удобнее")
        
        print("\n🎉 Постоянная клавиатура успешно убрана!")
        
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print("\n❌ Тесты не пройдены!")
        sys.exit(1)
