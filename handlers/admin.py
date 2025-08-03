# handlers/admin.py - Административные команды
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID

logger = logging.getLogger(__name__)

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin - административная панель"""
    try:
        user_id = update.effective_user.id if update.effective_user else 0
        
        if not update.message:
            return
            
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ У вас нет прав администратора")
            return
        
        admin_text = """🛠️ Административная панель

📊 Доступные команды:
/stats - Статистика бота
/users - Список пользователей
/broadcast - Рассылка сообщений

🔧 Статус: Активен
👤 Администратор: Подтвержден"""

        await update.message.reply_text(admin_text)
        logger.info(f"✅ Админ команда выполнена для {user_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка в admin_command: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /stats - статистика бота"""
    try:
        user_id = update.effective_user.id if update.effective_user else 0
        
        if not update.message:
            return
            
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ У вас нет прав администратора")
            return
        
        stats_text = """📊 Статистика бота

👤 Пользователи: 1
📝 Сообщений: 0
🔄 Время работы: активен

🤖 Статус: Работает стабильно"""

        await update.message.reply_text(stats_text)
        logger.info(f"✅ Команда stats выполнена для {user_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка в stats_command: {e}")
