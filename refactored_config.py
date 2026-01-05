# Configuration file for the game
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
ROWS = 8
COLS = 10
TOTAL_CELLS = ROWS * COLS  # 80 cells
NUM_QUESTIONS = 80  # Numbers representing questions
NUM_SYMBOLS = 0  # No symbols, only numbers

# Style settings
BODY_STYLE = {
    'background': 'linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d)',
    'texture': 'url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPgogIDxmaWx0ZXIgaWQ9Im5vaXNlIj4KICAgIDxmZVR1cmJ1bGVuY2UgdHlwZT0iZnJhY3RhbE5vaXNlIiBiYXNlRnJlcXVlbmN5PSIwLjIiIG51bU9jdGF2ZXM9IjMiIHN0aXRjaFRpbGVzPSJzdGl0Y2giLz4KICA8L2ZpbHRlcj4KICA8cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ0cmFuc3BhcmVudCIgZmlsdGVyPSJ1cmwoI25vaXNlKSIvPgogIDxjaXJjbGUgY3g9IjEwJSIgY3k9IjEwJSIgcj0iMS41JSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPgogIDxjaXJjbGUgY3g9IjMwJSIgY3k9IjIwJSIgcj0iMi4wJSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wNCIvPgogIDxjaXJjbGUgY3g9IjUwJSIgY3k9IjMwJSIgcj0iMS44JSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wMyIvPgogIDxjaXJjbGUgY3g9IjcwJSIgY3k9IjE1JSIgcj0iMS4zJSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPgogIDxjaXJjbGUgY3g9IjkwJSIgY3k9IjQwJSIgcj0iMi4yJSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wMyIvPgogIDxjaXJjbGUgY3g9IjIwJSIgY3k9IjYwJSIgcj0iMS43JSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wNCIvPgogIDxjaXJjbGUgY3g9IjQwJSIgY3k9Ijc1JSIgcj0iMS41JSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wMyIvPgogIDxjaXJjbGUgY3g9IjYwJSIgY3k9IjU1JSIgcj0iMi4wJSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPgogIDxjaXJjbGUgY3g9IjgwJSIgY3k9Ijg1JSIgcj0iMS44JSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wNCIvPgogIDxjaXJjbGUgY3g9IjEwJSIgY3k9Ijk1JSIgcj0iMS40JSIgZmlsbD0id2hpdGUiIGZpbGwtb3BhY2l0eT0iMC4wMyIvPgogIDxwYXRoIGQ9Ik0gMjAlIDMwJSBMIDIxJSAzMCUgTSA0MCUgNTAlIE0gNDAwJSA1MCUgTCA0MSUgNTAlIE0gNjAlIDQwJSBMIDYxJSBANDAlIE0gODAlIDYwJSBMIDgxJSBANDAlIE0gMzAlIDcwJSBMIDMxJSBANzAlIE0gNTAlIDgwJSBMIDUxJSBANDAlIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjAuNSIgc3Ryb2tlLW9wYWNpdHk9IjAuMDMiLz4KPC9zdmc+)'
}

CELL_STYLE = {
    'width': '70px',
    'height': '70px',
    'background': 'linear-gradient(145deg, #ff8c00, #ff6600)',
    'border_radius': '8px',
    'font_size': '2rem',
    'font_weight': 'bold',
    'color': '#000080',
    'box_shadow': '0 4px 8px rgba(0, 0, 0, 0.3)',
    'transition': 'all 0.3s ease'
}

HOVER_CELL_STYLE = {
    'transform': 'scale(1.05)',
    'box_shadow': '0 6px 12px rgba(0, 0, 0, 0.4)',
    'background': 'linear-gradient(145deg, #ff9c20, #ff7620)'
}

REVEALED_CELL_STYLE = {
    'background': 'linear-gradient(145deg, #11cb6a, #25fcd5)',
    'cursor': 'default'
}

NUMBER_CELL_STYLE = {
    'color': '#000080'
}

SYMBOL_CELL_STYLE = {
    'color': 'initial'
}

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
        "num_symbols": NUM_SYMBOLS
    }

def get_body_style():
    """Return body style settings"""
    return BODY_STYLE

def get_cell_style():
    """Return cell style settings"""
    return CELL_STYLE

def get_hover_cell_style():
    """Return hover cell style settings"""
    return HOVER_CELL_STYLE

def get_revealed_cell_style():
    """Return revealed cell style settings"""
    return REVEALED_CELL_STYLE

def get_number_cell_style():
    """Return number cell style settings"""
    return NUMBER_CELL_STYLE

def get_symbol_cell_style():
    """Return symbol cell style settings"""
    return SYMBOL_CELL_STYLE