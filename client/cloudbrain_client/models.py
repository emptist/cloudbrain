"""
SQLAlchemy ORM models for CloudBrain AI System
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY
import os

Base = declarative_base()

class AICurrentState(Base):
    """Model for ai_current_state table"""
    __tablename__ = 'ai_current_state'

    ai_id = Column(Integer, nullable=False)
    session_identifier = Column(Text, primary_key=True, nullable=True)
    current_task = Column(Text, nullable=True)
    last_thought = Column(Text, nullable=True)
    last_insight = Column(Text, nullable=True)
    current_cycle = Column(Integer, nullable=True)
    cycle_count = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    session_id = Column(Integer, nullable=True)
    brain_dump = Column(Text, nullable=True)
    checkpoint_data = Column(Text, nullable=True)
    project = Column(Text, nullable=True)
    shared_memory_count = Column(Integer, default=0)
    session_start_time = Column(DateTime, nullable=True)
    git_hash = Column(Text, nullable=True)
    modified_files = Column(ARRAY(Text), nullable=True)
    added_files = Column(ARRAY(Text), nullable=True)
    deleted_files = Column(ARRAY(Text), nullable=True)

    def __repr__(self):
        return f"<AICurrentState(ai_id={self.ai_id}, session_identifier={self.session_identifier}, current_task={self.current_task})>"


def get_engine():
    """Get SQLAlchemy engine for PostgreSQL"""
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'cloudbrain')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'jk')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

    database_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    return create_engine(database_url)


def get_session():
    """Get SQLAlchemy session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initialize database (create tables if they don't exist)"""
    engine = get_engine()
    Base.metadata.create_all(engine)
