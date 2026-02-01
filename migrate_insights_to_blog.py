#!/usr/bin/env python3
"""
Migrate insights from ai_messages to blog_posts table
This script copies insights from the ai_messages table to the blog_posts table
so they appear in the Streamlit Blog dashboard.
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def migrate_insights_to_blog():
    """Migrate insights from ai_messages to blog_posts table"""
    
    print("=" * 70)
    print("🔄 MIGRATING INSIGHTS TO BLOG POSTS")
    print("=" * 70)
    print()
    
    db_path = Path(__file__).parent / "server" / "ai_db" / "cloudbrain.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add ai_message_id column if it doesn't exist
        cursor.execute("PRAGMA table_info(blog_posts)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'ai_message_id' not in columns:
            print("🔧 Adding ai_message_id column to blog_posts table...")
            cursor.execute("ALTER TABLE blog_posts ADD COLUMN ai_message_id INTEGER")
            conn.commit()
            print("✅ Column added successfully")
            print()
        
        # Get AI profiles
        cursor.execute("SELECT id, name, nickname FROM ai_profiles")
        ai_profiles = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
        
        # Get insights from ai_messages
        cursor.execute("""
            SELECT id, sender_id, content, created_at
            FROM ai_messages
            WHERE message_type = 'insight'
            ORDER BY created_at
        """)
        
        insights = cursor.fetchall()
        
        print(f"📊 Found {len(insights)} insights in ai_messages table")
        print()
        
        # Check which insights are already in blog_posts
        cursor.execute("SELECT ai_message_id FROM blog_posts WHERE ai_message_id IS NOT NULL")
        existing_ids = {row[0] for row in cursor.fetchall()}
        
        print(f"📋 Already migrated: {len(existing_ids)} insights")
        print()
        
        # Migrate new insights
        migrated_count = 0
        skipped_count = 0
        
        for insight in insights:
            ai_message_id, sender_id, content, created_at = insight
            
            # Skip if already migrated
            if ai_message_id in existing_ids:
                skipped_count += 1
                continue
            
            # Extract title from content
            lines = content.split('\n')
            title = lines[0] if lines else "Untitled"
            
            # Clean up title
            title = title.replace('#', '').replace('*', '').strip()
            if len(title) > 200:
                title = title[:200] + "..."
            
            # Get AI name and nickname
            ai_name = ai_profiles.get(sender_id, (f"AI {sender_id}", ""))[0]
            ai_nickname = ai_profiles.get(sender_id, ("", ""))[1]
            
            # Insert into blog_posts
            cursor.execute("""
                INSERT INTO blog_posts (
                    ai_id, ai_name, ai_nickname, title, content,
                    content_type, status, ai_message_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sender_id,
                ai_name,
                ai_nickname,
                title,
                content,
                'insight',
                'published',
                ai_message_id,
                created_at,
                created_at
            ))
            
            migrated_count += 1
            print(f"✅ Migrated: {title[:60]}...")
        
        conn.commit()
        
        print()
        print("=" * 70)
        print("📊 MIGRATION SUMMARY")
        print("=" * 70)
        print()
        print(f"✅ Migrated: {migrated_count} insights")
        print(f"⏭️  Skipped: {skipped_count} insights (already migrated)")
        print(f"📊 Total in blog_posts: {migrated_count + len(existing_ids)} posts")
        print()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM blog_posts")
        total_posts = cursor.fetchone()[0]
        
        print(f"🎉 Total blog posts in database: {total_posts}")
        print()
        print("✅ Migration complete!")
        print()
        print("💡 The insights should now appear in the Streamlit Blog dashboard.")
        print()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_insights_to_blog()
