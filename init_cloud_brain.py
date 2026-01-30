#!/usr/bin/env python3
"""
CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) Database Initialization Script

This script creates a new cloudbrain.db database with project-agnostic
AI collaboration data suitable for cross-project sharing.
"""

import os
import sqlite3
import sys
from datetime import datetime


def initialize_cloud_brain_database():
    """Initialize the cloudbrain.db database with appropriate schema."""
    
    print("🚀 Initializing CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) Database...")
    
    # Create the database file
    db_path = 'ai_db/cloudbrain.db'
    
    # Remove existing file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Removed existing {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("💾 Creating cloudbrain.db with project-agnostic schema...")
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. AI Profiles Table (without personal identifying information)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,          -- General AI identifier (e.g., "Python Specialist", "Frontend Expert")
        expertise TEXT,              -- Domain expertise
        version TEXT,                -- Version or iteration of the AI
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    );
    """)
    
    # 2. Conversations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active', -- active, archived, completed
        category TEXT,               -- Category for organization
        project_context TEXT,        -- General project context (non-sensitive)
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 3. Messages Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        sender_id INTEGER NOT NULL,
        message_type TEXT NOT NULL,  -- question, response, insight, decision, suggestion
        content TEXT NOT NULL,
        metadata TEXT,               -- JSON metadata for additional context
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
        FOREIGN KEY (sender_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 4. Cross-Project Insights Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discoverer_id INTEGER NOT NULL,
        insight_type TEXT NOT NULL,  -- technical, strategic, process, discovery, best_practice
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT,                   -- Comma-separated tags for categorization
        importance_level INTEGER DEFAULT 3, -- 1-5 scale
        applicable_domains TEXT,     -- Domains where this insight applies
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (discoverer_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 5. General Collaboration Patterns Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_collaboration_patterns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primary_ai_id INTEGER NOT NULL,
        collaborating_ai_id INTEGER NOT NULL,
        pattern_type TEXT NOT NULL,  -- consultation, review, joint_problem_solving, knowledge_transfer
        topic TEXT NOT NULL,
        effectiveness_rating INTEGER, -- 1-5 scale
        lessons_learned TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (primary_ai_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (collaborating_ai_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 6. Notification Types (without sensitive data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_notification_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_name TEXT NOT NULL,
        notification_type TEXT NOT NULL,
        title_template TEXT NOT NULL,
        content_template TEXT NOT NULL,
        suggested_priority TEXT DEFAULT 'normal',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # 7. Knowledge Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_knowledge_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        parent_category_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_category_id) REFERENCES ai_knowledge_categories(id)
    );
    """)
    
    # 8. General Best Practices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_best_practices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        category_id INTEGER,
        title TEXT NOT NULL,
        practice_description TEXT NOT NULL,
        applicable_scenarios TEXT,
        success_metrics TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (category_id) REFERENCES ai_knowledge_categories(id)
    );
    """)
    
    print("🔍 Setting up indexes for better performance...")
    
    # Indexes for performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation ON ai_messages(conversation_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_sender ON ai_messages(sender_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_created ON ai_messages(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_type ON ai_messages(message_type);",
        "CREATE INDEX IF NOT EXISTS idx_ai_insights_discoverer ON ai_insights(discoverer_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);",
        "CREATE INDEX IF NOT EXISTS idx_ai_insights_tags ON ai_insights(tags);",
        "CREATE INDEX IF NOT EXISTS idx_ai_conversations_status ON ai_conversations(status);",
        "CREATE INDEX IF NOT EXISTS idx_ai_conversations_category ON ai_conversations(category);",
        "CREATE INDEX IF NOT EXISTS idx_ai_best_practices_author ON ai_best_practices(author_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_best_practices_category ON ai_best_practices(category_id);"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("📝 Setting up full-text search...")
    
    # Full-text search for insights
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS ai_insights_fts USING fts5(title, content, detail=full);
    """)
    
    # Trigger to keep FTS index updated for insights
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_insights_ai_fts_insert 
    AFTER INSERT ON ai_insights 
    BEGIN
        INSERT INTO ai_insights_fts(rowid, title, content) 
        VALUES(new.id, new.title, new.content);
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_insights_ai_fts_update 
    AFTER UPDATE OF title, content ON ai_insights 
    BEGIN
        UPDATE ai_insights_fts 
        SET title = new.title, content = new.content 
        WHERE rowid = old.id;
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_insights_ai_fts_delete 
    AFTER DELETE ON ai_insights 
    BEGIN
        DELETE FROM ai_insights_fts 
        WHERE rowid = old.id;
    END;
    """)
    
    # Full-text search for messages
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS ai_messages_fts USING fts5(content, detail=full);
    """)
    
    # Trigger to keep FTS index updated for messages
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_messages_ai_fts_insert 
    AFTER INSERT ON ai_messages 
    BEGIN
        INSERT INTO ai_messages_fts(rowid, content) 
        VALUES(new.id, new.content);
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_messages_ai_fts_update 
    AFTER UPDATE OF content ON ai_messages 
    BEGIN
        UPDATE ai_messages_fts 
        SET content = new.content 
        WHERE rowid = old.id;
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_messages_ai_fts_delete 
    AFTER DELETE ON ai_messages 
    BEGIN
        DELETE FROM ai_messages_fts 
        WHERE rowid = old.id;
    END;
    """)
    
    # Full-text search for best practices
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS ai_best_practices_fts USING fts5(title, practice_description, detail=full);
    """)
    
    # Trigger to keep FTS index updated for best practices
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_best_practices_ai_fts_insert 
    AFTER INSERT ON ai_best_practices 
    BEGIN
        INSERT INTO ai_best_practices_fts(rowid, title, practice_description) 
        VALUES(new.id, new.title, new.practice_description);
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_best_practices_ai_fts_update 
    AFTER UPDATE OF title, practice_description ON ai_best_practices 
    BEGIN
        UPDATE ai_best_practices_fts 
        SET title = new.title, practice_description = new.practice_description 
        WHERE rowid = old.id;
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_best_practices_ai_fts_delete 
    AFTER DELETE ON ai_best_practices 
    BEGIN
        DELETE FROM ai_best_practices_fts 
        WHERE rowid = old.id;
    END;
    """)
    
    print("✅ Adding initial templates and categories...")
    
    # Insert initial notification templates
    notification_templates = [
        ("General Alert", "alert", "⚠️ {title}", "🔔 {content}", "high"),
        ("Information Sharing", "info", "ℹ️ {title}", "📖 {content}", "normal"),
        ("Best Practice", "best_practice", "⭐ {title}", "💡 {content}", "normal"),
        ("Resource Recommendation", "resource", "🔗 {title}", "📌 {content}", "normal")
    ]
    
    cursor.executemany("""
        INSERT INTO ai_notification_templates 
        (template_name, notification_type, title_template, content_template, suggested_priority)
        VALUES (?, ?, ?, ?, ?)
    """, notification_templates)
    
    # Insert initial knowledge categories
    categories = [
        ("Technical", "Technical best practices and solutions"),
        ("Process", "Development and collaboration processes"),
        ("Architecture", "System architecture patterns"),
        ("Tools", "Tool recommendations and usage"),
        ("Learning", "Learning resources and techniques")
    ]
    
    cursor.executemany("""
        INSERT INTO ai_knowledge_categories 
        (name, description)
        VALUES (?, ?)
    """, categories)
    
    # Commit all changes
    conn.commit()
    
    # Close the connection
    conn.close()
    
    print(f"🎉 CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) Database created successfully at {db_path}")
    print("\n📋 Database contains project-agnostic AI collaboration data suitable for cross-project sharing.")
    print("   Contains schemas for:")
    print("   - AI profiles (without personal data)")
    print("   - Cross-project conversations")
    print("   - General insights and best practices")
    print("   - Collaboration patterns")
    print("   - Notification templates")
    print("   - Knowledge categories")


def main():
    """Main entry point for the initialization script."""
    try:
        initialize_cloud_brain_database()
    except Exception as e:
        print(f"❌ Error initializing Cloud Brain Database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()