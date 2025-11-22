from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)  # Enable CORS for frontend communication

# Database setup
DATABASE = 'quiz_game.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create table for game states
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            game_state TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create table for scores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            player_name TEXT,
            score INTEGER DEFAULT 0,
            round INTEGER DEFAULT 1,
            questions_answered INTEGER DEFAULT 0,
            game_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create table for questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            round_number INTEGER NOT NULL,
            theme TEXT NOT NULL,
            question_text TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def create_sample_questions():
    """Create sample questions for the quiz game"""
    conn = get_db_connection()
    
    # Sample questions for each round
    sample_questions = [
        # Round 1 - Music Genres
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой музыкальный жанр ассоциируется с Мадонной?", "correct_answer": "поп", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой инструмент является символом джаза?", "correct_answer": "саксофон", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой жанр музыки возник в Южном Бронксе?", "correct_answer": "рэп", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой музыкальный жанр связан с регги?", "correct_answer": "ямаيكا", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой инструмент является основным в рок-группе?", "correct_answer": "гитара", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой музыкальный жанр использует синтезаторы?", "correct_answer": "электроника", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой жанр возник в Ливерпуле?", "correct_answer": "битлз", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой жанр музыки ассоциируется с блюз?", "correct_answer": "джаз", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой музыкальный жанр появился в 1970-х?", "correct_answer": "диско", "points": 10},
        {"round_number": 1, "theme": "Музыкальные жанры", "question_text": "Какой жанр музыки ассоциируется с кантри?", "correct_answer": "америка", "points": 10},
        
        # Round 2 - Artists
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Кто является королем поп-музыки?", "correct_answer": "майкл джексон", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Как звали королеву диско?", "correct_answer": "донна соммер", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Какой исполнитель носит прозвище Thin White Duke?", "correct_answer": "дэвид боуи", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Кто написал песню 'Bohemian Rhapsody'?", "correct_answer": "квін", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Как звали певицу с прозвищем 'White Queen'?", "correct_answer": "джуди джексон", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Какой рэпер носит прозвище 'Notorious B.I.G.'?", "correct_answer": "кристофер воллес", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Кто является основателем группы The Beatles?", "correct_answer": "джон леннон", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Как зовут королеву соула?", "correct_answer": "эрика фримен", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Какой исполнитель носит прозвище 'King of Rock and Roll'?", "correct_answer": "элвис пресли", "points": 10},
        {"round_number": 2, "theme": "Музыкальные исполнители", "question_text": "Кто из этих артистов носит прозвище 'Material Girl'?", "correct_answer": "мадонна", "points": 10},
        
        # Round 3 - Instruments
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент имеет педали?", "correct_answer": "фортепиано", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент имеет 6 струн?", "correct_answer": "гитара", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент используют в джазе?", "correct_answer": "саксофон", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент имеет ударную головку?", "correct_answer": "барабан", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент используется в классической музыке?", "correct_answer": "скрипка", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент создает звук с помощью воздуха?", "correct_answer": "флейта", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент имеет 88 клавиш?", "correct_answer": "пианино", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент используют диджеи?", "correct_answer": "самплер", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент используют в регги?", "correct_answer": "гитара", "points": 10},
        {"round_number": 3, "theme": "Музыкальные инструменты", "question_text": "Какой инструмент используется в оркестре?", "correct_answer": "виолончель", "points": 10},
        
        # Round 4 - Music History
        {"round_number": 4, "theme": "История музыки", "question_text": "В каком году вышел альбом 'Thriller'?", "correct_answer": "1982", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "Какой год считается началом рока?", "correct_answer": "1954", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "В каком году умер Фредди Меркьюри?", "correct_answer": "1991", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "Какой год считается началом джаза?", "correct_answer": "1910", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "В каком году вышел первый альбом The Beatles?", "correct_answer": "1963", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "Какой год связан с рождением хип-хопа?", "correct_answer": "1973", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "В каком году вышел альбом 'Abbey Road'?", "correct_answer": "1969", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "Какой год связан с фестивалем Вудсток?", "correct_answer": "1969", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "В каком году вышел альбом 'Dark Side of the Moon'?", "correct_answer": "1973", "points": 10},
        {"round_number": 4, "theme": "История музыки", "question_text": "Какой год связан с смертью Джими Хендрикса?", "correct_answer": "1970", "points": 10},
        
        # Round 5 - Final Round - Mixed
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой жанр музыки ассоциируется с Битлз?", "correct_answer": "рок", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой инструмент использовал Игорь Стравинский?", "correct_answer": "оркестр", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Как звали композитора 'Времена года'?", "correct_answer": "вести", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой год связан с выходом 'Never Mind the Bollocks'?", "correct_answer": "1977", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой музыкальный жанр ассоциируется с Тупаком?", "correct_answer": "рэп", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой инструмент использовал Яннис Кризанакис?", "correct_answer": "оркестр", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой жанр музыки ассоциируется с Майлзом Дэвисом?", "correct_answer": "джаз", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Как зовут короля рока?", "correct_answer": "элвис", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой инструмент использовал Иегуди Менухин?", "correct_answer": "скрипка", "points": 10},
        {"round_number": 5, "theme": "Музыкальный микс", "question_text": "Какой жанр музыки ассоциируется с Бобом Марли?", "correct_answer": "регги", "points": 10},
    ]
    
    # Insert questions if they don't exist yet
    for q in sample_questions:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO questions (round_number, theme, question_text, correct_answer, points)
            VALUES (?, ?, ?, ?, ?)
        ''', (q['round_number'], q['theme'], q['question_text'], q['correct_answer'], q['points']))
    
    conn.commit()
    conn.close()

@app.route('/api/init-game', methods=['POST'])
def init_game():
    """Initialize a new game session"""
    data = request.json
    session_id = data.get('session_id', '')
    
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    # Create a default game state
    default_state = {
        'currentRound': 1,
        'score': 0,
        'openedCells': [],
        'questionsUsed': [],
        'isBreak': False,
        'board': [],
        'playerName': data.get('player_name', 'Игрок')
    }
    
    # Save the game state to the database
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO game_states (session_id, game_state)
            VALUES (?, ?)
        ''', (session_id, json.dumps(default_state)))
        
        # Create score entry
        cursor.execute('''
            INSERT INTO scores (session_id, player_name, score, round)
            VALUES (?, ?, ?, ?)
        ''', (session_id, default_state['playerName'], 0, 1))
        
        conn.commit()
        return jsonify({'success': True, 'game_state': default_state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/load-game/<session_id>', methods=['GET'])
def load_game(session_id):
    """Load an existing game session"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT game_state FROM game_states WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        
        if row:
            game_state = json.loads(row['game_state'])
            return jsonify({'success': True, 'game_state': game_state})
        else:
            return jsonify({'error': 'Game session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/save-game', methods=['POST'])
def save_game():
    """Save the current game state"""
    data = request.json
    session_id = data.get('session_id', '')
    game_state = data.get('game_state', {})
    
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO game_states (session_id, game_state, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (session_id, json.dumps(game_state)))
        
        # Update score in scores table
        cursor.execute('''
            UPDATE scores 
            SET score = ?, round = ?, questions_answered = ?
            WHERE session_id = ?
        ''', (game_state.get('score', 0), game_state.get('currentRound', 1), 
              len(game_state.get('questionsUsed', [])), session_id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/get-question/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """Get a specific question by ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
        row = cursor.fetchone()
        
        if row:
            question = {
                'id': row['id'],
                'round_number': row['round_number'],
                'theme': row['theme'],
                'question_text': row['question_text'],
                'points': row['points']
            }
            return jsonify({'success': True, 'question': question})
        else:
            return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    """Check if the provided answer is correct"""
    data = request.json
    question_id = data.get('question_id')
    provided_answer = data.get('answer', '').lower().strip()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT correct_answer FROM questions WHERE id = ?', (question_id,))
        row = cursor.fetchone()
        
        if row:
            correct_answer = row['correct_answer'].lower().strip()
            is_correct = provided_answer == correct_answer or correct_answer in provided_answer or provided_answer in correct_answer
            
            return jsonify({
                'success': True,
                'is_correct': is_correct,
                'correct_answer': row['correct_answer']
            })
        else:
            return jsonify({'error': 'Question not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/get-round-questions/<int:round_number>', methods=['GET'])
def get_round_questions(round_number):
    """Get all questions for a specific round"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, round_number, theme, question_text, points 
            FROM questions 
            WHERE round_number = ?
        ''', (round_number,))
        
        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row['id'],
                'round_number': row['round_number'],
                'theme': row['theme'],
                'question_text': row['question_text'],
                'points': row['points']
            })
        
        return jsonify({'success': True, 'questions': questions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/get-leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the top scores"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT player_name, score, round, created_at 
            FROM scores 
            ORDER BY score DESC 
            LIMIT 10
        ''')
        
        leaderboard = []
        for row in cursor.fetchall():
            leaderboard.append({
                'player_name': row['player_name'],
                'score': row['score'],
                'round': row['round'],
                'created_at': row['created_at']
            })
        
        return jsonify({'success': True, 'leaderboard': leaderboard})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialize database and create sample questions
    init_db()
    create_sample_questions()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)