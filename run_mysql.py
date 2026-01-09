#!/usr/bin/env python3
"""
Запуск LaLaGame приложения с безопасным подключением к MySQL
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

def check_environment():
    """Проверяем наличие необходимых переменных окружения"""
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Ошибка: Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        print("Пожалуйста, создайте файл .env с необходимыми параметрами подключения к базе данных")
        return False
    
    return True

def main():
    """Основная функция запуска приложения"""
    print("Проверка конфигурации окружения...")
    
    if not check_environment():
        sys.exit(1)
    
    print("Конфигурация окружения проверена. Запуск приложения...")
    
    try:
        # Импортируем и запускаем приложение
        from app_mysql import app, init_db
        
        print("Инициализация базы данных...")
        init_db()
        
        print("Запуск веб-сервера...")
        app.run(
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_PORT', 5555)),
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        )
        
    except ImportError as e:
        print(f"Ошибка импорта модулей: {e}")
        print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()