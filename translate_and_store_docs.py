#!/usr/bin/env python3
"""
Translate Documentation to Esperanto and Store in Cloud Brain

This script translates documentation files to Esperanto and stores them
in the cloud brain knowledge system for AI use.
"""

import os
import sys
from pathlib import Path
from ai_rule_engine import AIRuleEngine


def get_documentation_files():
    """Get list of documentation files to translate"""
    docs_to_translate = [
        'AI_CONVERSATION_SYSTEM.md',
        'AI_NOTIFICATION_SYSTEM.md',
        'AI_RULE_SYSTEM.md',
        'ANALYSIS_SUMMARY.md',
        'CLOUD_BRAIN_DB.md',
        'CURRENT_STATE.md',
        'EDITOR_PLUGIN_ARCHITECTURE.md',
        'PLUGIN_ENTRY.md',
        'README_FEEDBACK.md',
        'READY_FOR_COPY.md',
        'REFERENCES.md',
        'RULE_3_CLIENT_SECURITY_OVERRIDE.md',
        'SETUP_GUIDE.md'
    ]
    
    return docs_to_translate


def translate_to_esperanto(text):
    """
    Translate text to Esperanto
    Note: This is a placeholder. In production, use a proper translation service.
    """
    # Placeholder translation - in production, integrate with translation API
    # For now, we'll add a note that this needs proper translation
    return f"[Esperanto Translation Needed]\n\n{text}"


def store_in_cloud_brain(engine, title, content, category, db_path):
    """
    Store translated content in cloud brain knowledge system
    
    Args:
        engine: AIRuleEngine instance
        title: Title of the knowledge entry
        content: Content in Esperanto
        category: Category for organization
        db_path: Database path to use
    """
    conn = engine._get_connection()
    cursor = conn.cursor()
    
    # Store as an insight for AI knowledge
    cursor.execute("""
        INSERT INTO ai_insights 
        (discoverer_id, insight_type, title, content, tags, importance_level, related_to)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        1,  # System AI
        category,
        title,
        content,
        f"Esperanto,{category}",
        5,  # High importance
        "Cloud Brain Documentation"
    ))
    
    conn.commit()
    print(f"✅ Stored: {title}")


def process_documentation_files():
    """Process all documentation files"""
    docs = get_documentation_files()
    
    print(f"Processing {len(docs)} documentation files...")
    
    for doc_file in docs:
        file_path = Path(doc_file)
        
        if not file_path.exists():
            print(f"⚠️  File not found: {doc_file}")
            continue
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Translate to Esperanto
        esperanto_content = translate_to_esperanto(content)
        
        # Determine category based on filename
        if 'CONVERSATION' in doc_file:
            category = 'conversation_system'
        elif 'NOTIFICATION' in doc_file:
            category = 'notification_system'
        elif 'RULE' in doc_file:
            category = 'rule_system'
        elif 'SETUP' in doc_file:
            category = 'setup_guide'
        elif 'ARCHITECTURE' in doc_file:
            category = 'architecture'
        elif 'DB' in doc_file:
            category = 'database'
        else:
            category = 'general'
        
        # Store in cloud brain
        engine = AIRuleEngine(db_path='ai_db/ai_memory.db')
        store_in_cloud_brain(
            engine,
            title=doc_file.replace('.md', ''),
            content=esperanto_content,
            category=category,
            db_path='ai_db/ai_memory.db'
        )
        
        # Create Esperanto version file
        esperanto_file = file_path.stem + '_eo.md'
        with open(esperanto_file, 'w', encoding='utf-8') as f:
            f.write(esperanto_content)
        
        print(f"📝 Created: {esperanto_file}")


def create_knowledge_index():
    """Create an index of knowledge entries for easy reference"""
    engine = AIRuleEngine(db_path='ai_db/ai_memory.db')
    conn = engine._get_connection()
    cursor = conn.cursor()
    
    # Get all insights related to documentation
    cursor.execute("""
        SELECT id, title, insight_type, tags, created_at
        FROM ai_insights
        WHERE related_to = 'Cloud Brain Documentation'
        ORDER BY created_at DESC
    """)
    
    insights = cursor.fetchall()
    
    print(f"\n📚 Knowledge Index ({len(insights)} entries):")
    for insight in insights:
        print(f"  - [{insight['id']}] {insight['title']} ({insight['insight_type']})")
    
    # Store index as a note for AI reference
    index_content = "Cloud Brain Knowledge Index\n\n"
    for insight in insights:
        index_content += f"- {insight['title']}: ID {insight['id']}, Type: {insight['insight_type']}\n"
    
    cursor.execute("""
        INSERT INTO ai_next_session_notes 
        (sender_id, note_type, priority, title, content)
        VALUES (?, ?, ?, ?, ?)
    """, (
        1,
        'knowledge_index',
        'high',
        'Cloud Brain Knowledge Index',
        index_content
    ))
    
    conn.commit()
    print("\n✅ Knowledge index created as next session note")


def main():
    """Main execution function"""
    print("="*60)
    print("  Translate Documentation to Esperanto & Store in Cloud Brain")
    print("="*60)
    
    try:
        # Process documentation files
        process_documentation_files()
        
        # Create knowledge index
        create_knowledge_index()
        
        print("\n" + "="*60)
        print("  ✅ COMPLETED")
        print("="*60)
        print("\nNext steps:")
        print("1. Review Esperanto translations")
        print("2. Update translations with proper Esperanto")
        print("3. Git commit the changes")
        print("4. Delete original documentation files after verification")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
