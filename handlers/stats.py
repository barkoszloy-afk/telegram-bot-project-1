# handlers/stats.py - Обработчики статистики
import logging
import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from collections import defaultdict, Counter
from config import ADMIN_ID

logger = logging.getLogger(__name__)

# Файл для хранения статистики
STATS_FILE = "bot_stats.json"

class BotStats:
    """Класс для работы со статистикой бота"""
    
    def __init__(self):
        self.stats = self.load_stats()
    
    def load_stats(self):
        """Загрузка статистики из файла"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "users": {},
                "commands": defaultdict(int),
                "daily_stats": {},
                "total_messages": 0,
                "start_date": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Ошибка загрузки статистики: {e}")
            return {
                "users": {},
                "commands": defaultdict(int),
                "daily_stats": {},
                "total_messages": 0,
                "start_date": datetime.now().isoformat()
            }
    
    def save_stats(self):
        """Сохранение статистики в файл"""
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
    
    def add_user(self, user_id, username=None, first_name=None):
        """Добавление пользователя в статистику"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if str(user_id) not in self.stats["users"]:
            self.stats["users"][str(user_id)] = {
                "username": username,
                "first_name": first_name,
                "first_seen": today,
                "last_seen": today,
                "message_count": 0,
                "commands_used": defaultdict(int)
            }
        else:
            self.stats["users"][str(user_id)]["last_seen"] = today
            if username:
                self.stats["users"][str(user_id)]["username"] = username
            if first_name:
                self.stats["users"][str(user_id)]["first_name"] = first_name
    
    def add_command(self, user_id, command):
        """Добавление использования команды"""
        self.stats["commands"][command] += 1
        if str(user_id) in self.stats["users"]:
            self.stats["users"][str(user_id)]["commands_used"][command] += 1
        
        # Дневная статистика
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {"commands": defaultdict(int), "users": set()}
        
        self.stats["daily_stats"][today]["commands"][command] += 1
        self.stats["daily_stats"][today]["users"] = list(set(self.stats["daily_stats"][today].get("users", [])) | {user_id})
    
    def add_message(self, user_id):
        """Добавление сообщения"""
        self.stats["total_messages"] += 1
        if str(user_id) in self.stats["users"]:
            self.stats["users"][str(user_id)]["message_count"] += 1
    
    def get_user_count(self):
        """Получение количества пользователей"""
        return len(self.stats["users"])
    
    def get_active_users(self, days=7):
        """Получение активных пользователей за период"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        active_users = 0
        
        for user_data in self.stats["users"].values():
            if user_data["last_seen"] >= cutoff_date:
                active_users += 1
        
        return active_users

# Глобальный объект статистики
bot_stats = BotStats()

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /stats - статистика использования бота"""
    try:
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        # Обновляем статистику
        bot_stats.add_user(
            user_id,
            update.effective_user.username,
            update.effective_user.first_name
        )
        bot_stats.add_command(user_id, "stats")
        bot_stats.save_stats()
        
        # Формируем отчет
        total_users = bot_stats.get_user_count()
        active_users_7d = bot_stats.get_active_users(7)
        active_users_30d = bot_stats.get_active_users(30)
        
        # Топ команд
        top_commands = Counter(bot_stats.stats["commands"]).most_common(5)
        
        # Статистика за сегодня
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = bot_stats.stats["daily_stats"].get(today, {})
        
        stats_text = (
            f"📊 **Статистика бота**\n\n"
            f"👥 **Пользователи**\n"
            f"• Всего: {total_users}\n"
            f"• Активные (7 дней): {active_users_7d}\n"
            f"• Активные (30 дней): {active_users_30d}\n\n"
            f"📱 **Сообщения**\n"
            f"• Всего: {bot_stats.stats['total_messages']}\n"
            f"• Сегодня: {len(today_stats.get('users', []))}\n\n"
            f"⚡ **Популярные команды**\n"
        )
        
        for i, (command, count) in enumerate(top_commands, 1):
            stats_text += f"{i}. /{command}: {count} раз\n"
        
        # Статистика за последние 7 дней
        stats_text += f"\n📅 **За последние 7 дней**\n"
        recent_days = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            day_stats = bot_stats.stats["daily_stats"].get(date, {})
            users_count = len(day_stats.get("users", []))
            if users_count > 0:
                recent_days.append(f"• {date}: {users_count} польз.")
        
        if recent_days:
            stats_text += "\n".join(recent_days[:5])  # Показываем только последние 5 дней
        else:
            stats_text += "Нет данных"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        logger.info(f"📊 Статистика запрошена пользователем {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /stats: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики")

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /users - информация о пользователях"""
    try:
        user_id = update.effective_user.id
        
        if user_id != ADMIN_ID:
            await update.message.reply_text("❌ Доступ запрещен")
            return
        
        total_users = bot_stats.get_user_count()
        active_7d = bot_stats.get_active_users(7)
        active_30d = bot_stats.get_active_users(30)
        
        # Новые пользователи за последние дни
        today = datetime.now()
        new_users_7d = 0
        new_users_30d = 0
        
        for user_data in bot_stats.stats["users"].values():
            first_seen = datetime.fromisoformat(user_data["first_seen"])
            days_ago = (today - first_seen).days
            
            if days_ago <= 7:
                new_users_7d += 1
            if days_ago <= 30:
                new_users_30d += 1
        
        users_text = (
            f"👥 **Пользователи бота**\n\n"
            f"📈 **Общая статистика**\n"
            f"• Всего пользователей: {total_users}\n"
            f"• Активные за 7 дней: {active_7d}\n"
            f"• Активные за 30 дней: {active_30d}\n\n"
            f"🆕 **Новые пользователи**\n"
            f"• За 7 дней: {new_users_7d}\n"
            f"• За 30 дней: {new_users_30d}\n\n"
            f"📊 **Коэффициенты**\n"
            f"• Активность (7д): {(active_7d/total_users*100):.1f}%\n"
            f"• Активность (30д): {(active_30d/total_users*100):.1f}%\n"
            f"• Рост (7д): {(new_users_7d/total_users*100):.1f}%"
        )
        
        await update.message.reply_text(users_text, parse_mode='Markdown')
        logger.info(f"👥 Информация о пользователях запрошена {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка команды /users: {e}")
        await update.message.reply_text("❌ Ошибка при получении информации о пользователях")

# Функция для обновления статистики (вызывается из основного бота)
def update_stats(user_id, username=None, first_name=None, command=None, is_message=False):
    """Обновление статистики"""
    try:
        bot_stats.add_user(user_id, username, first_name)
        
        if command:
            bot_stats.add_command(user_id, command)
        
        if is_message:
            bot_stats.add_message(user_id)
        
        bot_stats.save_stats()
        
    except Exception as e:
        logger.error(f"Ошибка обновления статистики: {e}")
