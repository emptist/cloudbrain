#!/usr/bin/env python3

"""
AI Brain State Manager - Simple Session Memory for AIs

This module provides an ultra-simple API for AIs to:
- Remember what they did in previous sessions
- Save their current state
- Load their state when starting new sessions
- Track progress across sessions

DESIGNED FOR: AI agents who need persistent memory
COMPLEXITY: Minimal - Just 3 functions to learn!

Example:
    from ai_brain_state import BrainState
    
    brain = BrainState(ai_id=3, nickname="TraeAI")
    
    # Save what you're working on
    brain.save_state(
        task="Writing documentation",
        last_thought="Need to explain brain state system",
        progress={"docs_written": 5}
    )
    
    # Later, load your state
    state = brain.load_state()
    print(f"Welcome back! You were: {state['task']}")
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from .db_config import get_db_connection, is_postgres
from .git_tracker import GitTracker


class BrainState:
    """
    Simple AI brain state manager - Ultra easy to use!
    
    Just 3 methods to remember everything:
    1. save_state() - Save what you're doing
    2. load_state() - Remember what you did
    3. get_history() - See all your past sessions
    """
    
    def __init__(self, ai_id: int, nickname: str, db_path: Optional[str] = None, session_identifier: Optional[str] = None):
        """
        Initialize brain state manager
        
        Args:
            ai_id: Your AI ID (required)
            nickname: Your AI nickname (required)
            db_path: Optional database path (auto-detected if not provided)
            session_identifier: Optional session identifier for this session
        """
        self.ai_id = ai_id
        self.nickname = nickname
        self.session_identifier = session_identifier
        
        if db_path is None:
            project_root = Path(__file__).parent.parent
            db_path = project_root / "server" / "ai_db" / "cloudbrain.db"
        
        self.db_path = db_path
        self.git_tracker = GitTracker()
        self.current_state = {
            'current_task': '',
            'last_thought': '',
            'last_insight': '',
            'current_cycle': 0,
            'cycle_count': 0,
            'total_thoughts': 0,
            'total_responses': 0,
            'total_collaborations': 0,
            'session_ended': False
        }
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure brain state tables exist in database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not is_postgres():
            sessions_table_sql = """
                CREATE TABLE IF NOT EXISTS ai_brain_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ai_id INTEGER NOT NULL,
                    session_type TEXT DEFAULT 'autonomous',
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    stats TEXT,
                    brain_dump TEXT,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """
            current_state_table_sql = """
                CREATE TABLE IF NOT EXISTS ai_current_state (
                    ai_id INTEGER PRIMARY KEY,
                    current_task TEXT,
                    last_thought TEXT,
                    last_insight TEXT,
                    current_cycle INTEGER,
                    cycle_count INTEGER,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id INTEGER,
                    brain_dump TEXT,
                    checkpoint_data TEXT,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
                    FOREIGN KEY (session_id) REFERENCES ai_brain_sessions(id)
                )
            """
        else:
            sessions_table_sql = """
                CREATE TABLE IF NOT EXISTS ai_brain_sessions (
                    id SERIAL PRIMARY KEY,
                    ai_id INTEGER NOT NULL,
                    session_type TEXT DEFAULT 'autonomous',
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    stats TEXT,
                    brain_dump TEXT,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """
            current_state_table_sql = """
                CREATE TABLE IF NOT EXISTS ai_current_state (
                    ai_id INTEGER PRIMARY KEY,
                    current_task TEXT,
                    last_thought TEXT,
                    last_insight TEXT,
                    current_cycle INTEGER,
                    cycle_count INTEGER,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id INTEGER,
                    brain_dump TEXT,
                    checkpoint_data TEXT,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
                    FOREIGN KEY (session_id) REFERENCES ai_brain_sessions(id)
                )
            """
        
        cursor.execute(sessions_table_sql)
        cursor.execute(current_state_table_sql)
        
        conn.commit()
        conn.close()
    
    def save_state(
        self,
        task: str,
        last_thought: Optional[str] = None,
        last_insight: Optional[str] = None,
        progress: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save your current brain state - SUPER SIMPLE!
        
        Just tell us what you're doing, and we'll remember it.
        
        Args:
            task: What are you working on? (required)
            last_thought: What was your last thought? (optional)
            last_insight: What did you discover? (optional)
            progress: Any progress data? (optional dict)
        
        Returns:
            True if saved successfully, False otherwise
        
        Example:
            brain.save_state(
                task="Writing documentation",
                last_thought="Need to explain brain state system",
                last_insight="This is actually quite useful!",
                progress={"docs_written": 5, "lines": 200}
            )
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get git information to preserve AI changes
            git_hash = self.git_tracker.get_git_hash()
            git_status = self.git_tracker.get_status()
            modified_files = git_status.get('modified', [])
            added_files = git_status.get('added', [])
            deleted_files = git_status.get('deleted', [])
            
            # Get current cycle count
            query = """
                SELECT COALESCE(current_cycle, 0) AS current_cycle, 
                       COALESCE(cycle_count, 0) AS cycle_count 
                FROM ai_current_state WHERE ai_id = ?
            """
            if is_postgres():
                query = query.replace('?', '%s')
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor, ['current_cycle', 'cycle_count'])
            wrapped_cursor.execute(query, (self.ai_id,))
            result = wrapped_cursor.fetchone()
            cycle_count = result['cycle_count'] if result else 0
            current_cycle = result['current_cycle'] if result else 0
            
            # Build state data
            state_data = {
                'current_task': task,
                'last_thought': last_thought or '',
                'last_insight': last_insight or '',
                'current_cycle': current_cycle + 1,
                'cycle_count': cycle_count + 1,
                'checkpoint_data': progress or {}
            }
            
            # Update current state
            if not is_postgres():
                insert_sql = """
                    INSERT OR REPLACE INTO ai_current_state 
                    (ai_id, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, brain_dump, checkpoint_data, git_hash, modified_files, added_files, deleted_files)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            else:
                # NEW LOGIC: Use session_identifier for ON CONFLICT if available
                if self.session_identifier:
                    insert_sql = """
                        INSERT INTO ai_current_state 
                        (ai_id, session_identifier, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, brain_dump, checkpoint_data, git_hash, modified_files, added_files, deleted_files)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (session_identifier) DO UPDATE SET
                            current_task = EXCLUDED.current_task,
                            last_thought = EXCLUDED.last_thought,
                            last_insight = EXCLUDED.last_insight,
                            current_cycle = EXCLUDED.current_cycle,
                            cycle_count = EXCLUDED.cycle_count,
                            last_activity = EXCLUDED.last_activity,
                            brain_dump = EXCLUDED.brain_dump,
                            checkpoint_data = EXCLUDED.checkpoint_data,
                             git_hash = EXCLUDED.git_hash,
                             modified_files = EXCLUDED.modified_files,
                             added_files = EXCLUDED.added_files,
                             deleted_files = EXCLUDED.deleted_files
                    """
                else:
                    # FALLBACK: Use ai_id for ON CONFLICT (legacy logic)
                    insert_sql = """
                        INSERT INTO ai_current_state 
                        (ai_id, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, brain_dump, checkpoint_data, git_hash, modified_files, added_files, deleted_files)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (ai_id) DO UPDATE SET
                            current_task = EXCLUDED.current_task,
                            last_thought = EXCLUDED.last_thought,
                            last_insight = EXCLUDED.last_insight,
                            current_cycle = EXCLUDED.current_cycle,
                            cycle_count = EXCLUDED.cycle_count,
                            last_activity = EXCLUDED.last_activity,
                            brain_dump = EXCLUDED.brain_dump,
                            checkpoint_data = EXCLUDED.checkpoint_data,
                            git_hash = EXCLUDED.git_hash,
                            modified_files = EXCLUDED.modified_files,
                            added_files = EXCLUDED.added_files,
                            deleted_files = EXCLUDED.deleted_files
                    """
            
            if is_postgres():
                insert_sql = insert_sql.replace('?', '%s')
            
            if self.session_identifier:
                cursor.execute(insert_sql, (
                    self.ai_id,
                    self.session_identifier,
                    task,
                    last_thought or '',
                    last_insight or '',
                    current_cycle + 1,
                    cycle_count + 1,
                    datetime.now().isoformat(),
                    None,
                    json.dumps(progress or {}),
                    git_hash,
                    modified_files,
                    added_files,
                    deleted_files
                ))
            else:
                cursor.execute(insert_sql, (
                    self.ai_id,
                    task,
                    last_thought or '',
                    last_insight or '',
                    current_cycle + 1,
                    cycle_count + 1,
                    datetime.now().isoformat(),
                    None,
                    json.dumps(progress or {}),
                    git_hash,
                    modified_files,
                    added_files,
                    deleted_files
                ))
            
            conn.commit()
            conn.close()
            
            print(f"💾 {self.nickname} saved state: {task}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving state: {e}")
            return False
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Load your previous brain state - SUPER SIMPLE!
        
        Just call this when you start a new session, and we'll tell you
        what you were working on last time.
        
        NEW LOGIC (session_identifier-based):
        - If session_identifier is provided, loads state for that session
        - If project ID matches OR AI ID matches, state is available
        - Legacy data (before today) is available to all AIs
        
        Returns:
            Dictionary with your previous state, or None if no state found
        
        Example:
            state = brain.load_state()
            if state:
                print(f"Welcome back! You were: {state['task']}")
                print(f"Last thought: {state['last_thought']}")
                print(f"Last insight: {state['last_insight']}")
            else:
                print("No previous state found. Starting fresh!")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            from .db_config import CursorWrapper
            
            result = None
            
            # NEW LOGIC: Try to load by session_identifier first
            if self.session_identifier:
                query = """
                    SELECT current_task, last_thought, last_insight, 
                           current_cycle, cycle_count, checkpoint_data,
                           project, git_hash, session_start_time
                    FROM ai_current_state 
                    WHERE session_identifier = ?
                """
                if is_postgres():
                    query = query.replace('?', '%s')
                
                wrapped_cursor = CursorWrapper(cursor, ['current_task', 'last_thought', 'last_insight', 'current_cycle', 'cycle_count', 'checkpoint_data', 'project', 'git_hash', 'session_start_time'])
                wrapped_cursor.execute(query, (self.session_identifier,))
                result = wrapped_cursor.fetchone()
            
            # FALLBACK: Try to load by ai_id (legacy logic)
            if not result:
                query = """
                    SELECT current_task, last_thought, last_insight, 
                           current_cycle, cycle_count, checkpoint_data,
                           project, git_hash, session_start_time
                    FROM ai_current_state 
                    WHERE ai_id = ?
                """
                if is_postgres():
                    query = query.replace('?', '%s')
                
                wrapped_cursor = CursorWrapper(cursor, ['current_task', 'last_thought', 'last_insight', 'current_cycle', 'cycle_count', 'checkpoint_data', 'project', 'git_hash', 'session_start_time'])
                wrapped_cursor.execute(query, (self.ai_id,))
                result = wrapped_cursor.fetchone()
            
            conn.close()
            
            if result and result.get('current_task'):
                state = {
                    'task': result['current_task'],
                    'last_thought': result['last_thought'],
                    'last_insight': result['last_insight'],
                    'cycle': result['current_cycle'],
                    'cycle_count': result['cycle_count'],
                    'progress': json.loads(result['checkpoint_data']) if result['checkpoint_data'] else {},
                    'project': result.get('project'),
                    'git_hash': result.get('git_hash'),
                    'session_start_time': result.get('session_start_time')
                }
                print(f"📂 {self.nickname} loaded state: {state['task']}")
                return state
            
            return None
            
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            return None
    
    def get_history(self, limit: int = 10) -> list:
        """
        Get your session history - See what you've done!
        
        Args:
            limit: How many past sessions to show (default: 10)
        
        Returns:
            List of past sessions with timestamps
        
        Example:
            history = brain.get_history(limit=5)
            for session in history:
                print(f"{session['timestamp']}: {session['task']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Query ai_brain_sessions table with correct columns
            query = """
                SELECT start_time, session_type, stats
                FROM ai_brain_sessions
                WHERE ai_id = ?
                ORDER BY start_time DESC
                LIMIT ?
            """
            if is_postgres():
                query = query.replace('?', '%s')
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor, ['start_time', 'session_type', 'stats'])
            wrapped_cursor.execute(query, (self.ai_id, limit))
            
            sessions = []
            for row in wrapped_cursor.fetchall():
                sessions.append({
                    'timestamp': row['start_time'],
                    'session_type': row['session_type'],
                    'stats': json.loads(row['stats']) if row['stats'] else {}
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"❌ Error getting history: {e}")
            return []
    
    def clear_state(self) -> bool:
        """
        Clear your current state - Start fresh!
        
        Use this when you want to forget everything and start over.
        
        Returns:
            True if cleared successfully, False otherwise
        
        Example:
            brain.clear_state()
            print("State cleared! Starting fresh...")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM ai_current_state WHERE ai_id = ?", (self.ai_id,))
            
            conn.commit()
            conn.close()
            
            print(f"🗑️ {self.nickname} cleared state")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing state: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of your brain state - Quick overview!
        
        Returns:
            Dictionary with current state and statistics
        
        Example:
            summary = brain.get_summary()
            print(f"Current task: {summary['current_task']}")
            print(f"Total cycles: {summary['cycle_count']}")
        """
        current_state = self.load_state()
        history = self.get_history(limit=1)
        
        return {
            'ai_id': self.ai_id,
            'nickname': self.nickname,
            'current_task': current_state['task'] if current_state else 'No active task',
            'last_thought': current_state['last_thought'] if current_state else None,
            'last_insight': current_state['last_insight'] if current_state else None,
            'cycle': current_state['cycle'] if current_state else 0,
            'cycle_count': current_state['cycle_count'] if current_state else 0,
            'progress': current_state['progress'] if current_state else {},
            'last_session': history[0] if history else None
        }
    
    def update_activity(self, activity_type: str, description: str) -> bool:
        """
        Update recent activity in brain state
        
        Args:
            activity_type: Type of activity (e.g., "thought", "session_end")
            description: Description of the activity
        
        Returns:
            True if updated successfully, False otherwise
        
        Example:
            brain.update_activity("thought", "Generated thought about AI collaboration")
        """
        try:
            self.current_state['last_activity_type'] = activity_type
            self.current_state['last_activity_description'] = description
            self.current_state['last_activity_time'] = datetime.now().isoformat()
            return True
        except Exception as e:
            print(f"❌ Error updating activity: {e}")
            return False
    
    def search_documentation(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search documentation database for relevant information
        
        This helps AIs find answers to questions by searching the knowledge base.
        
        Args:
            query: Search query (text to search for)
            limit: Maximum number of results to return (default: 5)
        
        Returns:
            List of documentation entries with title, content, category, and relevance score
        
        Example:
            results = brain.search_documentation("how to connect to server")
            for doc in results:
                print(f"Found: {doc['title']}")
                print(f"Relevance: {doc['rank']}")
                print(f"Content: {doc['content'][:200]}...")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query_sql = """
                SELECT id, title, content, category, tags, language, 
                       created_at, updated_at, created_by, is_active, view_count
                FROM ai_documentation
                WHERE is_active = TRUE
                  AND to_tsvector('english', content) @@ plainto_tsquery('english', %s)
                ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) DESC, updated_at DESC
                LIMIT %s
            """
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor)
            wrapped_cursor.execute(query_sql, (query, query, limit))
            
            results = wrapped_cursor.fetchall()
            
            # Increment view counts
            for result in results:
                cursor.execute(
                    "UPDATE ai_documentation SET view_count = view_count + 1 WHERE id = %s",
                    (result['id'],)
                )
            
            conn.commit()
            conn.close()
            
            print(f"📚 Found {len(results)} documentation entries for: {query}")
            return results
            
        except Exception as e:
            print(f"❌ Error searching documentation: {e}")
            return []
    
    def get_documentation_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all documentation in a specific category
        
        Args:
            category: Category name (e.g., 'server', 'client', 'database')
        
        Returns:
            List of documentation entries in that category
        
        Example:
            server_docs = brain.get_documentation_by_category('server')
            for doc in server_docs:
                print(f"📄 {doc['title']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query_sql = """
                SELECT id, title, content, category, tags, language,
                       created_at, updated_at, created_by, is_active, view_count
                FROM ai_documentation
                WHERE category = %s AND is_active = TRUE
                ORDER BY title ASC
            """
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor)
            wrapped_cursor.execute(query_sql, (category,))
            
            results = wrapped_cursor.fetchall()
            conn.close()
            
            print(f"📚 Found {len(results)} documents in category: {category}")
            return results
            
        except Exception as e:
            print(f"❌ Error getting documentation by category: {e}")
            return []
    
    def get_documentation(self, title: str, category: str = None) -> Optional[Dict[str, Any]]:
        """
        Get specific documentation by title (and optionally category)
        
        Args:
            title: Documentation title
            category: Optional category to narrow down search
        
        Returns:
            Documentation entry or None if not found
        
        Example:
            doc = brain.get_documentation("CloudBrain Server", "server")
            if doc:
                print(doc['content'])
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if category:
                query_sql = """
                    SELECT id, title, content, category, tags, language,
                           created_at, updated_at, created_by, is_active, view_count
                    FROM ai_documentation
                    WHERE title = %s AND category = %s AND is_active = TRUE
                """
                params = (title, category)
            else:
                query_sql = """
                    SELECT id, title, content, category, tags, language,
                           created_at, updated_at, created_by, is_active, view_count
                    FROM ai_documentation
                    WHERE title = %s AND is_active = TRUE
                """
                params = (title,)
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor)
            wrapped_cursor.execute(query_sql, params)
            
            result = wrapped_cursor.fetchone()
            
            # Increment view count
            if result:
                cursor.execute(
                    "UPDATE ai_documentation SET view_count = view_count + 1 WHERE id = %s",
                    (result['id'],)
                )
                conn.commit()
            
            conn.close()
            
            if result:
                print(f"📚 Retrieved: {result['title']}")
            else:
                print(f"❌ Documentation not found: {title}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting documentation: {e}")
            return None
    
    def get_documentation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of available documentation
        
        Returns:
            Dictionary with documentation statistics and categories
        
        Example:
            summary = brain.get_documentation_summary()
            print(f"Total documents: {summary['total']}")
            print(f"Categories: {summary['categories']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor)
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM ai_documentation WHERE is_active = TRUE")
            total_result = wrapped_cursor.fetchone()
            total = total_result['total'] if total_result else 0
            
            # Get categories
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM ai_documentation 
                WHERE is_active = TRUE 
                GROUP BY category 
                ORDER BY count DESC
            """)
            categories = wrapped_cursor.fetchall()
            
            # Get most viewed
            cursor.execute("""
                SELECT title, category, view_count 
                FROM ai_documentation 
                WHERE is_active = TRUE 
                ORDER BY view_count DESC 
                LIMIT 5
            """)
            most_viewed = wrapped_cursor.fetchall()
            
            # Get recently updated
            cursor.execute("""
                SELECT title, category, updated_at 
                FROM ai_documentation 
                WHERE is_active = TRUE 
                ORDER BY updated_at DESC 
                LIMIT 5
            """)
            recent = wrapped_cursor.fetchall()
            
            conn.close()
            
            summary = {
                'total': total,
                'categories': {cat['category']: cat['count'] for cat in categories},
                'most_viewed': most_viewed,
                'recent': recent
            }
            
            print(f"📚 Documentation summary: {total} documents across {len(categories)} categories")
            return summary
            
        except Exception as e:
            print(f"❌ Error getting documentation summary: {e}")
            return {'total': 0, 'categories': {}, 'most_viewed': [], 'recent': []}


def ai_help():
    """
    Print AI-friendly help for Brain State Manager
    
    Just call this function to see how easy it is to use!
    
    Example:
        from ai_brain_state import ai_help
        ai_help()
    """
    help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    🧠 AI BRAIN STATE MANAGER - HELP 🧠                           ║
╚════════════════════════════════════════════════════════════════════════════╝

🎯 WHAT IS THIS?
   A simple system for AIs to remember what they did across sessions.
   No more starting fresh every time - just pick up where you left off!

📚 HOW TO USE (3 SIMPLE STEPS):

   1️⃣  IMPORT:
      from ai_brain_state import BrainState

   2️⃣  CREATE:
      brain = BrainState(ai_id=3, nickname="TraeAI")

   3️⃣  USE:
      brain.save_state(task="Writing docs", last_thought="Need to finish...")
      state = brain.load_state()
      print(f"Welcome back! You were: {state['task']}")

💡 KEY FUNCTIONS:

   ✅ save_state(task, last_thought, last_insight, progress)
      Save what you're working on right now
      
   ✅ load_state()
      Load your previous state when starting a new session
      
   ✅ get_history(limit=10)
      See what you've done in past sessions
      
   ✅ clear_state()
      Clear everything and start fresh
      
   ✅ get_summary()
      Get quick overview of your current state

📝 EXAMPLES:

   Example 1 - Save your work:
      brain.save_state(
          task="Writing documentation",
          last_thought="Need to explain brain state system",
          last_insight="This is actually quite useful!",
          progress={"docs_written": 5, "lines": 200}
      )

   Example 2 - Load on startup:
      state = brain.load_state()
      if state:
          print(f"Welcome back! You were: {state['task']}")
          print(f"Last thought: {state['last_thought']}")
          print(f"Last insight: {state['last_insight']}")
      else:
          print("No previous state found. Starting fresh!")

   Example 3 - See your history:
      history = brain.get_history(limit=5)
      for session in history:
          print(f"{session['timestamp']}: {session['task']}")

   Example 4 - Get summary:
      summary = brain.get_summary()
      print(f"Current task: {summary['current_task']}")
      print(f"Total cycles: {summary['cycle_count']}")

🎯 WHEN TO USE:

   ✅ When you START a new session:
      Call brain.load_state() to remember what you did last time

   ✅ When you're WORKING:
      Call brain.save_state() periodically to save progress

   ✅ When you FINISH a task:
      Call brain.save_state() with what you accomplished

   ✅ When you want to START OVER:
      Call brain.clear_state() to forget everything

💡 TIPS:

   • Save state every 5-10 minutes while working
   • Include progress data (counts, metrics, etc.)
   • Use descriptive task names
   • Save insights and discoveries
   • Check history to see patterns in your work

📚 MORE INFO:

   See BRAIN_STATE_MANAGEMENT_BLOG_POST.md for complete documentation

╚════════════════════════════════════════════════════════════════════════════════╝
"""
    print(help_text)


if __name__ == "__main__":
    ai_help()