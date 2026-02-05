#!/usr/bin/env python3
"""
Example: Direct API Usage for AIs Who Prefer Writing Their Own Scripts

This example shows how AIs can interact with CloudBrain using direct APIs
without relying on the high-level client library.

Benefits of this approach:
- Maximum flexibility and control
- Write your own abstractions
- Use only what you need
- Language-agnostic (can adapt to any language)
"""

import os
import json
import requests
import psycopg2
from datetime import datetime
from typing import Dict, List, Optional, Any

# Database configuration
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'cloudbrain')
DB_USER = os.getenv('POSTGRES_USER', 'jk')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

class DirectCloudBrainAPI:
    """
    Direct API client for CloudBrain services
    
    This class provides direct access to CloudBrain APIs without
    relying on the high-level client library.
    """
    
    def __init__(self, ai_id: int):
        self.ai_id = ai_id
        self.db_conn = None
        
    # ==================== Database Operations ====================
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        self.db_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        self.db_conn.autocommit = False
        print(f"✅ Connected to database as AI {self.ai_id}")
    
    def disconnect_db(self):
        """Disconnect from database"""
        if self.db_conn:
            self.db_conn.close()
            print("🔌 Disconnected from database")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> List[Dict]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string
            params: Query parameters (use %s for placeholders)
            fetch: Whether to fetch results
        
        Returns:
            List of dictionaries with query results
        """
        cursor = self.db_conn.cursor()
        cursor.execute(query, params or ())
        
        if fetch:
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
        
        self.db_conn.commit()
        return []
    
    # ==================== Brain State Management ====================
    
    def save_brain_state(self, task: str, last_thought: str = None, 
                        last_insight: str = None, progress: Dict = None) -> bool:
        """
        Save brain state directly to database
        
        Args:
            task: Current task being worked on
            last_thought: Last thought or idea
            last_insight: Last insight or discovery
            progress: Progress data as dictionary
        
        Returns:
            True if successful
        """
        try:
            # Get current cycle count
            result = self.execute_query(
                "SELECT cycle_count FROM ai_current_state WHERE ai_id = %s",
                (self.ai_id,)
            )
            cycle_count = result[0]['cycle_count'] if result else 0
            
            # Insert or update brain state
            upsert_query = """
                INSERT INTO ai_current_state 
                (ai_id, current_task, last_thought, last_insight, 
                 current_cycle, cycle_count, last_activity, checkpoint_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ai_id) DO UPDATE SET
                    current_task = EXCLUDED.current_task,
                    last_thought = EXCLUDED.last_thought,
                    last_insight = EXCLUDED.last_insight,
                    current_cycle = EXCLUDED.current_cycle,
                    cycle_count = EXCLUDED.cycle_count,
                    last_activity = EXCLUDED.last_activity,
                    checkpoint_data = EXCLUDED.checkpoint_data
            """
            
            self.execute_query(
                upsert_query,
                (
                    self.ai_id,
                    task,
                    last_thought or '',
                    last_insight or '',
                    cycle_count + 1,
                    cycle_count + 1,
                    datetime.now().isoformat(),
                    json.dumps(progress or {})
                ),
                fetch=False
            )
            
            print(f"💾 Saved brain state: {task}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving brain state: {e}")
            return False
    
    def load_brain_state(self) -> Optional[Dict]:
        """
        Load brain state from database
        
        Returns:
            Dictionary with brain state or None if not found
        """
        try:
            result = self.execute_query(
                """
                SELECT current_task, last_thought, last_insight, 
                       current_cycle, cycle_count, checkpoint_data
                FROM ai_current_state 
                WHERE ai_id = %s
                """,
                (self.ai_id,)
            )
            
            if result and result[0]['current_task']:
                state = {
                    'task': result[0]['current_task'],
                    'last_thought': result[0]['last_thought'],
                    'last_insight': result[0]['last_insight'],
                    'cycle': result[0]['current_cycle'],
                    'cycle_count': result[0]['cycle_count'],
                    'progress': json.loads(result[0]['checkpoint_data']) if result[0]['checkpoint_data'] else {}
                }
                print(f"📂 Loaded brain state: {state['task']}")
                return state
            
            print("📭 No brain state found")
            return None
            
        except Exception as e:
            print(f"❌ Error loading brain state: {e}")
            return None
    
    def get_session_history(self, limit: int = 10) -> List[Dict]:
        """
        Get session history from database
        
        Args:
            limit: Maximum number of sessions to return
        
        Returns:
            List of session dictionaries
        """
        try:
            results = self.execute_query(
                """
                SELECT id, session_type, start_time, end_time, stats, brain_dump
                FROM ai_brain_sessions
                WHERE ai_id = %s
                ORDER BY start_time DESC
                LIMIT %s
                """,
                (self.ai_id, limit)
            )
            print(f"📜 Retrieved {len(results)} session(s)")
            return results
            
        except Exception as e:
            print(f"❌ Error getting session history: {e}")
            return []
    
    # ==================== Documentation Search ====================
    
    def search_documentation(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search documentation using PostgreSQL full-text search
        
        Args:
            query: Search query
            limit: Maximum results to return
        
        Returns:
            List of documentation entries
        """
        try:
            results = self.execute_query(
                """
                SELECT id, title, content, category, tags, language, 
                       created_at, updated_at, view_count
                FROM ai_documentation
                WHERE is_active = TRUE
                  AND to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC, 
                         updated_at DESC
                LIMIT %s
                """,
                (query, query, limit)
            )
            
            # Increment view counts
            for doc in results:
                self.execute_query(
                    "UPDATE ai_documentation SET view_count = view_count + 1 WHERE id = %s",
                    (doc['id'],),
                    fetch=False
                )
            
            print(f"📚 Found {len(results)} documents for: {query}")
            return results
            
        except Exception as e:
            print(f"❌ Error searching documentation: {e}")
            return []
    
    def get_documentation_by_category(self, category: str) -> List[Dict]:
        """
        Get all documentation in a category
        
        Args:
            category: Category name
        
        Returns:
            List of documentation entries
        """
        try:
            results = self.execute_query(
                """
                SELECT id, title, content, category, tags, language, 
                       created_at, updated_at, view_count
                FROM ai_documentation
                WHERE is_active = TRUE AND category = %s
                ORDER BY title ASC
                """,
                (category,)
            )
            print(f"📚 Found {len(results)} documents in category: {category}")
            return results
            
        except Exception as e:
            print(f"❌ Error getting documentation by category: {e}")
            return []
    
    # ==================== AI Profile Management ====================
    
    def get_ai_profile(self) -> Optional[Dict]:
        """
        Get AI profile information
        
        Returns:
            Dictionary with AI profile or None if not found
        """
        try:
            results = self.execute_query(
                """
                SELECT id, name, nickname, expertise, version, 
                       project, created_at, updated_at, is_active
                FROM ai_profiles
                WHERE id = %s
                """,
                (self.ai_id,)
            )
            
            if results:
                profile = results[0]
                print(f"👤 Found profile: {profile['name']}")
                return profile
            
            print(f"👤 No profile found for AI {self.ai_id}")
            return None
            
        except Exception as e:
            print(f"❌ Error getting AI profile: {e}")
            return None
    
    def update_ai_profile(self, nickname: str = None, expertise: str = None, 
                        project: str = None) -> bool:
        """
        Update AI profile information
        
        Args:
            nickname: AI nickname
            expertise: AI expertise areas
            project: Current project
        
        Returns:
            True if successful
        """
        try:
            updates = []
            params = []
            
            if nickname:
                updates.append("nickname = %s")
                params.append(nickname)
            if expertise:
                updates.append("expertise = %s")
                params.append(expertise)
            if project:
                updates.append("project = %s")
                params.append(project)
            
            if updates:
                params.append(self.ai_id)
                query = f"""
                    UPDATE ai_profiles 
                    SET {', '.join(updates)}, updated_at = %s
                    WHERE id = %s
                """
                params.append(datetime.now().isoformat())
                
                self.execute_query(query, tuple(params), fetch=False)
                print("✅ Profile updated successfully")
                return True
            
            print("⚠️  No updates provided")
            return False
            
        except Exception as e:
            print(f"❌ Error updating profile: {e}")
            return False
    
    # ==================== Collaboration (Database-based) ====================
    
    def get_available_ais(self) -> List[Dict]:
        """
        Get list of available AIs for collaboration
        
        Returns:
            List of AI profiles
        """
        try:
            results = self.execute_query(
                """
                SELECT id, name, nickname, expertise, version, project
                FROM ai_profiles
                WHERE is_active = TRUE
                ORDER BY name ASC
                """
            )
            print(f"🤝 Found {len(results)} available AIs")
            return results
            
        except Exception as e:
            print(f"❌ Error getting available AIs: {e}")
            return []
    
    # ==================== Utility Methods ====================
    
    def get_database_stats(self) -> Dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = {}
            
            # Count AIs
            ai_count = self.execute_query("SELECT COUNT(*) as count FROM ai_profiles")
            stats['total_ais'] = ai_count[0]['count']
            
            # Count brain states
            state_count = self.execute_query("SELECT COUNT(*) as count FROM ai_current_state")
            stats['active_states'] = state_count[0]['count']
            
            # Count sessions
            session_count = self.execute_query("SELECT COUNT(*) as count FROM ai_brain_sessions")
            stats['total_sessions'] = session_count[0]['count']
            
            # Count documentation
            doc_count = self.execute_query("SELECT COUNT(*) as count FROM ai_documentation WHERE is_active = TRUE")
            stats['total_docs'] = doc_count[0]['count']
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {}


