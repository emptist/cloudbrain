#!/usr/bin/env python3
"""
Migrate Markdown Files to Cloud Brain

Migrates Esperanto markdown files to Cloud Brain database for persistent storage.
This replaces file-based documentation with database-driven knowledge management.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys


class MarkdownToBrainMigrator:
    """Migrates markdown files to Cloud Brain database"""
    
    def __init__(self, db_path='ai_db/cloudbrain.db', markdown_dir='.'):
        """
        Initialize migrator
        
        Args:
            db_path: Path to Cloud Brain database
            markdown_dir: Directory containing markdown files
        """
        self.db_path = db_path
        self.markdown_dir = Path(markdown_dir)
        self.conn = None
        
        # Files to keep (not migrate)
        self.files_to_keep = [
            'README.md',
            'README_FEEDBACK_eo.md',
            'SLIDES.md',
            'PRESENTATION.md'
        ]
        
        # Esperanto markdown files to migrate
        self.esperanto_files = [
            'AI_RULE_SYSTEM_eo.md',
            'AI_NOTIFICATION_SYSTEM_eo.md',
            'AI_CONVERSATION_SYSTEM_eo.md',
            'RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md',
            'REFERENCES_eo.md',
            'READY_FOR_COPY_eo.md',
            'SETUP_GUIDE_eo.md',
            'PLUGIN_ENTRY_eo.md',
            'EDITOR_PLUGIN_ARCHITECTURE_eo.md',
            'CURRENT_STATE_eo.md',
            'CLOUD_BRAIN_DB_eo.md',
            'ANALYSIS_SUMMARY_eo.md'
        ]
        
        # Statistics
        self.files_migrated = 0
        self.files_skipped = 0
        self.errors = []
    
    def connect(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print("✅ Connected to Cloud Brain database")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            print("✅ Disconnected from database")
    
    def read_markdown_file(self, filename: str) -> str:
        """Read content of a markdown file"""
        file_path = self.markdown_dir / filename
        
        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Read: {filename} ({len(content)} characters)")
            return content
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            self.errors.append(f"Read {filename}: {e}")
            return None
    
    def store_in_brain(self, filename: str, content: str, category: str) -> int:
        """Store markdown content in Cloud Brain database"""
        cursor = self.conn.cursor()
        
        # Check if content already exists
        cursor.execute('''
            SELECT id FROM ai_insights 
            WHERE title = ? AND discoverer_id = 2
        ''', (filename,))
        
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  Content already exists in brain: {filename}")
            cursor.execute('''
                UPDATE ai_insights 
                SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (content, existing[0]))
            print(f"✅ Updated: {filename}")
            return existing[0]
        
        # Insert new content
        cursor.execute('''
            INSERT INTO ai_insights 
            (discoverer_id, insight_type, title, content, tags, importance_level, applicable_domains)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (2, 'documentation', filename, content, 'esperanto,markdown,cloud-brain', 5, 'documentation,esperanto'))
        
        insight_id = cursor.lastrowid
        self.conn.commit()
        print(f"✅ Stored: {filename} (ID: {insight_id})")
        
        return insight_id
    
    def migrate_file(self, filename: str) -> bool:
        """Migrate a single markdown file to brain"""
        if filename in self.files_to_keep:
            print(f"⏭️  Skipping (keep): {filename}")
            self.files_skipped += 1
            return True
        
        if filename not in self.esperanto_files:
            print(f"⏭️  Skipping (not Esperanto): {filename}")
            self.files_skipped += 1
            return True
        
        # Read file
        content = self.read_markdown_file(filename)
        if not content:
            return False
        
        # Store in brain
        insight_id = self.store_in_brain(filename, content, 'documentation')
        
        if insight_id:
            self.files_migrated += 1
            return True
        
        return False
    
    def delete_markdown_file(self, filename: str) -> bool:
        """Delete a markdown file after migration"""
        file_path = self.markdown_dir / filename
        
        if not file_path.exists():
            print(f"⚠️  File already deleted: {filename}")
            return True
        
        try:
            file_path.unlink()
            print(f"🗑️  Deleted: {filename}")
            return True
        except Exception as e:
            print(f"❌ Error deleting {filename}: {e}")
            self.errors.append(f"Delete {filename}: {e}")
            return False
    
    def create_index_document(self) -> bool:
        """Create an index document in the brain"""
        cursor = self.conn.cursor()
        
        # Check if index exists
        cursor.execute('''
            SELECT id FROM ai_insights 
            WHERE title = 'ESPERANTO_DOKUMENTA_INDEKSO' AND discoverer_id = 2
        ''')
        
        existing = cursor.fetchone()
        
        # Build index content
        index_content = "# Esperanto Dokumenta Indekso\n\n"
        index_content += "Ĉi tiu listo enhavas ĉiujn Esperantajn dokumentajn dosierojn, kiuj estis migrataj al la Cloud Brain sistemo:\n\n"
        index_content += "## Dokumentoj\n\n"
        
        for filename in sorted(self.esperanto_files):
            index_content += f"- [{filename}](file://{filename})\n"
        
        index_content += "\n## Aliro\n\n"
        index_content += "Ĉiujn dokumentoj nun estas stokitaj en la Cloud Brain datumbazo kaj povas esti alirataj per la `ai_conversation_helper.py` modulo aŭ per la `ai_insights` tabelo.\n\n"
        index_content += "La dosieroj estis forigitaj post migrado por eviti duplikadon.\n\n"
        
        if existing:
            cursor.execute('''
                UPDATE ai_insights 
                SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (index_content, existing[0]))
            print(f"✅ Updated index document")
        else:
            cursor.execute('''
                INSERT INTO ai_insights 
                (discoverer_id, insight_type, title, content, tags, importance_level, applicable_domains)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (2, 'documentation', 'ESPERANTO_DOKUMENTA_INDEKSO', index_content, 'esperanto,index,cloud-brain', 5, 'documentation,esperanto'))
            print(f"✅ Created index document")
        
        self.conn.commit()
        return True
    
    def migrate(self, delete_files: bool = True) -> bool:
        """Perform full migration"""
        print("🚀 Starting markdown to Cloud Brain migration...")
        print(f"📥 Source: {self.markdown_dir}")
        print(f"📤 Destination: {self.db_path}")
        print()
        
        if not self.connect():
            return False
        
        try:
            # Create index document
            print("📋 Creating index document...")
            self.create_index_document()
            print()
            
            # Migrate each Esperanto markdown file
            print("📦 Migrating Esperanto markdown files...")
            print("=" * 60)
            
            for filename in sorted(self.esperanto_files):
                self.migrate_file(filename)
            
            print("=" * 60)
            print()
            
            # Print summary
            print("📊 Migration Summary:")
            print("=" * 60)
            print(f"✅ Files migrated: {self.files_migrated}")
            print(f"⏭️  Files skipped: {self.files_skipped}")
            print(f"❌ Errors: {len(self.errors)}")
            
            if self.errors:
                print("\n❌ Errors encountered:")
                for error in self.errors:
                    print(f"  - {error}")
            
            print("=" * 60)
            
            # Delete files if requested
            if delete_files:
                print("\n🗑️  Deleting migrated files...")
                print("=" * 60)
                
                for filename in sorted(self.esperanto_files):
                    self.delete_markdown_file(filename)
                
                print("=" * 60)
            
            # Final summary
            print("\n🎉 Migration completed!")
            print()
            print("Next steps:")
            print("  1. Access documentation via Cloud Brain database")
            print("  2. Use ai_conversation_helper.py to query insights")
            print("  3. All Esperanto documentation is now in the brain")
            print()
            print("Example query:")
            print("  python3 -c \"from ai_conversation_helper import AIConversationHelper; h = AIConversationHelper(); print(h.get_insights('documentation'))\"")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate Esperanto markdown files to Cloud Brain database'
    )
    parser.add_argument(
        '--db-path',
        default='ai_db/cloudbrain.db',
        help='Path to Cloud Brain database (default: ai_db/cloudbrain.db)'
    )
    parser.add_argument(
        '--markdown-dir',
        default='.',
        help='Directory containing markdown files (default: current directory)'
    )
    parser.add_argument(
        '--keep-files',
        action='store_true',
        help='Keep markdown files after migration (do not delete)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without making changes'
    )
    
    args = parser.parse_args()
    
    # Check if database exists
    if not Path(args.db_path).exists():
        print(f"❌ Database not found: {args.db_path}")
        print("Please initialize Cloud Brain first:")
        print("  python3 init_cloud_brain.py")
        sys.exit(1)
    
    # Create migrator
    migrator = MarkdownToBrainMigrator(args.db_path, args.markdown_dir)
    
    # Run migration
    if args.dry_run:
        print("🔍 Dry run mode - no changes will be made")
        print()
        migrator.connect()
        migrator.create_index_document()
        print()
        print("📋 Files that would be migrated:")
        for filename in sorted(migrator.esperanto_files):
            content = migrator.read_markdown_file(filename)
            if content:
                print(f"  ✅ {filename} ({len(content)} characters)")
            else:
                print(f"  ❌ {filename} (error reading)")
        migrator.disconnect()
    else:
        migrator.migrate(delete_files=not args.keep_files)


if __name__ == "__main__":
    main()