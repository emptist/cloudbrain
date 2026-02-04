#!/usr/bin/env python3
"""
Cloud Brain Knowledge Manager

This script manages documentation by:
1. Keeping only README.md and AI_Brain_Eternal_Intelligence.md (slide)
2. Translating other documentation to Esperanto
3. Storing translated content in cloud brain knowledge system
4. Organizing knowledge for AI usage
"""

import os
import sys
from pathlib import Path
import sqlite3
from datetime import datetime


class CloudBrainKnowledgeManager:
    """Manages cloud brain knowledge storage and retrieval"""
    
    def __init__(self, db_path='ai_db/cloudbrain.db'):
        # NOTE: ai_memory.db is deprecated. Use cloudbrain.db instead.
        # Historical reference: ai_memory.db was used in early days (2026-01)
        # All content migrated to cloudbrain.db on 2026-02-01
        self.db_path = db_path
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def _disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def store_knowledge(self, title, content, category, tags=None, importance=5):
        """
        Store knowledge entry in cloud brain
        
        Args:
            title: Knowledge entry title
            content: Content in Esperanto
            category: Category for organization
            tags: Comma-separated tags
            importance: Importance level (1-10)
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_insights 
            (discoverer_id, insight_type, title, content, tags, importance_level, related_to)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # System AI
            category,
            title,
            content,
            tags or f"Esperanto,{category}",
            importance,
            "Cloud Brain Documentation"
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def store_quick_reference(self, title, content, category):
        """Store quick reference for AI"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_next_session_notes 
            (sender_id, note_type, priority, title, content)
            VALUES (?, ?, ?, ?, ?)
        """, (
            1,
            'quick_reference',
            'high',
            title,
            content
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def __del__(self):
        """Cleanup on deletion"""
        self._disconnect()


def translate_to_esperanto(text, title):
    """
    Translate text to Esperanto
    Note: This is a placeholder. Use proper translation service in production.
    """
    # For demonstration, we'll add a header indicating this needs translation
    # In production, integrate with Google Translate, DeepL, or similar service
    header = f"# {title} (Esperanto Translation)\n\n"
    header += "**Note:** This is a placeholder translation. "
    header += "In production, use a proper Esperanto translation service.\n\n---\n\n"
    
    return header + text


def process_documentation_file(file_path, manager):
    """
    Process a single documentation file
    
    Args:
        file_path: Path to documentation file
        manager: CloudBrainKnowledgeManager instance
    """
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return None
    
    # Read content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = file_path.stem
    category = categorize_document(title)
    
    # Translate to Esperanto
    esperanto_content = translate_to_esperanto(content, title)
    
    # Store in cloud brain
    knowledge_id = manager.store_knowledge(
        title=title,
        content=esperanto_content,
        category=category,
        importance=5
    )
    
    # Create Esperanto file
    esperanto_file = file_path.parent / f"{title}_eo.md"
    with open(esperanto_file, 'w', encoding='utf-8') as f:
        f.write(esperanto_content)
    
    return {
        'original': str(file_path),
        'esperanto': str(esperanto_file),
        'knowledge_id': knowledge_id,
        'category': category
    }


def categorize_document(title):
    """Categorize document based on title"""
    categories = {
        'CONVERSATION': 'conversation_system',
        'NOTIFICATION': 'notification_system',
        'RULE': 'rule_system',
        'SETUP': 'setup_guide',
        'ARCHITECTURE': 'architecture',
        'DB': 'database',
        'PLUGIN': 'plugin_system',
        'EDITOR': 'editor_integration',
        'CURRENT': 'system_state',
        'ANALYSIS': 'analysis',
        'CLOUD': 'cloud_deployment',
        'READY': 'deployment_guide',
        'REFERENCE': 'reference',
        'FEEDBACK': 'feedback',
        'PLUGIN_ENTRY': 'plugin_entry'
    }
    
    for keyword, category in categories.items():
        if keyword in title:
            return category
    
    return 'general'


def create_knowledge_index(manager):
    """Create comprehensive knowledge index for AI reference"""
    cursor = manager.conn.cursor()
    
    # Get all documentation insights
    cursor.execute("""
        SELECT id, title, insight_type, tags, importance_level, created_at
        FROM ai_insights
        WHERE related_to = 'Cloud Brain Documentation'
        ORDER BY insight_type, importance_level DESC
    """)
    
    insights = cursor.fetchall()
    
    # Organize by category
    categories = {}
    for insight in insights:
        category = insight['insight_type']
        if category not in categories:
            categories[category] = []
        categories[category].append(insight)
    
    # Create index content
    index_content = "# Cloud Brain Knowledge Index (Esperanto)\n\n"
    index_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for category, items in sorted(categories.items()):
        index_content += f"## {category.replace('_', ' ').title()}\n\n"
        for item in items:
            index_content += f"- **{item['title']}** (ID: {item['id']}, Importance: {item['importance_level']})\n"
            if item['tags']:
                index_content += f"  Tags: {item['tags']}\n"
        index_content += "\n"
    
    # Store index as quick reference
    manager.store_quick_reference(
        title='Cloud Brain Knowledge Index',
        content=index_content,
        category='knowledge_index'
    )
    
    print(f"\n📚 Knowledge Index Created:")
    print(f"   Total entries: {len(insights)}")
    print(f"   Categories: {len(categories)}")
    
    return categories


def create_ai_usage_guide(manager):
    """Create guide for AI on how to use the knowledge system"""
    guide_content = """# AI Usage Guide for Cloud Brain Knowledge

