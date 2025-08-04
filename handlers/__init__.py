# handlers/__init__.py - Обработчики команд

# Импорты всех обработчиков
from .admin import *
from .reactions import *
from .diagnostics import *
from .stats import *
from .user_commands import *
from .content_commands import *
from .admin_commands import *

__all__ = [
    # Основные обработчики
    'show_main_menu',
    'handle_reaction',
    'show_post_reactions',
    
    # Диагностические команды
    'ping_command',
    'status_command', 
    'uptime_command',
    'version_command',
    'health_command',
    
    # Статистика
    'stats_command',
    'users_command',
    'update_stats',
    
    # Пользовательские команды
    'about_command',
    'profile_command',
    'feedback_command',
    'settings_command',
    
    # Контентные команды
    'random_command',
    'popular_command',
    'recent_command',
    'categories_command',
    'search_command',
    
    # Административные команды
    'logs_command',
    'restart_command',
    'broadcast_command',
    'cleanup_command',
]
