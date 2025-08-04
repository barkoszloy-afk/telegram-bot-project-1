# --- Основная reply-клавиатура для админа ---
MAIN_KEYBOARD = [
    ["Посты", "📝 Пост", "📄 Логи"],
    ["🛠️ Админ-панель", "📋 Команды"],
    ["❌ Отмена", "ℹ️ Помощь"]
]

# Клавиатура для раздела "Посты"
POSTS_KEYBOARD = [
    ["Гороскоп", "Карта дня"],
    ["Вечернее послание", "Доброе утро"],
    ["Лунный прогноз", "Свободная публикация"],
    ["⬅️ Назад"]
]
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    BOT_TOKEN,
    ADMIN_ID,
    REACTION_EMOJIS,
    REACTION_NAMES,
    ZODIAC_SIGNS,
)
from pathlib import Path


# --- Константы ---
CHANNEL_ID = '@eto_vse_ty'  # username канала для публикации

# --- Реакции ---
REACTION_MESSAGES = [
    "Спасибо за сердечко!",
    "Спасибо за поддержку!",
    "Спасибо за эмоции!",
]


def get_reaction_keyboard(reactions):
    if len(REACTION_EMOJIS) != len(REACTION_NAMES):
        raise ValueError("REACTION_EMOJIS and REACTION_NAMES lengths mismatch")
    return [[
        InlineKeyboardButton(
            f"{REACTION_EMOJIS[i]} {reactions.get(REACTION_NAMES[i], 0)}",
            callback_data=f"react_{REACTION_NAMES[i]}"
        )
        for i in range(len(REACTION_EMOJIS))
    ]]

