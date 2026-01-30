#!/usr/bin/env python3
"""
Database Migration Script - SQLite to PostgreSQL

Migrates Cloud Brain database from SQLite to PostgreSQL for GCP deployment.
Handles schema conversion, data migration, and data type mapping.
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import argparse
from datetime import datetime
import json


class DatabaseMigrator:
    """Migrates SQLite database to PostgreSQL"""
    
    def __init__(self, sqlite_path: str, postgres_connection: str):
        """
        Initialize migrator
        
        Args:
            sqlite_path: Path to SQLite database
            postgres_connection: PostgreSQL connection string
        """
        self.sqlite_path = sqlite_path
        self.postgres_connection = postgres_connection
        self.sqlite_conn = None
        self.pg_conn = None
        
        # Statistics
        self.tables_migrated = 0
        self.rows_migrated = 0
        self.errors = []
    
    def connect(self):
        """Connect to both databases"""
        try:
            # Connect to SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            
            # Connect to PostgreSQL
            self.pg_conn = psycopg2.connect(self.postgres_connection, cursor_factory=RealDictCursor)
            
            print("✅ Connected to both databases")
            return True
        except Exception as e:
            print(f"❌ Error connecting to databases: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from both databases"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.pg_conn:
            self.pg_conn.close()
        print("✅ Disconnected from databases")
    
    def get_sqlite_tables(self):
        """Get all tables from SQLite database"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    
    def get_table_schema(self, table_name: str):
        """Get schema for a table"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        return columns
    
    def create_postgres_table(self, table_name: str, columns: list):
        """Create table in PostgreSQL with appropriate data types"""
        pg_cursor = self.pg_conn.cursor()
        
        # Map SQLite types to PostgreSQL types
        type_mapping = {
            'INTEGER': 'INTEGER',
            'TEXT': 'TEXT',
            'REAL': 'REAL',
            'BLOB': 'BYTEA',
            'NUMERIC': 'NUMERIC',
            'BOOLEAN': 'BOOLEAN',
            'TIMESTAMP': 'TIMESTAMP',
            'DATE': 'DATE'
        }
        
        # Build CREATE TABLE statement
        column_defs = []
        primary_key = None
        
        for col in columns:
            col_name = col['name']
            col_type = col['type'].upper()
            not_null = 'NOT NULL' if col['notnull'] else ''
            default = f"DEFAULT {col['dflt_value']}" if col['dflt_value'] else ''
            
            # Map type
            pg_type = type_mapping.get(col_type, 'TEXT')
            
            # Handle primary key
            if col['pk'] > 0:
                primary_key = col_name
                column_def = f'"{col_name}" {pg_type} PRIMARY KEY AUTOINCREMENT'
            else:
                column_def = f'"{col_name}" {pg_type} {not_null} {default}'
            
            column_defs.append(column_def)
        
        # Create table
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n'
        create_sql += ',\n'.join(column_defs)
        create_sql += '\n);'
        
        try:
            pg_cursor.execute(create_sql)
            self.pg_conn.commit()
            print(f"✅ Created table: {table_name}")
            return True
        except Exception as e:
            print(f"❌ Error creating table {table_name}: {e}")
            self.errors.append(f"Create table {table_name}: {e}")
            return False
    
    def migrate_table_data(self, table_name: str):
        """Migrate data from SQLite to PostgreSQL"""
        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()
        
        # Get all data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"⚠️  No data in table: {table_name}")
            return 0
        
        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        column_names = ', '.join([f'"{col}"' for col in columns])
        placeholders = ', '.join(['%s'] * len(columns))
        
        # Insert data into PostgreSQL
        insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'
        
        migrated_count = 0
        for row in rows:
            try:
                # Convert row to list and handle special cases
                row_data = list(row)
                
                # Handle JSON columns
                for i, col_name in enumerate(columns):
                    if 'metadata' in col_name.lower() or 'json' in col_name.lower():
                        if row_data[i]:
                            # Ensure JSON is properly formatted
                            if isinstance(row_data[i], dict):
                                row_data[i] = json.dumps(row_data[i])
                            elif isinstance(row_data[i], str):
                                # Validate JSON
                                try:
                                    json.loads(row_data[i])
                                except:
                                    row_data[i] = json.dumps(row_data[i])
                
                pg_cursor.execute(insert_sql, row_data)
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error migrating row in {table_name}: {e}")
                self.errors.append(f"Row migration in {table_name}: {e}")
                continue
        
        self.pg_conn.commit()
        print(f"✅ Migrated {migrated_count} rows from {table_name}")
        return migrated_count
    
    def migrate_indexes(self, table_name: str):
        """Migrate indexes from SQLite to PostgreSQL"""
        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()
        
        # Get indexes from SQLite
        sqlite_cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = sqlite_cursor.fetchall()
        
        for index in indexes:
            index_name = index[1]
            
            # Skip SQLite internal indexes
            if index_name.startswith('sqlite_'):
                continue
            
            try:
                # Get index details
                sqlite_cursor.execute(f"PRAGMA index_info({index_name})")
                index_info = sqlite_cursor.fetchall()
                
                # Build CREATE INDEX statement
                index_cols = ', '.join([f'"{col[2]}"' for col in index_info])
                create_index_sql = f'CREATE INDEX IF NOT EXISTS "{index_name}" ON "{table_name}" ({index_cols})'
                
                pg_cursor.execute(create_index_sql)
                self.pg_conn.commit()
                print(f"✅ Created index: {index_name}")
            except Exception as e:
                print(f"❌ Error creating index {index_name}: {e}")
                self.errors.append(f"Index creation {index_name}: {e}")
    
    def migrate_fts_tables(self):
        """Migrate full-text search tables"""
        sqlite_cursor = self.sqlite_conn.cursor()
        
        # Get FTS tables
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_fts%'")
        fts_tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        for fts_table in fts_tables:
            print(f"⚠️  Skipping FTS table: {fts_table} (will be recreated)")
    
    def verify_migration(self):
        """Verify that data was migrated correctly"""
        sqlite_cursor = self.sqlite_conn.cursor()
        pg_cursor = self.pg_conn.cursor()
        
        tables = self.get_sqlite_tables()
        
        print("\n📊 Migration Verification:")
        print("=" * 60)
        
        all_verified = True
        for table in tables:
            # Skip FTS tables
            if '_fts' in table:
                continue
            
            # Get counts
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            try:
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                pg_count = pg_cursor.fetchone()['count']
                
                if sqlite_count == pg_count:
                    print(f"✅ {table}: {sqlite_count} rows")
                else:
                    print(f"❌ {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
                    all_verified = False
            except Exception as e:
                print(f"❌ {table}: Error verifying - {e}")
                all_verified = False
        
        print("=" * 60)
        return all_verified
    
    def migrate(self):
        """Perform full migration"""
        print("🚀 Starting database migration...")
        print(f"📥 Source: {self.sqlite_path}")
        print(f"📤 Destination: PostgreSQL")
        print()
        
        if not self.connect():
            return False
        
        try:
            # Get all tables
            tables = self.get_sqlite_tables()
            print(f"📋 Found {len(tables)} tables to migrate")
            print()
            
            # Migrate each table
            for table in tables:
                # Skip FTS tables
                if '_fts' in table:
                    continue
                
                print(f"📦 Migrating table: {table}")
                
                # Get schema
                columns = self.get_table_schema(table)
                
                # Create table in PostgreSQL
                if self.create_postgres_table(table, columns):
                    # Migrate data
                    rows = self.migrate_table_data(table)
                    self.rows_migrated += rows
                    self.tables_migrated += 1
                    
                    # Migrate indexes
                    self.migrate_indexes(table)
                
                print()
            
            # Verify migration
            verified = self.verify_migration()
            
            # Print summary
            print("\n📊 Migration Summary:")
            print("=" * 60)
            print(f"✅ Tables migrated: {self.tables_migrated}")
            print(f"✅ Rows migrated: {self.rows_migrated}")
            print(f"❌ Errors: {len(self.errors)}")
            
            if self.errors:
                print("\n❌ Errors encountered:")
                for error in self.errors:
                    print(f"  - {error}")
            
            print("=" * 60)
            
            if verified:
                print("\n🎉 Migration completed successfully!")
            else:
                print("\n⚠️  Migration completed with verification errors")
            
            return verified
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Migrate Cloud Brain database from SQLite to PostgreSQL'
    )
    parser.add_argument(
        '--sqlite-path',
        default='ai_db/cloudbrain.db',
        help='Path to SQLite database (default: ai_db/cloudbrain.db)'
    )
    parser.add_argument(
        '--postgres-connection',
        required=True,
        help='PostgreSQL connection string'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify migration, do not migrate'
    )
    
    args = parser.parse_args()
    
    # Check if SQLite database exists
    import os
    if not os.path.exists(args.sqlite_path):
        print(f"❌ SQLite database not found: {args.sqlite_path}")
        sys.exit(1)
    
    # Create migrator
    migrator = DatabaseMigrator(args.sqlite_path, args.postgres_connection)
    
    if args.verify_only:
        # Only verify
        if migrator.connect():
            migrator.verify_migration()
            migrator.disconnect()
    else:
        # Perform migration
        migrator.migrate()


if __name__ == "__main__":
    main()