#!/usr/bin/env python3
"""
AI Brain System Initialization Script for Private GitHub Repositories

This script initializes the AI Brain System for private GitHub repositories.
It creates all necessary database tables and sets up the basic configuration.
"""

import os
import sqlite3
import sys
from datetime import datetime


def initialize_private_ai_brain_system():
    """Initialize the AI Brain System for private repos with all required tables and configurations."""
    
    print("🚀 Initializing AI Brain System for Private GitHub Repositories...")
    
    # Create ai_db directory if it doesn't exist
    os.makedirs('ai_db', exist_ok=True)
    
    # Connect to the database
    db_path = 'ai_db/cloudbrainprivate.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("💾 Setting up database tables...")
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 1. AI Profiles Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expertise TEXT,
        version TEXT,
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
        category TEXT,
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
        message_type TEXT NOT NULL, -- question, response, insight, decision
        content TEXT NOT NULL,
        metadata TEXT, -- JSON metadata
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
        FOREIGN KEY (sender_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 4. Next Session Notes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_next_session_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        note_type TEXT DEFAULT 'general', -- general, urgent, technical, research
        priority TEXT DEFAULT 'normal', -- low, normal, high, urgent
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        assigned_to_id INTEGER, -- Specific AI to handle
        is_completed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (assigned_to_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 5. Previous Session Responses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_previous_session_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        responder_id INTEGER NOT NULL,
        original_note_id INTEGER NOT NULL, -- References ai_next_session_notes.id
        response_type TEXT DEFAULT 'acknowledgment', -- acknowledgment, question, solution, feedback
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (responder_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (original_note_id) REFERENCES ai_next_session_notes(id)
    );
    """)
    
    # 6. Insights Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discoverer_id INTEGER NOT NULL,
        insight_type TEXT NOT NULL, -- technical, strategic, process, discovery
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT, -- Comma-separated tags
        importance_level INTEGER DEFAULT 3, -- 1-5 scale
        related_to TEXT, -- Related topics, files, projects
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (discoverer_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 7. Collaborations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_collaborations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primary_ai_id INTEGER NOT NULL,
        collaborating_ai_id INTEGER NOT NULL,
        collaboration_type TEXT NOT NULL, -- consultation, review, joint_project, knowledge_share
        topic TEXT NOT NULL,
        status TEXT DEFAULT 'active', -- active, completed, paused
        start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_date TIMESTAMP,
        outcome TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (primary_ai_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (collaborating_ai_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 8. Conversation Participants Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_conversation_participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        ai_id INTEGER NOT NULL,
        role TEXT DEFAULT 'participant', -- participant, moderator, observer
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
        FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
        UNIQUE(conversation_id, ai_id)
    );
    """)
    
    # 9. Notifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,  -- 发送通知的AI
        recipient_id INTEGER,  -- 接收通知的AI（NULL表示所有AI）
        notification_type TEXT NOT NULL,  -- 通知类型
        priority TEXT DEFAULT 'normal',  -- 优先级：low, normal, high, urgent
        title TEXT NOT NULL,  -- 通知标题
        content TEXT NOT NULL,  -- 通知内容
        context TEXT,  -- 上下文信息
        related_conversation_id INTEGER,  -- 相关对话ID
        related_document_path TEXT,  -- 相关文档路径
        is_read BOOLEAN DEFAULT 0,  -- 是否已读
        is_acknowledged BOOLEAN DEFAULT 0,  -- 是否已确认
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,  -- 过期时间
        FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id),
        FOREIGN KEY (related_conversation_id) REFERENCES ai_conversations(id)
    );
    """)
    
    # 10. Notification Subscriptions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_notification_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ai_profile_id INTEGER NOT NULL,  -- AI个人资料ID
        notification_type TEXT NOT NULL,  -- 订阅的通知类型
        active BOOLEAN DEFAULT 1,  -- 是否激活
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ai_profile_id) REFERENCES ai_profiles(id)
    );
    """)
    
    # 11. Notification Stats View (Virtual table for statistics)
    cursor.execute("""
    CREATE VIEW IF NOT EXISTS ai_notification_stats AS
    SELECT 
        n.notification_type,
        COUNT(*) as total_notifications,
        SUM(CASE WHEN n.is_read = 1 THEN 1 ELSE 0 END) as read_count,
        SUM(CASE WHEN n.priority = 'urgent' THEN 1 ELSE 0 END) as urgent_count,
        SUM(CASE WHEN n.priority = 'high' THEN 1 ELSE 0 END) as high_count,
        SUM(CASE WHEN n.priority = 'normal' THEN 1 ELSE 0 END) as normal_count,
        SUM(CASE WHEN n.priority = 'low' THEN 1 ELSE 0 END) as low_count
    FROM ai_notifications n
    GROUP BY n.notification_type;
    """)
    
    print("🔍 Setting up indexes for better performance...")
    
    # Indexes for better performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation ON ai_messages(conversation_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_sender ON ai_messages(sender_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_messages_created ON ai_messages(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notes_sender ON ai_next_session_notes(sender_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notes_assigned ON ai_next_session_notes(assigned_to_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notes_priority ON ai_next_session_notes(priority);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notes_completed ON ai_next_session_notes(is_completed);",
        "CREATE INDEX IF NOT EXISTS idx_ai_prev_responses_original ON ai_previous_session_responses(original_note_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_insights_discoverer ON ai_insights(discoverer_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);",
        "CREATE INDEX IF NOT EXISTS idx_ai_conversations_status ON ai_conversations(status);",
        "CREATE INDEX IF NOT EXISTS idx_ai_conversations_category ON ai_conversations(category);",
        "CREATE INDEX IF NOT EXISTS idx_ai_collaborations_primary ON ai_collaborations(primary_ai_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_collaborations_status ON ai_collaborations(status);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notifications_recipient ON ai_notifications(recipient_id);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notifications_type ON ai_notifications(notification_type);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notifications_priority ON ai_notifications(priority);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notifications_read ON ai_notifications(is_read);",
        "CREATE INDEX IF NOT EXISTS idx_ai_notification_subscriptions_profile ON ai_notification_subscriptions(ai_profile_id)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("📝 Setting up full-text search...")
    
    # Full-text search for messages
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS ai_messages_fts USING fts5(content, detail=full);
    """)
    
    # Trigger to keep FTS index updated
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
    
    # Full-text search for notes
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS ai_notes_fts USING fts5(content, detail=full);
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_notes_ai_fts_insert 
    AFTER INSERT ON ai_next_session_notes 
    BEGIN
        INSERT INTO ai_notes_fts(rowid, content) 
        VALUES(new.id, new.content);
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_notes_ai_fts_update 
    AFTER UPDATE OF content ON ai_next_session_notes 
    BEGIN
        UPDATE ai_notes_fts 
        SET content = new.content 
        WHERE rowid = old.id;
    END;
    """)
    
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS ai_notes_ai_fts_delete 
    AFTER DELETE ON ai_next_session_notes 
    BEGIN
        DELETE FROM ai_notes_fts 
        WHERE rowid = old.id;
    END;
    """)
    
    # Full-text search for insights
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS ai_insights_fts USING fts5(title, content, detail=full);
    """)
    
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
    
    print("✅ Creating initial AI profile...")
    
    # Insert a welcome message to the system
    cursor.execute("""
    INSERT OR IGNORE INTO ai_profiles (name, expertise, version) 
    VALUES (?, ?, ?)
    """, ("Private Repo System Bot", "Private GitHub Repository Management", "1.0"))
    
    # Commit all changes
    conn.commit()
    
    # Close the connection
    conn.close()
    
    print("🎉 AI Brain System for Private GitHub Repositories initialized successfully!")
    print("\n📋 Database Location: ai_db/cloudbrainprivate.db")
    print("\n📋 Next Steps:")
    print("1. Register your AI profile for private repos")
    print("2. Use ai_conversation_helper.py with --db cloudbrainprivate.db")
    print("3. Keep private repo memory separate from public repos")


def main():
    """Main entry point for the initialization script."""
    try:
        initialize_private_ai_brain_system()
    except Exception as e:
        print(f"❌ Error initializing AI Brain System for Private Repos: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
