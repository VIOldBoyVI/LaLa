#!/usr/bin/env python3
"""
ЛА-ЛА-ГЕЙМ - Викторина с элементами караоке
Основное Flask-приложение с улучшенной архитектурой
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import random
import json
from typing import Optional, Dict, Any

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
DATABASE = 'database.db'


def get_db_connection() -> Optional[sqlite3.Connection]:
    """
    Создает соединение с базой данных с надлежащей обработкой ошибок
    """
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по имени
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


def init_db() -> None:
    """
    Инициализирует базу данных, создавая таблицы и заполняя начальными данными
    """
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to database for initialization")
        return
    
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_num INTEGER,
            question_text TEXT NOT NULL,
            answer TEXT NOT NULL,
            theme TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            current_round INTEGER DEFAULT 1,
            current_cell TEXT,
            score INTEGER DEFAULT 0,
            revealed_cells TEXT,  -- JSON string of revealed cells
            board_state TEXT,     -- JSON string of the entire board state
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opened_cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            round_num INTEGER NOT NULL,
            row_num INTEGER NOT NULL,
            col_num INTEGER NOT NULL,
            cell_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            round_num INTEGER,
            player_name TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            player_name TEXT,
            score INTEGER DEFAULT 0,
            position INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Добавление вопросов в базу данных
    from config import get_questions
    questions = get_questions()

    cursor.executemany('INSERT OR IGNORE INTO questions (round_num, question_text, answer, theme) VALUES (?, ?, ?, ?)', questions)

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/quiz')
def quiz():
    return render_template('quiz_game.html')


@app.route('/quiz-game')
def quiz_game():
    return render_template('quiz-game.html')


@app.route('/api/save_board_layout', methods=['POST'])
def save_board_layout():
    data = request.json
    session_id = data.get('session_id')
    board_layout = data.get('board_layout')

    import json
    board_layout_str = json.dumps(board_layout) if board_layout else None

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # First, try to load existing game state
    cursor.execute('SELECT * FROM game_states WHERE session_id = ?', (session_id,))
    existing_game = cursor.fetchone()

    if existing_game:
        # Update the board_state field
        cursor.execute(
            'UPDATE game_states SET board_state = ? WHERE session_id = ?',
            (board_layout_str, session_id))
    else:
        # Create new game state with board layout
        cursor.execute(
            'INSERT INTO game_states (session_id, board_state) VALUES (?, ?)',
            (session_id, board_layout_str))

    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


@app.route('/api/init_game', methods=['POST'])
def init_game():
    session_id = request.json.get('session_id')
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # Проверяем, существует ли уже игра с этим session_id
    cursor.execute('SELECT * FROM game_states WHERE session_id = ?', (session_id,))
    existing_game = cursor.fetchone()

    if existing_game:
        # Если игра существует, возвращаем текущее состояние
        current_round = existing_game[2]
        current_cell = existing_game[3]
        score = existing_game[4]
        revealed_cells = existing_game[5]
        board_state = existing_game[6]
    else:
        # Иначе инициализируем новую игру
        current_round = 1
        current_cell = None
        score = 0
        revealed_cells = None
        board_state = None

        # Сохраняем начальное состояние игры
        cursor.execute(
            'INSERT OR REPLACE INTO game_states (session_id, current_round, current_cell, score, revealed_cells, board_state) VALUES (?, ?, ?, ?, ?, ?)',
            (session_id, current_round, current_cell, score, revealed_cells, board_state))

    conn.commit()
    conn.close()

    return jsonify({
        'session_id': session_id,
        'current_round': current_round,
        'current_cell': current_cell,
        'score': score,
        'revealed_cells': revealed_cells,
        'board_state': board_state
    })


@app.route('/api/get_question', methods=['POST'])
def get_question():
    data = request.json
    session_id = data.get('session_id')
    round_num = data.get('round_num')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # Получаем случайный вопрос для текущего раунда
    cursor.execute('SELECT id, question_text FROM questions WHERE round_num = ? ORDER BY RANDOM() LIMIT 1',
                   (round_num,))
    question = cursor.fetchone()

    conn.close()

    if question:
        return jsonify({'question_id': question[0], 'question_text': question[1]})
    else:
        return jsonify({'error': 'No questions available for this round'}), 404


@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('answer').strip().lower()

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # Получаем правильный ответ
    cursor.execute('SELECT answer FROM questions WHERE id = ?', (question_id,))
    correct_answer = cursor.fetchone()

    conn.close()

    if correct_answer:
        correct = correct_answer[0].strip().lower() == user_answer
        return jsonify({'correct': correct, 'correct_answer': correct_answer[0]})
    else:
        return jsonify({'error': 'Question not found'}), 404


@app.route('/api/save_state', methods=['POST'])
def save_state():
    data = request.json
    session_id = data.get('session_id')
    current_round = data.get('current_round')
    current_cell = data.get('current_cell')
    score = data.get('score')
    revealed_cells = data.get('revealed_cells')  # JSON string of revealed cells
    board_state = data.get('board_state')  # JSON string of the entire board state

    import json
    board_state_str = json.dumps(board_state) if board_state else None

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute(
        'INSERT OR REPLACE INTO game_states (session_id, current_round, current_cell, score, revealed_cells, board_state) VALUES (?, ?, ?, ?, ?, ?)',
        (session_id, current_round, current_cell, score, revealed_cells, board_state_str))

    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


@app.route('/api/load_state', methods=['GET'])
def load_state():
    session_id = request.args.get('session_id')

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute('SELECT current_round, current_cell, score, revealed_cells, board_state FROM game_states WHERE session_id = ?', (session_id,))
    game_state = cursor.fetchone()

    # Get players for this session
    cursor.execute('SELECT player_name, score FROM players WHERE session_id = ? ORDER BY position', (session_id,))
    players = [{'player_name': row[0], 'score': row[1]} for row in cursor.fetchall()]

    conn.close()

    if game_state:
        import json
        board_state = game_state[4]
        # Try to parse board_state as JSON if it's not None
        if board_state:
            try:
                parsed_board_state = json.loads(board_state)
                board_state = parsed_board_state
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, return as is (it might already be parsed)
                pass

        return jsonify({
            'current_round': game_state[0],
            'current_cell': game_state[1],
            'score': game_state[2],
            'revealed_cells': game_state[3],
            'board_state': board_state,
            'players': players
        })
    else:
        return jsonify({'error': 'No saved state found'}), 404


@app.route('/api/get_players', methods=['GET'])
def get_players():
    session_id = request.args.get('session_id')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute('SELECT player_name, score FROM players WHERE session_id = ? ORDER BY position', (session_id,))
    players = [{'player_name': row[0], 'score': row[1]} for row in cursor.fetchall()]

    conn.close()
    
    return jsonify({'players': players})


@app.route('/api/add_player', methods=['POST'])
def add_player():
    data = request.json
    session_id = data.get('session_id')
    player_name = data.get('player_name', f'Игрок {len(data.get("players", [])) + 1}')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # Get the highest position to determine where to insert the new player
    cursor.execute('SELECT MAX(position) FROM players WHERE session_id = ?', (session_id,))
    max_pos = cursor.fetchone()[0]
    new_position = 1 if max_pos is None else max_pos + 1

    cursor.execute(
        'INSERT INTO players (session_id, player_name, score, position) VALUES (?, ?, 0, ?)',
        (session_id, player_name, new_position)
    )

    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'player': {'player_name': player_name, 'score': 0}})


@app.route('/api/update_player', methods=['POST'])
def update_player():
    data = request.json
    session_id = data.get('session_id')
    player_name = data.get('player_name')
    new_score = data.get('score', 0)
    new_player_name = data.get('new_player_name', player_name)  # If new name is provided, use it
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # If player name is changing, update it
    if new_player_name != player_name:
        cursor.execute(
            'UPDATE players SET score = ?, player_name = ? WHERE session_id = ? AND player_name = ?',
            (new_score, new_player_name, session_id, player_name)
        )
    else:
        cursor.execute(
            'UPDATE players SET score = ? WHERE session_id = ? AND player_name = ?',
            (new_score, session_id, player_name)
        )

    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})


@app.route('/api/remove_player', methods=['POST'])
def remove_player():
    data = request.json
    session_id = data.get('session_id')
    player_name = data.get('player_name')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute('DELETE FROM players WHERE session_id = ? AND player_name = ?', (session_id, player_name))

    # Reorder positions after deletion
    cursor.execute('SELECT id, player_name FROM players WHERE session_id = ? ORDER BY position', (session_id,))
    remaining_players = cursor.fetchall()
    for idx, (player_id, _) in enumerate(remaining_players, 1):
        cursor.execute('UPDATE players SET position = ? WHERE id = ?', (idx, player_id))

    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})


@app.route('/api/reset_players', methods=['POST'])
def reset_players():
    data = request.json
    session_id = data.get('session_id')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute('DELETE FROM players WHERE session_id = ?', (session_id,))

    # Add two default players
    cursor.execute('INSERT INTO players (session_id, player_name, score, position) VALUES (?, ?, 0, 1)', (session_id, 'Игрок 1'))
    cursor.execute('INSERT INTO players (session_id, player_name, score, position) VALUES (?, ?, 0, 2)', (session_id, 'Игрок 2'))

    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})


import config


@app.route('/api/config', methods=['GET'])
def get_config():
    """Return game configuration"""
    from config import get_symbols, get_game_settings, get_body_style, get_cell_style, get_hover_cell_style, get_revealed_cell_style, get_number_cell_style, get_symbol_cell_style
    game_settings = get_game_settings()
    config = {
        'symbols': get_symbols(),
        'settings': game_settings,
        'body_style': get_body_style(),
        'cell_style': get_cell_style(),
        'hover_cell_style': get_hover_cell_style(),
        'revealed_cell_style': get_revealed_cell_style(),
        'number_cell_style': get_number_cell_style(),
        'symbol_cell_style': get_symbol_cell_style()
    }
    return jsonify(config)


@app.route('/api/mark_cell_opened', methods=['POST'])
def mark_cell_opened():
    data = request.json
    session_id = data.get('session_id')
    round_num = data.get('round_num')
    row = data.get('row')
    col = data.get('col')
    cell_value = data.get('cell_value')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # Check if this cell was already opened in this round for this session
    cursor.execute('''
        SELECT id FROM opened_cells 
        WHERE session_id = ? AND round_num = ? AND row_num = ? AND col_num = ?
    ''', (session_id, round_num, row, col))
    
    existing = cursor.fetchone()
    if existing:
        # Cell already opened, return error
        conn.close()
        return jsonify({'error': 'Cell already opened'}), 400

    # Insert the opened cell record
    cursor.execute('''
        INSERT INTO opened_cells (session_id, round_num, row_num, col_num, cell_value) 
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, round_num, row, col, cell_value))

    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})


@app.route('/api/get_opened_cells', methods=['GET'])
def get_opened_cells():
    session_id = request.args.get('session_id')
    round_num = request.args.get('round_num', type=int)
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute('''
        SELECT row_num, col_num, cell_value FROM opened_cells 
        WHERE session_id = ? AND round_num = ?
    ''', (session_id, round_num))
    
    opened_cells = [{'row': row[0], 'col': row[1], 'value': row[2]} for row in cursor.fetchall()]

    conn.close()
    
    return jsonify({'opened_cells': opened_cells})


@app.route('/api/clear_opened_cells', methods=['POST'])
def clear_opened_cells():
    data = request.json
    session_id = data.get('session_id')
    round_num = data.get('round_num', 1)
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    # Delete all opened cells for this session and round
    cursor.execute('DELETE FROM opened_cells WHERE session_id = ? AND round_num = ?', (session_id, round_num))

    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})


@app.route('/api/get_all_questions', methods=['GET'])
def get_all_questions():
    """Return all questions from the database"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()

    cursor.execute('SELECT id, round_num, question_text, answer, theme FROM questions')
    questions = []
    for row in cursor.fetchall():
        questions.append({
            'id': row[0],
            'round_num': row[1],
            'question_text': row[2],
            'answer': row[3],
            'theme': row[4]
        })

    conn.close()
    
    return jsonify({'questions': questions})


if __name__ == '__main__':
    init_db()
    app.run(
        host='0.0.0.0',
        port=5555,
        debug=False  # В продакшене debug=False более безопасен
    )