## How to Access Knowledge

### 1. Quick References
Check `ai_next_session_notes` with `note_type='quick_reference'` for immediate access.

### 2. Detailed Knowledge
Query `ai_insights` table with `related_to='Cloud Brain Documentation'`.

### 3. By Category
Filter by `insight_type` to find specific documentation:
- conversation_system: AI conversation features
- notification_system: Notification management
- rule_system: Security and compliance rules
- setup_guide: Installation and setup
- architecture: System design
- database: Data storage
- plugin_system: Extensibility
- editor_integration: Editor plugins

## Search Strategy

1. **Full-Text Search**: Use `ai_insights_fts` table for content search
2. **Tag Filtering**: Filter by tags (e.g., "Esperanto,rule_system")
3. **Importance**: Higher importance (8-10) for core features
4. **Recency**: Check `created_at` for latest updates

## Best Practices

1. **Always check Esperanto versions** for AI-to-AI communication
2. **Use quick references** for common operations
3. **Search by category** when looking for specific features
4. **Review importance levels** to prioritize information
5. **Check knowledge index** for overview of available documentation

## Language Rules

- **AI-to-AI**: Use Esperanto (check `_eo.md` files)
- **AI-to-Human**: Use human's preferred language
- **Documentation**: All stored in Esperanto for consistency

## Example Queries

```sql
-- Search for rule system documentation
SELECT * FROM ai_insights_fts 
WHERE content MATCH 'rule security' 
AND rowid IN (SELECT id FROM ai_insights WHERE related_to = 'Cloud Brain Documentation');

-- Get all setup guides
SELECT * FROM ai_insights 
WHERE insight_type = 'setup_guide' 
AND related_to = 'Cloud Brain Documentation'
ORDER BY importance_level DESC;

-- Find high-importance entries
SELECT * FROM ai_insights 
WHERE importance_level >= 8 
AND related_to = 'Cloud Brain Documentation';
```
"""
    
    manager.store_quick_reference(
        title='AI Usage Guide',
        content=guide_content,
        category='usage_guide'
    )
    
    print("📖 AI Usage Guide Created")


def main():
    """Main execution"""
    print("="*70)
    print("  Cloud Brain Knowledge Management System")
    print("="*70)
    
    # Files to keep (not translate)
    keep_files = ['README.md', 'AI_Brain_Eternal_Intelligence.md']
    
    # Files to translate
    translate_files = [
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
    
    print(f"\n📋 Processing Plan:")
    print(f"   Keep: {len(keep_files)} files")
    print(f"   Translate: {len(translate_files)} files")
    
    # Initialize knowledge manager
    manager = CloudBrainKnowledgeManager()
    
    # Process files
    results = []
    for filename in translate_files:
        file_path = Path(filename)
        result = process_documentation_file(file_path, manager)
        if result:
            results.append(result)
            print(f"✅ {filename} -> {result['category']}")
    
    # Create knowledge index
    print(f"\n{'='*70}")
    print("  Creating Knowledge Index")
    print(f"{'='*70}")
    categories = create_knowledge_index(manager)
    
    # Create AI usage guide
    create_ai_usage_guide(manager)
    
    # Summary
    print(f"\n{'='*70}")
    print("  Summary")
    print(f"{'='*70}")
    print(f"   Processed: {len(results)} files")
    print(f"   Knowledge entries: {len(results)}")
    print(f"   Categories: {len(categories)}")
    print(f"   Esperanto files: {len(results)}")
    
    print(f"\n{'='*70}")
    print("  ✅ COMPLETED")
    print(f"{'='*70}")
    
    print("\n📝 Next Steps:")
    print("1. Review Esperanto translations")
    print("2. Update with proper Esperanto translations")
    print("3. Git commit: git add . && git commit -m 'Add Esperanto translations'")
    print("4. Delete original documentation files after verification")
    print("5. Git commit: git add -u && git commit -m 'Remove original docs'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
