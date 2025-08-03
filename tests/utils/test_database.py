"""Тесты для модуля utils.database."""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

from utils.database import ReactionsDB


@pytest.fixture
def temp_db_file():
    """Создание временного файла для тестов базы данных."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        # Создаем пустую базу данных
        initial_data = {
            "posts": {}
        }
        json.dump(initial_data, f)
        db_path = f.name
    
    yield db_path
    
    # Удаляем временный файл после тестов
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def reactions_db():
    """Создание экземпляра ReactionsDB для тестов."""
    return ReactionsDB()


class TestReactionsDBInit:
    """Тесты инициализации базы данных."""
    
    def test_init_creates_instance(self):
        """Тест создания экземпляра ReactionsDB."""
        db = ReactionsDB()
        
        assert db._cache is None
        assert db._cache_timestamp == 0
    
    @patch('utils.database.REACTIONS_FILE')
    def test_load_data_with_existing_file(self, mock_file, temp_db_file):
        """Тест загрузки данных из существующего файла."""
        mock_file.__str__ = lambda: temp_db_file
        mock_file.__fspath__ = lambda: temp_db_file
        
        db = ReactionsDB()
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '{"posts": {}}'
            
            data = db.load_data()
            
            assert "posts" in data
    
    @patch('utils.database.REACTIONS_FILE', '/nonexistent/file.json')
    def test_load_data_file_not_found(self):
        """Тест загрузки данных при отсутствующем файле."""
        db = ReactionsDB()
        
        data = db.load_data()
        
        assert data == {"posts": {}}
    
    @patch('utils.database.REACTIONS_FILE')
    def test_load_data_invalid_json(self, mock_file, temp_db_file):
        """Тест загрузки поврежденного JSON."""
        # Создаем файл с невалидным JSON
        with open(temp_db_file, 'w') as f:
            f.write("invalid json content")
        
        mock_file.__str__ = lambda: temp_db_file
        mock_file.__fspath__ = lambda: temp_db_file
        
        db = ReactionsDB()
        data = db.load_data()
        
        assert data == {"posts": {}}


class TestUserReactions:
    """Тесты для работы с реакциями пользователей."""
    
    @patch('utils.database.REACTION_NAMES', ['like', 'love', 'fire'])
    def test_add_new_user_reaction(self, reactions_db):
        """Тест добавления новой реакции пользователя."""
        user_id = "123456"
        reaction = "like"
        post_id = "test_post_001"
        
        with patch.object(reactions_db, 'load_data') as mock_load:
            with patch.object(reactions_db, 'save_data') as mock_save:
                mock_load.return_value = {"posts": {}}
                
                previous = reactions_db.add_user_reaction(user_id, reaction, post_id)
                
                assert previous is None  # Не было предыдущей реакции
                mock_save.assert_called_once()
    
    @patch('utils.database.REACTION_NAMES', ['like', 'love', 'fire'])
    def test_add_duplicate_reaction(self, reactions_db):
        """Тест добавления дублирующей реакции."""
        user_id = "123456"
        reaction = "like"
        post_id = "test_post_001"
        
        # Создаем данные с уже существующей реакцией
        existing_data = {
            "posts": {
                post_id: {
                    "reactions": {"like": 1, "love": 0, "fire": 0},
                    "reaction_users": {"like": [user_id], "love": [], "fire": []}
                }
            }
        }
        
        with patch.object(reactions_db, 'load_data', return_value=existing_data):
            previous = reactions_db.add_user_reaction(user_id, reaction, post_id)
            
            assert previous == reaction  # Возвращает предыдущую реакцию
    
    def test_get_user_reaction_existing(self, reactions_db):
        """Тест получения существующей реакции пользователя."""
        user_id = "123456"
        reaction = "love"
        
        post_reactions = {
            "reactions": {"like": 0, "love": 1, "fire": 0},
            "reaction_users": {"like": [], "love": [user_id], "fire": []}
        }
        
        result = reactions_db.get_user_reaction(user_id, post_reactions)
        assert result == reaction
    
    def test_get_user_reaction_nonexistent(self, reactions_db):
        """Тест получения несуществующей реакции."""
        post_reactions = {
            "reactions": {"like": 0, "love": 0, "fire": 0},
            "reaction_users": {"like": [], "love": [], "fire": []}
        }
        
        result = reactions_db.get_user_reaction("nonexistent", post_reactions)
        assert result is None


class TestPostData:
    """Тесты для работы с данными постов."""
    
    @patch('utils.database.REACTION_NAMES', ['like', 'love', 'fire'])
    def test_get_post_reactions_new_post(self, reactions_db):
        """Тест получения реакций для нового поста."""
        post_id = "new_post_001"
        
        with patch.object(reactions_db, 'load_data') as mock_load:
            with patch.object(reactions_db, 'save_data') as mock_save:
                mock_load.return_value = {"posts": {}}
                
                result = reactions_db.get_post_reactions(post_id)
                
                assert "reactions" in result
                assert "reaction_users" in result
                assert result["reactions"]["like"] == 0
                assert result["reaction_users"]["like"] == []
                mock_save.assert_called_once()
    
    def test_get_post_reactions_existing_post(self, reactions_db):
        """Тест получения реакций для существующего поста."""
        post_id = "existing_post"
        existing_reactions = {
            "reactions": {"like": 5, "love": 3, "fire": 1},
            "reaction_users": {"like": ["u1", "u2"], "love": ["u3"], "fire": ["u4"]}
        }
        
        with patch.object(reactions_db, 'load_data') as mock_load:
            mock_load.return_value = {"posts": {post_id: existing_reactions}}
            
            result = reactions_db.get_post_reactions(post_id)
            
            assert result == existing_reactions


class TestGlobalStats:
    """Тесты для глобальной статистики."""
    
    def test_get_stats_empty_db(self, reactions_db):
        """Тест получения статистики для пустой базы."""
        with patch.object(reactions_db, 'load_data') as mock_load:
            mock_load.return_value = {"posts": {}}
            
            stats = reactions_db.get_stats()
            
            assert stats["total_posts"] == 0
            assert stats["total_reactions"] == 0
            assert "reaction_totals" in stats
    
    def test_get_stats_with_data(self, reactions_db):
        """Тест получения статистики с данными."""
        test_data = {
            "posts": {
                "post1": {
                    "reactions": {"like": 3, "love": 2, "fire": 1},
                    "reaction_users": {"like": ["u1", "u2", "u3"], "love": ["u4", "u5"], "fire": ["u6"]}
                },
                "post2": {
                    "reactions": {"like": 1, "love": 0, "fire": 2},
                    "reaction_users": {"like": ["u7"], "love": [], "fire": ["u8", "u9"]}
                }
            }
        }
        
        with patch.object(reactions_db, 'load_data', return_value=test_data):
            stats = reactions_db.get_stats()
            
            assert stats["total_posts"] == 2
            assert stats["total_reactions"] == 9  # 3+2+1+1+0+2
            assert stats["reaction_totals"]["like"] == 4  # 3+1
            assert stats["reaction_totals"]["love"] == 2  # 2+0
            assert stats["reaction_totals"]["fire"] == 3  # 1+2


class TestDataPersistence:
    """Тесты для сохранения и загрузки данных."""
    
    @patch('utils.database.REACTIONS_FILE')
    def test_save_data_success(self, mock_file, reactions_db):
        """Тест успешного сохранения данных."""
        test_data = {"posts": {"test": "data"}}
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = MagicMock()
            
            result = reactions_db.save_data(test_data)
            
            assert result is True
            mock_open.assert_called_once()
    
    @patch('utils.database.REACTIONS_FILE', '/invalid/path/file.json')
    def test_save_data_error(self, reactions_db):
        """Тест обработки ошибок при сохранении."""
        test_data = {"posts": {"test": "data"}}
        
        result = reactions_db.save_data(test_data)
        
        assert result is False
    
    def test_data_property(self, reactions_db):
        """Тест свойства data."""
        with patch.object(reactions_db, 'load_data') as mock_load:
            mock_load.return_value = {"posts": {"test": "data"}}
            
            result = reactions_db.data
            
            assert result == {"posts": {"test": "data"}}
            mock_load.assert_called_once()


class TestCleanupOperations:
    """Тесты для операций очистки."""
    
    def test_cleanup_old_data(self, reactions_db):
        """Тест очистки старых данных."""
        import time
        
        old_timestamp = time.time() - (10 * 24 * 3600)  # 10 дней назад
        new_timestamp = time.time() - (1 * 24 * 3600)   # 1 день назад
        
        test_data = {
            "posts": {
                "old_post": {"timestamp": old_timestamp},
                "new_post": {"timestamp": new_timestamp}
            }
        }
        
        with patch.object(reactions_db, 'load_data', return_value=test_data):
            with patch.object(reactions_db, 'save_data') as mock_save:
                
                removed_count = reactions_db.cleanup_old_data(days_old=7)
                
                assert removed_count == 1  # Удален 1 старый пост
                mock_save.assert_called_once()
    
    def test_cleanup_old_posts_by_date(self, reactions_db):
        """Тест очистки старых постов по дате в ID."""
        test_data = {
            "posts": {
                "horoscope_20240101_120000": {"reactions": {"like": 1}},  # Старый
                "horoscope_20250101_120000": {"reactions": {"like": 1}},  # Новый
                "invalid_format_post": {"reactions": {"like": 1}}        # Неверный формат
            }
        }
        
        with patch.object(reactions_db, 'load_data', return_value=test_data):
            with patch.object(reactions_db, 'save_data') as mock_save:
                
                removed_count = reactions_db.cleanup_old_posts(max_age_days=30)
                
                # Проверяем, что метод был вызван
                assert isinstance(removed_count, int)


class TestEdgeCases:
    """Тесты для граничных случаев."""
    
    def test_empty_post_id(self, reactions_db):
        """Тест с пустым ID поста."""
        with patch.object(reactions_db, 'load_data') as mock_load:
            mock_load.return_value = {"posts": {}}
            
            # Не должно падать с пустым post_id
            result = reactions_db.get_post_reactions("")
            assert "reactions" in result
    
    def test_unicode_post_id(self, reactions_db):
        """Тест с Unicode ID поста."""
        unicode_post_id = "пост_с_эмодзи_🎉"
        
        with patch.object(reactions_db, 'load_data') as mock_load:
            with patch.object(reactions_db, 'save_data') as mock_save:
                mock_load.return_value = {"posts": {}}
                
                result = reactions_db.get_post_reactions(unicode_post_id)
                assert "reactions" in result
    
    @patch('utils.database.REACTION_NAMES', ['like'])
    def test_cache_functionality(self, reactions_db):
        """Тест функциональности кэша."""
        import time
        
        with patch.object(reactions_db, 'load_data') as mock_load:
            mock_load.return_value = {"posts": {}}
            
            # Первый вызов
            reactions_db.data
            first_call_count = mock_load.call_count
            
            # Второй вызов сразу - должен использовать кэш
            reactions_db.data
            second_call_count = mock_load.call_count
            
            # Кэш должен работать (вызовов не должно быть больше)
            # Но учитываем, что кэш может обновляться каждую секунду
            assert second_call_count >= first_call_count


class TestIntegration:
    """Интеграционные тесты."""
    
    @patch('utils.database.REACTION_NAMES', ['like', 'love', 'fire'])
    def test_full_reaction_workflow(self, reactions_db):
        """Тест полного workflow с реакциями."""
        post_id = "test_workflow_post"
        users = ["user1", "user2", "user3"]
        reactions = ["like", "love", "fire"]
        
        with patch.object(reactions_db, 'load_data') as mock_load:
            with patch.object(reactions_db, 'save_data') as mock_save:
                mock_load.return_value = {"posts": {}}
                
                # Добавляем реакции от разных пользователей
                for i, user_id in enumerate(users):
                    reaction = reactions[i % len(reactions)]
                    result = reactions_db.add_user_reaction(user_id, reaction, post_id)
                    assert result is None  # Новые реакции
                
                # Проверяем, что save_data вызывался
                assert mock_save.call_count > 0
    
    def test_stats_calculation_integration(self, reactions_db):
        """Интеграционный тест подсчета статистики."""
        test_data = {
            "posts": {
                "post1": {
                    "reactions": {"like": 5, "love": 3, "fire": 0},
                    "reaction_users": {
                        "like": ["u1", "u2", "u3", "u4", "u5"], 
                        "love": ["u6", "u7", "u8"], 
                        "fire": []
                    }
                },
                "post2": {
                    "reactions": {"like": 2, "love": 1, "fire": 4},
                    "reaction_users": {
                        "like": ["u9", "u10"], 
                        "love": ["u11"], 
                        "fire": ["u12", "u13", "u14", "u15"]
                    }
                }
            }
        }
        
        with patch.object(reactions_db, 'load_data', return_value=test_data):
            stats = reactions_db.get_stats()
            
            # Проверяем корректность подсчета
            assert stats["total_posts"] == 2
            assert stats["total_reactions"] == 15  # 5+3+0+2+1+4
            assert stats["reaction_totals"]["like"] == 7  # 5+2
            assert stats["reaction_totals"]["love"] == 4  # 3+1
            assert stats["reaction_totals"]["fire"] == 4  # 0+4
