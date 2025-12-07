# Configuration file for symbols
SYMBOLS = [
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

# Game settings
ROWS = 10
COLS = 10
TOTAL_CELLS = ROWS * COLS  # 100 cells
NUM_QUESTIONS = 90  # Numbers representing questions
NUM_SYMBOLS = len(SYMBOLS)  # Special symbols
ROUND_COUNTERS = [0, 20, 20, 20, 20, 10]  # Number of questions in each round

def get_symbols():
    """Return the list of symbols for the game"""
    return SYMBOLS

def get_game_settings():
    """Return game settings"""
    return {
        "rows": ROWS,
        "cols": COLS,
        "total_cells": TOTAL_CELLS,
        "num_questions": NUM_QUESTIONS,
        "num_symbols": NUM_SYMBOLS,
        "round_counters": ROUND_COUNTERS
    }
