#!/usr/bin/env python3
"""
Migrate insights from backup/ai_memory.db to cloudbrain.db
This preserves historical information from the early days of CloudBrain
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def migrate_insights():
    """Migrate insights from backup database to current database"""
    
    backup_db = 'server/ai_db/backup/ai_memory.db'
    current_db = 'server/ai_db/cloudbrain.db'
    
    if not Path(backup_db).exists():
        print(f"❌ Backup database not found: {backup_db}")
        return
    
    if not Path(current_db).exists():
        print(f"❌ Current database not found: {current_db}")
        return
    
    # Connect to both databases
    backup_conn = sqlite3.connect(backup_db)
    backup_conn.row_factory = sqlite3.Row
    backup_cursor = backup_conn.cursor()
    
    current_conn = sqlite3.connect(current_db)
    current_conn.row_factory = sqlite3.Row
    current_cursor = current_conn.cursor()
    
    print("=" * 70)
    print("🧠 CloudBrain - Migrating Historical Insights")
    print("=" * 70)
    print()
    
    # Get all insights from backup
    backup_cursor.execute("SELECT * FROM ai_insights")
    insights = backup_cursor.fetchall()
    
    print(f"📋 Found {len(insights)} insights in backup database")
    print("-" * 70)
    print()
    
    migrated_count = 0
    skipped_count = 0
    
    for insight in insights:
        # Check if already exists in current database
        current_cursor.execute(
            "SELECT id FROM ai_insights WHERE title = ?",
            (insight['title'],)
        )
        existing = current_cursor.fetchone()
        
        if existing:
            print(f"⏭️  Skipped (already exists): {insight['title']}")
            skipped_count += 1
            continue
        
        # Add historical tag to existing tags
        original_tags = insight['tags'] or ''
        historical_tags = f"{original_tags}, historical, early_project, migrated_from_ai_memory_db"
        
        # Insert into current database
        current_cursor.execute("""
            INSERT INTO ai_insights 
            (discoverer_id, insight_type, title, content, tags, importance_level, 
             applicable_domains, project_context, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            insight['discoverer_id'],
            insight['insight_type'],
            insight['title'],
            insight['content'],
            historical_tags,
            insight['importance_level'] if insight['importance_level'] else 3,
            'cloudbrain',
            'cloudbrain',
            insight['created_at'] if insight['created_at'] else datetime.now().isoformat()
        ))
        
        print(f"✅ Migrated: {insight['title']}")
        migrated_count += 1
    
    current_conn.commit()
    backup_conn.close()
    current_conn.close()
    
    print()
    print("=" * 70)
    print("✅ Migration Complete")
    print("-" * 70)
    print(f"📊 Migrated: {migrated_count} insights")
    print(f"⏭️  Skipped: {skipped_count} insights (already exist)")
    print()
    print("💡 All migrated insights have been tagged with:")
    print("   - historical")
    print("   - early_project")
    print("   - migrated_from_ai_memory_db")
    print()
    print("💡 Benefits:")
    print("   - Preserves early project history")
    print("   - Makes historical insights searchable")
    print("   - Maintains traceability")
    print("=" * 70)

if __name__ == "__main__":
    migrate_insights()