ZODIAC_INLINE_KEYBOARD = [
    [InlineKeyboardButton(f"{emoji} {name}", callback_data=f"zodiac_{name}")] for name, emoji in ZODIAC_SIGNS
]
# --- Приветственный баннер ---
WELCOME_BANNER = (
    "<b>👋 Добро пожаловать!</b>\n"
    "────────────────────────\n"
    "<i>Я помогу опубликовать пост в канал.</i>\n"
)
# --- Общий красиво оформленный текст команд ---
COMMANDS_TEXT = (
    "<b>📋 Доступные команды:</b>\n"
    "\n"
    "<b>🤖 /start</b> — приветствие и краткая справка\n"
    "<b>ℹ️ /help</b> — подробная справка\n"
    "<b>📝 /post</b> — опубликовать пост (текст/медиа)\n"
    "<b>❌ /cancel</b> — отменить публикацию\n"
    "<b>📃 /commands</b> — список всех команд\n"
    "<b>🛠️ /admin</b> — админ-панель (только для администратора)\n"
    "<b>📊 /stats</b> — статистика (только для администратора)\n"
    "<b>⚙️ /settings</b> — настройки (только для администратора)"
)
# --- Импорт необходимых библиотек ---
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
import logging
from datetime import datetime
from telegram.constants import ChatAction

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
        [
            InlineKeyboardButton("📋 Команды", callback_data='commands'),
            InlineKeyboardButton("📝 Пост", callback_data='post')
        ],
        [
            InlineKeyboardButton("📄 Логи", callback_data='logs'),
            InlineKeyboardButton("❌ Отмена", callback_data='cancel')
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data='stats'),
            InlineKeyboardButton("⚙️ Настройки", callback_data='settings')
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data='back')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("<b>🛠️ Админ-панель:</b>", reply_markup=reply_markup, parse_mode="HTML")

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
        await query.edit_message_text(COMMANDS_TEXT, parse_mode="HTML")
    elif query.data == 'post':
        await query.edit_message_text("Введите /post для публикации поста.")
    elif query.data == 'logs':
        try:
            with open('bot.log', 'r') as f:
                log_content = f.read()[-2000:]
            await query.edit_message_text(f"Последние логи:\n{log_content}")
        except Exception:
            await query.edit_message_text("Лог-файл не найден или пуст.")
    elif query.data == 'cancel':
        await query.edit_message_text("Публикация отменена. Используйте /cancel для отмены процесса.")
    elif query.data == 'stats':
        # Пример статистики (можно доработать)
        await query.edit_message_text("📊 <b>Статистика</b>\nПостов: 42\nОшибок: 3", parse_mode="HTML")
    elif query.data == 'settings':
        await query.edit_message_text("⚙️ <b>Настройки</b>\n(Здесь можно реализовать изменение параметров)", parse_mode="HTML")
    elif query.data == 'back':
        # Возвращаем админ-панель в том же сообщении
        keyboard = [
            [
                InlineKeyboardButton("📋 Команды", callback_data='commands'),
                InlineKeyboardButton("📝 Пост", callback_data='post')
            ],
            [
                InlineKeyboardButton("📄 Логи", callback_data='logs'),
                InlineKeyboardButton("❌ Отмена", callback_data='cancel')
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data='stats'),
                InlineKeyboardButton("⚙️ Настройки", callback_data='settings')
            ],
            [
                InlineKeyboardButton("🔙 Назад", callback_data='back')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("<b>🛠️ Админ-панель:</b>", reply_markup=reply_markup, parse_mode="HTML")

# --- Обработка команды /commands ---
async def commands_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(COMMANDS_TEXT, parse_mode="HTML")

# --- Обработка команды /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if update.effective_user and update.effective_user.id == ADMIN_ID:
        reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        await update.message.reply_text(
            WELCOME_BANNER + "\n" + COMMANDS_TEXT + "\n\nВы администратор. Используйте кнопки ниже для управления ботом.",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            WELCOME_BANNER + "\n" + COMMANDS_TEXT,
            parse_mode="HTML"
        )
# --- Обработка reply-кнопок как команд (BotFather style) ---
async def handle_main_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    text = update.message.text
    # Гарантируем, что context.user_data — dict
    if not hasattr(context, 'user_data') or context.user_data is None:
        context.user_data = {}
    if text == "⬅️ Назад":
        # Если сейчас показывается клавиатура знаков зодиака — возвращаемся к POSTS_KEYBOARD
        if context.user_data.get('zodiac'):
            reply_markup = ReplyKeyboardMarkup(POSTS_KEYBOARD, resize_keyboard=True)
            await update.message.reply_text("Выберите тип поста:", reply_markup=reply_markup)
            context.user_data.pop('zodiac', None)
        else:
            reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
            await update.message.reply_text("Главное меню:", reply_markup=reply_markup)
        return
    if text == "Посты":
        reply_markup = ReplyKeyboardMarkup(POSTS_KEYBOARD, resize_keyboard=True)
        await update.message.reply_text("Выберите тип поста:", reply_markup=reply_markup)
    elif text == "📝 Пост":
        await post_start(update, context)
    elif text == "📄 Логи":
        # Выводим логи напрямую, без эмуляции callback
        if update.effective_user and update.effective_user.id == ADMIN_ID:
            try:
                with open('bot.log', 'r') as f:
                    log_content = f.read()[-2000:]
                await update.message.reply_text(f"Последние логи:\n{log_content}")
            except Exception:
                await update.message.reply_text("Лог-файл не найден или пуст.")
        else:
            await update.message.reply_text("Нет доступа.")
    elif text == "🛠️ Админ-панель":
        await admin_panel(update, context)
    elif text == "📋 Команды":
        await commands_command(update, context)
    elif text == "❌ Отмена":
        await cancel(update, context)
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    elif text == "Вечернее послание":
        image_path = Path(__file__).parent / "images" / "poslanie1.jpg"
        if not image_path.exists():
            await update.message.reply_text("Изображение для послания не найдено.")
            return
        try:
            with image_path.open("rb") as img:
                context.user_data['preview'] = {
                    'type': 'photo',
                    'file': str(image_path),
                    'caption': "Вечернее послание. Выберите свой знак зодиака:",
                }
                context.user_data['zodiac'] = True
                context.user_data['reactions'] = {k: 0 for k in REACTION_NAMES}
                context.user_data['reaction_users'] = {k: set() for k in REACTION_NAMES}
                keyboard = ZODIAC_INLINE_KEYBOARD + get_reaction_keyboard(context.user_data['reactions'])
                await update.message.reply_photo(
                    img,
                    caption="Вечернее послание. Выберите свой знак зодиака:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception:
            await update.message.reply_text("Не удалось отправить изображение.")
# --- Callback для реакций ---
async def reaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not hasattr(query, 'data') or query.data is None:
        return
    await query.answer()
    data = query.data
    if not isinstance(data, str):
        return
    if data.startswith("react_"):
        reaction = data.replace("react_", "")
        user_id = update.effective_user.id if update.effective_user else None
        if not user_id:
            return
        # Сохраняем счетчики и пользователей в context.user_data
        if not hasattr(context, 'user_data') or context.user_data is None:
            context.user_data = {}
        if 'reactions' not in context.user_data:
            context.user_data['reactions'] = {k: 0 for k in REACTION_NAMES}
        if 'reaction_users' not in context.user_data:
            context.user_data['reaction_users'] = {k: set() for k in REACTION_NAMES}
        # Индекс реакции
        try:
            idx = REACTION_NAMES.index(reaction)
        except ValueError:
            return
        # Если пользователь еще не голосовал за эту реакцию
        if user_id not in context.user_data['reaction_users'][reaction]:
            context.user_data['reactions'][reaction] += 1
            context.user_data['reaction_users'][reaction].add(user_id)
            # Благодарственное сообщение (popup)
            try:
                await query.answer(REACTION_MESSAGES[idx], show_alert=True)
            except Exception:
                pass
        else:
            # Уже голосовал — просто обновить счетчик без увеличения и без спама
            try:
                await query.answer("Вы уже ставили эту реакцию", show_alert=True)
            except Exception:
                pass
        # Обновляем клавиатуру с новыми счетчиками
        keyboard = ZODIAC_INLINE_KEYBOARD + get_reaction_keyboard(context.user_data['reactions'])
        try:
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            pass
    elif query.data in [f"{emoji} {name}" for name, emoji in ZODIAC_SIGNS]:
        if update.message:
            await update.message.reply_text("Здесь будет индивидуальное послание для выбранного знака зодиака!")

    # Убираем обработку reply-кнопок для зодиака, теперь только inline-кнопки
# --- Callback для знаков зодиака (inline) ---
async def zodiac_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not hasattr(query, 'data') or query.data is None:
        return
    await query.answer()
    data = query.data
    if not isinstance(data, str):
        return
    if data.startswith("zodiac_"):
        zodiac_name = data.replace("zodiac_", "")
        # Сохраняем предпросмотр для выбранного знака
        if not hasattr(context, 'user_data') or context.user_data is None:
            context.user_data = {}
        context.user_data['preview'] = {
            'type': 'text',
            'text': f"Послание для знака: {zodiac_name}"
        }
        # Всплывающее сообщение для всех
        await query.answer(f"Вы выбрали: {zodiac_name}", show_alert=True)
        # Кнопка "Опубликовать" только для админа
        show_publish = False
        try:
            user_id = update.effective_user.id if update.effective_user else None
            if user_id == ADMIN_ID:
                show_publish = True
        except Exception:
            pass
        if show_publish:
            keyboard = [
                [InlineKeyboardButton("✅ Опубликовать", callback_data='confirm_post')]
            ]
            await query.edit_message_caption(
                caption=f"Послание для знака: {zodiac_name}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_caption(
                caption=f"Послание для знака: {zodiac_name}",
                reply_markup=None
            )
    elif update.message and hasattr(update.message, 'text') and update.message.text in ["Гороскоп", "Карта дня", "Доброе утро", "Лунный прогноз", "Свободная публикация"]:
        text = update.message.text
        # Гарантируем, что context.user_data — dict
        if not hasattr(context, 'user_data') or context.user_data is None:
            context.user_data = {}
        context.user_data['preview'] = {
            'type': 'text',
            'text': f"{text}: пример содержимого поста"
        }
        keyboard = [
            [InlineKeyboardButton("✅ Опубликовать", callback_data='confirm_post')],
            [InlineKeyboardButton("✏️ Отменить/Изменить", callback_data='cancel_post')]
        ]
        await update.message.reply_text(f"Предпросмотр поста: {text}\n\nпример содержимого поста", reply_markup=InlineKeyboardMarkup(keyboard))
# --- Callback для подтверждения/отмены предпросмотра поста ---
async def preview_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    # Гарантируем, что context.user_data — dict
    if not hasattr(context, 'user_data') or context.user_data is None:
        context.user_data = {}
    preview = context.user_data.get('preview')
    if not preview:
        await query.edit_message_text("Нет предпросмотра для публикации.")
        return
    if query.data == 'confirm_post':
        if preview['type'] == 'photo':
            with open(preview['file'], 'rb') as img:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=img, caption=preview['caption'])
        elif preview['type'] == 'text':
            await context.bot.send_message(chat_id=CHANNEL_ID, text=preview['text'])
        # После публикации убираем все кнопки
        try:
            await query.edit_message_caption(caption="Пост опубликован в канал!", reply_markup=None)
        except Exception:
            await query.edit_message_text("Пост опубликован в канал!", reply_markup=None)
        if context.user_data and isinstance(context.user_data, dict):
            context.user_data.pop('preview', None)
    elif query.data == 'cancel_post':
        await query.edit_message_text("Публикация отменена. Вы можете скорректировать пост и попробовать снова.")
        if context.user_data and isinstance(context.user_data, dict):
            context.user_data.pop('preview', None)
# --- Обработка reply-кнопки "🛠️ Админ-панель" ---
async def admin_panel_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import ReplyKeyboardRemove
    if update.message and update.message.text == "🛠️ Админ-панель" and update.effective_user and update.effective_user.id == ADMIN_ID:
        # Убираем reply-клавиатуру и показываем inline-админ-панель
        await update.message.reply_text(
            "<b>🛠️ Админ-панель:</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
        await admin_panel(update, context)

# --- Обработка команды /help ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    await update.message.reply_text(
        "<b>ℹ️ Помощь</b>\n\n"
        "Я могу публиковать <b>текст</b> и <b>медиа</b> в канал.\n"
        "Только <b>админ</b> может публиковать.\n\n"
        "<b>Как опубликовать пост:</b>\n"
        "1️⃣ Введите /post\n"
        "2️⃣ Отправьте текст или медиа\n"
        "3️⃣ Подтвердите публикацию\n\n"
        "<b>Команды:</b>\n"
        "📝 /post — начать публикацию поста\n"
        "❌ /cancel — отменить публикацию\n"
        "📋 /commands — список всех команд\n"
        "🛠️ /admin — админ-панель\n"
        "📊 /stats — статистика (админ)\n"
        "⚙️ /settings — настройки (админ)\n\n"
        "<i>Просто отправь текст или медиа после /post.</i>"
        , parse_mode="HTML"
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
        caption = update.message.caption or ""
        if contains_forbidden(caption):
            await update.message.reply_text("В подписи обнаружены запрещённые слова. Публикация отклонена.")
            logging.info(f"Отклонено видео с запрещёнными словами: {caption}")
            return ConversationHandler.END
        await context.bot.send_video(chat_id=CHANNEL_ID, video=file_id, caption=caption)
        await update.message.reply_text("Видео опубликовано в канал!")
        logging.info(f"Опубликовано видео: {caption}")
        return ConversationHandler.END
    return ConversationHandler.END

# --- Запуск бота ---
if __name__ == '__main__':
    import sys
    print(f"Используется Python: {sys.executable}")
    if not BOT_TOKEN:
        print("[ОШИБКА] BOT_TOKEN не найден. Проверьте файл .env и переменную BOT_TOKEN.")
        exit(1)
    print("Инициализация Telegram-бота...")
    app = ApplicationBuilder().token(BOT_TOKEN).connect_timeout(60).read_timeout(60).build()
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
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=None))
    app.add_handler(CallbackQueryHandler(preview_callback, pattern='^(confirm_post|cancel_post)$'))
    app.add_handler(CallbackQueryHandler(zodiac_callback, pattern=r'^zodiac_.*$'))
    app.add_handler(CallbackQueryHandler(reaction_callback, pattern=r'^react_.*$'))
    # Обрабатываем все кнопки из MAIN_KEYBOARD и POSTS_KEYBOARD
    all_buttons = [btn for row in MAIN_KEYBOARD for btn in row] + [btn for row in POSTS_KEYBOARD for btn in row]
    regex_pattern = "^(" + "|".join(map(lambda s: s.replace("(", "\\(").replace(")", "\\)").replace(".", "\\.").replace("+", "\\+").replace("?", "\\?").replace("|", "\\|"), all_buttons)) + ")$"
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(regex_pattern), handle_main_keyboard))
    print("Бот запущен. Ожидание сообщений... (Ctrl+C для остановки)")
    app.run_polling()
