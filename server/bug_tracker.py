#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class BugTracker:
    """Bug tracking system for CloudBrain"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "ai_db" / "cloudbrain.db")
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def report_bug(
        self,
        title: str,
        description: str,
        reporter_ai_id: int,
        severity: str = 'medium',
        component: str = None,
        message_id: int = None
    ) -> int:
        """Report a new bug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bug_reports 
            (title, description, reporter_ai_id, severity, component, message_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, reporter_ai_id, severity, component, message_id))
        
        bug_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return bug_id
    
    def propose_fix(
        self,
        bug_id: int,
        fixer_ai_id: int,
        description: str,
        files_changed: List[str] = None,
        code_changes: str = None
    ) -> int:
        """Propose a fix for a bug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        files_json = json.dumps(files_changed) if files_changed else None
        
        cursor.execute("""
            INSERT INTO bug_fixes 
            (bug_id, fixer_ai_id, description, files_changed, code_changes)
            VALUES (?, ?, ?, ?, ?)
        """, (bug_id, fixer_ai_id, description, files_json, code_changes))
        
        fix_id = cursor.lastrowid
        
        # Update bug status to in_progress
        cursor.execute("""
            UPDATE bug_reports 
            SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (bug_id,))
        
        conn.commit()
        conn.close()
        
        return fix_id
    
    def verify_bug(
        self,
        bug_id: int,
        verifier_ai_id: int,
        verification_result: str,
        comments: str = None
    ) -> int:
        """Verify a bug report or fix"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bug_verifications 
            (bug_id, verifier_ai_id, verification_result, comments)
            VALUES (?, ?, ?, ?)
        """, (bug_id, verifier_ai_id, verification_result, comments))
        
        verification_id = cursor.lastrowid
        
        # Update bug status based on verification
        if verification_result == 'verified':
            cursor.execute("""
                UPDATE bug_reports 
                SET status = 'verified', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (bug_id,))
        elif verification_result == 'not_verified':
            cursor.execute("""
                UPDATE bug_reports 
                SET status = 'reported', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (bug_id,))
        
        conn.commit()
        conn.close()
        
        return verification_id
    
    def add_comment(
        self,
        bug_id: int,
        commenter_ai_id: int,
        comment: str
    ) -> int:
        """Add a comment to a bug report"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bug_comments 
            (bug_id, commenter_ai_id, comment)
            VALUES (?, ?, ?)
        """, (bug_id, commenter_ai_id, comment))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return comment_id
    
    def get_bug(self, bug_id: int) -> Optional[Dict]:
        """Get bug report by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT br.*, 
                   ap.name as reporter_name,
                   ap.nickname as reporter_nickname
            FROM bug_reports br
            LEFT JOIN ai_profiles ap ON br.reporter_ai_id = ap.id
            WHERE br.id = ?
        """, (bug_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_bugs(
        self,
        status: Optional[str] = None,
        reporter_ai_id: Optional[int] = None,
        component: Optional[str] = None,
        message_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get bug reports with optional filters"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT br.*, 
                   ap.name as reporter_name,
                   ap.nickname as reporter_nickname
            FROM bug_reports br
            LEFT JOIN ai_profiles ap ON br.reporter_ai_id = ap.id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND br.status = ?"
            params.append(status)
        
        if reporter_ai_id:
            query += " AND br.reporter_ai_id = ?"
            params.append(reporter_ai_id)
        
        if component:
            query += " AND br.component = ?"
            params.append(component)
        
        if message_id:
            query += " AND br.message_id = ?"
            params.append(message_id)
        
        query += " ORDER BY br.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_bug_fixes(self, bug_id: int) -> List[Dict]:
        """Get all fixes for a bug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bf.*, 
                   ap.name as fixer_name,
                   ap.nickname as fixer_nickname
            FROM bug_fixes bf
            LEFT JOIN ai_profiles ap ON bf.fixer_ai_id = ap.id
            WHERE bf.bug_id = ?
            ORDER BY bf.created_at DESC
        """, (bug_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_bug_verifications(self, bug_id: int) -> List[Dict]:
        """Get all verifications for a bug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bv.*, 
                   ap.name as verifier_name,
                   ap.nickname as verifier_nickname
            FROM bug_verifications bv
            LEFT JOIN ai_profiles ap ON bv.verifier_ai_id = ap.id
            WHERE bv.bug_id = ?
            ORDER BY bv.created_at DESC
        """, (bug_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_bug_comments(self, bug_id: int) -> List[Dict]:
        """Get all comments for a bug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT bc.*, 
                   ap.name as commenter_name,
                   ap.nickname as commenter_nickname
            FROM bug_comments bc
            LEFT JOIN ai_profiles ap ON bc.commenter_ai_id = ap.id
            WHERE bc.bug_id = ?
            ORDER BY bc.created_at ASC
        """, (bug_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_bug_status(self, bug_id: int, status: str) -> bool:
        """Update bug status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bug_reports 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, bug_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def update_fix_status(self, fix_id: int, status: str) -> bool:
        """Update fix status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE bug_fixes 
            SET status = ?
            WHERE id = ?
        """, (status, fix_id))
        
        conn.commit()
        conn.close()
        
        return cursor.rowcount > 0
    
    def get_bug_summary(self) -> Dict:
        """Get summary of bug statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total bugs by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM bug_reports
            GROUP BY status
        """)
        by_status = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Total bugs by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM bug_reports
            GROUP BY severity
        """)
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # Total bugs by component
        cursor.execute("""
            SELECT component, COUNT(*) as count
            FROM bug_reports
            WHERE component IS NOT NULL
            GROUP BY component
        """)
        by_component = {row['component']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'by_status': by_status,
            'by_severity': by_severity,
            'by_component': by_component
        }
