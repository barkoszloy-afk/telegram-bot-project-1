# handlers/user_commands.py - Пользовательские команды
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /about - информация о боте"""
    try:
        about_text = (
            f"🤖 **О боте**\n\n"
            f"**Название:** Telegram Bot Project\n"
            f"**Версия:** 1.0.0\n"
            f"**Создан:** 2025\n"
            f"**Платформа:** Railway\n\n"
            f"📋 **Возможности:**\n"
            f"• Главное меню с категориями\n"
            f"• Система реакций на посты\n"
            f"• Административные команды\n"
            f"• Статистика использования\n"
            f"• Диагностика системы\n\n"
            f"🔧 **Технологии:**\n"
            f"• Python 3.11+\n"
            f"• python-telegram-bot\n"
            f"• Railway Cloud\n"
            f"• Webhook архитектура\n\n"
            f"📞 **Поддержка:**\n"
            f"Используйте команду /help для получения справки\n"
            f"или /feedback для обратной связи"
        )
        
        if update.message:
            await update.message.reply_text(about_text, parse_mode='Markdown')
        
        logger.info(f"ℹ️ О боте запрошено пользователем {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /about: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении информации о боте")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /profile - профиль пользователя"""
    try:
        user = update.effective_user
        if not user:
            return
            
        # Получаем информацию о пользователе
        user_id = user.id
        username = user.username or "Не указан"
        first_name = user.first_name or "Не указано"
        last_name = user.last_name or ""
        language_code = user.language_code or "Не определен"
        
        # Пытаемся получить дополнительную информацию из статистики
        try:
            from handlers.stats import bot_stats
            user_stats = bot_stats.stats["users"].get(str(user_id), {})
            
            first_seen = user_stats.get("first_seen", "Не известно")
            last_seen = user_stats.get("last_seen", "Не известно")
            message_count = user_stats.get("message_count", 0)
            commands_used = user_stats.get("commands_used", {})
            
            # Самая используемая команда
            if commands_used:
                favorite_command = max(commands_used.items(), key=lambda x: x[1])
                favorite_cmd_text = f"/{favorite_command[0]} ({favorite_command[1]} раз)"
            else:
                favorite_cmd_text = "Нет данных"
            
        except Exception:
            first_seen = "Не известно"
            last_seen = "Не известно"
            message_count = 0
            favorite_cmd_text = "Нет данных"
        
        profile_text = (
            f"👤 **Ваш профиль**\n\n"
            f"**Основная информация:**\n"
            f"• ID: `{user_id}`\n"
            f"• Имя: {first_name} {last_name}".strip() + "\n"
            f"• Username: {username if username != 'Не указан' else 'Не указан'}\n"
            f"• Язык: {language_code}\n\n"
            f"**Статистика использования:**\n"
            f"• Первое посещение: {first_seen}\n"
            f"• Последняя активность: {last_seen}\n"
            f"• Отправлено сообщений: {message_count}\n"
            f"• Любимая команда: {favorite_cmd_text}\n\n"
            f"🕐 **Текущее время:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
        
        if update.message:
            await update.message.reply_text(profile_text, parse_mode='Markdown')
        
        logger.info(f"👤 Профиль запрошен пользователем {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /profile: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении профиля")

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /feedback - обратная связь"""
    try:
        feedback_text = (
            f"📝 **Обратная связь**\n\n"
            f"Спасибо за интерес к улучшению бота!\n\n"
            f"**Как оставить отзыв:**\n"
            f"1. Опишите вашу проблему или предложение\n"
            f"2. Укажите, в какой команде возникла проблема\n"
            f"3. Напишите, что вы ожидали увидеть\n\n"
            f"**Контакты для обратной связи:**\n"
            f"• Создайте issue в GitHub репозитории\n"
            f"• Напишите администратору бота\n"
            f"• Используйте команду /help для справки\n\n"
            f"**Популярные запросы:**\n"
            f"• Добавление новых команд\n"
            f"• Улучшение интерфейса\n"
            f"• Исправление ошибок\n"
            f"• Новые возможности\n\n"
            f"Ваши отзывы помогают делать бота лучше! 🚀"
        )
        
        if update.message:
            await update.message.reply_text(feedback_text, parse_mode='Markdown')
        
        logger.info(f"📝 Обратная связь запрошена пользователем {update.effective_user.id if update.effective_user else 'Unknown'}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /feedback: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении информации об обратной связи")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /settings - настройки пользователя"""
    try:
        user = update.effective_user
        if not user:
            return
            
        settings_text = (
            f"⚙️ **Настройки пользователя**\n\n"
            f"В данный момент доступны следующие настройки:\n\n"
            f"**Язык интерфейса:**\n"
            f"• Текущий: Русский 🇷🇺\n"
            f"• Доступные: Русский\n\n"
            f"**Уведомления:**\n"
            f"• Реакции на посты: ✅ Включены\n"
            f"• Системные сообщения: ✅ Включены\n\n"
            f"**Отображение:**\n"
            f"• Формат времени: 24-часовой\n"
            f"• Временная зона: UTC\n\n"
            f"**Приватность:**\n"
            f"• Сбор статистики: ✅ Включен\n"
            f"• История команд: ✅ Включена\n\n"
            f"🔧 Дополнительные настройки будут добавлены в будущих обновлениях.\n"
            f"Используйте /feedback для предложений!"
        )
        
        if update.message:
            await update.message.reply_text(settings_text, parse_mode='Markdown')
        
        logger.info(f"⚙️ Настройки запрошены пользователем {user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /settings: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении настроек")
