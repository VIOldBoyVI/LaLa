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
from typing import Optional, Dict, Any


class QuizGameApp:
    """
    Класс-обертка для Flask-приложения викторины
    """
    
    def __init__(self):
        # Set template folder to use templates from the main directory
        self.app = Flask(__name__, template_folder='../templates')
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
        CORS(self.app)  # Enable CORS for all routes
        self.DATABASE = 'database.db'
        self._setup_routes()
    
    def get_db_connection(self) -> Optional[sqlite3.Connection]:
        """
        Создает соединение с базой данных с надлежащей обработкой ошибок
        """
        try:
            conn = sqlite3.connect(self.DATABASE)
            conn.row_factory = sqlite3.Row  # Позволяет обращаться к столбцам по имени
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def init_db(self) -> None:
        """
        Инициализирует базу данных, создавая таблицы и заполняя начальными данными
        """
        conn = self.get_db_connection()
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

        # Добавление вопросов в базу данных
        questions = [
            # Round 1: Музыкальные жанры
            (1, "Какое музыкальное направление считается предшественником рока?", "Блюз", "Музыкальные жанры"),
            (1, "Кто считается королем рок-н-ролла?", "Элвис Пресли", "Музыкальные жанры"),
            (1, "Как называется группа, выпустившая альбом 'Dark Side of the Moon'?", "Pink Floyd", "Музыкальные жанры"),
            (1, "Как звали вокалиста группы Queen?", "Фредди Меркьюри", "Музыкальные жанры"),
            (1, "Какой инструмент использовал Игорь Стравинский в 'Весне Священной'?", "Оркестр", "Музыкальные жанры"),
            (1, "Какой музыкальный инструмент является самым большим в оркестре?", "Контрабас", "Музыкальные жанры"),
            (1, "Как называется стиль музыки, происходящий из Ямайки?", "Регги", "Музыкальные жанры"),
            (1, "Кто написал оперу 'Волшебная флейта'?", "Моцарт", "Музыкальные жанры"),
            (1, "Как называется танец в ¾ времени?", "Вальс", "Музыкальные жанры"),
            (1, "Какой инструмент использовал Бах в своих произведениях?", "Орган", "Музыкальные жанры"),
            (1, "Какой жанр музыки связан с джазом?", "Блюз", "Музыкальные жанры"),
            (1, "Какой инструмент используется в стиле 'караоке'?", "Клавишные", "Музыкальные жанры"),
            (1, "Какой стиль музыки был популярен в 80-х?", "Поп", "Музыкальные жанры"),
            (1, "Какой инструмент является основным в рок-группе?", "Гитара", "Музыкальные жанры"),
            (1, "Какой музыкальный стиль ассоциируется с Бобом Марли?", "Регги", "Музыкальные жанры"),
            (1, "Какой инструмент использовал Сергей Рахманинов?", "Фортепиано", "Музыкальные жанры"),
            (1, "Какой стиль музыки использует синтезаторы?", "Электроника", "Музыкальные жанры"),
            (1, "Какой музыкальный жанр возник в Новом Орлеане?", "Джаз", "Музыкальные жанры"),
            (1, "Как называется группа, исполняющая 'Bohemian Rhapsody'?", "Queen", "Музыкальные жанры"),
            (1, "Какой инструмент использовал Пётр Чайковский?", "Скрипка", "Музыкальные жанры"),
            
            # Round 2: Музыкальные исполнители
            (2, "Кто является основателем группы The Beatles?", "Джон Леннон", "Музыкальные исполнители"),
            (2, "Как звали солистку группы ABBA?", "Агнета Фельтског", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы AC/DC?", "Бон Сcott", "Музыкальные исполнители"),
            (2, "Какой псевдоним у Роберта Зоммера?", "Боб Марли", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Led Zeppelin?", "Роберт Плант", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Deep Purple?", "Иэн Гиллан", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Black Sabbath?", "Оззи Осборн", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы The Rolling Stones?", "Мик Джаггер", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы The Who?", "Роджер Долтри", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы The Doors?", "Джим Моррисон", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы The Eagles?", "Гленн Фрай", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Lynyrd Skynyrd?", "Ронни Ван Зант", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы ZZ Top?", "Билли Гиббонс", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Kiss?", "Пол Стэйн", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Rush?", "Гэддзи Ли", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Van Halen?", "Дэвид Ли Рот", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Foreigner?", "Лу Грамм", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Journey?", "Стиви Перри", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Boston?", "Брюс Куланж", "Музыкальные исполнители"),
            (2, "Как зовут солиста группы Styx?", "Деннис ДеЯнг", "Музыкальные исполнители"),
            
            # Round 3: Музыкальные инструменты
            (3, "Какой инструмент имеет 6 струн?", "Гитара", "Музыкальные инструменты"),
            (3, "Какой инструмент имеет педали?", "Фортепиано", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в джазе?", "Саксофон", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в оркестре?", "Скрипка", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в рок-группе?", "Ударные", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в классической музыке?", "Виолончель", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в блюзе?", "Тромбон", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в регги?", "Конга", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в фолк-музыке?", "Мандолина", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в электронной музыке?", "Синтезатор", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в народной музыке?", "Балалайка", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в рэпе?", "Сэмплер", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в опере?", "Арфа", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в рок-н-ролле?", "Саксофон", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в хип-хопе?", "Драм-машина", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в фанке?", "Бас-гитара", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в соуле?", "Труба", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в кантри?", "Педальная сталь", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в латиноамериканской музыке?", "Маракас", "Музыкальные инструменты"),
            (3, "Какой инструмент используется в фолк-роке?", "Укулеле", "Музыкальные инструменты"),
            
            # Round 4: Музыкальная история
            (4, "Когда был изобретён первый музыкальный инструмент?", "35000 лет назад", "Музыкальная история"),
            (4, "Кто написал 'Лунную сонату'?", "Бетховен", "Музыкальная история"),
            (4, "Какой музыкальный инструмент был изобретён первым?", "Барабан", "Музыкальная история"),
            (4, "Когда появился первый граммофон?", "1877", "Музыкальная история"),
            (4, "Кто основал компанию Fender?", "Лео Фендер", "Музыкальная история"),
            (4, "Когда была основана компания Gibson?", "1902", "Музыкальная история"),
            (4, "Кто изобрёл первый синтезатор?", "Роберт Мууг", "Музыкальная история"),
            (4, "Когда был изобретён первый синтезатор?", "1964", "Музыкальная история"),
            (4, "Кто написал 'Лето' в стиле вивальди?", "Антонио Вивальди", "Музыкальная история"),
            (4, "Когда был изобретён первый музыкальный автомат?", "1890", "Музыкальная история"),
            (4, "Кто написал 'Реквием'?", "Моцарт", "Музыкальная история"),
            (4, "Когда был изобретён первый пианино?", "1709", "Музыкальная история"),
            (4, "Кто изобрёл первый пианино?", "Бартоломео Кристофори", "Музыкальная история"),
            (4, "Когда была основана первая опера?", "1637", "Музыкальная история"),
            (4, "Кто написал первую оперу?", "Клаудио Монтеверди", "Музыкальная история"),
            (4, "Когда был изобретён первый гитар?", "1500", "Музыкальная история"),
            (4, "Кто написал 'Симфонию №9'?", "Бетховен", "Музыкальная история"),
            (4, "Когда была написана 'Симфония №9'?", "1824", "Музыкальная история"),
            (4, "Кто изобрёл первый виолончель?", "Андреа Аматьи", "Музыкальная история"),
            (4, "Когда был изобретён первый виолончель?", "1600", "Музыкальная история"),
            
            # Round 5: Смешанные темы
            (5, "Какой музыкальный инструмент используется в 'Bohemian Rhapsody'?", "Фортепиано", "Смешанные темы"),
            (5, "Какой стиль музыки использовался в 'Thriller'?", "Поп", "Смешанные темы"),
            (5, "Какой инструмент использовался в 'Stairway to Heaven'?", "Гитара", "Смешанные темы"),
            (5, "Какой стиль музыки использовался в 'Imagine'?", "Поп", "Смешанные темы"),
            (5, "Какой инструмент использовался в 'Hotel California'?", "Гитара", "Смешанные темы"),
            (5, "Какой стиль музыки использовался в 'Like a Rolling Stone'?", "Фолк-рок", "Смешанные темы"),
            (5, "Какой инструмент использовался в 'Yesterday'?", "Струнные", "Смешанные темы"),
            (5, "Какой стиль музыки использовался в 'Hey Jude'?", "Поп", "Смешанные темы"),
            (5, "Какой инструмент использовался в 'Sweet Child O' Mine'?", "Гитара", "Смешанные темы"),
            (5, "Какой стиль музыки использовался в 'Billie Jean'?", "Поп", "Смешанные темы")
        ]

        cursor.executemany('INSERT OR IGNORE INTO questions (round_num, question_text, answer, theme) VALUES (?, ?, ?, ?)', questions)

        conn.commit()
        conn.close()

    def _setup_routes(self) -> None:
        """
        Настройка маршрутов Flask-приложения
        """
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/quiz')
        def quiz():
            return render_template('quiz_game.html')

        @self.app.route('/quiz-game')
        def quiz_game():
            return render_template('quiz-game.html')

        @self.app.route('/api/init_game', methods=['POST'])
        def init_game():
            session_id = request.json.get('session_id')
            conn = self.get_db_connection()
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

        @self.app.route('/api/get_question', methods=['POST'])
        def get_question():
            data = request.json
            session_id = data.get('session_id')
            round_num = data.get('round_num')

            conn = self.get_db_connection()
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            # Получаем случайный вопрос для текущего раунда
        #     cursor.execute('SELECT id, question_text FROM questions WHERE round_num = ? ORDER BY RANDOM() LIMIT 1',
        #                    (round_num,))
        #     question = cursor.fetchone()
        #
        #     conn.close()
        #
        #     if question:
        #         return jsonify({'question_id': question[0], 'question_text': question[1]})
        #     else:
        #         return jsonify({'error': 'No questions available for this round'}), 404
        #
        # @self.app.route('/api/check_answer', methods=['POST'])
        # def check_answer():
        #     data = request.json
        #     question_id = data.get('question_id')
        #     user_answer = data.get('answer').strip().lower()
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     # Получаем правильный ответ
        #     cursor.execute('SELECT answer FROM questions WHERE id = ?', (question_id,))
        #     correct_answer = cursor.fetchone()
        #
        #     conn.close()
        #
        #     if correct_answer:
        #         correct = correct_answer[0].strip().lower() == user_answer
        #         return jsonify({'correct': correct, 'correct_answer': correct_answer[0]})
        #     else:
        #         return jsonify({'error': 'Question not found'}), 404
        #
        # @self.app.route('/api/save_state', methods=['POST'])
        # def save_state():
        #     data = request.json
        #     session_id = data.get('session_id')
        #     current_round = data.get('current_round')
        #     current_cell = data.get('current_cell')
        #     score = data.get('score')
        #     revealed_cells = data.get('revealed_cells')  # JSON string of revealed cells
        #     board_state = data.get('board_state')  # JSON string of the entire board state
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     cursor.execute(
        #         'INSERT OR REPLACE INTO game_states (session_id, current_round, current_cell, score, revealed_cells, board_state) VALUES (?, ?, ?, ?, ?, ?)',
        #         (session_id, current_round, current_cell, score, revealed_cells, board_state))
        #
        #     conn.commit()
        #     conn.close()
        #
        #     return jsonify({'status': 'success'})
        #
        # @self.app.route('/api/load_state', methods=['GET'])
        # def load_state():
        #     session_id = request.args.get('session_id')
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     cursor.execute('SELECT current_round, current_cell, score, revealed_cells, board_state FROM game_states WHERE session_id = ?', (session_id,))
        #     game_state = cursor.fetchone()
        #
        #     conn.close()
        #
        #     if game_state:
        #         return jsonify({
        #             'current_round': game_state[0],
        #             'current_cell': game_state[1],
        #             'score': game_state[2],
        #             'revealed_cells': game_state[3],
        #             'board_state': game_state[4]
        #         })
        #     else:
        #         return jsonify({'error': 'No saved state found'}), 404
        #
        # @self.app.route('/api/get_players', methods=['GET'])
        # def get_players():
        #     session_id = request.args.get('session_id')
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     cursor.execute('SELECT player_name, score FROM scores WHERE session_id = ?', (session_id,))
        #     players = cursor.fetchall()
        #
        #     conn.close()
        #
        #     player_list = []
        #     for player in players:
        #         player_list.append({
        #             'player_name': player[0],
        #             'score': player[1]
        #         })
        #
        #     return jsonify({'players': player_list})
        #
        # @self.app.route('/api/add_player', methods=['POST'])
        # def add_player():
        #     data = request.json
        #     session_id = data.get('session_id')
        #     player_name = data.get('player_name', f'Игрок {int(data.get("score", 0)) + 1}')
        #     score = data.get('score', 0)
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     try:
        #         cursor.execute(
        #             'INSERT INTO scores (session_id, player_name, score) VALUES (?, ?, ?)',
        #             (session_id, player_name, score)
        #         )
        #         conn.commit()
        #         conn.close()
        #         return jsonify({'status': 'success'})
        #     except sqlite3.Error as e:
        #         conn.close()
        #         return jsonify({'error': str(e)}), 500
        #
        # @self.app.route('/api/remove_player', methods=['POST'])
        # def remove_player():
        #     data = request.json
        #     session_id = data.get('session_id')
        #     player_name = data.get('player_name')
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     try:
        #         cursor.execute(
        #             'DELETE FROM scores WHERE session_id = ? AND player_name = ?',
        #             (session_id, player_name)
        #         )
        #         conn.commit()
        #         conn.close()
        #         return jsonify({'status': 'success'})
        #     except sqlite3.Error as e:
        #         conn.close()
        #         return jsonify({'error': str(e)}), 500
        #
        # @self.app.route('/api/update_player', methods=['POST'])
        # def update_player():
        #     data = request.json
        #     session_id = data.get('session_id')
        #     player_name = data.get('player_name')
        #     new_player_name = data.get('new_player_name')
        #     score = data.get('score')
        #
        #     conn = self.get_db_connection()
        #     if conn is None:
        #         return jsonify({'error': 'Database connection failed'}), 500
        #     cursor = conn.cursor()
        #
        #     try:
        #         if new_player_name:
        #             # Update both name and score
        #             cursor.execute(
        #                 'UPDATE scores SET player_name = ?, score = ? WHERE session_id = ? AND player_name = ?',
        #                 (new_player_name, score, session_id, player_name)
        #             )
        #         else:
        #             # Update only score
        #             cursor.execute(
        #                 'UPDATE scores SET score = ? WHERE session_id = ? AND player_name = ?',
        #                 (score, session_id, player_name)
        #             )
        #         conn.commit()
        #         conn.close()
        #         return jsonify({'status': 'success'})
        #     except sqlite3.Error as e:
        #         conn.close()
        #         return jsonify({'error': str(e)}), 500

        @self.app.route('/api/config', methods=['GET'])
        def get_config():
            # Return the game configuration
            config = {
                'symbols': [
                    '🙂',  # смайлик
                    '👍',  # лайк
                    '👏',  # ладошки
                    '⭐',  # звезда
                    '❤️',  # сердце
                    '🎵',  # нота
                    '🎶',  # музыка (две ноты или музыкальный фрагмент)
                    '☀️',  # солнце
                    '☁️',  # облако
                    '☂️'   # зонт
                ]
                # 'settings': {
                #     'round_counters': [0, 20, 20, 20, 20, 10]  # Number of cells to open per round
                }
            return jsonify(config)

        @self.app.route('/api/get_opened_cells', methods=['GET'])
        def get_opened_cells():
            session_id = request.args.get('session_id')
            round_num = request.args.get('round_num', type=int)
            
            conn = self.get_db_connection()
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            try:
                # Get all opened cells for this session and round
                cursor.execute('''
                    SELECT row_num, col_num, cell_value 
                    FROM opened_cells 
                    WHERE session_id = ? AND round_num = ?
                ''', (session_id, round_num))
                
                opened_cells = []
                for row in cursor.fetchall():
                    opened_cells.append({
                        'position': f"{row[0]},{row[1]}",  # row,col format
                        'value': row[2]
                    })
                
                conn.close()
                return jsonify({'opened_cells': opened_cells})
            except sqlite3.Error as e:
                conn.close()
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/mark_cell_opened', methods=['POST'])
        def mark_cell_opened():
            data = request.json
            session_id = data.get('session_id')
            round_num = data.get('round_num')
            row = data.get('row')
            col = data.get('col')
            cell_value = data.get('cell_value')
            
            conn = self.get_db_connection()
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            try:
                # Check if cell is already opened
                cursor.execute('''
                    SELECT id FROM opened_cells 
                    WHERE session_id = ? AND round_num = ? AND row_num = ? AND col_num = ?
                ''', (session_id, round_num, row, col))
                
                existing = cursor.fetchone()
                if existing:
                    conn.close()
                    return jsonify({'error': 'Cell already opened'}), 400
                
                # Insert the opened cell
                cursor.execute('''
                    INSERT INTO opened_cells (session_id, round_num, row_num, col_num, cell_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, round_num, row, col, cell_value))
                
                conn.commit()
                conn.close()
                return jsonify({'status': 'success'})
            except sqlite3.Error as e:
                conn.close()
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/reset_players', methods=['POST'])
        def reset_players():
            data = request.json
            session_id = data.get('session_id')
            
            conn = self.get_db_connection()
            if conn is None:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            try:
                # Delete existing players for this session
                cursor.execute('DELETE FROM scores WHERE session_id = ?', (session_id,))
                
                # Add default players
                cursor.execute('INSERT INTO scores (session_id, player_name, score) VALUES (?, ?, ?)', (session_id, 'Игрок 1', 0))
                cursor.execute('INSERT INTO scores (session_id, player_name, score) VALUES (?, ?, ?)', (session_id, 'Игрок 2', 0))
                
                conn.commit()
                conn.close()
                return jsonify({'status': 'success'})
            except sqlite3.Error as e:
                conn.close()
                return jsonify({'error': str(e)}), 500

    def run(self, host: str = '0.0.0.0', port: int = 5555, debug: bool = False) -> None:
        """
        Запуск Flask-приложения
        """
        self.init_db()
        self.app.run(
            host=host,
            port=port,
            debug=debug  # В продакшене debug=False более безопасен
        )


def create_app() -> QuizGameApp:
    """
    Фабричная функция для создания экземпляра приложения
    """
    return QuizGameApp()


if __name__ == '__main__':
    app = create_app()
    app.run()