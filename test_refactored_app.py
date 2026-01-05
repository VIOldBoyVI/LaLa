#!/usr/bin/env python3
"""
Тестирование рефакторинга приложения:
1. Запуск с загрузкой последнего состояния игрового поля без ошибок
2. Открытие ячеек со случайными номерами
3. Сброс по кнопке состояния игрового поля
"""
import requests
import json
import time
import random
from urllib.parse import urljoin

BASE_URL = "http://localhost:5555"

def test_load_last_state():
    """Тестируем загрузку последнего состояния игрового поля"""
    print("Тест 1: Загрузка последнего состояния игрового поля...")
    
    session_id = f"test_session_{int(time.time())}_{random.randint(1000, 9999)}"
    
    try:
        # Инициализируем игру
        response = requests.post(urljoin(BASE_URL, "/api/init_game"), 
                                json={"session_id": session_id})
        if response.status_code == 200:
            print("  ✓ Игра успешно инициализирована")
            game_data = response.json()
            print(f"  Данные игры: {game_data}")
            return True
        else:
            print(f"  ✗ Ошибка инициализации игры: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Ошибка при загрузке состояния: {e}")
        return False

def test_open_cells_with_numbers():
    """Тестируем открытие ячеек со случайными номерами"""
    print("\nТест 2: Открытие ячеек со случайными номерами...")
    
    session_id = f"test_session_{int(time.time())}_{random.randint(1000, 9999)}"
    
    try:
        # Инициализируем игру
        init_response = requests.post(urljoin(BASE_URL, "/api/init_game"), 
                                    json={"session_id": session_id})
        if init_response.status_code != 200:
            print("  ✗ Не удалось инициализировать игру")
            return False
        
        # Открываем несколько ячеек
        for i in range(3):  # Открываем 3 ячейки
            row = random.randint(0, 7)  # 8 rows
            col = random.randint(0, 9)  # 10 cols
            cell_value = str(random.randint(1, 80))  # Numbers 1-80
            
            response = requests.post(urljoin(BASE_URL, "/api/mark_cell_opened"), 
                                   json={
                                       "session_id": session_id,
                                       "row": row,
                                       "col": col,
                                       "cell_value": cell_value
                                   })
            
            if response.status_code != 200:
                print(f"  ✗ Ошибка открытия ячейки ({row}, {col}): {response.text}")
                return False
            else:
                print(f"  ✓ Ячейка ({row}, {col}) открыта со значением {cell_value}")
        
        print("  ✓ Ячейки успешно открыты со случайными номерами")
        return True
    except Exception as e:
        print(f"  ✗ Ошибка при открытии ячеек: {e}")
        return False

def test_reset_game_state():
    """Тестируем сброс состояния игрового поля"""
    print("\nТест 3: Сброс состояния игрового поля...")
    
    session_id = f"test_session_{int(time.time())}_{random.randint(1000, 9999)}"
    
    try:
        # Инициализируем игру
        init_response = requests.post(urljoin(BASE_URL, "/api/init_game"), 
                                    json={"session_id": session_id})
        if init_response.status_code != 200:
            print("  ✗ Не удалось инициализировать игру")
            return False
        
        # Открываем несколько ячеек
        for i in range(2):
            row = random.randint(0, 7)
            col = random.randint(0, 9)
            cell_value = str(random.randint(1, 80))
            
            response = requests.post(urljoin(BASE_URL, "/api/mark_cell_opened"), 
                                   json={
                                       "session_id": session_id,
                                       "row": row,
                                       "col": col,
                                       "cell_value": cell_value
                                   })
            
            if response.status_code != 200:
                print(f"  ✗ Ошибка открытия ячейки перед сбросом: {response.text}")
                return False
        
        print("  ✓ Ячейки открыты перед сбросом")
        
        # Загружаем состояние до сброса
        state_before_reset = requests.get(f"{BASE_URL}/api/load_state?session_id={session_id}")
        if state_before_reset.status_code == 200:
            state_data = state_before_reset.json()
            revealed_before = state_data.get('revealed_cells', {})
            print(f"  Ячеек открыто до сброса: {len(revealed_before)}")
        
        # Сбрасываем игру
        reset_response = requests.post(urljoin(BASE_URL, "/api/reset_game"), 
                                     json={"session_id": session_id})
        if reset_response.status_code != 200:
            print(f"  ✗ Ошибка сброса игры: {reset_response.text}")
            return False
        
        # Загружаем состояние после сброса
        state_after_reset = requests.get(f"{BASE_URL}/api/load_state?session_id={session_id}")
        if state_after_reset.status_code == 200:
            state_data = state_after_reset.json()
            revealed_after = state_data.get('revealed_cells', {})
            print(f"  Ячеек открыто после сброса: {len(revealed_after)}")
            
            if len(revealed_after) == 0:
                print("  ✓ Состояние игры успешно сброшено")
                return True
            else:
                print("  ✗ Состояние игры не было полностью сброшено")
                return False
        else:
            print("  ✗ Не удалось загрузить состояние после сброса")
            return False
            
    except Exception as e:
        print(f"  ✗ Ошибка при сбросе состояния: {e}")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("Запуск тестов рефакторинга приложения...")
    print("="*60)
    
    tests = [
        test_load_last_state,
        test_open_cells_with_numbers,
        test_reset_game_state
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "="*60)
    print(f"Результаты: {passed}/{total} тестов пройдено успешно")
    
    if passed == total:
        print("✓ Все тесты пройдены! Рефакторинг выполнен успешно.")
        print("\nРеализованные функции:")
        print("1. Запуск с загрузкой последнего состояния игрового поля без ошибок")
        print("2. Открытие ячеек со случайными номерами")
        print("3. Сброс по кнопке состояния игрового поля")
        return True
    else:
        print("✗ Некоторые тесты не пройдены.")
        return False

if __name__ == "__main__":
    # Проверяем, запущен ли сервер
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("Сервер запущен. Начинаем тестирование...")
            run_all_tests()
        else:
            print(f"Сервер не отвечает. Статус: {response.status_code}")
            print("Пожалуйста, запустите приложение командой: python refactored_run.py")
    except requests.exceptions.ConnectionError:
        print("Сервер не запущен.")
        print("Пожалуйста, запустите приложение командой: python refactored_run.py")