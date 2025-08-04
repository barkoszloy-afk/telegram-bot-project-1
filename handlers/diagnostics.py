# handlers/diagnostics.py - Диагностические команды
import logging
import os
import psutil
import time
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

logger = logging.getLogger(__name__)

# Время запуска бота
bot_start_time = time.time()

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /ping - проверка отклика бота"""
    try:
        start_time = time.time()
        message = await update.message.reply_text("🏓 Pong!")
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)
        
        await message.edit_text(
            f"🏓 Pong!\n"
            f"⚡ Время отклика: {response_time}ms\n"
            f"🕐 Время сервера: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        logger.info(f"🏓 Ping от пользователя {update.effective_user.id}: {response_time}ms")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /ping: {e}")
        await update.message.reply_text("❌ Ошибка при выполнении ping")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /status - статус системы (только для админа)"""
    try:
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        # Получаем системную информацию
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        uptime = datetime.now() - datetime.fromtimestamp(bot_start_time)
        uptime_str = str(uptime).split('.')[0]  # Убираем микросекунды
        
        status_text = (
            "📊 **Статус системы**\n\n"
            f"🤖 **Бот**\n"
            f"⏱ Время работы: {uptime_str}\n"
            f"🆔 PID: {os.getpid()}\n\n"
            f"💾 **Память**\n"
            f"📈 Использовано: {memory.percent}%\n"
            f"📊 Доступно: {memory.available // (1024**2)} MB\n\n"
            f"💽 **Диск**\n"
            f"📈 Использовано: {disk.percent}%\n"
            f"📊 Свободно: {disk.free // (1024**3)} GB\n\n"
            f"⚙️ **CPU**\n"
            f"📈 Загрузка: {cpu_percent}%\n"
            f"🔧 Ядер: {psutil.cpu_count()}"
        )
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
        logger.info(f"📊 Статус системы запрошен пользователем {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /status: {e}")
        await update.message.reply_text("❌ Ошибка при получении статуса")

async def uptime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /uptime - время работы бота"""
    try:
        uptime = datetime.now() - datetime.fromtimestamp(bot_start_time)
        uptime_str = str(uptime).split('.')[0]  # Убираем микросекунды
        
        uptime_text = (
            f"⏰ **Время работы бота**\n\n"
            f"🚀 Запущен: {datetime.fromtimestamp(bot_start_time).strftime('%d.%m.%Y %H:%M:%S')}\n"
            f"⏱ Работает: {uptime_str}\n"
            f"📅 Текущее время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
        
        await update.message.reply_text(uptime_text, parse_mode='Markdown')
        logger.info(f"⏰ Uptime запрошен пользователем {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /uptime: {e}")
        await update.message.reply_text("❌ Ошибка при получении времени работы")

async def version_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /version - версия бота и компонентов"""
    try:
        import telegram
        import sys
        
        version_text = (
            f"🔖 **Версия бота**\n\n"
            f"🤖 Бот: v1.0.0\n"
            f"🐍 Python: {sys.version.split()[0]}\n"
            f"📱 python-telegram-bot: {telegram.__version__}\n"
            f"🖥 Система: {os.name}\n"
            f"📦 Платформа: Railway\n"
            f"🔄 Последнее обновление: {datetime.now().strftime('%d.%m.%Y')}"
        )
        
        await update.message.reply_text(version_text, parse_mode='Markdown')
        logger.info(f"🔖 Версия запрошена пользователем {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /version: {e}")
        await update.message.reply_text("❌ Ошибка при получении версии")

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /health - проверка здоровья системы"""
    try:
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        # Проверки здоровья системы
        checks = []
        
        # Проверка памяти
        memory = psutil.virtual_memory()
        if memory.percent < 90:
            checks.append("✅ Память: OK")
        else:
            checks.append("⚠️ Память: Высокое использование")
        
        # Проверка диска
        disk = psutil.disk_usage('/')
        if disk.percent < 90:
            checks.append("✅ Диск: OK")
        else:
            checks.append("⚠️ Диск: Мало места")
        
        # Проверка CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent < 80:
            checks.append("✅ CPU: OK")
        else:
            checks.append("⚠️ CPU: Высокая загрузка")
        
        # Проверка времени работы
        uptime = time.time() - bot_start_time
        if uptime > 60:  # Больше минуты
            checks.append("✅ Время работы: OK")
        else:
            checks.append("⚠️ Время работы: Недавно перезапущен")
        
        # Проверка базы данных (если есть)
        try:
            from utils.database import reactions_db
            # Простая проверка
            reactions_db.get_post_reactions("test")
            checks.append("✅ База данных: OK")
        except Exception:
            checks.append("❌ База данных: Ошибка")
        
        health_text = (
            f"🏥 **Проверка здоровья системы**\n\n"
            + "\n".join(checks)
        )
        
        await update.message.reply_text(health_text, parse_mode='Markdown')
        logger.info(f"🏥 Health check запрошен пользователем {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /health: {e}")
        await update.message.reply_text("❌ Ошибка при проверке здоровья системы")
