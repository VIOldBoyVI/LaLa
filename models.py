"""
SQLAlchemy ORM models for the LaLaGame application.
These models can be shared across multiple applications accessing the same database.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()

class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    round_num = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    theme = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<Question(id={self.id}, round_num={self.round_num}, theme='{self.theme}')>"

class GameState(Base):
    __tablename__ = 'game_states'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False)
    current_round = Column(Integer, default=1)
    current_cell = Column(String(50))
    score = Column(Integer, default=0)
    revealed_cells = Column(Text)  # JSON string of revealed cells
    board_state = Column(Text)     # JSON string of the entire board state
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<GameState(session_id='{self.session_id}', round={self.current_round})>"

class OpenedCell(Base):
    __tablename__ = 'opened_cells'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)
    round_num = Column(Integer, nullable=False)
    row_num = Column(Integer, nullable=False)
    col_num = Column(Integer, nullable=False)
    cell_value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<OpenedCell(session_id='{self.session_id}', round={self.round_num}, pos=({self.row_num},{self.col_num}))>"

class Score(Base):
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255))
    round_num = Column(Integer)
    player_name = Column(String(255))
    score = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Score(player_name='{self.player_name}', score={self.score})>"

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255))
    player_name = Column(String(255))
    score = Column(Integer, default=0)
    position = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Player(name='{self.player_name}', score={self.score})>"

def get_database_url():
    """
    Generate database URL from environment variables.
    This allows multiple applications to share the same database configuration.
    """
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', 3306)
    database = os.getenv('DB_NAME', 'mydb')
    user = os.getenv('DB_USER', 'lalagame_user')
    password = os.getenv('DB_PASSWORD', '')
    
    # Basic URL without SSL params
    base_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    
    # Build SSL parameters if available
    ssl_params = []
    ssl_ca = os.getenv('DB_SSL_CA')
    ssl_cert = os.getenv('DB_SSL_CERT')
    ssl_key = os.getenv('DB_SSL_KEY')
    
    # Only add SSL params if at least one is defined
    if ssl_ca or ssl_cert or ssl_key:
        # For SQLAlchemy with PyMySQL, SSL params go in query string
        ssl_dict = {}
        if ssl_ca:
            ssl_dict['ssl_ca'] = ssl_ca
        if ssl_cert:
            ssl_dict['ssl_cert'] = ssl_cert
        if ssl_key:
            ssl_dict['ssl_key'] = ssl_key
        
        # Convert to URL parameters
        import urllib.parse
        query_string = urllib.parse.urlencode(ssl_dict, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"
    
    return base_url

def get_engine():
    """
    Create SQLAlchemy engine with connection pooling and other optimizations.
    """
    database_url = get_database_url()
    
    # Engine configuration with pooling and other optimizations
    engine = create_engine(
        database_url,
        pool_size=int(os.getenv('DB_POOL_SIZE', 10)),
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=int(os.getenv('DB_POOL_RECYCLE', 3600)),  # Recycle connections after 1 hour
        echo=False  # Set to True for SQL debugging
    )
    
    return engine

def get_session():
    """
    Get a new database session.
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_database():
    """
    Initialize the database tables.
    This should be called once during application startup.
    """
    engine = get_engine()
    Base.metadata.create_all(engine)