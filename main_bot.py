# --- Импорт необходимых библиотек ---
from dotenv import load_dotenv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
import logging
from datetime import datetime
from telegram.constants import ChatAction

# --- Загрузка переменных окружения из .env ---
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Токен бота берётся из .env
ADMIN_ID = 345470935  # ID администратора
CHANNEL_ID = '@eto_vse_ty'  # username канала для публикации

# --- Логирование ---
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

# --- Фильтр запрещённых слов ---
FORBIDDEN_WORDS = ['badword1', 'badword2', 'spam']

# --- Состояния для ConversationHandler ---
POST_TEXT, POST_MEDIA = range(2)

# --- Админ-панель ---
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет доступа к админ-панели.")
        return
    keyboard = [
        [InlineKeyboardButton("Список команд", callback_data='commands')],
        [InlineKeyboardButton("Публикация поста", callback_data='post')],
        [InlineKeyboardButton("Просмотреть логи", callback_data='logs')],
        [InlineKeyboardButton("Отмена публикации", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Админ-панель:", reply_markup=reply_markup)

# --- Обработка нажатий на кнопки админ-панели ---
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not update.effective_user:
        return
    await query.answer()
    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("Нет доступа.")
        return
    if not hasattr(query, 'data') or query.data is None:
        await query.edit_message_text("Ошибка: нет данных для обработки.")
        return
    if query.data == 'commands':
        await query.edit_message_text(
            "Доступные команды:\n"
            "/start — приветствие и краткая справка\n"
            "/help — подробная справка\n"
            "/post — опубликовать пост (текст/медиа)\n"
            "/cancel — отменить публикацию\n"
            "/commands — список всех команд\n"
            "/admin — админ-панель"
        )
    elif query.data == 'post':
        await query.edit_message_text("Введите /post для публикации поста.")
    elif query.data == 'logs':
        try:
            with open('bot.log', 'r') as f:
                log_content = f.read()[-2000:]  # Показываем последние 2000 символов
            await query.edit_message_text(f"Последние логи:\n{log_content}")
        except Exception:
            await query.edit_message_text("Лог-файл не найден или пуст.")
    elif query.data == 'cancel':
        await query.edit_message_text("Публикация отменена. Используйте /cancel для отмены процесса.")

# --- Обработка команды /commands ---
async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — приветствие и краткая справка\n"
        "/help — подробная справка\n"
        "/post — опубликовать пост (текст/медиа)\n"
        "/cancel — отменить публикацию\n"
        "/commands — список всех команд"
    )

# --- Обработка команды /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "Привет! Я бот для публикации постов в канал.\n"
        "Доступные команды:\n"
        "/help — справка\n"
        "/post — опубликовать пост (текст/медиа)\n"
        "/cancel — отменить публикацию\n"
    )
    # Если пользователь — админ, сразу показываем админ-панель
    if update.effective_user and update.effective_user.id == ADMIN_ID:
        await admin_panel(update, context)

# --- Обработка команды /help ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "Я могу публиковать текст и медиа в канал.\n"
        "Только админ может публиковать.\n"
        "Команды:\n"
        "/post — начать публикацию поста\n"
        "/cancel — отменить публикацию\n"
        "Просто отправь текст или медиа после /post."
    )

# --- Обработка команды /cancel ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return ConversationHandler.END
    await update.message.reply_text("Публикация отменена.")
    return ConversationHandler.END

# --- Модерация и фильтр запрещённых слов ---
def contains_forbidden(text):
    return any(word.lower() in (text or '').lower() for word in FORBIDDEN_WORDS)

# --- ConversationHandler: публикация поста ---
async def post_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.message:
        return ConversationHandler.END
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет прав для публикации.")
        return ConversationHandler.END
    await update.message.reply_text("Отправьте текст или медиа для публикации, либо /cancel для отмены.")
    return POST_TEXT

async def post_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return ConversationHandler.END
    text = update.message.text or ""
    if contains_forbidden(text):
        await update.message.reply_text("В сообщении обнаружены запрещённые слова. Публикация отклонена.")
        logging.info(f"Отклонено сообщение с запрещёнными словами: {text}")
        return ConversationHandler.END
    if not text:
        await update.message.reply_text("Пустое сообщение не может быть опубликовано.")
        return POST_TEXT
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    await update.message.reply_text("Пост опубликован в канал!")
    logging.info(f"Опубликован текст: {text}")
    return ConversationHandler.END

async def post_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return ConversationHandler.END
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        if contains_forbidden(caption):
            await update.message.reply_text("В подписи обнаружены запрещённые слова. Публикация отклонена.")
            logging.info(f"Отклонено фото с запрещёнными словами: {caption}")
            return ConversationHandler.END
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=caption)
        await update.message.reply_text("Фото опубликовано в канал!")
        logging.info(f"Опубликовано фото: {caption}")
        return ConversationHandler.END
    if update.message.document:
        file_id = update.message.document.file_id
        caption = update.message.caption or ""
        if contains_forbidden(caption):
            await update.message.reply_text("В подписи обнаружены запрещённые слова. Публикация отклонена.")
            logging.info(f"Отклонён документ с запрещёнными словами: {caption}")
            return ConversationHandler.END
        await context.bot.send_document(chat_id=CHANNEL_ID, document=file_id, caption=caption)
        await update.message.reply_text("Документ опубликован в канал!")
        logging.info(f"Опубликован документ: {caption}")
        return ConversationHandler.END
    if update.message.video:
        file_id = update.message.video.file_id

# --- Запуск бота ---
if __name__ == '__main__':
    import sys
    print(f"Используется Python: {sys.executable}")
    if not BOT_TOKEN:
        print("[ОШИБКА] BOT_TOKEN не найден. Проверьте файл .env и переменную BOT_TOKEN.")
        exit(1)
    print("Инициализация Telegram-бота...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # Команды

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # ConversationHandler для публикации постов
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("post", post_start)],
        states={
            POST_TEXT: [MessageHandler(filters.TEXT & (~filters.COMMAND), post_text),
                        MessageHandler(filters.PHOTO | filters.Document.ALL | filters.VIDEO, post_media)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("commands", commands_command))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(admin_callback))
    print("Бот запущен. Ожидание сообщений... (Ctrl+C для остановки)")
    app.run_polling()
