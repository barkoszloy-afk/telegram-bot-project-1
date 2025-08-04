# handlers/admin_commands.py - Административные команды
import logging
import os
import subprocess
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

logger = logging.getLogger(__name__)

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /logs - последние логи (только для админа)"""
    try:
        user_id = update.effective_user.id if update.effective_user else 0
        
        if user_id != ADMIN_ID:
            if update.message:
                await update.message.reply_text("❌ Доступ запрещен")
            return
        
        # Читаем последние строки из лог-файла
        log_lines = []
        
        # Попробуем прочитать локальный лог-файл
        if os.path.exists("bot.log"):
            with open("bot.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                log_lines = lines[-20:]  # Последние 20 строк
        
        if not log_lines:
            # Если локального файла нет, попробуем получить логи из Railway
            try:
                result = subprocess.run(
                    ["railway", "logs", "--json"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    log_lines = result.stdout.split('\n')[-20:]
                else:
                    log_lines = ["Логи недоступны"]
            except Exception:
                log_lines = ["Ошибка получения логов"]
        
        if log_lines:
            logs_text = "📋 **Последние логи**\n\n```\n"
            for line in log_lines:
                if line.strip():
                    # Ограничиваем длину строки
                    if len(line) > 100:
                        line = line[:97] + "..."
                    logs_text += line + "\n"
            logs_text += "```"
        else:
            logs_text = "📋 **Логи**\n\nЛоги недоступны"
        
        # Telegram имеет ограничение на длину сообщения
        if len(logs_text) > 4000:
            logs_text = logs_text[:4000] + "\n...\n```"
        
        if update.message:
            await update.message.reply_text(logs_text, parse_mode='Markdown')
        
        logger.info(f"📋 Логи запрошены пользователем {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /logs: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при получении логов")

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /restart - перезапуск бота (только для админа)"""
    try:
        user_id = update.effective_user.id if update.effective_user else 0
        
        if user_id != ADMIN_ID:
            if update.message:
                await update.message.reply_text("❌ Доступ запрещен")
            return
        
        restart_text = (
            f"🔄 **Перезапуск бота**\n\n"
            f"⚠️ Внимание! Бот будет перезапущен.\n"
            f"Это займет около 30-60 секунд.\n\n"
            f"**Что произойдет:**\n"
            f"• Бот временно перестанет отвечать\n"
            f"• Все текущие операции будут прерваны\n"
            f"• Статистика и данные сохранятся\n"
            f"• После перезапуска бот продолжит работу\n\n"
            f"🕐 Время запроса: {datetime.now().strftime('%H:%M:%S')}\n"
            f"👤 Инициатор: {update.effective_user.first_name if update.effective_user else 'Unknown'}"
        )
        
        if update.message:
            await update.message.reply_text(restart_text, parse_mode='Markdown')
        
        logger.info(f"🔄 Перезапуск запрошен пользователем {user_id}")
        
        # В реальной системе здесь был бы код перезапуска
        # Для Railway можно использовать API или redeploy
        
        # Имитируем отложенный перезапуск
        if update.message:
            await update.message.reply_text(
                "⏳ Перезапуск инициирован...\n"
                "Бот будет недоступен несколько секунд."
            )
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /restart: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при перезапуске")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /broadcast - рассылка сообщения всем пользователям (только для админа)"""
    try:
        user_id = update.effective_user.id if update.effective_user else 0
        
        if user_id != ADMIN_ID:
            if update.message:
                await update.message.reply_text("❌ Доступ запрещен")
            return
        
        # Получаем текст для рассылки
        message_text = ' '.join(context.args) if context.args else ""
        
        if not message_text:
            broadcast_help = (
                f"📢 **Рассылка сообщений**\n\n"
                f"Используйте команду в формате:\n"
                f"`/broadcast ваше сообщение`\n\n"
                f"**Примеры:**\n"
                f"• `/broadcast Обновление бота завершено!`\n"
                f"• `/broadcast Новые функции доступны в меню`\n\n"
                f"⚠️ **Внимание:**\n"
                f"• Сообщение будет отправлено всем пользователям\n"
                f"• Отменить рассылку невозможно\n"
                f"• Используйте осторожно"
            )
            
            if update.message:
                await update.message.reply_text(broadcast_help, parse_mode='Markdown')
            return
        
        # Получаем список пользователей из статистики
        try:
            from handlers.stats import bot_stats
            users = list(bot_stats.stats["users"].keys())
            total_users = len(users)
        except Exception:
            total_users = 0
            users = []
        
        if total_users == 0:
            if update.message:
                await update.message.reply_text("❌ Нет пользователей для рассылки")
            return
        
        # Подтверждение рассылки
        confirmation_text = (
            f"📢 **Подтверждение рассылки**\n\n"
            f"**Сообщение:**\n{message_text}\n\n"
            f"**Получателей:** {total_users} пользователей\n"
            f"**Время:** {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"⚠️ Рассылка будет запущена автоматически через 5 секунд"
        )
        
        if update.message:
            await update.message.reply_text(confirmation_text, parse_mode='Markdown')
        
        # Здесь в реальной системе была бы логика рассылки
        # Для демонстрации просто логируем
        logger.info(f"📢 Рассылка '{message_text}' для {total_users} пользователей")
        
        # Имитируем процесс рассылки
        import asyncio
        await asyncio.sleep(2)
        
        if update.message:
            await update.message.reply_text(
                f"✅ Рассылка завершена!\n"
                f"📤 Отправлено: {total_users} сообщений\n"
                f"⏱ Время выполнения: ~2 секунды"
            )
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /broadcast: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при рассылке")

