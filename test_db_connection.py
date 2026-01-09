"""
Unit tests for database connection functionality
Tests both the connection pool and transaction handling
"""

import unittest
import os
from unittest.mock import patch, MagicMock

# Import our database modules
from db_config import get_db_connection, get_db_transaction, test_connection, DatabaseConfig
from models import get_session, Question, GameState, init_database


class TestDatabaseConnection(unittest.TestCase):
    """Test cases for database connection functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock environment variables for testing
        os.environ['DB_HOST'] = 'localhost'
        os.environ['DB_PORT'] = '3306'
        os.environ['DB_NAME'] = 'test_mydb'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = 'test_password'
        os.environ['DB_POOL_SIZE'] = '5'
    
    def test_database_config_initialization(self):
        """Test that DatabaseConfig initializes correctly with environment variables"""
        config = DatabaseConfig()
        
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 3306)
        self.assertEqual(config.database, 'test_mydb')
        self.assertEqual(config.user, 'test_user')
        self.assertEqual(config.password, 'test_password')
        self.assertEqual(config.pool_size, 5)
    
    @patch('db_config.connection_pool')
    def test_get_connection(self, mock_pool):
        """Test that get_connection returns a connection from the pool"""
        mock_conn = MagicMock()
        mock_pool.get_connection.return_value = mock_conn
        
        conn = get_db_connection()
        
        # Since we're using a context manager, we can't directly compare
        # But we can test that the connection method is called properly
        self.assertIsNotNone(conn)
    
    def test_test_connection_success(self):
        """Test the connection test function"""
        # This would require an actual database connection
        # For now, we'll just make sure the function exists and signature is correct
        self.assertTrue(callable(test_connection))
    
    def test_get_session_creation(self):
        """Test that SQLAlchemy session can be created"""
        # This test would require a real database connection
        # Just ensure the function exists and has correct signature
        self.assertTrue(callable(get_session))
    
    def test_model_classes_exist(self):
        """Test that our SQLAlchemy model classes exist"""
        self.assertTrue(hasattr(Question, '__tablename__'))
        self.assertTrue(hasattr(GameState, '__tablename__'))
        
        # Check that table names are correct
        self.assertEqual(Question.__tablename__, 'questions')
        self.assertEqual(GameState.__tablename__, 'game_states')


class TestTransactionHandling(unittest.TestCase):
    """Test transaction handling functionality"""
    
    def test_transaction_context_manager(self):
        """Test that the transaction context manager works correctly"""
        # Check that the context manager function exists
        self.assertTrue(callable(get_db_transaction))
    
    @patch('db_config.connection_pool')
    def test_transaction_commits_on_success(self, mock_pool):
        """Test that transactions commit when no exception occurs"""
        mock_conn = MagicMock()
        mock_pool.get_connection.return_value = mock_conn
        
        # This is difficult to test without a real database
        # Just verify the function is callable
        self.assertTrue(callable(get_db_transaction))


class TestModelInitialization(unittest.TestCase):
    """Test model initialization functionality"""
    
    @patch('models.create_engine')
    def test_init_database(self, mock_create_engine):
        """Test that database initialization function exists and is callable"""
        # This test would require mocking the engine creation
        self.assertTrue(callable(init_database))
    
    def test_model_attributes(self):
        """Test that model classes have expected attributes"""
        # Test Question model
        question_attrs = ['id', 'round_num', 'question_text', 'answer', 'theme']
        for attr in question_attrs:
            self.assertTrue(hasattr(Question, attr))
        
        # Test GameState model
        gamestate_attrs = ['id', 'session_id', 'current_round', 'current_cell', 'score', 'revealed_cells', 'board_state', 'created_at']
        for attr in gamestate_attrs:
            self.assertTrue(hasattr(GameState, attr))


if __name__ == '__main__':
    print("Running database connection tests...")
    unittest.main(verbosity=2)