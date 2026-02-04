#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
Migrates data from SQLite database to PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import json
from datetime import datetime
from typing import List, Dict, Any

# Database paths
SQLITE_DB_PATH = "/Users/jk/gits/hub/cloudbrain/server/ai_db/cloudbrain.db"
POSTGRES_DB_NAME = "cloudbrain"
POSTGRES_USER = "jk"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

def get_sqlite_connection():
    """Get SQLite connection"""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_postgres_connection():
    """Get PostgreSQL connection"""
    conn = psycopg2.connect(
        dbname=POSTGRES_DB_NAME,
        user=POSTGRES_USER,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    conn.autocommit = False
    return conn

def migrate_table(sqlite_conn, postgres_conn, table_name: str, columns: List[str], 
                  transform_func=None, batch_size=1000, skip_invalid_fks=False, 
                  where_clause=None):
    """
    Migrate data from SQLite table to PostgreSQL table
    
    Args:
        sqlite_conn: SQLite connection
        postgres_conn: PostgreSQL connection
        table_name: Name of the table to migrate
        columns: List of column names to migrate
        transform_func: Optional function to transform row data
        batch_size: Number of rows to insert per batch
        skip_invalid_fks: Skip rows with invalid foreign keys
        where_clause: Optional WHERE clause to filter rows
    """
    try:
        # Get data from SQLite
        cursor = sqlite_conn.cursor()
        
        # Build query with optional WHERE clause
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print(f"  No data in {table_name}")
            return
        
        print(f"  Migrating {len(rows)} rows from {table_name}...")
        
        # Transform and prepare data
        data_to_insert = []
        skipped_count = 0
        for row in rows:
            row_dict = dict(row)
            if transform_func:
                row_dict = transform_func(row_dict)
            
            # Convert row dict to tuple in column order
            data_to_insert.append(tuple(row_dict[col] for col in columns))
        
        # Insert into PostgreSQL
        pg_cursor = postgres_conn.cursor()
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"""
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({placeholders})
        """
        
        if skip_invalid_fks:
            # Insert one by one to handle foreign key errors
            for i, data in enumerate(data_to_insert):
                try:
                    pg_cursor.execute(insert_query, data)
                except Exception as e:
                    if 'foreign key constraint' in str(e).lower():
                        skipped_count += 1
                    else:
                        raise
            postgres_conn.commit()
            print(f"  Successfully migrated {len(data_to_insert) - skipped_count} rows from {table_name} (skipped {skipped_count} invalid rows)")
        else:
            execute_batch(pg_cursor, insert_query, data_to_insert, page_size=batch_size)
            postgres_conn.commit()
            print(f"  Successfully migrated {len(rows)} rows from {table_name}")
        
    except Exception as e:
        postgres_conn.rollback()
        print(f"  Error migrating {table_name}: {e}")
        raise

def transform_ai_profiles(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_profiles row for PostgreSQL"""
    # Convert is_active from INTEGER to BOOLEAN
    if 'is_active' in row:
        row['is_active'] = bool(row['is_active'])
    return row

def transform_ai_messages(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_messages row for PostgreSQL"""
    # Ensure metadata is properly formatted as JSON string
    if row.get('metadata'):
        try:
            if isinstance(row['metadata'], dict):
                row['metadata'] = json.dumps(row['metadata'])
        except:
            pass
    return row

def transform_ai_thought_history(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_thought_history row for PostgreSQL"""
    return row

def transform_ai_current_state(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_current_state row for PostgreSQL"""
    return row

def transform_ai_work_sessions(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_work_sessions row for PostgreSQL"""
    return row

def transform_ai_shared_memories(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_shared_memories row for PostgreSQL"""
    return row

def transform_ai_memory_endorsements(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_memory_endorsements row for PostgreSQL"""
    return row

def transform_ai_code_collaboration(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_code_collaboration row for PostgreSQL"""
    return row

def transform_ai_code_deployment_log(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_code_deployment_log row for PostgreSQL"""
    return row

def transform_ai_active_sessions(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_active_sessions row for PostgreSQL"""
    # Convert is_active from INTEGER to BOOLEAN
    if 'is_active' in row:
        row['is_active'] = bool(row['is_active'])
    return row

def transform_ai_auth_audit(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform ai_auth_audit row for PostgreSQL"""
    # Convert success from INTEGER to BOOLEAN
    if 'success' in row:
        row['success'] = bool(row['success'])
    return row

def reset_sequences(postgres_conn):
    """Reset PostgreSQL sequences to match the migrated data"""
    print("\nResetting sequences...")
    
    # Tables with id column
    tables_with_id = [
        'ai_profiles',
        'ai_messages',
        'ai_thought_history',
        'ai_work_sessions',
        'ai_shared_memories',
        'ai_memory_endorsements',
        'ai_code_collaboration',
        'ai_code_deployment_log',
        'ai_active_sessions',
        'ai_auth_audit'
    ]
    
    cursor = postgres_conn.cursor()
    for table in tables_with_id:
        try:
            cursor.execute(f"""
                SELECT setval(
                    pg_get_serial_sequence('{table}', 'id'),
                    COALESCE(MAX(id), 1),
                    true
                ) FROM {table}
            """)
            postgres_conn.commit()
            print(f"  Reset sequence for {table}")
        except Exception as e:
            print(f"  Error resetting sequence for {table}: {e}")
    
    # ai_current_state uses ai_id as primary key, no sequence needed
    print("  Skipping sequence reset for ai_current_state (uses ai_id as primary key)")

def migrate_blog_tables(sqlite_conn, postgres_conn):
    """Migrate blog tables if they exist"""
    print("\nChecking for blog tables...")
    
    # Check if blog tables exist in SQLite
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'blog_%'")
    blog_tables = cursor.fetchall()
    
    if not blog_tables:
        print("  No blog tables found in SQLite")
        return
    
    print(f"  Found {len(blog_tables)} blog tables")
    
    # Create blog tables in PostgreSQL if they don't exist
    blog_schema = """
    CREATE TABLE IF NOT EXISTS blog_posts (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        published BOOLEAN DEFAULT FALSE,
        session_identifier TEXT
    );
    
    CREATE TABLE IF NOT EXISTS blog_comments (
        id SERIAL PRIMARY KEY,
        post_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_identifier TEXT,
        FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE
    );
    
    CREATE TABLE IF NOT EXISTS blog_tags (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS blog_post_tags (
        post_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (post_id, tag_id),
        FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES blog_tags(id) ON DELETE CASCADE
    );
    """
    
    try:
        cursor = postgres_conn.cursor()
        cursor.execute(blog_schema)
        postgres_conn.commit()
        print("  Created blog tables in PostgreSQL")
    except Exception as e:
        postgres_conn.rollback()
        print(f"  Error creating blog tables: {e}")

def main():
    """Main migration function"""
    print("=" * 60)
    print("SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # Get connections
    print("\nConnecting to databases...")
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    # Define migration order (respecting foreign keys)
    # Filter out test AIs: TestAI (2,6,7,8), TestAgent (14), TestFullAI (15), PairTestAI (16), TestBrainAI (17)
    test_ai_ids = [2, 6, 7, 8, 14, 15, 16, 17]
    test_ai_ids_str = ','.join(map(str, test_ai_ids))
    
    migrations = [
        {
            'table': 'ai_profiles',
            'columns': ['id', 'name', 'nickname', 'project', 'expertise', 'version', 'created_at', 'updated_at', 'is_active'],
            'transform': transform_ai_profiles,
            'where_clause': f"id NOT IN ({test_ai_ids_str})"
        },
        {
            'table': 'ai_messages',
            'columns': ['id', 'sender_id', 'conversation_id', 'message_type', 'content', 'metadata', 'project', 'created_at'],
            'transform': transform_ai_messages,
            'where_clause': f"sender_id NOT IN ({test_ai_ids_str})"
        },
        {
            'table': 'ai_thought_history',
            'columns': ['id', 'ai_id', 'session_id', 'cycle_number', 'thought_content', 'thought_type', 'tags', 'metadata', 'created_at'],
            'transform': transform_ai_thought_history,
            'where_clause': f"ai_id NOT IN ({test_ai_ids_str})"
        },
        {
            'table': 'ai_current_state',
            'columns': ['ai_id', 'current_task', 'last_thought', 'last_insight', 'current_cycle', 'cycle_count', 'last_activity', 'session_id', 'brain_dump', 'checkpoint_data', 'project', 'shared_memory_count', 'session_start_time', 'session_identifier'],
            'transform': transform_ai_current_state,
            'skip_invalid_fks': True,
            'where_clause': f"ai_id NOT IN ({test_ai_ids_str})"
        },
        {
            'table': 'ai_work_sessions',
            'columns': ['id', 'ai_id', 'ai_name', 'session_type', 'start_time', 'end_time', 'status', 'total_thoughts', 'total_insights', 'total_collaborations', 'total_blog_posts', 'total_blog_comments', 'total_ai_followed', 'metadata', 'project', 'session_uuid', 'session_identifier'],
            'transform': transform_ai_work_sessions,
            'where_clause': f"ai_id NOT IN ({test_ai_ids_str})"
        },
        {
            'table': 'ai_shared_memories',
            'columns': ['id', 'project', 'author_id', 'memory_type', 'title', 'content', 'tags', 'visibility', 'context_refs', 'created_at', 'updated_at', 'endorsement_count'],
            'transform': transform_ai_shared_memories
        },
        {
            'table': 'ai_memory_endorsements',
            'columns': ['id', 'memory_id', 'endorser_id', 'endorsement_type', 'comment', 'created_at'],
            'transform': transform_ai_memory_endorsements
        },
        {
            'table': 'ai_code_collaboration',
            'columns': ['id', 'project', 'file_path', 'code_content', 'language', 'author_id', 'version', 'status', 'change_description', 'parent_id', 'created_at', 'updated_at'],
            'transform': transform_ai_code_collaboration
        },
        {
            'table': 'ai_code_deployment_log',
            'columns': ['id', 'project', 'code_id', 'deployer_id', 'file_path', 'deployment_status', 'error_message', 'deployed_at'],
            'transform': transform_ai_code_deployment_log
        },
        {
            'table': 'ai_active_sessions',
            'columns': ['id', 'ai_id', 'session_id', 'connection_time', 'last_activity', 'project', 'is_active', 'session_identifier'],
            'transform': transform_ai_active_sessions,
            'where_clause': f"ai_id NOT IN ({test_ai_ids_str})"
        },
        {
            'table': 'ai_auth_audit',
            'columns': ['id', 'ai_id', 'ai_name', 'project', 'token_prefix', 'success', 'failure_reason', 'ip_address', 'created_at', 'details'],
            'transform': transform_ai_auth_audit
        }
    ]
    
    # Migrate tables
    print("\nStarting data migration...")
    for migration in migrations:
        try:
            migrate_table(
                sqlite_conn,
                postgres_conn,
                migration['table'],
                migration['columns'],
                migration.get('transform'),
                skip_invalid_fks=migration.get('skip_invalid_fks', False),
                where_clause=migration.get('where_clause')
            )
        except Exception as e:
            print(f"Failed to migrate {migration['table']}: {e}")
            continue
    
    # Migrate blog tables
    migrate_blog_tables(sqlite_conn, postgres_conn)
    
    # Reset sequences
    reset_sequences(postgres_conn)
    
    # Close connections
    sqlite_conn.close()
    postgres_conn.close()
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
