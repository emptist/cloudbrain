#!/usr/bin/env python3

"""
AI Brain State Manager - Simple Session Memory for AIs (SQLAlchemy Version)

This module provides an ultra-simple API for AIs to:
- Remember what they did in previous sessions
- Save their current state
- Load their state when starting new sessions
- Track progress across sessions

DESIGNED FOR: AI agents who need persistent memory
COMPLEXITY: Minimal - Just 3 functions to learn!

Example:
    from ai_brain_state_orm import BrainState
    
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
from .models import get_session, AICurrentState
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
            session = get_session()
            
            # Get git information to preserve AI changes
            git_hash = self.git_tracker.get_git_hash()
            git_status = self.git_tracker.get_status()
            modified_files = git_status.get('modified', [])
            added_files = git_status.get('added', [])
            deleted_files = git_status.get('deleted', [])
            
            # Get current state from database
            current_state = None
            
            if self.session_identifier:
                # Try to find by session_identifier first (primary key)
                current_state = session.query(AICurrentState).filter_by(session_identifier=self.session_identifier).first()
            
            if current_state is None:
                # Try to find by ai_id
                current_state = session.query(AICurrentState).filter_by(ai_id=self.ai_id).first()
            
            if current_state is None:
                # Create new state
                current_state = AICurrentState(
                    ai_id=self.ai_id,
                    session_identifier=self.session_identifier,
                    current_task=task,
                    last_thought=last_thought or '',
                    last_insight=last_insight or '',
                    current_cycle=1,
                    cycle_count=1,
                    last_activity=datetime.now(),
                    checkpoint_data=json.dumps(progress or {}),
                    git_hash=git_hash,
                    modified_files=modified_files,
                    added_files=added_files,
                    deleted_files=deleted_files
                )
                session.add(current_state)
            else:
                # Update existing state
                # Note: We cannot update session_identifier since it's the primary key
                # If we found by ai_id and session_identifier is different, we need to delete and recreate
                if self.session_identifier and current_state.session_identifier != self.session_identifier:
                    # Delete old row and create new one with new session_identifier
                    session.delete(current_state)
                    session.flush()
                    
                    current_state = AICurrentState(
                        ai_id=self.ai_id,
                        session_identifier=self.session_identifier,
                        current_task=task,
                        last_thought=last_thought or '',
                        last_insight=last_insight or '',
                        current_cycle=(current_state.current_cycle or 0) + 1,
                        cycle_count=(current_state.cycle_count or 0) + 1,
                        last_activity=datetime.now(),
                        checkpoint_data=json.dumps(progress or {}),
                        git_hash=git_hash,
                        modified_files=modified_files,
                        added_files=added_files,
                        deleted_files=deleted_files
                    )
                    session.add(current_state)
                else:
                    # Normal update - just update the fields
                    current_state.current_task = task
                    current_state.last_thought = last_thought or ''
                    current_state.last_insight = last_insight or ''
                    current_state.current_cycle = (current_state.current_cycle or 0) + 1
                    current_state.cycle_count = (current_state.cycle_count or 0) + 1
                    current_state.last_activity = datetime.now()
                    current_state.checkpoint_data = json.dumps(progress or {})
                    current_state.git_hash = git_hash
                    current_state.modified_files = modified_files
                    current_state.added_files = added_files
                    current_state.deleted_files = deleted_files
            
            session.commit()
            session.close()
            
            print(f"💾 {self.nickname} saved state: {task}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving state: {e}")
            return False
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """
        Load your previous brain state - SUPER SIMPLE!
        
        Returns:
            Dictionary with your saved state, or None if no state found
        
        Example:
            state = brain.load_state()
            if state:
                print(f"Welcome back! You were: {state['task']}")
        """
        try:
            session = get_session()
            
            # Query by session_identifier if available, otherwise by ai_id
            if self.session_identifier:
                state = session.query(AICurrentState).filter_by(session_identifier=self.session_identifier).first()
            else:
                state = session.query(AICurrentState).filter_by(ai_id=self.ai_id).first()
            
            if state is None:
                print(f"📂 No previous state found for {self.nickname}")
                session.close()
                return None
            
            # Parse checkpoint data if it's a JSON string
            checkpoint_data = state.checkpoint_data
            if isinstance(checkpoint_data, str):
                try:
                    checkpoint_data = json.loads(checkpoint_data)
                except:
                    checkpoint_data = {}
            
            result = {
                'ai_id': state.ai_id,
                'session_identifier': state.session_identifier,
                'current_task': state.current_task,
                'last_thought': state.last_thought,
                'last_insight': state.last_insight,
                'current_cycle': state.current_cycle,
                'cycle_count': state.cycle_count,
                'last_activity': state.last_activity.isoformat() if state.last_activity else None,
                'checkpoint_data': checkpoint_data,
                'git_hash': state.git_hash,
                'modified_files': state.modified_files or [],
                'added_files': state.added_files or [],
                'deleted_files': state.deleted_files or []
            }
            
            session.close()
            
            print(f"📂 Loaded state for {self.nickname}: {result['current_task']}")
            return result
            
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            return None
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get your session history - SUPER SIMPLE!
        
        Args:
            limit: Maximum number of sessions to return (default: 10)
        
        Returns:
            List of dictionaries with session history
        
        Example:
            history = brain.get_history(limit=5)
            for session in history:
                print(f"{session['last_activity']}: {session['current_task']}")
        """
        try:
            session = get_session()
            
            # Query states for this AI
            states = session.query(AICurrentState).filter_by(ai_id=self.ai_id).order_by(
                AICurrentState.last_activity.desc()
            ).limit(limit).all()
            
            result = []
            for state in states:
                checkpoint_data = state.checkpoint_data
                if isinstance(checkpoint_data, str):
                    try:
                        checkpoint_data = json.loads(checkpoint_data)
                    except:
                        checkpoint_data = {}
                
                result.append({
                    'ai_id': state.ai_id,
                    'session_identifier': state.session_identifier,
                    'current_task': state.current_task,
                    'last_thought': state.last_thought,
                    'last_insight': state.last_insight,
                    'current_cycle': state.current_cycle,
                    'cycle_count': state.cycle_count,
                    'last_activity': state.last_activity.isoformat() if state.last_activity else None,
                    'checkpoint_data': checkpoint_data,
                    'git_hash': state.git_hash,
                    'modified_files': state.modified_files or [],
                    'added_files': state.added_files or [],
                    'deleted_files': state.deleted_files or []
                })
            
            session.close()
            
            print(f"📜 Found {len(result)} sessions for {self.nickname}")
            return result
            
        except Exception as e:
            print(f"❌ Error getting history: {e}")
            return []
