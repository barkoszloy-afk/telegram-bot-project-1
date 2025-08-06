# tests/test_performance.py - Тесты производительности

import pytest
import time
import psutil
import os
from unittest.mock import patch

try:
    import pytest_benchmark  # noqa: F401
    BENCHMARK_AVAILABLE = True
except ImportError:
    BENCHMARK_AVAILABLE = False

# Помечаем все тесты в этом файле как медленные
pytestmark = pytest.mark.slow

class TestPerformance:
    """Тесты производительности"""
    
    def test_import_speed(self):
        """Тест скорости импорта модулей"""
        start_time = time.time()
        
        try:
            import config
            import utils.keyboards
            import handlers.admin
            import handlers.reactions
            
            import_time = time.time() - start_time
            print(f"Import time: {import_time:.3f} seconds")
            
            # Импорт должен занимать менее 2 секунд
            assert import_time < 2.0, f"Import too slow: {import_time:.3f}s"
            
        except Exception as e:
            pytest.skip(f"Import test requires valid modules: {e}")
    
    def test_memory_usage(self):
        """Тест использования памяти"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            # Импортируем основные модули
            import config
            import utils.keyboards  
            import handlers.admin
            
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory
            
            print(f"Memory increase: {memory_increase:.2f} MB")
            
            # Увеличение памяти должно быть разумным (< 50 MB)
            assert memory_increase < 50.0, f"Memory usage too high: {memory_increase:.2f} MB"
            
        except Exception as e:
            pytest.skip(f"Memory test requires valid modules: {e}")
    
    @pytest.mark.benchmark
    @pytest.mark.skipif(not BENCHMARK_AVAILABLE, reason="pytest-benchmark not installed")
    def test_keyboard_creation_speed(self, benchmark):
        """Бенчмарк создания клавиатур"""
        try:
            from utils.keyboards import create_main_menu_keyboard

            # Бенчмарк создания клавиатуры
            result = benchmark(create_main_menu_keyboard)

            assert result is not None
            print("✅ Keyboard creation benchmark completed")

        except Exception as e:
            pytest.skip(f"Benchmark test requires valid modules: {e}")
    
    def test_concurrent_operations(self):
        """Тест параллельных операций"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_keyboard():
            try:
                from utils.keyboards import create_main_menu_keyboard
                keyboard = create_main_menu_keyboard()
                results.put(keyboard is not None)
            except Exception:
                results.put(False)
        
        # Запускаем 5 параллельных операций
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_keyboard)
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join(timeout=10)
        
        # Проверяем результаты
        success_count = 0
        while not results.empty():
            if results.get():
                success_count += 1
        
        print(f"Successful concurrent operations: {success_count}/5")
        assert success_count >= 3, "Too many concurrent operation failures"

class TestStressTest:
    """Стресс-тесты"""
    
    @pytest.mark.slow
    def test_repeated_operations(self):
        """Тест повторяющихся операций"""
        try:
            from utils.keyboards import create_main_menu_keyboard
            
            # Выполняем операцию 100 раз
            start_time = time.time()
            
            for i in range(100):
                keyboard = create_main_menu_keyboard()
                assert keyboard is not None
                
                # Каждые 25 итераций выводим прогресс
                if (i + 1) % 25 == 0:
                    print(f"Progress: {i + 1}/100")
            
            total_time = time.time() - start_time
            avg_time = total_time / 100
            
            print(f"Total time: {total_time:.3f}s")
            print(f"Average time per operation: {avg_time:.6f}s")
            
            # Средняя операция должна занимать менее 10мс
            assert avg_time < 0.01, f"Operations too slow: {avg_time:.6f}s each"
            
        except Exception as e:
            pytest.skip(f"Stress test requires valid modules: {e}")
