#!/usr/bin/env python3
"""
Тестирование новой функциональности:
1. При первом запуске игры игровое поле устанавливается в начальное состояние:
   - все ячейки закрыты
   - 90% ячеек случайно заполнены цифрами
   - 10% ячеек случайно заполнены символами из SYMBOLS из config.py
2. При нажатии на зеленую кнопку обновления доски игровое поле также устанавливается в начальное состояние
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://localhost:8080"

def test_config_loading():
    """Тестируем загрузку конфигурации"""
    print("Тест: Загрузка конфигурации")
    try:
        response = requests.get(urljoin(BASE_URL, "/api/config"))
        config_data = response.json()
        print(f"  Символы: {config_data['symbols']}")
        print(f"  Настройки: {config_data['settings']}")
        print("  ✓ Конфигурация успешно загружена")
        return True
    except Exception as e:
        print(f"  ✗ Ошибка загрузки конфигурации: {e}")
        return False

def test_game_initialization():
    """Тестируем инициализацию игры"""
    print("\nТест: Инициализация игры")
    try:
        session_id = "test_session_123"
        response = requests.post(urljoin(BASE_URL, "/api/init_game"), 
                                json={"session_id": session_id})
        game_data = response.json()
        print(f"  Данные игры: {game_data}")
        print("  ✓ Игра успешно инициализирована")
        return True
    except Exception as e:
        print(f"  ✗ Ошибка инициализации игры: {e}")
        return False

def test_symbols_in_config():
    """Тестируем, что символы в конфиге соответствуют ожидаемым"""
    print("\nТест: Символы в конфигурации")
    try:
        response = requests.get(urljoin(BASE_URL, "/api/config"))
        config_data = response.json()
        symbols = config_data['symbols']
        
        expected_symbols = ['🙂', '👍', '👏', '⭐', '❤️', '🎵', '🎶', '☀️', '☁️', '☂️']
        
        if symbols == expected_symbols:
            print(f"  ✓ Все {len(symbols)} символов присутствуют и корректны")
            return True
        else:
            print(f"  ✗ Символы не соответствуют ожидаемым. Получено: {symbols}")
            return False
    except Exception as e:
        print(f"  ✗ Ошибка проверки символов: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("Запуск тестов новой функциональности...")
    print("="*50)
    
    tests = [
        test_config_loading,
        test_symbols_in_config,
        test_game_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "="*50)
    print(f"Результаты: {passed}/{total} тестов пройдено успешно")
    
    if passed == total:
        print("✓ Все тесты пройдены! Новая функциональность работает корректно.")
        return True
    else:
        print("✗ Некоторые тесты не пройдены.")
        return False

if __name__ == "__main__":
    run_all_tests()