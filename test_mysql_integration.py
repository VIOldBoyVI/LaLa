#!/usr/bin/env python3
"""
Тестирование интеграции с MySQL базой данных
"""

import os
from dotenv import load_dotenv
from db_config import test_connection, get_db_connection, get_db_transaction
from models import init_database, Question, get_session

def test_basic_connection():
    """Тест базового подключения к базе данных"""
    print("Тест 1: Проверка подключения к базе данных...")
    try:
        is_connected = test_connection()
        if is_connected:
            print("✓ Подключение к базе данных успешно установлено")
            return True
        else:
            print("✗ Не удалось подключиться к базе данных")
            return False
    except Exception as e:
        print(f"✗ Ошибка при подключении: {e}")
        return False

def test_connection_with_context_manager():
    """Тест использования контекстного менеджера для подключения"""
    print("\nТест 2: Проверка контекстного менеджера подключения...")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print("✓ Контекстный менеджер подключения работает корректно")
                return True
            else:
                print("✗ Контекстный менеджер подключения возвращает неверный результат")
                return False
    except Exception as e:
        print(f"✗ Ошибка при использовании контекстного менеджера: {e}")
        return False

def test_transaction():
    """Тест транзакции"""
    print("\nТест 3: Проверка работы транзакций...")
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()
            # Выполняем простую операцию в транзакции
            cursor.execute("SELECT COUNT(*) as count FROM questions")
            result = cursor.fetchone()
            print(f"✓ Транзакция выполнена успешно, найдено вопросов: {result[0] if result else 'N/A'}")
            return True
    except Exception as e:
        print(f"✗ Ошибка при выполнении транзакции: {e}")
        return False

def test_sqlalchemy_models():
    """Тест SQLAlchemy моделей"""
    print("\nТест 4: Проверка SQLAlchemy моделей...")
    try:
        # Инициализируем базу данных
        init_database()
        print("✓ Инициализация базы данных прошла успешно")
        
        # Проверяем работу сессии
        session = get_session()
        question_count = session.query(Question).count()
        session.close()
        print(f"✓ SQLAlchemy модели работают корректно, количество вопросов: {question_count}")
        return True
    except Exception as e:
        print(f"✗ Ошибка при работе с SQLAlchemy моделями: {e}")
        return False

def main():
    """Основная функция запуска тестов"""
    print("Запуск тестов интеграции с MySQL базой данных...")
    print("="*60)
    
    # Загружаем переменные окружения
    load_dotenv()
    
    # Запускаем тесты
    results = []
    results.append(test_basic_connection())
    results.append(test_connection_with_context_manager())
    results.append(test_transaction())
    results.append(test_sqlalchemy_models())
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Пройдено тестов: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ Все тесты пройдены успешно!")
        return True
    else:
        print("✗ Некоторые тесты не прошли")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)