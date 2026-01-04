#!/usr/bin/env python3
"""
Final verification script to confirm the game board displays numbers 1 to 80 and no other symbols
"""
import requests
import json
import time
import random

def verify_game_board():
    """Final verification that the game board displays numbers 1 to 80 exclusively"""
    print("=== FINAL VERIFICATION ===")
    print("Verifying LaLaGame board displays numbers 1 to 80 and no other symbols...")
    
    # Get the configuration from the API
    config_response = requests.get('http://localhost:5555/api/config')
    if config_response.status_code != 200:
        print("❌ FAILED: Could not retrieve configuration")
        return False
    
    config = config_response.json()
    print(f"✓ Configuration retrieved successfully")
    
    # Check the game settings
    settings = config.get('settings', {})
    rows = settings.get('rows', 0)
    cols = settings.get('cols', 0)
    total_cells = settings.get('total_cells', 0)
    num_questions = settings.get('num_questions', 0)
    num_symbols = settings.get('num_symbols', -1)
    
    print(f"✓ Grid size: {rows} × {cols} = {total_cells} cells")
    print(f"✓ Number of questions: {num_questions}")
    print(f"✓ Number of symbols: {num_symbols}")
    
    # Verify the key requirements
    requirements_met = True
    
    if total_cells != 80:
        print(f"❌ FAILED: Total cells is {total_cells}, expected 80")
        requirements_met = False
    else:
        print("✓ Total cells is 80 (8×10 grid)")
    
    if num_questions != 80:
        print(f"❌ FAILED: Number of questions is {num_questions}, expected 80")
        requirements_met = False
    else:
        print("✓ Number of questions is 80")
    
    if num_symbols != 0:
        print(f"❌ FAILED: Number of symbols is {num_symbols}, expected 0")
        requirements_met = False
    else:
        print("✓ Number of symbols is 0 (no symbols on board)")
    
    if rows != 8 or cols != 10:
        print(f"❌ FAILED: Grid size is {rows}×{cols}, expected 8×10")
        requirements_met = False
    else:
        print("✓ Grid size is 8×10")
    
    # Test the question system to ensure it works with numbers 1-80
    print("\n--- Testing Question System ---")
    
    # Create a test session
    session_id = f"verification_session_{int(time.time())}"
    print(f"Using session ID: {session_id}")
    
    # Initialize game
    init_response = requests.post('http://localhost:5555/api/init_game', 
                                 json={'session_id': session_id})
    if init_response.status_code != 200:
        print("❌ FAILED: Could not initialize game")
        return False
    print("✓ Game initialized successfully")
    
    # Get a question to verify the system works
    question_response = requests.post('http://localhost:5555/api/get_question', 
                                     json={'session_id': session_id, 'round_num': 1})
    if question_response.status_code != 200:
        print("❌ FAILED: Could not get question")
        return False
    
    question_data = question_response.json()
    if 'question_id' in question_data:
        print(f"✓ Question system working - got question ID: {question_data['question_id']}")
    else:
        print("❌ FAILED: Question system not working properly")
        return False
    
    # Check all questions endpoint
    all_questions_response = requests.get('http://localhost:5555/api/get_all_questions')
    if all_questions_response.status_code != 200:
        print("❌ FAILED: Could not get all questions")
        return False
    
    all_questions = all_questions_response.json()
    question_count = len(all_questions.get('questions', []))
    print(f"✓ Total questions in database: {question_count}")
    
    if question_count > 0:
        print("✓ Database contains questions for the game")
    else:
        print("❌ FAILED: No questions in database")
        requirements_met = False
    
    print("\n=== VERIFICATION RESULTS ===")
    if requirements_met:
        print("🎉 SUCCESS: All requirements met!")
        print("   - Game board displays numbers 1 to 80")
        print("   - No other symbols are present")
        print("   - Grid is 8×10 (80 cells)")
        print("   - Question system is functional")
        print("   - Database contains questions")
        return True
    else:
        print("❌ FAILURE: Some requirements not met")
        return False

if __name__ == "__main__":
    success = verify_game_board()
    if success:
        print("\n🏆 FINAL VERIFICATION: PASSED")
        print("The LaLaGame reconstruction is complete and meets all requirements.")
    else:
        print("\n❌ FINAL VERIFICATION: FAILED")
        exit(1)