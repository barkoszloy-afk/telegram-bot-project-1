#!/usr/bin/env python3
# security_check.py - Дополнительная проверка безопасности

import os
import re
import ast
import sys
from pathlib import Path

class SecurityChecker:
    """Класс для проверки безопасности кода"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        
    def check_file(self, file_path):
        """Проверяет файл на проблемы безопасности"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Проверяем различные аспекты безопасности
            self._check_hardcoded_secrets(file_path, content)
            self._check_sql_injection(file_path, content)
            self._check_insecure_imports(file_path, content)
            self._check_eval_usage(file_path, content)
            
        except Exception as e:
            self.warnings.append(f"Не удалось проверить {file_path}: {e}")
    
    def _check_hardcoded_secrets(self, file_path, content):
        """Проверка на жестко заданные секреты"""
        patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Пропускаем комментарии и os.getenv
            if line.strip().startswith('#') or 'os.getenv' in line or 'BOT_TOKEN}' in line:
                continue
                
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Исключаем тестовые токены
                    if 'TEST' not in line.upper() and 'EXAMPLE' not in line.upper():
                        self.issues.append(f"🔐 Потенциальный секрет в {file_path}:{i}")
    
    def _check_sql_injection(self, file_path, content):
        """Проверка на потенциальные SQL инъекции"""
        if 'sql' in content.lower() or 'execute' in content.lower():
            # Ищем строки с SQL и форматированием
            sql_patterns = [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'execute\s*\(\s*f["\'].*{.*}.*["\']'
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern in sql_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.issues.append(f"💉 Потенциальная SQL инъекция в {file_path}:{i}")
    
    def _check_insecure_imports(self, file_path, content):
        """Проверка на небезопасные импорты"""
        dangerous_imports = ['pickle', 'marshal', 'shelve']
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for imp in dangerous_imports:
                if f'import {imp}' in line or f'from {imp}' in line:
                    self.warnings.append(f"⚠️ Потенциально небезопасный импорт в {file_path}:{i} - {imp}")
    
    def _check_eval_usage(self, file_path, content):
        """Проверка на использование eval/exec"""
        dangerous_functions = ['eval', 'exec', 'compile']
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            for func in dangerous_functions:
                if f'{func}(' in line and not line.strip().startswith('#'):
                    self.issues.append(f"⚡ Использование {func} в {file_path}:{i}")
    
    def check_project(self):
        """Проверяет весь проект"""
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Пропускаем служебные директории
            if any(skip in root for skip in ['__pycache__', '.git', '.venv', 'venv']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        print(f"🔍 Проверяю {len(python_files)} Python файлов...")
        
        for file_path in python_files:
            self.check_file(file_path)
        
        return self.generate_report()
    
    def generate_report(self):
        """Генерирует отчет по безопасности"""
        print("\n" + "="*60)
        print("🛡️ ОТЧЕТ ПО БЕЗОПАСНОСТИ")
        print("="*60)
        
        if self.issues:
            print(f"\n❌ Найдено {len(self.issues)} проблем безопасности:")
            for issue in self.issues:
                print(f"   {issue}")
        else:
            print("\n✅ Критических проблем безопасности не найдено")
        
        if self.warnings:
            print(f"\n⚠️ Предупреждения ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   {warning}")
        else:
            print("\n✅ Предупреждений нет")
        
        # Общая оценка
        total_problems = len(self.issues) + len(self.warnings)
        if total_problems == 0:
            security_level = "🟢 ВЫСОКИЙ"
        elif len(self.issues) == 0:
            security_level = "🟡 СРЕДНИЙ"
        else:
            security_level = "🔴 НИЗКИЙ"
        
        print(f"\n🎯 Уровень безопасности: {security_level}")
        print(f"📊 Всего проблем: {total_problems}")
        
        return len(self.issues) == 0


def main():
    """Основная функция"""
    print("🚀 ЗАПУСК ПРОВЕРКИ БЕЗОПАСНОСТИ")
    
    checker = SecurityChecker()
    is_secure = checker.check_project()
    
    if is_secure:
        print("\n🎉 Проект прошел проверку безопасности!")
        sys.exit(0)
    else:
        print("\n⚠️ Найдены проблемы безопасности, требующие внимания")
        sys.exit(1)


if __name__ == "__main__":
    main()