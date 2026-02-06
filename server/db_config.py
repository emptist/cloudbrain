"""
Database Configuration for CloudBrain
PostgreSQL-only configuration
"""

import os
from typing import Optional, List, Any, Tuple

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'cloudbrain')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'jk')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

def get_db_connection():
    """
    Get PostgreSQL database connection
    
    Returns:
        Connection object (psycopg2.extensions.connection)
    """
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

def get_cursor():
    """
    Get a PostgreSQL cursor with automatic placeholder conversion
    
    Returns:
        CursorWrapper object that converts SQLite (?) to PostgreSQL (%s) placeholders
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    return CursorWrapper(cursor)

def get_db_path() -> str:
    """
    Get database connection string
    
    Returns:
        str: PostgreSQL connection string
    """
    return f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def is_postgres() -> bool:
    """Check if using PostgreSQL (always True)"""
    return True

class CursorWrapper:
    """Wrapper for database cursor to handle PostgreSQL queries"""
    
    def __init__(self, cursor, columns: List[str] = None):
        self.cursor = cursor
        self.columns = columns
    
    def execute(self, query: str, params: Tuple = None):
        """Execute query with PostgreSQL placeholders"""
        if params is None:
            return self.cursor.execute(query)
        
        # Convert SQLite placeholders (?) to PostgreSQL placeholders (%s)
        postgres_query = query.replace('?', '%s')
        return self.cursor.execute(postgres_query, params)
    
    def fetchone(self) -> Optional[dict]:
        """Fetch one row as dictionary"""
        row = self.cursor.fetchone()
        if row is None:
            return None
        
        # Check if row is already a dictionary (e.g., from RealDictCursor)
        if isinstance(row, dict):
            return row
        
        # Otherwise, convert tuple to dictionary
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
        
        # Check if rows are already dictionaries (e.g., from RealDictCursor)
        if rows and isinstance(rows[0], dict):
            return rows
        
        # Otherwise, convert tuples to dictionaries
        if self.columns:
            return [dict(zip(self.columns, row)) for row in rows]
        elif self.cursor.description:
            column_names = [desc[0] for desc in self.cursor.description]
            return [dict(zip(column_names, row)) for row in rows]
        else:
            return [dict(zip(['id', 'name', 'nickname', 'expertise', 'version', 'project', 'created_at', 'updated_at', 'is_active'], row)) for row in rows]
    
    def __getattr__(self, name):
        """Delegate to cursor"""
        return getattr(self.cursor, name)
