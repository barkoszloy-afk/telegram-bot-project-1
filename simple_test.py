# simple_test.py - Простая проверка основного функционала
import logging
from config import validate_config, ZODIAC_SIGNS, REACTION_EMOJIS
from utils.database import reactions_db
from utils.keyboards import get_zodiac_keyboard, get_reaction_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """Простая проверка основного функционала"""
    try:
        logger.info("🧪 Тестирование основного функционала...")
        
        # 1. Проверка конфигурации
        logger.info("📋 Проверка конфигурации...")
        validate_config()
        assert len(ZODIAC_SIGNS) > 0, "Знаки зодиака не настроены"
        assert len(REACTION_EMOJIS) > 0, "Реакции не настроены"
        logger.info("✅ Конфигурация: OK")
        
        # 2. Проверка базы данных
        logger.info("💾 Проверка базы данных...")
        data = reactions_db.data
        assert isinstance(data, dict), "Данные не являются словарем"
        
        # Добавление тестовой реакции
        result = reactions_db.add_user_reaction("test_123", "heart", "post_456")
        logger.info(f"   Результат добавления реакции: {result}")
        logger.info("✅ База данных: OK")
        
        # 3. Проверка клавиатур
        logger.info("⌨️ Проверка клавиатур...")
        zodiac_kb = get_zodiac_keyboard()
        assert len(zodiac_kb) > 0, "Клавиатура зодиака пустая"
        
        reaction_kb = get_reaction_keyboard("test_post")
        assert len(reaction_kb) > 0, "Клавиатура реакций пустая"
        logger.info("✅ Клавиатуры: OK")
        
        # 4. Проверка импортов
        logger.info("📦 Проверка импортов...")
        from handlers.admin import handle_admin_command
        from handlers.reactions import handle_reaction_callback
        logger.info("✅ Импорты: OK")
        
        logger.info("\n🎉 ВСЕ ОСНОВНЫЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        logger.info("🚀 Бот готов к запуску!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n" + "="*50)
        print("✅ УСПЕШНО: Все основные компоненты работают!")
        print("🚀 Можно запускать бота: python main_bot.py")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ ОШИБКА: Обнаружены проблемы в коде")
        print("🔧 Нужно исправить ошибки перед запуском")
        print("="*50)
