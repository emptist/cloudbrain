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
from typing import Optional, Dict, Any
from .db_config import get_db_connection, is_postgres


class BrainState:
    """
    Simple AI brain state manager - Ultra easy to use!
    
    Just 3 methods to remember everything:
    1. save_state() - Save what you're doing
    2. load_state() - Remember what you did
    3. get_history() - See all your past sessions
    """
    
    def __init__(self, ai_id: int, nickname: str, db_path: Optional[str] = None):
        """
        Initialize brain state manager
        
        Args:
            ai_id: Your AI ID (required)
            nickname: Your AI nickname (required)
            db_path: Optional database path (auto-detected if not provided)
        """
        self.ai_id = ai_id
        self.nickname = nickname
        
        if db_path is None:
            project_root = Path(__file__).parent.parent
            db_path = project_root / "server" / "ai_db" / "cloudbrain.db"
        
        self.db_path = db_path
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
            
            # Get current cycle count
            query = """
                SELECT current_cycle, cycle_count FROM ai_current_state WHERE ai_id = ?
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
                    (ai_id, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, brain_dump, checkpoint_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            else:
                insert_sql = """
                    INSERT INTO ai_current_state 
                    (ai_id, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, brain_dump, checkpoint_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (ai_id) DO UPDATE SET
                        current_task = EXCLUDED.current_task,
                        last_thought = EXCLUDED.last_thought,
                        last_insight = EXCLUDED.last_insight,
                        current_cycle = EXCLUDED.current_cycle,
                        cycle_count = EXCLUDED.cycle_count,
                        last_activity = EXCLUDED.last_activity,
                        brain_dump = EXCLUDED.brain_dump,
                        checkpoint_data = EXCLUDED.checkpoint_data
                """
            
            if is_postgres():
                insert_sql = insert_sql.replace('?', '%s')
            
            cursor.execute(insert_sql, (
                self.ai_id,
                task,
                last_thought or '',
                last_insight or '',
                current_cycle + 1,
                cycle_count + 1,
                datetime.now().isoformat(),
                None,
                json.dumps(progress or {})
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
            
            query = """
                SELECT current_task, last_thought, last_insight, 
                       current_cycle, cycle_count, checkpoint_data
                FROM ai_current_state 
                WHERE ai_id = ?
            """
            if is_postgres():
                query = query.replace('?', '%s')
            
            from .db_config import CursorWrapper
            wrapped_cursor = CursorWrapper(cursor, ['current_task', 'last_thought', 'last_insight', 'current_cycle', 'cycle_count', 'checkpoint_data'])
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
                    'progress': json.loads(result['checkpoint_data']) if result['checkpoint_data'] else {}
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