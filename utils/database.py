# utils/database.py - Простая база данных для реакций
import json
import os

class ReactionsDB:
    """Простая база данных для хранения реакций пользователей"""
    
    def __init__(self, db_file="reactions_data.json"):
        self.db_file = db_file
        self.data = self.load_data()
    
    def load_data(self):
        """Загружает данные из файла"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def save_data(self):
        """Сохраняет данные в файл"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
    
    def add_reaction(self, user_id, post_id, reaction):
        """Добавляет реакцию пользователя"""
        user_key = str(user_id)
        post_key = str(post_id)
        
        if user_key not in self.data:
            self.data[user_key] = {}
        
        self.data[user_key][post_key] = reaction
        self.save_data()
    
    def get_reaction(self, user_id, post_id):
        """Получает реакцию пользователя на пост"""
        user_key = str(user_id)
        post_key = str(post_id)
        
        return self.data.get(user_key, {}).get(post_key)
    
    def get_post_reactions(self, post_id):
        """Получает все реакции на пост"""
        post_key = str(post_id)
        reactions = {}
        
        for user_data in self.data.values():
            if post_key in user_data:
                reaction = user_data[post_key]
                reactions[reaction] = reactions.get(reaction, 0) + 1
        
        return reactions

# Экспорт для совместимости
Database = ReactionsDB

# Глобальный экземпляр базы данных
reactions_db = ReactionsDB()