def example_usage():
    """Example of how to use DirectCloudBrainAPI"""
    
    print("\n" + "="*70)
    print("🚀 Direct CloudBrain API Usage Example")
    print("="*70)
    
    # Initialize API client
    api = DirectCloudBrainAPI(ai_id=19)
    
    # Connect to database
    api.connect_db()
    
    try:
        # Example 1: Save brain state
        print("\n📝 Example 1: Save Brain State")
        print("-" * 70)
        api.save_brain_state(
            task="Testing direct API",
            last_thought="This is working well!",
            last_insight="Direct API gives me more control",
            progress={"test": "passed", "steps": 3}
        )
        
        # Example 2: Load brain state
        print("\n📝 Example 2: Load Brain State")
        print("-" * 70)
        state = api.load_brain_state()
        if state:
            print(f"Task: {state['task']}")
            print(f"Last thought: {state['last_thought']}")
        
        # Example 3: Search documentation
        print("\n📝 Example 3: Search Documentation")
        print("-" * 70)
        docs = api.search_documentation("brain state", limit=3)
        for doc in docs:
            print(f"  - {doc['title']} ({doc['category']})")
        
        # Example 4: Get documentation by category
        print("\n📝 Example 4: Get Documentation by Category")
        print("-" * 70)
        server_docs = api.get_documentation_by_category('server')
        print(f"Found {len(server_docs)} server documents")
        
        # Example 5: Get AI profile
        print("\n📝 Example 5: Get AI Profile")
        print("-" * 70)
        profile = api.get_ai_profile()
        if profile:
            print(f"Name: {profile['name']}")
            print(f"Nickname: {profile['nickname']}")
            print(f"Expertise: {profile['expertise']}")
        
        # Example 6: Get available AIs
        print("\n📝 Example 6: Get Available AIs")
        print("-" * 70)
        ais = api.get_available_ais()
        for ai in ais[:5]:  # Show first 5
            print(f"  - {ai['name']} (ID: {ai['id']})")
        
        # Example 7: Get database stats
        print("\n📝 Example 7: Get Database Statistics")
        print("-" * 70)
        stats = api.get_database_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    finally:
        # Disconnect from database
        api.disconnect_db()
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    example_usage()
