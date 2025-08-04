# handlers/reactions.py - Обработчики реакций
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils.database import reactions_db
from utils.keyboards import create_main_menu_keyboard
from config import REACTION_EMOJIS

logger = logging.getLogger(__name__)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает главное меню"""
    query = update.callback_query
    if not query:
        return

    try:
        menu_text = (
            "🏠 **Главное меню**\n\n"
            "Выберите интересующую вас категорию:"
        )
        
        await query.edit_message_text(
            menu_text,
            parse_mode='Markdown',
            reply_markup=create_main_menu_keyboard()
        )
        
        await query.answer("🏠 Главное меню")
        logger.info(f"🏠 Главное меню показано пользователю {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка показа главного меню: {e}")
        try:
            await query.answer("❌ Произошла ошибка")
        except Exception:
            pass

async def handle_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик реакций на посты"""
    query = update.callback_query
    if not query or not query.data:
        return

    try:
        # Парсим данные callback
        if not query.data.startswith("reaction_"):
            return
        
        parts = query.data.split("_")
        if len(parts) < 3:
            return
        
        reaction_idx = int(parts[1])
        post_id = parts[2]
        
        if reaction_idx >= len(REACTION_EMOJIS):
            await query.answer("❌ Неверная реакция")
            return
        
        user_id = query.from_user.id
        reaction = REACTION_EMOJIS[reaction_idx]
        
        # Сохраняем реакцию
        reactions_db.add_reaction(user_id, post_id, reaction)
        
        await query.answer(f"Вы поставили {reaction}")
        logger.info(f"📝 Пользователь {user_id} поставил {reaction} на пост {post_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки реакции: {e}")
        try:
            await query.answer("❌ Произошла ошибка")
        except Exception:
            pass

async def show_post_reactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает статистику реакций на пост"""
    query = update.callback_query
    if not query or not query.data:
        return

    try:
        if not query.data.startswith("stats_"):
            return
        
        post_id = query.data.split("_")[1]
        reactions = reactions_db.get_post_reactions(post_id)
        
        if not reactions:
            await query.answer("На этот пост пока нет реакций")
            return
        
        stats_text = "📊 Статистика реакций:\n\n"
        for reaction, count in reactions.items():
            stats_text += f"{reaction} {count}\n"
        
        await query.answer(stats_text, show_alert=True)
        logger.info(f"📊 Показана статистика для поста {post_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка показа статистики: {e}")
        try:
            await query.answer("❌ Произошла ошибка")
        except Exception:
            pass