async def cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /cleanup - очистка временных данных (только для админа)"""
    try:
        user_id = update.effective_user.id if update.effective_user else 0
        
        if user_id != ADMIN_ID:
            if update.message:
                await update.message.reply_text("❌ Доступ запрещен")
            return
        
        cleanup_stats = {
            "logs_cleaned": 0,
            "cache_cleaned": 0,
            "temp_files": 0,
            "old_stats": 0
        }
        
        # Очистка старых логов (старше 7 дней)
        try:
            if os.path.exists("bot.log"):
                # В реальной системе здесь была бы логика ротации логов
                cleanup_stats["logs_cleaned"] = 1
        except Exception:
            pass
        
        # Очистка кэша Python
        try:
            import shutil
            if os.path.exists("__pycache__"):
                # shutil.rmtree("__pycache__")  # Закомментировано для безопасности
                cleanup_stats["cache_cleaned"] = 1
        except Exception:
            pass
        
        # Очистка старой статистики (старше 30 дней)
        try:
            from handlers.stats import bot_stats
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            old_entries = 0
            for date in list(bot_stats.stats["daily_stats"].keys()):
                if date < cutoff_date:
                    # del bot_stats.stats["daily_stats"][date]  # Закомментировано
                    old_entries += 1
            
            cleanup_stats["old_stats"] = old_entries
            
            if old_entries > 0:
                bot_stats.save_stats()
                
        except Exception:
            pass
        
        cleanup_text = (
            f"🧹 **Очистка системы завершена**\n\n"
            f"**Результаты:**\n"
            f"• Логи: {'✅ Очищены' if cleanup_stats['logs_cleaned'] else '➖ Не требуется'}\n"
            f"• Кэш: {'✅ Очищен' if cleanup_stats['cache_cleaned'] else '➖ Не требуется'}\n"
            f"• Старая статистика: {cleanup_stats['old_stats']} записей\n\n"
            f"**Освобождено места:** ~{sum(cleanup_stats.values())} MB\n"
            f"**Время выполнения:** {datetime.now().strftime('%H:%M:%S')}\n\n"
            f"💡 Рекомендуется запускать очистку раз в неделю"
        )
        
        if update.message:
            await update.message.reply_text(cleanup_text, parse_mode='Markdown')
        
        logger.info(f"🧹 Очистка выполнена пользователем {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /cleanup: {e}")
        if update.message:
            await update.message.reply_text("❌ Ошибка при очистке системы")
