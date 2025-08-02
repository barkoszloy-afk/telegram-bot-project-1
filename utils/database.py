# utils/database.py - Работа с базой данных реакций
import json
import time
import logging
from typing import Dict, Any, Optional
from config import REACTIONS_FILE, CACHE_TTL, REACTION_NAMES

class ReactionsDB:
    """Класс для работы с базой данных реакций с кэшированием"""
    
    def __init__(self):
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: float = 0
        
    def load_data(self) -> Dict[str, Any]:
        """Загружает данные с кэшированием"""
        current_time = time.time()
        
        # Обновляем кэш только если он устарел
        if self._cache is None or (current_time - self._cache_timestamp > 1):
            try:
                with open(REACTIONS_FILE, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                    self._cache_timestamp = current_time
                    logging.info("🔄 Данные реакций загружены из файла")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.warning(f"⚠️ Не удалось загрузить данные реакций: {e}")
                self._cache = {'posts': {}}
                self._cache_timestamp = current_time
                
        return self._cache.copy() if self._cache else {'posts': {}}
    
    def save_data(self, data: Dict[str, Any]) -> bool:
        """Сохраняет данные и обновляет кэш"""
        try:
            with open(REACTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Обновляем кэш
            self._cache = data.copy()
            self._cache_timestamp = time.time()
            logging.info("💾 Данные реакций сохранены")
            return True
            
        except Exception as e:
            logging.error(f"❌ Ошибка сохранения реакций: {e}")
            return False
    
    def get_post_reactions(self, post_id: str) -> Dict[str, Any]:
        """Получает данные о реакциях для конкретного поста"""
        data = self.load_data()
        
        if post_id not in data['posts']:
            data['posts'][post_id] = {
                'reactions': {k: 0 for k in REACTION_NAMES},
                'reaction_users': {k: [] for k in REACTION_NAMES}
            }
            self.save_data(data)
            
        return data['posts'][post_id]
    
    @property
    def data(self) -> dict:
        """Возвращает текущие данные реакций"""
        return self.load_data()
    
    def get_data(self) -> dict:
        """Альтернативный метод для получения данных"""
        return self.load_data()
    
    def cleanup_old_data(self, days_old: int = 7) -> int:
        """Очищает старые данные реакций"""
        try:
            data = self.load_data()
            current_time = time.time()
            cutoff_time = current_time - (days_old * 24 * 3600)
            
            posts_to_remove = []
            for post_id, post_data in data.get('posts', {}).items():
                if post_data.get('timestamp', 0) < cutoff_time:
                    posts_to_remove.append(post_id)
            
            for post_id in posts_to_remove:
                del data['posts'][post_id]
            
            if posts_to_remove:
                self.save_data(data)
                logging.info(f"🧹 Очищено {len(posts_to_remove)} старых постов")
            
            return len(posts_to_remove)
            
        except Exception as e:
            logging.error(f"❌ Ошибка очистки данных: {e}")
            return 0

    def add_user_reaction(self, user_id: str, reaction: str, post_id: str) -> Optional[str]:
        """Добавляет реакцию пользователя. Возвращает предыдущую реакцию если была"""
        data = self.load_data()
        post_reactions = self.get_post_reactions(post_id)
        
        # Проверяем существующую реакцию
        previous_reaction = self.get_user_reaction(user_id, post_reactions)
        if previous_reaction:
            return previous_reaction
            
        # Добавляем новую реакцию
        post_reactions['reactions'][reaction] += 1
        post_reactions['reaction_users'][reaction].append(user_id)
        
        # Сохраняем изменения
        data['posts'][post_id] = post_reactions
        self.save_data(data)
        
        logging.info(f"✅ Добавлена реакция {reaction} от пользователя {user_id} для поста {post_id}")
        return None
    
    def get_user_reaction(self, user_id: str, post_reactions: Dict[str, Any]) -> Optional[str]:
        """Возвращает реакцию пользователя для поста, если есть"""
        for reaction_name, users in post_reactions['reaction_users'].items():
            if user_id in users:
                return reaction_name
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику по реакциям"""
        data = self.load_data()
        total_posts = len(data['posts'])
        total_reactions = 0
        reaction_totals = {k: 0 for k in REACTION_NAMES}
        
        for post_data in data['posts'].values():
            for reaction, count in post_data['reactions'].items():
                total_reactions += count
                reaction_totals[reaction] += count
                
        return {
            'total_posts': total_posts,
            'total_reactions': total_reactions,
            'reaction_totals': reaction_totals
        }
    
    def cleanup_old_posts(self, max_age_days: int = 30) -> int:
        """Очищает старые посты (по умолчанию старше 30 дней)"""
        data = self.load_data()
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        posts_to_remove = []
        for post_id in data['posts']:
            # Извлекаем timestamp из post_id, если возможно
            try:
                # Формат: horoscope_20250802_031344
                if '_' in post_id:
                    date_str = post_id.split('_')[1]
                    if len(date_str) == 8:  # YYYYMMDD
                        post_year = int(date_str[:4])
                        post_month = int(date_str[4:6])
                        post_day = int(date_str[6:8])
                        
                        import datetime
                        post_date = datetime.datetime(post_year, post_month, post_day)
                        post_timestamp = post_date.timestamp()
                        
                        if current_time - post_timestamp > max_age_seconds:
                            posts_to_remove.append(post_id)
            except (ValueError, IndexError):
                continue
                
        # Удаляем старые посты
        for post_id in posts_to_remove:
            del data['posts'][post_id]
            
        if posts_to_remove:
            self.save_data(data)
            logging.info(f"🧹 Очищено {len(posts_to_remove)} старых постов")
            
        return len(posts_to_remove)

# Глобальный экземпляр
reactions_db = ReactionsDB()
