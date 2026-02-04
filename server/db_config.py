"""
Database Configuration for CloudBrain
Supports both SQLite and PostgreSQL
"""

import os
from typing import Optional, List, Any, Tuple
import sqlite3

# Database type: 'sqlite' or 'postgres'
DB_TYPE = os.getenv('DB_TYPE', 'postgres')

# SQLite Configuration
SQLITE_DB_PATH = os.getenv('SQLITE_DB_PATH', 'ai_db/cloudbrain.db')

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'cloudbrain')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'jk')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

def get_db_connection():
    """
    Get database connection based on DB_TYPE
    
    Returns:
        Connection object (sqlite3.Connection or psycopg2.extensions.connection)
    """
    if DB_TYPE == 'postgres':
        import psycopg2
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        conn.autocommit = False
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def get_db_path() -> str:
    """
    Get database path or connection string
    
    Returns:
        str: Database file path for SQLite or connection info for PostgreSQL
    """
    if DB_TYPE == 'postgres':
        return f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        return SQLITE_DB_PATH

def is_postgres() -> bool:
    """Check if using PostgreSQL"""
    return DB_TYPE == 'postgres'

def is_sqlite() -> bool:
    """Check if using SQLite"""
    return DB_TYPE == 'sqlite'

class CursorWrapper:
    """Wrapper for database cursor to handle both SQLite and PostgreSQL"""
    
    def __init__(self, cursor, columns: List[str] = None):
        self.cursor = cursor
        self.columns = columns
        self.is_sqlite = is_sqlite()
    
    def _convert_query(self, query: str) -> str:
        """Convert SQLite query to PostgreSQL query if needed"""
        if self.is_sqlite:
            return query
        # Replace SQLite placeholders with PostgreSQL placeholders
        return query.replace('?', '%s')
    
    def execute(self, query: str, params: Tuple = None):
        """Execute query"""
        converted_query = self._convert_query(query)
        if params is None:
            return self.cursor.execute(converted_query)
        return self.cursor.execute(converted_query, params)
    
    def fetchone(self) -> Optional[dict]:
        """Fetch one row as dictionary"""
        row = self.cursor.fetchone()
        if row is None:
            return None
        if self.is_sqlite:
            return dict(row)
        else:
            # Use cursor.description to get actual column names from query result
            if self.cursor.description:
                column_names = [desc[0] for desc in self.cursor.description]
                return dict(zip(column_names, row))
            elif self.columns:
                return dict(zip(self.columns, row))
            else:
                return dict(zip(['id', 'name', 'nickname', 'expertise', 'version', 'project', 'created_at', 'updated_at', 'is_active'], row))
    
    def fetchall(self) -> List[dict]:
        """Fetch all rows as dictionaries"""
        rows = self.cursor.fetchall()
        if self.is_sqlite:
            return [dict(row) for row in rows]
        else:
            # Use cursor.description to get actual column names from query result
            if self.cursor.description:
                column_names = [desc[0] for desc in self.cursor.description]
                return [dict(zip(column_names, row)) for row in rows]
            elif self.columns:
                return [dict(zip(self.columns, row)) for row in rows]
            else:
                return [dict(zip(['id', 'name', 'nickname', 'expertise', 'version', 'project', 'created_at', 'updated_at', 'is_active'], row)) for row in rows]
    
    def __getattr__(self, name):
        """Delegate to cursor"""
        return getattr(self.cursor, name)
