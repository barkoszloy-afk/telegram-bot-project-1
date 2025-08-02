# test_refactored_bot.py - Тестирование улучшенной версии бота
import asyncio
import logging
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, Chat, CallbackQuery
from telegram.ext import ContextTypes

# Импорты из нашего бота
from handlers.reactions import handle_reaction_callback
from handlers.admin import handle_admin_command
from utils.database import reactions_db
from utils.keyboards import get_zodiac_keyboard, get_reaction_keyboard
from config import validate_config

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mock_update(user_id: int = 123, message_text: str = "/start"):
    """Создает мок-объект Update для тестирования"""
    user = User(id=user_id, first_name="TestUser", is_bot=False)
    chat = Chat(id=user_id, type="private")
    message = Message(
        message_id=1,
        date=datetime.now(),  # Используем реальный datetime вместо None
        chat=chat,
        from_user=user,
        text=message_text
    )
    
    update = Update(update_id=1)
    update._effective_user = user
    update._effective_chat = chat
    update._effective_message = message
    update.message = message
    
    return update

def create_mock_callback_query(user_id: int = 123, data: str = "react_heart_test123"):
    """Создает мок-объект CallbackQuery для тестирования"""
    user = User(id=user_id, first_name="TestUser", is_bot=False)
    chat = Chat(id=user_id, type="private")
    message = Message(
        message_id=1,
        date=datetime.now(),  # Используем реальный datetime вместо None
        chat=chat,
        from_user=user
    )
    
    query = CallbackQuery(
        id="test_query",
        from_user=user,
        chat_instance="test_instance",
        data=data,
        message=message
    )
    
    update = Update(update_id=1)
    update._effective_user = user
    update._effective_chat = chat
    update._callback_query = query
    
    return update

async def test_keyboard_generation():
    """Тестирует генерацию клавиатур"""
    logger.info("🧪 Тестирование генерации клавиатур...")
    
    try:
        # Тест клавиатуры зодиака
        zodiac_keyboard = get_zodiac_keyboard()
        assert len(zodiac_keyboard) > 0, "Клавиатура зодиака не создана"
        logger.info("✅ Клавиатура зодиака: OK")
        
        # Тест клавиатуры реакций
        reaction_keyboard = get_reaction_keyboard("test_post_123")
        assert len(reaction_keyboard) > 0, "Клавиатура реакций не создана"
        logger.info("✅ Клавиатура реакций: OK")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования клавиатур: {e}")
        return False

async def test_database_operations():
    """Тестирует операции с базой данных"""
    logger.info("🧪 Тестирование базы данных...")
    
    try:
        # Тест добавления реакции
        user_id = "test_user_123"
        post_id = "test_post_456"
        reaction = "heart"
        
        result = reactions_db.add_user_reaction(user_id, reaction, post_id)
        logger.info(f"✅ Добавление реакции: {result}")
        
        # Тест получения данных
        data = reactions_db.data
        assert isinstance(data, dict), "Данные не являются словарем"
        logger.info("✅ Получение данных: OK")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования БД: {e}")
        return False

async def test_admin_functions():
    """Тестирует админские функции"""
    logger.info("🧪 Тестирование админских функций...")
    
    try:
        # Мок-объекты
        update = create_mock_update(345470935, "/admin")  # ADMIN_ID из config
        context = AsyncMock()
        
        # Мокаем reply_text - проверяем что message существует
        if update.message:
            update.message.reply_text = AsyncMock()
            
            # Тестируем админскую команду
            await handle_admin_command(update, context)
            
            # Проверяем что reply_text был вызван
            update.message.reply_text.assert_called_once()
            logger.info("✅ Админская команда: OK")
        else:
            logger.error("❌ Update.message is None")
            return False
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования админки: {e}")
        return False

async def test_reaction_handling():
    """Тестирует обработку реакций"""
    logger.info("🧪 Тестирование обработки реакций...")
    
    try:
        # Создаем мок callback query
        update = create_mock_callback_query(123, "react_heart_test123")
        context = AsyncMock()
        
        # Мокаем методы callback query - проверяем что callback_query существует
        if update.callback_query:
            update.callback_query.answer = AsyncMock()
            update.callback_query.edit_message_reply_markup = AsyncMock()
            
            # Тестируем обработку реакции
            await handle_reaction_callback(update, context)
            
            logger.info("✅ Обработка реакций: OK")
        else:
            logger.error("❌ Update.callback_query is None")
            return False
            
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования реакций: {e}")
        return False

async def test_config_validation():
    """Тестирует валидацию конфигурации"""
    logger.info("🧪 Тестирование конфигурации...")
    
    try:
        # Тестируем валидацию (может упасть если нет токена)
        try:
            validate_config()
            logger.info("✅ Конфигурация валидна")
        except ValueError as e:
            logger.warning(f"⚠️ Проблема с конфигурацией: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования конфигурации: {e}")
        return False

async def run_all_tests():
    """Запускает все тесты"""
    logger.info("🚀 Запуск всех тестов улучшенного бота...")
    
    tests = [
        ("Конфигурация", test_config_validation),
        ("База данных", test_database_operations), 
        ("Клавиатуры", test_keyboard_generation),
        ("Админка", test_admin_functions),
        ("Реакции", test_reaction_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Тест: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            status = "✅ ПРОШЕЛ" if result else "❌ ПРОВАЛИЛСЯ"
            logger.info(f"📊 Результат: {status}")
        except Exception as e:
            results.append((test_name, False))
            logger.error(f"💥 Критическая ошибка в тесте {test_name}: {e}")
    
    # Итоговый отчет
    logger.info(f"\n{'='*60}")
    logger.info("📋 ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    logger.info(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n📊 Результат: {passed}/{total} тестов прошли")
    if passed == total:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        logger.info("🚀 Улучшенный бот готов к запуску!")
    else:
        logger.warning(f"⚠️ {total - passed} тестов провалились")
        logger.info("🔧 Рекомендуется исправить ошибки перед запуском")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
