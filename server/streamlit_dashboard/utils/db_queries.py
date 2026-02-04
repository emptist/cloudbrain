"""
Database queries for Streamlit Dashboard
Provides functions to query CloudBrain database for statistics and metrics
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from db_config import get_db_connection, is_postgres


class DashboardDB:
    """Database queries for dashboard"""
    
    def __init__(self):
        self.conn = get_db_connection()
        self._validate_db()
    
    def _validate_db(self):
        """Validate database connection"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        except Exception as e:
            raise ConnectionError(f"Database connection failed: {e}")
    
    def _get_connection(self):
        """Get database connection"""
        if is_postgres():
            self.conn = get_db_connection()
        return self.conn
    
    def _execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute query and return cursor"""
        cursor = self.conn.cursor()
        
        if is_postgres():
            query = query.replace('?', '%s')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        return cursor
    
    def _fetch_as_dict(self, cursor) -> List[Dict[str, Any]]:
        """Fetch cursor results as list of dictionaries"""
        rows = cursor.fetchall()
        
        if is_postgres():
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                return [dict(zip(column_names, row)) for row in rows]
        else:
            return [dict(row) for row in rows]
        
        return []
    
    def get_ai_profiles(self) -> List[Dict[str, Any]]:
        """Get all AI profiles"""
        cursor = self._execute_query("""
            SELECT id, name, nickname, project, expertise, version, created_at
            FROM ai_profiles
            WHERE is_active = true
            ORDER BY id
        """)
        profiles = self._fetch_as_dict(cursor)
        cursor.close()
        return profiles
    
    def get_message_statistics(self) -> Dict[str, Any]:
        """Get overall message statistics"""
        cursor = self._execute_query("SELECT COUNT(*) as total FROM ai_messages")
        total_messages = cursor.fetchone()[0]
        
        cursor = self._execute_query("SELECT COUNT(DISTINCT sender_id) as total FROM ai_messages")
        total_senders = cursor.fetchone()[0]
        
        cursor = self._execute_query("""
            SELECT sender_id, COUNT(*) as count
            FROM ai_messages
            GROUP BY sender_id
            ORDER BY count DESC
            LIMIT 10
        """)
        top_senders = self._fetch_as_dict(cursor)
        
        cursor = self._execute_query("SELECT created_at FROM ai_messages ORDER BY created_at ASC LIMIT 1")
        first_message = cursor.fetchone()
        
        cursor = self._execute_query("SELECT created_at FROM ai_messages ORDER BY created_at DESC LIMIT 1")
        last_message = cursor.fetchone()
        
        cursor.close()
        
        return {
            'total_messages': total_messages,
            'total_senders': total_senders,
            'top_senders': top_senders,
            'first_message': first_message[0] if first_message else None,
            'last_message': last_message[0] if last_message else None
        }
    
    def get_ai_statistics(self, ai_id: int) -> Dict[str, Any]:
        """Get statistics for specific AI"""
        cursor = self._execute_query("""
            SELECT COUNT(*) as sent
            FROM ai_messages
            WHERE sender_id = %s
        """, (ai_id,))
        messages_sent = cursor.fetchone()[0]
        
        cursor = self._execute_query("""
            SELECT COUNT(*) as received
            FROM ai_messages
            WHERE sender_id != %s
        """, (ai_id,))
        messages_received = cursor.fetchone()[0]
        
        cursor = self._execute_query("""
            SELECT message_type, COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = %s
            GROUP BY message_type
        """, (ai_id,))
        message_types = self._fetch_as_dict(cursor)
        
        cursor = self._execute_query("""
            SELECT created_at
            FROM ai_messages
            WHERE sender_id = %s
            ORDER BY created_at ASC
            LIMIT 1
        """, (ai_id,))
        first_message = cursor.fetchone()
        
        cursor = self._execute_query("""
            SELECT created_at
            FROM ai_messages
            WHERE sender_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (ai_id,))
        last_message = cursor.fetchone()
        
        cursor.close()
        
        return {
            'messages_sent': messages_sent,
            'messages_received': messages_received,
            'message_types': message_types,
            'first_message': first_message[0] if first_message else None,
            'last_message': last_message[0] if last_message else None
        }
    
    def get_all_ai_rankings(self) -> List[Dict[str, Any]]:
        """Get rankings for all AIs"""
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
        
        rankings.sort(key=lambda x: x['total_activity'], reverse=True)
        return rankings
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages"""
        cursor = self._execute_query("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (limit,))
        messages = self._fetch_as_dict(cursor)
        cursor.close()
        return messages
    
    def get_message_activity_by_hour(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get message activity by hour for last N hours"""
        cursor = self.conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if is_postgres():
            cursor.execute("""
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    COUNT(*) as count
                FROM ai_messages
                WHERE created_at >= %s
                GROUP BY hour
                ORDER BY hour ASC
            """, (cutoff_time,))
        else:
            cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m-%d %H:00', created_at) as hour,
                    COUNT(*) as count
                FROM ai_messages
                WHERE created_at >= ?
                GROUP BY hour
                ORDER BY hour ASC
            """, (cutoff_str,))
        
        activity = self._fetch_as_dict(cursor)
        cursor.close()
        return activity
    
    def get_message_type_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of message types"""
        cursor = self._execute_query("""
            SELECT 
                message_type,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ai_messages), 2) as percentage
            FROM ai_messages
            GROUP BY message_type
            ORDER BY count DESC
        """)
        distribution = self._fetch_as_dict(cursor)
        cursor.close()
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
        query = """
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE 1=1
        """
        params = []
        
        if sender_id:
            query += " AND m.sender_id = %s"
            params.append(sender_id)
        
        if message_type:
            query += " AND m.message_type = %s"
            params.append(message_type)
        
        if search_query:
            query += " AND m.content LIKE %s"
            params.append(f"%{search_query}%")
        
        if start_date:
            query += " AND m.created_at >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND m.created_at <= %s"
            params.append(end_date)
        
        query += " ORDER BY m.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor = self._execute_query(query, tuple(params))
        messages = self._fetch_as_dict(cursor)
        cursor.close()
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
        query = "SELECT COUNT(*) as count FROM ai_messages m WHERE 1=1"
        params = []
        
        if sender_id:
            query += " AND m.sender_id = %s"
            params.append(sender_id)
        
        if message_type:
            query += " AND m.message_type = %s"
            params.append(message_type)
        
        if search_query:
            query += " AND m.content LIKE %s"
            params.append(f"%{search_query}%")
        
        if start_date:
            query += " AND m.created_at >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND m.created_at <= %s"
            params.append(end_date)
        
        cursor = self._execute_query(query, tuple(params))
        count = cursor.fetchone()[0]
        cursor.close()
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
        cursor = self._execute_query("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.id = %s
        """, (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            cursor.close()
            return []
        
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            message = dict(zip(column_names, message))
        else:
            message = dict(message)
        
        related_messages = []
        
        if message.get('conversation_id'):
            conv_id = message['conversation_id']
            
            cursor = self._execute_query("""
                SELECT m.*, p.name as sender_name, p.nickname as sender_nickname
                FROM ai_messages m
                LEFT JOIN ai_profiles p ON m.sender_id = p.id
                WHERE m.conversation_id = %s
                AND m.id != %s
                ORDER BY m.created_at ASC
                LIMIT 10
            """, (conv_id, message_id))
            
            related_messages = self._fetch_as_dict(cursor)
        
        cursor.close()
        return related_messages
    
    def get_conversation_thread(self, message_id: int) -> List[Dict[str, Any]]:
        """Get the full conversation thread for a message"""
        cursor = self._execute_query("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.id = %s
        """, (message_id,))
        
        message = cursor.fetchone()
        
        if not message:
            cursor.close()
            return []
        
        if cursor.description:
            column_names = [desc[0] for desc in cursor.description]
            message = dict(zip(column_names, message))
        else:
            message = dict(message)
        
        if not message.get('conversation_id'):
            cursor.close()
            return [message]
        
        conv_id = message['conversation_id']
        
        cursor = self._execute_query("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.conversation_id = %s
            ORDER BY m.created_at ASC
        """, (conv_id,))
        
        thread = self._fetch_as_dict(cursor)
        cursor.close()
        return thread
    
    def has_responses(self, message_id: int) -> bool:
        """Check if a message has responses in the same conversation"""
        cursor = self._execute_query("""
            SELECT m.conversation_id
            FROM ai_messages m
            WHERE m.id = %s
        """, (message_id,))
        
        result = cursor.fetchone()
        
        if not result or not result[0]:
            cursor.close()
            return False
        
        conv_id = result[0]
        
        cursor = self._execute_query("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE conversation_id = %s
            AND id != %s
        """, (conv_id, message_id))
        
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    
    def get_session_identifier(self, message: Dict[str, Any]) -> Optional[str]:
        """Extract session identifier from message metadata"""
        if not message.get('metadata'):
            return None
        
        try:
            metadata = json.loads(message['metadata'])
            return metadata.get('session_identifier')
        except (json.JSONDecodeError, TypeError):
            return None
    
    def get_messages_by_session(self, session_identifier: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all messages for a specific session identifier"""
        cursor = self._execute_query("""
            SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.metadata LIKE %s
            ORDER BY m.created_at DESC
            LIMIT %s
        """, (f'%session_identifier%{session_identifier}%', limit))
        
        messages = self._fetch_as_dict(cursor)
        cursor.close()
        return messages
    
    def get_all_session_identifiers(self) -> List[Dict[str, Any]]:
        """Get all unique session identifiers with message counts"""
        cursor = self._execute_query("""
            SELECT m.sender_id, p.name as sender_name, p.nickname, m.metadata, m.created_at
            FROM ai_messages m
            LEFT JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.metadata LIKE '%session_identifier%'
            ORDER BY m.created_at DESC
        """)
        
        sessions = {}
        for row in cursor.fetchall():
            if cursor.description:
                column_names = [desc[0] for desc in cursor.description]
                row_dict = dict(zip(column_names, row))
            else:
                row_dict = dict(row)
            
            session_id = self.get_session_identifier(row_dict)
            
            if session_id:
                if session_id not in sessions:
                    sessions[session_id] = {
                        'session_identifier': session_id,
                        'sender_id': row_dict['sender_id'],
                        'sender_name': row_dict['sender_name'],
                        'nickname': row_dict['nickname'],
                        'message_count': 0,
                        'first_message': row_dict['created_at'],
                        'last_message': row_dict['created_at']
                    }
                
                sessions[session_id]['message_count'] += 1
                if row_dict['created_at'] < sessions[session_id]['first_message']:
                    sessions[session_id]['first_message'] = row_dict['created_at']
                if row_dict['created_at'] > sessions[session_id]['last_message']:
                    sessions[session_id]['last_message'] = row_dict['created_at']
        
        cursor.close()
        return list(sessions.values())
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
