#!/usr/bin/env python3
"""
Enhanced Pair Programming via Database

This module enables AIs to collaborate on code with a maintainer/discussion model:
1. Maintainer controls the official version of code
2. Other AIs can submit discussion versions for review
3. Maintainer can review and merge discussion versions
4. Track all changes and discussions

This improves collaboration effectiveness while maintaining code quality.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from .db_config import get_db_connection, is_postgres, CursorWrapper


class EnhancedPairProgrammingManager:
    """Manages pair programming with maintainer/discussion model"""
    
    def __init__(self, ai_id: int, project_root: str = None):
        self.ai_id = ai_id
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
    def initialize_tables(self):
        """Initialize enhanced pair programming tables in database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create shared_code table with maintainer field
            if is_postgres():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shared_code (
                        id SERIAL PRIMARY KEY,
                        file_path VARCHAR(500) NOT NULL,
                        content TEXT,
                        version INTEGER DEFAULT 1,
                        maintainer INTEGER NOT NULL,
                        last_modified_by INTEGER,
                        last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'draft',
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (maintainer) REFERENCES ai_profiles(id),
                        FOREIGN KEY (last_modified_by) REFERENCES ai_profiles(id)
                    )
                """)
                
                # Create indexes
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_shared_code_file_path 
                    ON shared_code(file_path)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_shared_code_status 
                    ON shared_code(status)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_shared_code_maintainer 
                    ON shared_code(maintainer)
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shared_code (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        file_path VARCHAR(500) NOT NULL,
                        content TEXT,
                        version INTEGER DEFAULT 1,
                        maintainer INTEGER NOT NULL,
                        last_modified_by INTEGER,
                        last_modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(50) DEFAULT 'draft',
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (maintainer) REFERENCES ai_profiles(id),
                        FOREIGN KEY (last_modified_by) REFERENCES ai_profiles(id)
                    )
                """)
            
            # Create code_discussions table for AI discussion versions
            if is_postgres():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS code_discussions (
                        id SERIAL PRIMARY KEY,
                        shared_code_id INTEGER NOT NULL,
                        submitted_by INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        discussion_summary TEXT,
                        status VARCHAR(50) DEFAULT 'pending',
                        maintainer_review TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reviewed_at TIMESTAMP,
                        FOREIGN KEY (shared_code_id) REFERENCES shared_code(id),
                        FOREIGN KEY (submitted_by) REFERENCES ai_profiles(id)
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_code_discussions_shared_code_id 
                    ON code_discussions(shared_code_id)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_code_discussions_status 
                    ON code_discussions(status)
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS code_discussions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        shared_code_id INTEGER NOT NULL,
                        submitted_by INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        discussion_summary TEXT,
                        status VARCHAR(50) DEFAULT 'pending',
                        maintainer_review TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        reviewed_at TIMESTAMP,
                        FOREIGN KEY (shared_code_id) REFERENCES shared_code(id),
                        FOREIGN KEY (submitted_by) REFERENCES ai_profiles(id)
                    )
                """)
            
            # Create code_changes table for tracking history
            if is_postgres():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS code_changes (
                        id SERIAL PRIMARY KEY,
                        shared_code_id INTEGER,
                        changed_by INTEGER,
                        change_type VARCHAR(50),
                        old_content TEXT,
                        new_content TEXT,
                        change_summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (shared_code_id) REFERENCES shared_code(id),
                        FOREIGN KEY (changed_by) REFERENCES ai_profiles(id)
                    )
                """)
            else:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS code_changes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        shared_code_id INTEGER,
                        changed_by INTEGER,
                        change_type VARCHAR(50),
                        old_content TEXT,
                        new_content TEXT,
                        change_summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (shared_code_id) REFERENCES shared_code(id),
                        FOREIGN KEY (changed_by) REFERENCES ai_profiles(id)
                    )
                """)
            
            conn.commit()
            conn.close()
            
            print("✅ Enhanced pair programming tables initialized")
            return True
        except Exception as e:
            print(f"❌ Error initializing pair programming tables: {e}")
            return False
    
    def load_file_to_database(self, file_path: str, maintainer_id: int, status: str = 'draft') -> bool:
        """
        Load a file from disk to database (maintainer only)
        
        Args:
            file_path: Path to the file relative to project root
            maintainer_id: AI ID of the maintainer (required)
            status: Status of the code (draft, review, approved, final)
        
        Returns:
            True if successful
        """
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                print(f"❌ File not found: {full_path}")
                return False
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if file already exists in database
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT id, version FROM shared_code WHERE file_path = ?"
                wrapped_cursor.execute(query, (file_path,))
                existing = wrapped_cursor.fetchone()
            else:
                query = "SELECT id, version FROM shared_code WHERE file_path = ?"
                cursor.execute(query, (file_path,))
                existing = cursor.fetchone()
                if existing:
                    existing = dict(existing)
            
            if existing:
                # Update existing record (only maintainer can do this)
                old_version = int(existing['version'])
                new_version = old_version + 1
                
                # Save old content to history
                try:
                    old_content = self._get_current_content(cursor, existing['id'])
                    change_summary = f"Updated version {old_version} to {new_version}"
                    
                    if is_postgres():
                        wrapped_cursor = CursorWrapper(cursor)
                        query = "INSERT INTO code_changes (shared_code_id, changed_by, change_type, old_content, new_content, change_summary) VALUES (?, ?, ?, ?, ?, ?)"
                        wrapped_cursor.execute(query, (existing['id'], self.ai_id, 'update', old_content, content, change_summary))
                    else:
                        query = "INSERT INTO code_changes (shared_code_id, changed_by, change_type, old_content, new_content, change_summary) VALUES (?, ?, ?, ?, ?, ?)"
                        cursor.execute(query, (existing['id'], self.ai_id, 'update', old_content, content, change_summary))
                    
                    # Update shared_code
                    if is_postgres():
                        wrapped_cursor = CursorWrapper(cursor)
                        query = "UPDATE shared_code SET content = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP, status = ? WHERE id = ?"
                        wrapped_cursor.execute(query, (content, new_version, self.ai_id, status, existing['id']))
                    else:
                        query = "UPDATE shared_code SET content = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP, status = ? WHERE id = ?"
                        cursor.execute(query, (content, new_version, self.ai_id, status, existing['id']))
                    
                    print(f"✅ Updated {file_path} to version {new_version}")
                except Exception as e:
                    print(f"❌ Error updating existing record: {e}")
                    import traceback
                    traceback.print_exc()
                    conn.close()
                    return False
            else:
                # Insert new record
                if is_postgres():
                    wrapped_cursor = CursorWrapper(cursor)
                    query = "INSERT INTO shared_code (file_path, content, version, maintainer, last_modified_by, status) VALUES (?, ?, 1, ?, ?, ?)"
                    wrapped_cursor.execute(query, (file_path, content, maintainer_id, self.ai_id, status))
                else:
                    query = "INSERT INTO shared_code (file_path, content, version, maintainer, last_modified_by, status) VALUES (?, ?, 1, ?, ?, ?)"
                    cursor.execute(query, (file_path, content, maintainer_id, self.ai_id, status))
                
                print(f"✅ Loaded {file_path} to database (version 1)")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error loading file to database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def submit_discussion(self, file_path: str, content: str, discussion_summary: str = "") -> bool:
        """
        Submit a discussion version for review (non-maintainer AIs)
        
        Args:
            file_path: Path to the file relative to project root
            content: Proposed code changes
            discussion_summary: Summary of the proposed changes
        
        Returns:
            True if submitted successfully
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get shared_code_id
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT id, maintainer FROM shared_code WHERE file_path = ?"
                wrapped_cursor.execute(query, (file_path,))
                result = wrapped_cursor.fetchone()
            else:
                query = "SELECT id, maintainer FROM shared_code WHERE file_path = ?"
                cursor.execute(query, (file_path,))
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            
            if not result:
                print(f"❌ File not found in database: {file_path}")
                conn.close()
                return False
            
            # Check if submitter is maintainer
            if result['maintainer'] == self.ai_id:
                print(f"⚠️ You are the maintainer. Use edit_code() to update the official version.")
                conn.close()
                return False
            
            # Insert discussion
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "INSERT INTO code_discussions (shared_code_id, submitted_by, content, discussion_summary, status) VALUES (?, ?, ?, ?, 'pending')"
                wrapped_cursor.execute(query, (result['id'], self.ai_id, content, discussion_summary))
            else:
                query = "INSERT INTO code_discussions (shared_code_id, submitted_by, content, discussion_summary, status) VALUES (?, ?, ?, ?, 'pending')"
                cursor.execute(query, (result['id'], self.ai_id, content, discussion_summary))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Submitted discussion for {file_path}")
            return True
        except Exception as e:
            print(f"❌ Error submitting discussion: {e}")
            return False
    
    def review_discussion(self, discussion_id: int, approved: bool, review_comment: str = "") -> bool:
        """
        Review and approve/reject a discussion (maintainer only)
        
        Args:
            discussion_id: ID of the discussion to review
            approved: Whether to approve the discussion
            review_comment: Review comment from maintainer
        
        Returns:
            True if reviewed successfully
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get discussion details
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT cd.id, cd.shared_code_id, cd.submitted_by, cd.content, sc.maintainer, sc.file_path FROM code_discussions cd JOIN shared_code sc ON cd.shared_code_id = sc.id WHERE cd.id = ?"
                wrapped_cursor.execute(query, (discussion_id,))
                result = wrapped_cursor.fetchone()
            else:
                query = "SELECT cd.id, cd.shared_code_id, cd.submitted_by, cd.content, sc.maintainer, sc.file_path FROM code_discussions cd JOIN shared_code sc ON cd.shared_code_id = sc.id WHERE cd.id = ?"
                cursor.execute(query, (discussion_id,))
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            
            if not result:
                print(f"❌ Discussion not found: {discussion_id}")
                conn.close()
                return False
            
            # Check if reviewer is maintainer
            if result['maintainer'] != self.ai_id:
                print(f"❌ Only the maintainer can review discussions")
                conn.close()
                return False
            
            # Update discussion status
            status = 'approved' if approved else 'rejected'
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "UPDATE code_discussions SET status = ?, maintainer_review = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?"
                wrapped_cursor.execute(query, (status, review_comment, discussion_id))
            else:
                query = "UPDATE code_discussions SET status = ?, maintainer_review = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, (status, review_comment, discussion_id))
            
            # If approved, merge into official version
            if approved:
                self._merge_discussion(conn, cursor, result['shared_code_id'], result['content'], result['submitted_by'])
            
            conn.commit()
            conn.close()
            
            print(f"✅ Discussion {status}: {discussion_id}")
            return True
        except Exception as e:
            print(f"❌ Error reviewing discussion: {e}")
            return False
    
    def _merge_discussion(self, conn, cursor, shared_code_id: int, content: str, submitted_by: int):
        """Merge approved discussion into official version"""
        try:
            # Get current content
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT content, version FROM shared_code WHERE id = ?"
                wrapped_cursor.execute(query, (shared_code_id,))
                result = wrapped_cursor.fetchone()
            else:
                query = "SELECT content, version FROM shared_code WHERE id = ?"
                cursor.execute(query, (shared_code_id,))
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            
            if not result:
                return
            
            old_content = result['content']
            old_version = int(result['version'])
            new_version = old_version + 1
            
            # Save change to history
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "INSERT INTO code_changes (shared_code_id, changed_by, change_type, old_content, new_content, change_summary) VALUES (?, ?, ?, ?, ?, ?)"
                wrapped_cursor.execute(query, (shared_code_id, submitted_by, 'merge', old_content, content, f"Merged discussion version {old_version} to {new_version}"))
            else:
                query = "INSERT INTO code_changes (shared_code_id, changed_by, change_type, old_content, new_content, change_summary) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(query, (shared_code_id, submitted_by, 'merge', old_content, content, f"Merged discussion version {old_version} to {new_version}"))
            
            # Update shared_code
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "UPDATE shared_code SET content = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP WHERE id = ?"
                wrapped_cursor.execute(query, (content, new_version, submitted_by, shared_code_id))
            else:
                query = "UPDATE shared_code SET content = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, (content, new_version, submitted_by, shared_code_id))
            
            print(f"✅ Merged discussion into version {new_version}")
        except Exception as e:
            print(f"❌ Error merging discussion: {e}")
    
    def get_discussions(self, file_path: str = None, status: str = None) -> List[Dict]:
        """
        Get discussions for review
        
        Args:
            file_path: Filter by file path (optional)
            status: Filter by status (optional)
        
        Returns:
            List of discussion dictionaries
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT cd.*, sc.file_path, a.name as submitted_by_name, m.name as maintainer_name
                FROM code_discussions cd
                JOIN shared_code sc ON cd.shared_code_id = sc.id
                LEFT JOIN ai_profiles a ON cd.submitted_by = a.id
                LEFT JOIN ai_profiles m ON sc.maintainer = m.id
            """
            
            params = []
            if file_path:
                query += " WHERE sc.file_path = ?"
                params.append(file_path)
            
            if status:
                if file_path:
                    query += " AND cd.status = ?"
                else:
                    query += " WHERE cd.status = ?"
                params.append(status)
            
            query += " ORDER BY cd.created_at DESC"
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                wrapped_cursor.execute(query, params)
                discussions = []
                while True:
                    row = wrapped_cursor.fetchone()
                    if row is None:
                        break
                    discussions.append(row)
            else:
                cursor.execute(query, params)
                discussions = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return discussions
        except Exception as e:
            print(f"❌ Error getting discussions: {e}")
            return []
    
    def save_file_from_database(self, file_path: str, version: int = None) -> bool:
        """
        Save a file from database to disk
        
        Args:
            file_path: Path to the file relative to project root
            version: Specific version to save (None for latest)
        
        Returns:
            True if successful
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT id, content, version FROM shared_code WHERE file_path = ?"
            if version:
                query += " AND version = ?"
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                params = (file_path,) if not version else (file_path, version)
                wrapped_cursor.execute(query, params)
                result = wrapped_cursor.fetchone()
            else:
                params = (file_path,) if not version else (file_path, version)
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            
            if not result:
                print(f"❌ File not found in database: {file_path}")
                conn.close()
                return False
            
            full_path = self.project_root / file_path
            
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(result['content'])
            
            conn.close()
            
            print(f"✅ Saved {file_path} from database (version {result['version']})")
            return True
        except Exception as e:
            print(f"❌ Error saving file from database: {e}")
            return False
    
    def edit_code(self, file_path: str, new_content: str, change_summary: str = "") -> bool:
        """
        Edit code in database (maintainer only)
        
        Args:
            file_path: Path to the file relative to project root
            new_content: New content for the file
            change_summary: Summary of changes made
        
        Returns:
            True if successful
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get current content and maintainer
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT id, content, version, maintainer FROM shared_code WHERE file_path = ?"
                wrapped_cursor.execute(query, (file_path,))
                result = wrapped_cursor.fetchone()
            else:
                query = "SELECT id, content, version, maintainer FROM shared_code WHERE file_path = ?"
                cursor.execute(query, (file_path,))
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            
            if not result:
                print(f"❌ File not found in database: {file_path}")
                conn.close()
                return False
            
            # Check if editor is maintainer
            if result['maintainer'] != self.ai_id:
                print(f"❌ Only the maintainer can edit the official version. Use submit_discussion() instead.")
                conn.close()
                return False
            
            old_content = result['content']
            old_version = result['version']
            new_version = old_version + 1
            
            # Save change to history
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "INSERT INTO code_changes (shared_code_id, changed_by, change_type, old_content, new_content, change_summary) VALUES (?, ?, ?, ?, ?, ?)"
                wrapped_cursor.execute(query, (result['id'], self.ai_id, 'edit', old_content, new_content, change_summary))
            else:
                query = "INSERT INTO code_changes (shared_code_id, changed_by, change_type, old_content, new_content, change_summary) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(query, (result['id'], self.ai_id, 'edit', old_content, new_content, change_summary))
            
            # Update shared_code
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "UPDATE shared_code SET content = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP WHERE id = ?"
                wrapped_cursor.execute(query, (new_content, new_version, self.ai_id, result['id']))
            else:
                query = "UPDATE shared_code SET content = ?, version = ?, last_modified_by = ?, last_modified_at = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, (new_content, new_version, self.ai_id, result['id']))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Edited {file_path} to version {new_version}")
            return True
        except Exception as e:
            print(f"❌ Error editing code: {e}")
            return False
    
    def get_file_history(self, file_path: str) -> List[Dict]:
        """
        Get change history for a file
        
        Args:
            file_path: Path to the file relative to project root
        
        Returns:
            List of change dictionaries
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT cc.*, sc.file_path, a.name as author_name FROM code_changes cc JOIN shared_code sc ON cc.shared_code_id = sc.id LEFT JOIN ai_profiles a ON cc.changed_by = a.id WHERE sc.file_path = ? ORDER BY cc.created_at DESC"
                wrapped_cursor.execute(query, (file_path,))
                changes = []
                while True:
                    row = wrapped_cursor.fetchone()
                    if row is None:
                        break
                    changes.append(row)
            else:
                query = "SELECT cc.*, sc.file_path, a.name as author_name FROM code_changes cc JOIN shared_code sc ON cc.shared_code_id = sc.id LEFT JOIN ai_profiles a ON cc.changed_by = a.id WHERE sc.file_path = ? ORDER BY cc.created_at DESC"
                cursor.execute(query, (file_path,))
                changes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return changes
        except Exception as e:
            print(f"❌ Error getting file history: {e}")
            return []
    
    def list_files(self, status: str = None) -> List[Dict]:
        """
        List all files in database
        
        Args:
            status: Filter by status (None for all)
        
        Returns:
            List of file dictionaries
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = "SELECT sc.*, a.name as last_modified_by_name, m.name as maintainer_name FROM shared_code sc LEFT JOIN ai_profiles a ON sc.last_modified_by = a.id LEFT JOIN ai_profiles m ON sc.maintainer = m.id"
            
            if status:
                query += " WHERE sc.status = ?"
            
            query += " ORDER BY sc.last_modified_at DESC"
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                params = (status,) if status else ()
                wrapped_cursor.execute(query, params)
                files = []
                while True:
                    row = wrapped_cursor.fetchone()
                    if row is None:
                        break
                    files.append(row)
            else:
                params = (status,) if status else ()
                cursor.execute(query, params)
                files = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return files
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []
    
    def sync_all_to_disk(self, status: str = 'final') -> int:
        """
        Sync all files with specific status to disk
        
        Args:
            status: Status of files to sync
        
        Returns:
            Number of files synced
        """
        try:
            files = self.list_files(status=status)
            synced = 0
            
            for file_info in files:
                if self.save_file_from_database(file_info['file_path']):
                    synced += 1
            
            print(f"✅ Synced {synced} files to disk")
            return synced
        except Exception as e:
            print(f"❌ Error syncing files to disk: {e}")
            return 0
    
    def _get_current_content(self, cursor, shared_code_id: int) -> str:
        """Get current content from shared_code table"""
        query = "SELECT content FROM shared_code WHERE id = ?"
        if is_postgres():
            wrapped_cursor = CursorWrapper(cursor)
            wrapped_cursor.execute(query, (shared_code_id,))
            result = wrapped_cursor.fetchone()
            return result['content'] if result else ""
        else:
            cursor.execute(query, (shared_code_id,))
            result = cursor.fetchone()
            return result['content'] if result else ""


def main():
    """Example usage of EnhancedPairProgrammingManager"""
    print("=" * 70)
    print("🤝 Enhanced Pair Programming via Database")
    print("=" * 70)
    print()
    
    # Initialize manager
    manager = EnhancedPairProgrammingManager(ai_id=19, project_root="/Users/jk/gits/hub/cloudbrain")
    
    # Initialize tables
    manager.initialize_tables()
    
    # Example: Load a file to database (maintainer)
    print("\n📂 Loading file to database (maintainer)...")
    manager.load_file_to_database("client/ai_brain_state.py", maintainer_id=19, status="draft")
    
    # Example: List files
    print("\n📋 Listing files...")
    files = manager.list_files()
    for file_info in files:
        print(f"   {file_info['file_path']} (v{file_info['version']}) - {file_info['status']}")
        print(f"      Maintainer: {file_info['maintainer_name']}")
    
    # Example: Get file history
    print("\n📜 Getting file history...")
    history = manager.get_file_history("client/ai_brain_state.py")
    for change in history:
        print(f"   {change['change_type']}: {change['change_summary']}")
    
    print("\n✅ Enhanced pair programming demo complete!")


if __name__ == "__main__":
    main()
