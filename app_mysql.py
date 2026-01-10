#!/usr/bin/env python3
"""
ЛА-ЛА-ГЕЙМ - Викторина с элементами караоке
Обновленное Flask-приложение с безопасным подключением к MySQL
и поддержкой пула соединений, SSL/TLS и транзакций
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import random
import json
from typing import Optional, Dict, Any
import logging

from db_config import get_db_connection, get_db_transaction, test_connection
from models import Question, GameState, OpenedCell, Score, Player, init_database

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """
    Инициализирует базу данных MySQL, создавая таблицы и заполняя начальными данными
    """
    try:
        # Initialize the SQLAlchemy models
        init_database()
        logger.info("Database initialized successfully")
        
        # Add initial questions if they don't exist
        from config import get_questions
        
        # We'll use SQLAlchemy session to add questions
        from models import get_session
        session = get_session()
        
        # Check if questions already exist
        existing_count = session.query(Question).count()
        if existing_count == 0:
            questions = get_questions()
            for q in questions:
                question = Question(
                    round_num=q[0],
                    question_text=q[1],
                    answer=q[2],
                    theme=q[3]
                )
                session.add(question)
            session.commit()
            logger.info(f"Added {len(questions)} initial questions to the database")
        else:
            logger.info(f"Database already contains {existing_count} questions")
        
        session.close()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        # Don't raise the exception here so the app can continue
        # This allows fallback to SQLite if MySQL is not available
        print(f"Warning: Could not initialize MySQL database: {e}")
        print("Application will continue without MySQL database")

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

    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor(dictionary=True)

            # First, try to load existing game state
            cursor.execute('SELECT * FROM game_states WHERE session_id = %s', (session_id,))
            existing_game = cursor.fetchone()

            if existing_game:
                # Update the board_state field
                cursor.execute(
                    'UPDATE game_states SET board_state = %s WHERE session_id = %s',
                    (board_layout_str, session_id))
            else:
                # Create new game state with board layout
                cursor.execute(
                    'INSERT INTO game_states (session_id, board_state) VALUES (%s, %s)',
                    (session_id, board_layout_str))

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving board layout: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/init_game', methods=['POST'])
def init_game():
    session_id = request.json.get('session_id')
    
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor(dictionary=True)

            # Проверяем, существует ли уже игра с этим session_id
            cursor.execute('SELECT * FROM game_states WHERE session_id = %s', (session_id,))
            existing_game = cursor.fetchone()

            if existing_game:
                # Если игра существует, возвращаем текущее состояние
                current_round = existing_game['current_round']
                current_cell = existing_game['current_cell']
                score = existing_game['score']
                revealed_cells = existing_game['revealed_cells']
                board_state = existing_game['board_state']
            else:
                # Иначе инициализируем новую игру
                current_round = 1
                current_cell = None
                score = 0
                revealed_cells = None
                board_state = None

                # Сохраняем начальное состояние игры
                cursor.execute(
                    'INSERT INTO game_states (session_id, current_round, current_cell, score, revealed_cells, board_state) VALUES (%s, %s, %s, %s, %s, %s)',
                    (session_id, current_round, current_cell, score, revealed_cells, board_state))

            conn.commit()

            return jsonify({
                'session_id': session_id,
                'current_round': current_round,
                'current_cell': current_cell,
                'score': score,
                'revealed_cells': revealed_cells,
                'board_state': board_state
            })
    except Exception as e:
        logger.error(f"Error initializing game: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/get_question', methods=['POST'])
def get_question():
    data = request.json
    session_id = data.get('session_id')
    round_num = data.get('round_num')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Получаем случайный вопрос для текущего раунда
            cursor.execute('SELECT id, question_text FROM questions WHERE round_num = %s ORDER BY RAND() LIMIT 1',
                           (round_num,))
            question = cursor.fetchone()

            if question:
                return jsonify({'question_id': question['id'], 'question_text': question['question_text']})
            else:
                return jsonify({'error': 'No questions available for this round'}), 404
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('answer').strip().lower()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            # Получаем правильный ответ
            cursor.execute('SELECT answer FROM questions WHERE id = %s', (question_id,))
            correct_answer = cursor.fetchone()

            if correct_answer:
                correct = correct_answer['answer'].strip().lower() == user_answer
                return jsonify({'correct': correct, 'correct_answer': correct_answer['answer']})
            else:
                return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        logger.error(f"Error checking answer: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

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

    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            cursor.execute(
                'INSERT INTO game_states (session_id, current_round, current_cell, score, revealed_cells, board_state) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE current_round=%s, current_cell=%s, score=%s, revealed_cells=%s, board_state=%s',
                (session_id, current_round, current_cell, score, revealed_cells, board_state_str,
                 current_round, current_cell, score, revealed_cells, board_state_str))

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving game state: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/load_state', methods=['GET'])
def load_state():
    session_id = request.args.get('session_id')

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute('SELECT current_round, current_cell, score, revealed_cells, board_state FROM game_states WHERE session_id = %s', (session_id,))
            game_state = cursor.fetchone()

            # Get players for this session
            cursor.execute('SELECT player_name, score FROM players WHERE session_id = %s ORDER BY position', (session_id,))
            players = [{'player_name': row['player_name'], 'score': row['score']} for row in cursor.fetchall()]

            if game_state:
                import json
                board_state = game_state['board_state']
                # Try to parse board_state as JSON if it's not None
                if board_state:
                    try:
                        parsed_board_state = json.loads(board_state)
                        board_state = parsed_board_state
                    except (json.JSONDecodeError, TypeError):
                        # If parsing fails, return as is (it might already be parsed)
                        pass

                return jsonify({
                    'current_round': game_state['current_round'],
                    'current_cell': game_state['current_cell'],
                    'score': game_state['score'],
                    'revealed_cells': game_state['revealed_cells'],
                    'board_state': board_state,
                    'players': players
                })
            else:
                return jsonify({'error': 'No saved state found'}), 404
    except Exception as e:
        logger.error(f"Error loading game state: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/get_players', methods=['GET'])
def get_players():
    session_id = request.args.get('session_id')
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute('SELECT player_name, score FROM players WHERE session_id = %s ORDER BY position', (session_id,))
            players = [{'player_name': row['player_name'], 'score': row['score']} for row in cursor.fetchall()]

            return jsonify({'players': players})
    except Exception as e:
        logger.error(f"Error getting players: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/add_player', methods=['POST'])
def add_player():
    data = request.json
    session_id = data.get('session_id')
    player_name = data.get('player_name', f'Игрок {len(data.get("players", [])) + 1}')
    
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            # Get the highest position to determine where to insert the new player
            cursor.execute('SELECT MAX(position) FROM players WHERE session_id = %s', (session_id,))
            result = cursor.fetchone()
            max_pos = result[0] if result[0] is not None else 0
            new_position = 1 if max_pos == 0 else max_pos + 1

            cursor.execute(
                'INSERT INTO players (session_id, player_name, score, position) VALUES (%s, %s, 0, %s)',
                (session_id, player_name, new_position)
            )

            conn.commit()
            return jsonify({'status': 'success', 'player': {'player_name': player_name, 'score': 0}})
    except Exception as e:
        logger.error(f"Error adding player: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/update_player', methods=['POST'])
def update_player():
    data = request.json
    session_id = data.get('session_id')
    player_name = data.get('player_name')
    new_score = data.get('score', 0)
    new_player_name = data.get('new_player_name', player_name)  # If new name is provided, use it
    
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            # If player name is changing, update it
            if new_player_name != player_name:
                cursor.execute(
                    'UPDATE players SET score = %s, player_name = %s WHERE session_id = %s AND player_name = %s',
                    (new_score, new_player_name, session_id, player_name)
                )
            else:
                cursor.execute(
                    'UPDATE players SET score = %s WHERE session_id = %s AND player_name = %s',
                    (new_score, session_id, player_name)
                )

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error updating player: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/remove_player', methods=['POST'])
def remove_player():
    data = request.json
    session_id = data.get('session_id')
    player_name = data.get('player_name')
    
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM players WHERE session_id = %s AND player_name = %s', (session_id, player_name))

            # Reorder positions after deletion
            cursor.execute('SELECT id, player_name FROM players WHERE session_id = %s ORDER BY position', (session_id,))
            remaining_players = cursor.fetchall()
            for idx, (player_id, _) in enumerate(remaining_players, 1):
                cursor.execute('UPDATE players SET position = %s WHERE id = %s', (idx, player_id))

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error removing player: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/reset_players', methods=['POST'])
def reset_players():
    data = request.json
    session_id = data.get('session_id')
    
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM players WHERE session_id = %s', (session_id,))

            # Add two default players
            cursor.execute('INSERT INTO players (session_id, player_name, score, position) VALUES (%s, %s, 0, 1)', (session_id, 'Игрок 1'))
            cursor.execute('INSERT INTO players (session_id, player_name, score, position) VALUES (%s, %s, 0, 2)', (session_id, 'Игрок 2'))

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error resetting players: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

import config

@app.route('/api/config', methods=['GET'])
def get_config():
    """Return game configuration"""
    from config import get_symbols, get_game_settings, get_body_style, get_cell_style, get_hover_cell_style, get_revealed_cell_style, get_number_cell_style, get_symbol_cell_style
    game_settings = get_game_settings()
    config_data = {
        'symbols': get_symbols(),
        'settings': game_settings,
        'body_style': get_body_style(),
        'cell_style': get_cell_style(),
        'hover_cell_style': get_hover_cell_style(),
        'revealed_cell_style': get_revealed_cell_style(),
        'number_cell_style': get_number_cell_style(),
        'symbol_cell_style': get_symbol_cell_style()
    }
    return jsonify(config_data)

@app.route('/api/mark_cell_opened', methods=['POST'])
def mark_cell_opened():
    data = request.json
    session_id = data.get('session_id')
    round_num = data.get('round_num')
    row = data.get('row')
    col = data.get('col')
    cell_value = data.get('cell_value')
    
    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            # Check if this cell was already opened in this round for this session
            cursor.execute('''
                SELECT id FROM opened_cells 
                WHERE session_id = %s AND round_num = %s AND row_num = %s AND col_num = %s
            ''', (session_id, round_num, row, col))
            
            existing = cursor.fetchone()
            if existing:
                # Cell already opened, return error
                return jsonify({'error': 'Cell already opened'}), 400

            # Insert the opened cell record
            cursor.execute('''
                INSERT INTO opened_cells (session_id, round_num, row_num, col_num, cell_value) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (session_id, round_num, row, col, cell_value))

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error marking cell as opened: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/get_opened_cells', methods=['GET'])
def get_opened_cells():
    session_id = request.args.get('session_id')
    round_num = request.args.get('round_num', type=int)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute('''
                SELECT row_num, col_num, cell_value FROM opened_cells
                WHERE session_id = %s AND round_num = %s
            ''', (session_id, round_num))

            opened_cells = [{'row': row['row_num'], 'col': row['col_num'], 'value': row['cell_value']} for row in cursor.fetchall()]

            return jsonify({'opened_cells': opened_cells})
    except Exception as e:
        logger.error(f"Error getting opened cells: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/clear_opened_cells', methods=['POST'])
def clear_opened_cells():
    data = request.json
    session_id = data.get('session_id')
    round_num = data.get('round_num', 1)

    try:
        with get_db_transaction() as conn:
            cursor = conn.cursor()

            # Delete all opened cells for this session and round
            cursor.execute('DELETE FROM opened_cells WHERE session_id = %s AND round_num = %s', (session_id, round_num))

            conn.commit()
            return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error clearing opened cells: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/api/get_all_questions', methods=['GET'])
def get_all_questions():
    """Return all questions from the database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute('SELECT id, round_num, question_text, answer, theme FROM questions')
            questions = []
            for row in cursor.fetchall():
                questions.append({
                    'id': row['id'],
                    'round_num': row['round_num'],
                    'question_text': row['question_text'],
                    'answer': row['answer'],
                    'theme': row['theme']
                })

            return jsonify({'questions': questions})
    except Exception as e:
        logger.error(f"Error getting all questions: {e}")
        return jsonify({'error': 'Database operation failed'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify database connectivity"""
    try:
        is_connected = test_connection()
        if is_connected:
            return jsonify({'status': 'healthy', 'database': 'connected'})
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

if __name__ == '__main__':
    init_db()
    app.run(
        host='0.0.0.0',
        port=5555,
        debug=False  # В продакшене debug=False более безопасен
    )