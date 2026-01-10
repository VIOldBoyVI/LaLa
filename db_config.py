"""
Database configuration module for secure MySQL connections with SSL/TLS support
and connection pooling for shared database access.
"""

import os
from dotenv import load_dotenv
from mysql.connector import pooling
from mysql.connector.constants import ClientFlag
import mysql.connector
from contextlib import contextmanager
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class with SSL and pooling support."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME', 'mydb')
        self.user = os.getenv('DB_USER', 'lalagame_user')
        self.password = os.getenv('DB_PASSWORD', '')
        self.pool_size = int(os.getenv('DB_POOL_SIZE', 10))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', 30))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))
        
        # SSL configuration
        self.ssl_ca = os.getenv('DB_SSL_CA')
        self.ssl_cert = os.getenv('DB_SSL_CERT')
        self.ssl_key = os.getenv('DB_SSL_KEY')
        self.ssl_mode = os.getenv('DB_SSL_MODE', 'REQUIRED')
    
    def get_ssl_config(self):
        """Get SSL configuration dictionary."""
        ssl_config = {}
        
        if self.ssl_ca:
            ssl_config['ca'] = self.ssl_ca
        if self.ssl_cert:
            ssl_config['cert'] = self.ssl_cert
        if self.ssl_key:
            ssl_config['key'] = self.ssl_key
            
        # Set SSL mode
        if self.ssl_mode.upper() == 'REQUIRED':
            ssl_config['ssl_disabled'] = False
            ssl_config['ssl_verify_cert'] = True
        elif self.ssl_mode.upper() == 'PREFERRED':
            ssl_config['ssl_disabled'] = False
        elif self.ssl_mode.upper() == 'DISABLED':
            ssl_config['ssl_disabled'] = True
        elif self.ssl_mode.upper() == 'VERIFY_CA':
            ssl_config['ssl_verify_cert'] = True
        elif self.ssl_mode.upper() == 'VERIFY_IDENTITY':
            ssl_config['ssl_verify_cert'] = True
            ssl_config['ssl_verify_identity'] = True
            
        return ssl_config
    
    def get_pool_config(self):
        """Get connection pool configuration."""
        config = {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'pool_size': self.pool_size,
            'pool_name': 'lalagame_pool',
            'pool_reset_session': True,
            'autocommit': False,  # We'll handle transactions manually
        }
        
        # Add SSL config if available (using individual parameters instead of 'ssl' dict)
        if self.ssl_ca:
            config['ssl_ca'] = self.ssl_ca
        if self.ssl_cert:
            config['ssl_cert'] = self.ssl_cert
        if self.ssl_key:
            config['ssl_key'] = self.ssl_key
        
        # Handle SSL mode settings
        if self.ssl_mode.upper() in ['REQUIRED', 'VERIFY_CA', 'VERIFY_IDENTITY']:
            config['use_unicode'] = True
        elif self.ssl_mode.upper() == 'DISABLED':
            config['ssl_disabled'] = True
                
        return config

# Global connection pool
connection_pool = None

def initialize_connection_pool():
    """Initialize the global connection pool."""
    global connection_pool
    try:
        db_config = DatabaseConfig()
        pool_config = db_config.get_pool_config()
        connection_pool = pooling.MySQLConnectionPool(**pool_config)
        logger.info(f"Connection pool initialized with size {db_config.pool_size}")
    except Exception as e:
        logger.error(f"Error initializing connection pool: {e}")
        raise

def get_connection():
    """Get a connection from the pool."""
    global connection_pool
    if connection_pool is None:
        initialize_connection_pool()
    
    try:
        conn = connection_pool.get_connection()
        # Set proper isolation level for consistency
        cursor = conn.cursor()
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        cursor.close()
        return conn
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}")
        raise

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db_transaction():
    """Context manager for database transactions with automatic rollback on error."""
    conn = None
    try:
        conn = get_connection()
        conn.start_transaction()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Transaction failed and rolled back: {e}")
        raise
    finally:
        if conn:
            conn.close()

def test_connection():
    """Test database connection."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            return result is not None
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

# Initialize the pool when module is imported
try:
    initialize_connection_pool()
except Exception as e:
    logger.warning(f"Could not initialize connection pool: {e}. Will initialize on first use.")