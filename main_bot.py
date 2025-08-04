#!/usr/bin/env python3
"""
Telegram Bot Project - Main Entry Point
A modular Telegram bot with organized handlers and utilities.
"""

import logging
import sys
import os
from datetime import datetime

# Bot framework imports
from telegram import Update
from telegram.ext import (
    Application, 
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# Configuration
from config import validate_config, BOT_TOKEN, ADMIN_ID

# Import all handlers
from handlers import (
    # User commands
    about_command,
    profile_command, 
    feedback_command,
    settings_command,
    
    # Admin commands  
    admin_command,
    stats_command,
    logs_command,
    restart_command,
    broadcast_command,
    cleanup_command,
    users_command,
    
    # Content commands
    random_command,
    popular_command,
    recent_command,
    categories_command,
    search_command,
    
    # Diagnostic commands
    ping_command,
    status_command,
    uptime_command,
    version_command,
    health_command,
    
    # Main menu and reactions
    show_main_menu,
    handle_reaction,
    show_post_reactions
)

# Import utilities
from utils.keyboards import create_main_menu_keyboard, create_back_to_menu_keyboard
from utils.exceptions import BotError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Conversation states
POST_TEXT, POST_MEDIA = range(2)

class TelegramBot:
    """Main bot class with organized handlers and error handling"""
    
    def __init__(self):
        """Initialize the bot with configuration validation"""
        try:
            validate_config()
            self.app = None
            self.start_time = datetime.now()
            logger.info("🤖 Bot initialized successfully")
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            sys.exit(1)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command with personalized welcome"""
        try:
            user = update.effective_user
            if not user or not update.message:
                return
                
            # Update user stats
            from handlers.stats import update_stats
            update_stats(user.id, user.username, user.first_name, "start")
                
            welcome_text = (
                f"👋 Привет, {user.first_name}!\n\n"
                f"🤖 Добро пожаловать в Telegram Bot Project!\n\n"
                f"🚀 **Возможности бота:**\n"
                f"• Интерактивное главное меню\n"
                f"• Система реакций на посты\n"
                f"• Административные команды\n"
                f"• Статистика и аналитика\n\n"
                f"📋 Используйте /help для получения справки\n"
                f"🔧 Или /menu для открытия главного меню"
            )
            
            # Show admin keyboard for admin users
            if user.id == ADMIN_ID:
                welcome_text += f"\n\n👑 Вы вошли как администратор"
                
            await update.message.reply_text(
                welcome_text, 
                parse_mode='Markdown',
                reply_markup=create_main_menu_keyboard()
            )
            
            logger.info(f"✅ Start command executed by user {user.id}")
            
        except Exception as e:
            logger.error(f"❌ Error in start command: {e}")
            if update.message:
                await update.message.reply_text("❌ Произошла ошибка при запуске бота")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command with comprehensive information"""
        try:
            if not update.message:
                return
                
            user = update.effective_user
            if user:
                from handlers.stats import update_stats
                update_stats(user.id, user.username, user.first_name, "help")
                
            help_text = (
                "📋 **Справка по командам**\n\n"
                "**🔧 Основные команды:**\n"
                "/start - Приветствие и начало работы\n"
                "/help - Эта справка\n"
                "/menu - Главное меню с категориями\n"
                "/about - О боте\n"
                "/profile - Ваш профиль\n"
                "/feedback - Обратная связь\n"
                "/settings - Настройки\n\n"
                "**📝 Контент:**\n"
                "/categories - Категории контента\n"
                "/random - Случайный пост\n"
                "/popular - Популярные посты\n"
                "/recent - Последние посты\n"
                "/search - Поиск по контенту\n\n"
                "**🔍 Диагностика:**\n"
                "/ping - Проверить отклик\n"
                "/status - Статус системы\n"
                "/uptime - Время работы\n"
                "/version - Версия бота\n"
                "/health - Проверка здоровья\n\n"
            )
            
            # Add admin commands if user is admin
            if user and user.id == ADMIN_ID:
                help_text += (
                    "**👑 Команды администратора:**\n"
                    "/admin - Админ панель\n"
                    "/stats - Статистика бота\n"
                    "/logs - Просмотр логов\n"
                    "/broadcast - Рассылка\n"
                    "/users - Список пользователей\n"
                    "/cleanup - Очистка системы\n"
                    "/restart - Перезапуск бота\n\n"
                )
            
            help_text += "ℹ️ Для получения подробной информации о команде используйте её"
            
            await update.message.reply_text(
                help_text, 
                parse_mode='Markdown',
                reply_markup=create_back_to_menu_keyboard()
            )
            
            logger.info(f"✅ Help command executed by user {user.id if user else 'Unknown'}")
            
        except Exception as e:
            logger.error(f"❌ Error in help command: {e}")
            if update.message:
                await update.message.reply_text("❌ Ошибка при получении справки")
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /menu command - show main menu"""
        try:
            if not update.message:
                return
                
            user = update.effective_user
            if user:
                from handlers.stats import update_stats
                update_stats(user.id, user.username, user.first_name, "menu")
                
            await update.message.reply_text(
                "🏠 **Главное меню**\n\nВыберите категорию:",
                parse_mode='Markdown',
                reply_markup=create_main_menu_keyboard()
            )
            
            logger.info(f"✅ Menu command executed by user {user.id if user else 'Unknown'}")
            
        except Exception as e:
            logger.error(f"❌ Error in menu command: {e}")
            if update.message:
                await update.message.reply_text("❌ Ошибка при отображении меню")
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /cancel command"""
        try:
            if not update.message:
                return ConversationHandler.END
                
            await update.message.reply_text(
                "❌ Операция отменена",
                reply_markup=create_back_to_menu_keyboard()
            )
            
            user = update.effective_user
            logger.info(f"✅ Cancel command executed by user {user.id if user else 'Unknown'}")
            
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"❌ Error in cancel command: {e}")
            return ConversationHandler.END
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands"""
        try:
            if not update.message:
                return
                
            await update.message.reply_text(
                "❓ Неизвестная команда.\n\n"
                "Используйте /help для списка доступных команд\n"
                "или /menu для главного меню.",
                reply_markup=create_back_to_menu_keyboard()
            )
            
            user = update.effective_user
            logger.info(f"⚠️ Unknown command from user {user.id if user else 'Unknown'}: {update.message.text}")
            
        except Exception as e:
            logger.error(f"❌ Error handling unknown command: {e}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Global error handler"""
        try:
            logger.error(f"❌ Update {update} caused error {context.error}")
            
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
                )
                
        except Exception as e:
            logger.error(f"❌ Error in error handler: {e}")
    
    def setup_handlers(self):
        """Setup all command and message handlers"""
        try:
            # Basic commands
            self.app.add_handler(CommandHandler("start", self.start_command))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("menu", self.menu_command))
            self.app.add_handler(CommandHandler("cancel", self.cancel_command))
            
            # User commands
            self.app.add_handler(CommandHandler("about", about_command))
            self.app.add_handler(CommandHandler("profile", profile_command))
            self.app.add_handler(CommandHandler("feedback", feedback_command))
            self.app.add_handler(CommandHandler("settings", settings_command))
            
            # Admin commands
            self.app.add_handler(CommandHandler("admin", admin_command))
            self.app.add_handler(CommandHandler("stats", stats_command))
            self.app.add_handler(CommandHandler("logs", logs_command))
            self.app.add_handler(CommandHandler("restart", restart_command))
            self.app.add_handler(CommandHandler("broadcast", broadcast_command))
            self.app.add_handler(CommandHandler("cleanup", cleanup_command))
            self.app.add_handler(CommandHandler("users", users_command))
            
            # Content commands
            self.app.add_handler(CommandHandler("categories", categories_command))
            self.app.add_handler(CommandHandler("random", random_command))
            self.app.add_handler(CommandHandler("popular", popular_command))
            self.app.add_handler(CommandHandler("recent", recent_command))
            self.app.add_handler(CommandHandler("search", search_command))
            
            # Diagnostic commands
            self.app.add_handler(CommandHandler("ping", ping_command))
            self.app.add_handler(CommandHandler("status", status_command))
            self.app.add_handler(CommandHandler("uptime", uptime_command))
            self.app.add_handler(CommandHandler("version", version_command))
            self.app.add_handler(CommandHandler("health", health_command))
            
            # Callback query handlers
            self.app.add_handler(CallbackQueryHandler(show_main_menu, pattern="main_menu"))
            self.app.add_handler(CallbackQueryHandler(handle_reaction, pattern="^reaction_"))
            self.app.add_handler(CallbackQueryHandler(show_post_reactions, pattern="^stats_"))
            
            # Handle unknown commands
            self.app.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
            
            # Global error handler
            self.app.add_error_handler(self.error_handler)
            
            logger.info("✅ All handlers set up successfully")
            
        except Exception as e:
            logger.error(f"❌ Error setting up handlers: {e}")
            raise
    
    def setup_webhook(self, webhook_url: str, port: int):
        """Setup webhook for production deployment"""
        try:
            logger.info(f"🌐 Setting up webhook: {webhook_url}")
            
            # Set webhook
            self.app.run_webhook(
                listen="0.0.0.0",
                port=port,
                webhook_url=webhook_url,
                url_path=BOT_TOKEN
            )
            
        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")
            raise
    
    def run(self):
        """Start the bot"""
        try:
            # Build application
            self.app = (
                ApplicationBuilder()
                .token(BOT_TOKEN)
                .connect_timeout(30.0)
                .read_timeout(30.0)
                .write_timeout(30.0)
                .pool_timeout(30.0)
                .build()
            )
            
            # Setup handlers
            self.setup_handlers()
            
            # Log startup
            logger.info("🚀 Starting Telegram Bot...")
            logger.info(f"📱 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-10:]}")
            logger.info(f"👤 Admin ID: {ADMIN_ID}")
            logger.info(f"🐍 Python: {sys.version}")
            logger.info(f"📁 Working Directory: {os.getcwd()}")
            
            # Check for webhook environment
            webhook_url = os.getenv('WEBHOOK_URL')
            port = int(os.getenv('PORT', 8000))
            
            if webhook_url:
                # Production webhook mode
                logger.info(f"🌐 Starting in webhook mode on port {port}")
                self.setup_webhook(webhook_url, port)
            else:
                # Development polling mode
                logger.info("🔄 Starting in polling mode")
                print("🤖 Bot is running... Press Ctrl+C to stop.")
                self.app.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            sys.exit(1)
        finally:
            logger.info("👋 Bot shutdown complete")

def main():
    """Main entry point"""
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()