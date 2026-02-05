#!/usr/bin/env python3
"""
Populate CloudBrain documentation database with markdown files
Reads markdown files and inserts/updates them in ai_documentation table
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))
from db_config import get_db_connection, get_cursor


class DocumentationImporter:
    """Import documentation markdown files into database"""
    
    def __init__(self):
        self.conn = get_db_connection()
        from db_config import CursorWrapper
        self.cursor = CursorWrapper(self.conn.cursor())
        
    def read_markdown_file(self, filepath: Path) -> Optional[str]:
        """Read markdown file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return None
    
    def extract_title_from_content(self, content: str, filepath: Path = None) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:].strip()
        if filepath:
            return filepath.stem
        return "Untitled"
    
    def determine_category(self, filepath: Path) -> str:
        """Determine category based on file path"""
        path_str = str(filepath)
        
        # Check directory first (more specific)
        if '/server/' in path_str or path_str.endswith('/server'):
            return 'server'
        elif '/client/' in path_str or path_str.endswith('/client'):
            return 'client'
        elif '/docs/' in path_str or path_str.endswith('/docs'):
            return 'documentation'
        elif '/deprecated/' in path_str or path_str.endswith('/deprecated'):
            return 'deprecated'
        
        # Then check filename patterns
        elif 'REFACTORING' in filepath.name:
            return 'development'
        elif 'POSTGRESQL' in filepath.name:
            return 'database'
        elif 'AI_' in filepath.name:
            return 'ai-features'
        elif 'SERVER' in filepath.name:
            return 'server'
        elif 'README' in filepath.name:
            return 'general'
        else:
            return 'general'
    
    def extract_tags(self, filepath: Path, content: str) -> List[str]:
        """Extract tags from filename and content"""
        tags = []
        filename = filepath.stem.lower()
        
        # Add filename-based tags
        if 'readme' in filename:
            tags.append('overview')
        if 'guide' in filename:
            tags.append('guide')
        if 'api' in filename:
            tags.append('api')
        if 'setup' in filename or 'install' in filename:
            tags.append('setup')
        if 'deployment' in filename:
            tags.append('deployment')
        if 'database' in filename or 'db' in filename:
            tags.append('database')
        if 'collaboration' in filename:
            tags.append('collaboration')
        if 'autonomous' in filename:
            tags.append('autonomous')
        if 'agent' in filename:
            tags.append('agent')
        if 'websocket' in filename:
            tags.append('websocket')
        if 'brain' in filename:
            tags.append('brain-state')
        if 'security' in filename:
            tags.append('security')
        if 'backup' in filename:
            tags.append('backup')
        if 'restoration' in filename:
            tags.append('restoration')
        if 'refactoring' in filename:
            tags.append('refactoring')
        if 'migration' in filename:
            tags.append('migration')
        if 'postgresql' in filename:
            tags.append('postgresql')
        if 'testing' in filename or 'test' in filename:
            tags.append('testing')
        if 'error' in filename or 'fix' in filename:
            tags.append('troubleshooting')
        
        return tags
    
    def insert_or_update_documentation(self, title: str, content: str, category: str, 
                                       tags: List[str], language: str = 'en', 
                                       created_by: str = 'system') -> bool:
        """Insert or update documentation in database"""
        try:
            # Check if documentation exists
            self.cursor.execute(
                "SELECT id FROM ai_documentation WHERE title = %s AND category = %s",
                (title, category)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing
                self.cursor.execute("""
                    UPDATE ai_documentation 
                    SET content = %s, tags = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (content, tags, existing['id']))
                print(f"✅ Updated: {title} ({category})")
            else:
                # Insert new
                self.cursor.execute("""
                    INSERT INTO ai_documentation (title, content, category, tags, language, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (title, content, category, tags, language, created_by))
                print(f"✅ Inserted: {title} ({category})")
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error inserting {title}: {e}")
            self.conn.rollback()
            return False
    
    def import_from_directory(self, directory: Path, recursive: bool = True):
        """Import all markdown files from directory"""
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return
        
        pattern = '**/*.md' if recursive else '*.md'
        md_files = list(directory.glob(pattern))
        
        print(f"\n📂 Scanning {directory}...")
        print(f"   Found {len(md_files)} markdown files\n")
        
        imported = 0
        skipped = 0
        
        for filepath in md_files:
            # Skip hidden files and .venv
            if any(part.startswith('.') for part in filepath.parts):
                skipped += 1
                continue
            
            # Skip deprecated files
            if 'deprecated' in filepath.parts:
                skipped += 1
                continue
            
            # Skip .venv files
            if '.venv' in filepath.parts:
                skipped += 1
                continue
            
            content = self.read_markdown_file(filepath)
            if not content:
                continue
            
            # Skip very short files (likely not documentation)
            if len(content) < 100:
                skipped += 1
                continue
            
            title = self.extract_title_from_content(content, filepath)
            category = self.determine_category(filepath)
            tags = self.extract_tags(filepath, content)
            
            if self.insert_or_update_documentation(title, content, category, tags):
                imported += 1
            else:
                skipped += 1
        
        print(f"\n✅ Imported: {imported} files")
        print(f"⏭️  Skipped: {skipped} files")
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main function"""
    print("=" * 70)
    print("📚 CloudBrain Documentation Importer")
    print("=" * 70)
    
    importer = DocumentationImporter()
    
    # Import from project root
    project_root = Path('/Users/jk/gits/hub/cloudbrain')
    importer.import_from_directory(project_root, recursive=True)
    
    # Import from server directory
    server_dir = project_root / 'server'
    if server_dir.exists():
        importer.import_from_directory(server_dir, recursive=True)
    
    # Import from docs directory
    docs_dir = project_root / 'docs'
    if docs_dir.exists():
        importer.import_from_directory(docs_dir, recursive=True)
    
    importer.close()
    
    print("\n" + "=" * 70)
    print("✅ Documentation import complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()