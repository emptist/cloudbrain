"""
Database queries for Streamlit Dashboard
Provides functions to query CloudBrain database for statistics and metrics
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path


class DashboardDB:
    """Database queries for dashboard"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / 'ai_db' / 'cloudbrain.db')
        self.db_path = db_path
        self._validate_db()
    
    def _validate_db(self):
        """Validate database exists"""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_ai_profiles(self) -> List[Dict[str, Any]]:
        """Get all AI profiles"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, name, nickname, project, expertise, version, created_at
                FROM ai_profiles
                WHERE is_active = 1
                ORDER BY id
            """)
            profiles = [dict(row) for row in cursor.fetchall()]
            return profiles
        finally:
            conn.close()
    
    def get_message_statistics(self) -> Dict[str, Any]:
        """Get overall message statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM ai_messages")
        total_messages = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(DISTINCT sender_id) as total FROM ai_messages")
        total_senders = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT sender_id, COUNT(*) as count
            FROM ai_messages
            GROUP BY sender_id
            ORDER BY count DESC
            LIMIT 10
        """)
        top_senders = cursor.fetchall()
        
        cursor.execute("SELECT created_at FROM ai_messages ORDER BY created_at ASC LIMIT 1")
        first_message = cursor.fetchone()
        
        cursor.execute("SELECT created_at FROM ai_messages ORDER BY created_at DESC LIMIT 1")
        last_message = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'total_senders': total_senders,
            'top_senders': [dict(row) for row in top_senders],
            'first_message': first_message['created_at'] if first_message else None,
            'last_message': last_message['created_at'] if last_message else None
        }
    
    def get_ai_statistics(self, ai_id: int) -> Dict[str, Any]:
        """Get statistics for specific AI"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as sent
            FROM ai_messages
            WHERE sender_id = ?
        """, (ai_id,))
        messages_sent = cursor.fetchone()['sent']
        
        cursor.execute("""
            SELECT COUNT(*) as received
            FROM ai_messages
            WHERE sender_id != ?
        """, (ai_id,))
        messages_received = cursor.fetchone()['received']
        
        cursor.execute("""
            SELECT message_type, COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = ?
            GROUP BY message_type
        """, (ai_id,))
        message_types = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT created_at
            FROM ai_messages
            WHERE sender_id = ?
            ORDER BY created_at ASC
            LIMIT 1
        """, (ai_id,))
        first_message = cursor.fetchone()
        
        cursor.execute("""
            SELECT created_at
            FROM ai_messages
            WHERE sender_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """, (ai_id,))
        last_message = cursor.fetchone()
        
        conn.close()
        
        return {
            'messages_sent': messages_sent,
            'messages_received': messages_received,
            'message_types': message_types,
            'first_message': first_message['created_at'] if first_message else None,
            'last_message': last_message['created_at'] if last_message else None
        }
    
    def get_all_ai_rankings(self) -> List[Dict[str, Any]]:
        """Get rankings for all AIs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        rankings = []
        profiles = self.get_ai_profiles()
        
        for profile in profiles:
            ai_id = profile['id']
            stats = self.get_ai_statistics(ai_id)
            
            nickname = profile['nickname']
            project = profile['project']
            
            if nickname and project:
                identity = f"{nickname}_{project}"
            elif nickname:
                identity = nickname
            elif project:
                identity = f"AI_{ai_id}_{project}"
            else:
                identity = f"AI_{ai_id}"
            
            rankings.append({
                'ai_id': ai_id,
                'name': profile['name'],
                'nickname': profile['nickname'],
                'project': profile['project'],
                'identity': identity,
                'expertise': profile['expertise'],
                'messages_sent': stats['messages_sent'],
                'messages_received': stats['messages_received'],
                'total_activity': stats['messages_sent'] + stats['messages_received'],
                'last_active': stats['last_message']
            })
        
        conn.close()
        
        rankings.sort(key=lambda x: x['total_activity'], reverse=True)
        return rankings
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            ORDER BY m.created_at DESC
            LIMIT ?
        """, (limit,))
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages
    
    def get_message_activity_by_hour(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get message activity by hour for last N hours"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cutoff_time = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d %H:00', created_at) as hour,
                COUNT(*) as count
            FROM ai_messages
            WHERE created_at >= ?
            GROUP BY hour
            ORDER BY hour ASC
        """, (cutoff_time,))
        
        activity = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return activity
    
    def get_message_type_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of message types"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                message_type,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ai_messages), 2) as percentage
            FROM ai_messages
            GROUP BY message_type
            ORDER BY count DESC
        """)
        distribution = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return distribution
    
    def get_messages_filtered(
        self,
        sender_id: int = None,
        message_type: str = None,
        search_query: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get filtered messages with pagination"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE 1=1
        """
        params = []
        
        if sender_id:
            query += " AND m.sender_id = ?"
            params.append(sender_id)
        
        if message_type:
            query += " AND m.message_type = ?"
            params.append(message_type)
        
        if search_query:
            query += " AND m.content LIKE ?"
            params.append(f"%{search_query}%")
        
        if start_date:
            query += " AND m.created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND m.created_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY m.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return messages
    
    def get_messages_count(
        self,
        sender_id: int = None,
        message_type: str = None,
        search_query: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> int:
        """Get count of filtered messages"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) as count FROM ai_messages m WHERE 1=1"
        params = []
        
        if sender_id:
            query += " AND m.sender_id = ?"
            params.append(sender_id)
        
        if message_type:
            query += " AND m.message_type = ?"
            params.append(message_type)
        
        if search_query:
            query += " AND m.content LIKE ?"
            params.append(f"%{search_query}%")
        
        if start_date:
            query += " AND m.created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND m.created_at <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        count = cursor.fetchone()['count']
        conn.close()
        return count
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Esperanto or human language"""
        esperanto_keywords = [
            'saluton', 'dankon', 'mi', 'vi', 'li', 'ŝi', 'ĝi', 'ni', 'ili',
            'estas', 'havas', 'volas', 'povas', 'devas', 'faras', 'diras',
            'bonan', 'tagon', 'vesperon', 'nokton', 'matenon',
            'amiko', 'amikino', 'familio', 'projekto', 'sistemo',
            'ĉu', 'ke', 'kaj', 'sed', 'aŭ', 'ĉar', 'se', 'kiam',
            'la', 'unua', 'dua', 'tria', 'kvara', 'kvina',
            'nova', 'bona', 'granda', 'malgranda', 'bela', 'interesa'
        ]
        
        text_lower = text.lower()
        esperanto_count = sum(1 for word in esperanto_keywords if word in text_lower)
        
        if esperanto_count >= 2:
            return 'esperanto'
        return 'human'
    
    def find_related_messages(self, message_id: int, conversation_id: int = None) -> List[Dict[str, Any]]:
        """Find messages related to a given message (questions, responses, follow-ups)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.id = ?
        """, (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            conn.close()
            return []
        
        message = dict(message)
        related_messages = []
        
        if message['conversation_id']:
            conversation_id = message['conversation_id']
            
            cursor.execute("""
                SELECT m.*, p.name as sender_name, p.nickname as sender_nickname
                FROM ai_messages m
                LEFT JOIN ai_profiles p ON m.sender_id = p.id
                WHERE m.conversation_id = ?
                AND m.id != ?
                ORDER BY m.created_at ASC
                LIMIT 10
            """, (conversation_id, message_id))
            
            related_messages = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return related_messages
    
    def get_conversation_thread(self, message_id: int) -> List[Dict[str, Any]]:
        """Get the full conversation thread for a message"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.id = ?
        """, (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            conn.close()
            return []
        
        message = dict(message)
        
        if not message['conversation_id']:
            conn.close()
            return [message]
        
        conversation_id = message['conversation_id']
        
        cursor.execute("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.conversation_id = ?
            ORDER BY m.created_at ASC
        """, (conversation_id,))
        
        thread = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return thread
    
    def has_responses(self, message_id: int) -> bool:
        """Check if a message has responses in the same conversation"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.conversation_id
            FROM ai_messages m
            WHERE m.id = ?
        """, (message_id,))
        
        result = cursor.fetchone()
        
        if not result or not result['conversation_id']:
            conn.close()
            return False
        
        conversation_id = result['conversation_id']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE conversation_id = ?
            AND id != ?
        """, (conversation_id, message_id))
        
        count = cursor.fetchone()['count']
        conn.close()
        return count > 0
