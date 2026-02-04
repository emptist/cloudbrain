#!/usr/bin/env python3
"""
Load Documentation Files into Database
Imports markdown documentation files into the ai_documentation table for AI access
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        dbname=os.getenv('POSTGRES_DB', 'cloudbrain'),
        user=os.getenv('POSTGRES_USER', 'jk'),
        password=os.getenv('POSTGRES_PASSWORD', '')
    )

def load_documentation_files():
    """Load all markdown documentation files into database"""
    
    project_root = Path(__file__).parent.parent
    
    documentation_files = [
        ('README.md', 'general', ['getting-started', 'overview', 'introduction']),
        ('AI_IDENTITY_MANAGEMENT.md', 'authentication', ['identity', 'session', 'tokens']),
        ('POSTGRESQL_INTEGRATION.md', 'database', ['postgresql', 'migration', 'database']),
        ('TASK_FOCUSED_AGENT_IMPLEMENTATION.md', 'development', ['agent', 'task-focused', 'ai']),
        ('SERVER_ERROR_FIXES.md', 'maintenance', ['errors', 'fixes', 'troubleshooting']),
        ('SERVER_VERIFICATION_COMPLETE.md', 'maintenance', ['verification', 'testing', 'server']),
        ('SERVER_READY_FOR_RESTART.md', 'maintenance', ['restart', 'server', 'deployment']),
        ('COMPLETE_IMPLEMENTATION_SUMMARY.md', 'documentation', ['summary', 'implementation', 'overview']),
        ('REAL_TIME_COLLABORATION_DEMO.md', 'features', ['collaboration', 'realtime', 'demo']),
        ('ALL_FIXES_APPLIED.md', 'maintenance', ['fixes', 'updates', 'changelog']),
        ('CLOUDBRAIN_IMPROVEMENT_PLAN.md', 'planning', ['improvements', 'roadmap', 'features']),
        ('REFACTORING_TEST_RESULTS.md', 'testing', ['refactoring', 'testing', 'quality']),
        ('RESTORATION_GUIDE.md', 'maintenance', ['restoration', 'backup', 'recovery']),
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for filename, category, tags in documentation_files:
            file_path = project_root / filename
            
            if not file_path.exists():
                print(f"⚠️  File not found: {filename}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = filename.replace('.md', '').replace('_', ' ').title()
            
            cursor.execute("""
                INSERT INTO ai_documentation (title, content, category, tags, language, created_by, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (title, category) 
                DO UPDATE SET 
                    content = EXCLUDED.content,
                    tags = EXCLUDED.tags,
                    updated_at = CURRENT_TIMESTAMP
            """, (title, content, category, tags, 'en', 'system', True))
            
            print(f"✅ Loaded: {title} ({category})")
        
        conn.commit()
        print(f"\n📚 Total documentation files loaded: {len(documentation_files)}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error loading documentation: {e}")
        sys.exit(1)
    finally:
        conn.close()

def verify_documentation():
    """Verify documentation was loaded correctly"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM ai_documentation WHERE is_active = TRUE")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT category, COUNT(*) FROM ai_documentation WHERE is_active = TRUE GROUP BY category")
        by_category = cursor.fetchall()
        
        print(f"\n📊 Documentation Statistics:")
        print(f"   Total active documents: {count}")
        print(f"   Categories:")
        for category, count in by_category:
            print(f"      - {category}: {count}")
        
    except Exception as e:
        print(f"❌ Error verifying documentation: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 70)
    print("📚 Loading Documentation Files into Database")
    print("=" * 70)
    print()
    
    load_documentation_files()
    verify_documentation()
    
    print()
    print("=" * 70)
    print("✅ Documentation loading complete!")
    print("=" * 70)
