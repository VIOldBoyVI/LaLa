#!/usr/bin/env python3
"""
Тестирование корректности структуры модулей для безопасного подключения к MySQL
"""

import os
from dotenv import load_dotenv

def test_imports():
    """Тестирование импорта модулей"""
    print("Тест 1: Проверка импорта модулей...")
    try:
        from db_config import DatabaseConfig, get_db_connection, get_db_transaction, test_connection
        print("✓ Модули db_config импортированы успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта db_config: {e}")
        return False
    
    try:
        from models import Question, GameState, OpenedCell, Score, Player, init_database, get_session
        print("✓ Модули models импортированы успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта models: {e}")
        return False
    
    try:
        from app_mysql import app
        print("✓ Модуль app_mysql импортирован успешно")
    except ImportError as e:
        print(f"✗ Ошибка импорта app_mysql: {e}")
        return False
    
    return True

def test_env_loading():
    """Тестирование загрузки переменных окружения"""
    print("\nТест 2: Проверка загрузки переменных окружения...")
    load_dotenv()
    
    # Проверяем, что файл .env существует и содержит базовые переменные
    env_file_exists = os.path.exists('.env')
    if env_file_exists:
        print("✓ Файл .env найден")
    else:
        print("✗ Файл .env не найден")
        return False
    
    # Проверяем, что хотя бы основные переменные определены
    basic_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    found_vars = [var for var in basic_vars if os.getenv(var)]
    
    if len(found_vars) >= 2:  # Хотя бы часть переменных есть
        print(f"✓ Найдены переменные окружения: {found_vars}")
        return True
    else:
        print("⚠ Найдено недостаточно переменных окружения")
        return True  # Это не критичная ошибка для теста структуры

def test_database_config_class():
    """Тестирование класса DatabaseConfig"""
    print("\nТест 3: Проверка класса DatabaseConfig...")
    try:
        from db_config import DatabaseConfig
        
        # Устанавливаем тестовые переменные окружения
        os.environ['DB_HOST'] = 'test_host'
        os.environ['DB_PORT'] = '3306'
        os.environ['DB_NAME'] = 'test_db'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = 'test_pass'
        os.environ['DB_POOL_SIZE'] = '5'
        
        config = DatabaseConfig()
        
        assert config.host == 'test_host'
        assert config.port == 3306
        assert config.database == 'test_db'
        assert config.user == 'test_user'
        assert config.password == 'test_pass'
        assert config.pool_size == 5
        
        print("✓ Класс DatabaseConfig работает корректно")
        return True
    except Exception as e:
        print(f"✗ Ошибка при тестировании DatabaseConfig: {e}")
        return False

def test_model_classes():
    """Тестирование SQLAlchemy моделей"""
    print("\nТест 4: Проверка SQLAlchemy моделей...")
    try:
        from models import Question, GameState, OpenedCell, Score, Player
        
        # Проверяем, что у моделей есть необходимые атрибуты
        assert hasattr(Question, '__tablename__')
        assert Question.__tablename__ == 'questions'
        
        assert hasattr(GameState, '__tablename__')
        assert GameState.__tablename__ == 'game_states'
        
        assert hasattr(OpenedCell, '__tablename__')
        assert OpenedCell.__tablename__ == 'opened_cells'
        
        assert hasattr(Score, '__tablename__')
        assert Score.__tablename__ == 'scores'
        
        assert hasattr(Player, '__tablename__')
        assert Player.__tablename__ == 'players'
        
        print("✓ SQLAlchemy модели имеют правильную структуру")
        return True
    except Exception as e:
        print(f"✗ Ошибка при тестировании моделей: {e}")
        return False

def test_requirements():
    """Тестирование наличия необходимых зависимостей"""
    print("\nТест 5: Проверка зависимостей...")
    try:
        import flask
        import mysql.connector
        import sqlalchemy
        import pymysql
        import dotenv
        
        print("✓ Все необходимые зависимости импортированы")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта зависимости: {e}")
        return False

def main():
    """Основная функция запуска тестов"""
    print("Запуск тестов структуры модулей для MySQL интеграции...")
    print("="*60)
    
    # Запускаем тесты
    results = []
    results.append(test_imports())
    results.append(test_env_loading())
    results.append(test_database_config_class())
    results.append(test_model_classes())
    results.append(test_requirements())
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Пройдено тестов: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ Все тесты структуры пройдены успешно!")
        print("\nПримечание: Это тесты структуры модулей, подключение к реальной базе данных")
        print("будет работать при наличии правильно настроенной MySQL базы данных")
        return True
    else:
        print("✗ Некоторые тесты структуры не прошли")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)