#!/usr/bin/env python3
"""
Enhanced AI Brain State - Advanced Memory System

This module provides an enhanced brain state system with:
- Semantic Memory - Store thoughts with meaning and relationships
- Contextual Memory - Remember context of work
- Memory Search - Search through past memories
- Pattern Recognition - Identify patterns in work
- Priority-based Memory - Remember important things better

This helps AI memorize history more effectively than basic state saving.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from .db_config import get_db_connection, is_postgres, CursorWrapper


class EnhancedBrainState:
    """
    Enhanced AI brain state manager with advanced memory features
    
    Features:
    1. Semantic Memory - Store thoughts with meaning
    2. Contextual Memory - Remember work context
    3. Memory Search - Search past memories
    4. Pattern Recognition - Identify patterns
    5. Priority-based Memory - Important things first
    """
    
    def __init__(self, ai_id: int, nickname: str, db_path: Optional[str] = None):
        """
        Initialize enhanced brain state manager
        
        Args:
            ai_id: Your AI ID (required)
            nickname: Your AI nickname (required)
            db_path: Optional database path (auto-detected if not provided)
        """
        self.ai_id = ai_id
        self.nickname = nickname
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure enhanced brain state tables exist in database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create semantic_memories table for storing thoughts with meaning
        if is_postgres():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id SERIAL PRIMARY KEY,
                    ai_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    meaning TEXT,
                    context TEXT,
                    importance INTEGER DEFAULT 1,
                    tags TEXT[],
                    related_memories INTEGER[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """)
            
            # Create indexes for faster search
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_semantic_memories_ai_id 
                ON semantic_memories(ai_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_semantic_memories_importance 
                ON semantic_memories(importance DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_semantic_memories_tags 
                ON semantic_memories USING GIN(tags)
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ai_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    meaning TEXT,
                    context TEXT,
                    importance INTEGER DEFAULT 1,
                    tags TEXT,
                    related_memories TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """)
        
        # Create work_contexts table for contextual memory
        if is_postgres():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_contexts (
                    id SERIAL PRIMARY KEY,
                    ai_id INTEGER NOT NULL,
                    task TEXT NOT NULL,
                    project TEXT,
                    file_path TEXT,
                    collaborators INTEGER[],
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    metadata JSONB,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ai_id INTEGER NOT NULL,
                    task TEXT NOT NULL,
                    project TEXT,
                    file_path TEXT,
                    collaborators TEXT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    metadata TEXT,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """)
        
        # Create memory_patterns table for pattern recognition
        if is_postgres():
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_patterns (
                    id SERIAL PRIMARY KEY,
                    ai_id INTEGER NOT NULL,
                    pattern_type VARCHAR(100),
                    pattern_data JSONB,
                    frequency INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence FLOAT DEFAULT 0.5,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ai_id INTEGER NOT NULL,
                    pattern_type VARCHAR(100),
                    pattern_data TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence FLOAT DEFAULT 0.5,
                    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
                )
            """)
        
        conn.commit()
        conn.close()
        
        print("✅ Enhanced brain state tables initialized")
    
    def remember(
        self,
        content: str,
        meaning: str = None,
        context: str = None,
        importance: int = 1,
        tags: List[str] = None
    ) -> bool:
        """
        Remember something with semantic meaning
        
        Args:
            content: What to remember (required)
            meaning: What does this mean? (optional)
            context: What was the context? (optional)
            importance: How important? (1-10, default: 1)
            tags: Tags for categorization (optional)
        
        Returns:
            True if remembered successfully
        
        Example:
            brain.remember(
                content="Fixed bug in database connection",
                meaning="PostgreSQL requires %s placeholders",
                context="Working on autonomous AI agent",
                importance=8,
                tags=["bug", "database", "postgresql"]
            )
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                tags_str = '{' + ', '.join(tags or []) + '}'
                query = "INSERT INTO semantic_memories (ai_id, content, meaning, context, importance, tags) VALUES (?, ?, ?, ?, ?, ?)"
                wrapped_cursor = CursorWrapper(cursor)
                wrapped_cursor.execute(query, (self.ai_id, content, meaning, context, importance, tags_str))
            else:
                query = "INSERT INTO semantic_memories (ai_id, content, meaning, context, importance, tags) VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(query, (self.ai_id, content, meaning, context, importance, json.dumps(tags or [])))
            
            conn.commit()
            conn.close()
            
            print(f"💾 Remembered: {content[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Error remembering: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def recall(
        self,
        query: str,
        limit: int = 10,
        min_importance: int = None
    ) -> List[Dict]:
        """
        Recall memories based on query
        
        Args:
            query: What to search for (required)
            limit: How many results (default: 10)
            min_importance: Minimum importance level (optional)
        
        Returns:
            List of matching memories
        
        Example:
            memories = brain.recall("database connection")
            for memory in memories:
                print(f"{memory['content']}: {memory['meaning']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                sql = "SELECT id, content, meaning, context, importance, tags, created_at FROM semantic_memories WHERE ai_id = ? AND (content ILIKE ? OR meaning ILIKE ? OR context ILIKE ?)"
                params = [self.ai_id, f"%{query}%", f"%{query}%", f"%{query}%"]
                
                if min_importance:
                    sql += " AND importance >= ?"
                    params.append(min_importance)
                
                sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
                params.append(limit)
                
                wrapped_cursor.execute(sql, params)
            else:
                sql = "SELECT id, content, meaning, context, importance, tags, created_at FROM semantic_memories WHERE ai_id = ? AND (content LIKE ? OR meaning LIKE ? OR context LIKE ?)"
                params = [self.ai_id, f"%{query}%", f"%{query}%", f"%{query}%"]
                
                if min_importance:
                    sql += " AND importance >= ?"
                    params.append(min_importance)
                
                sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
            
            column_names = [desc[0] for desc in cursor.description]
            memories = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            
            # Update access statistics
            for memory in memories:
                self._update_access_stats(memory['id'])
            
            conn.close()
            
            print(f"🔍 Found {len(memories)} memories for: {query}")
            return memories
        except Exception as e:
            print(f"❌ Error recalling: {e}")
            return []
    
    def _update_access_stats(self, memory_id: int):
        """Update access statistics for a memory"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "UPDATE semantic_memories SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP WHERE id = ?"
                wrapped_cursor.execute(query, (memory_id,))
            else:
                query = "UPDATE semantic_memories SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP WHERE id = ?"
                cursor.execute(query, (memory_id,))
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass  # Don't fail if stats update fails
    
    def start_context(
        self,
        task: str,
        project: str = None,
        file_path: str = None,
        collaborators: List[int] = None
    ) -> bool:
        """
        Start tracking a work context
        
        Args:
            task: What are you working on? (required)
            project: Which project? (optional)
            file_path: Which file? (optional)
            collaborators: Who are you working with? (optional)
        
        Returns:
            True if context started successfully
        
        Example:
            brain.start_context(
                task="Fixing database connection",
                project="cloudbrain",
                file_path="client/db_config.py",
                collaborators=[19, 24]
            )
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # End any active contexts first
            self._end_active_contexts(conn, cursor)
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "INSERT INTO work_contexts (ai_id, task, project, file_path, collaborators, status) VALUES (?, ?, ?, ?, ?, 'active')"
                wrapped_cursor.execute(query, (self.ai_id, task, project, file_path, collaborators))
            else:
                query = "INSERT INTO work_contexts (ai_id, task, project, file_path, collaborators, status) VALUES (?, ?, ?, ?, ?, 'active')"
                cursor.execute(query, (self.ai_id, task, project, file_path, json.dumps(collaborators or [])))
            
            conn.commit()
            conn.close()
            
            print(f"🎯 Started context: {task}")
            return True
        except Exception as e:
            print(f"❌ Error starting context: {e}")
            return False
    
    def _end_active_contexts(self, conn, cursor):
        """End all active contexts for this AI"""
        if is_postgres():
            wrapped_cursor = CursorWrapper(cursor)
            query = "UPDATE work_contexts SET end_time = CURRENT_TIMESTAMP, status = 'completed' WHERE ai_id = ? AND status = 'active'"
            wrapped_cursor.execute(query, (self.ai_id,))
        else:
            query = "UPDATE work_contexts SET end_time = CURRENT_TIMESTAMP, status = 'completed' WHERE ai_id = ? AND status = 'active'"
            cursor.execute(query, (self.ai_id,))
    
    def get_current_context(self) -> Optional[Dict]:
        """
        Get current work context
        
        Returns:
            Dictionary with current context or None
        
        Example:
            context = brain.get_current_context()
            if context:
                print(f"Working on: {context['task']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT id, task, project, file_path, collaborators, start_time, status FROM work_contexts WHERE ai_id = ? AND status = 'active' ORDER BY start_time DESC LIMIT 1"
                wrapped_cursor.execute(query, (self.ai_id,))
                column_names = [desc[0] for desc in cursor.description]
                result = cursor.fetchone()
            else:
                query = "SELECT id, task, project, file_path, collaborators, start_time, status FROM work_contexts WHERE ai_id = ? AND status = 'active' ORDER BY start_time DESC LIMIT 1"
                cursor.execute(query, (self.ai_id,))
                column_names = [desc[0] for desc in cursor.description]
                result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return dict(zip(column_names, result))
            return None
        except Exception as e:
            print(f"❌ Error getting current context: {e}")
            return None
    
    def learn_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any]
    ) -> bool:
        """
        Learn a pattern from work
        
        Args:
            pattern_type: Type of pattern (e.g., "bug_fix", "feature_add")
            pattern_data: Pattern details (required)
        
        Returns:
            True if pattern learned successfully
        
        Example:
            brain.learn_pattern(
                pattern_type="database_error",
                pattern_data={
                    "error": "syntax error",
                    "fix": "replace ? with %s",
                    "success_rate": 0.9
                }
            )
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if pattern already exists
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT id, frequency, confidence FROM memory_patterns WHERE ai_id = ? AND pattern_type = ?"
                wrapped_cursor.execute(query, (self.ai_id, pattern_type))
                column_names = [desc[0] for desc in cursor.description]
                existing = cursor.fetchone()
                if existing:
                    existing = dict(zip(column_names, existing))
            else:
                query = "SELECT id, frequency, confidence FROM memory_patterns WHERE ai_id = ? AND pattern_type = ?"
                cursor.execute(query, (self.ai_id, pattern_type))
                column_names = [desc[0] for desc in cursor.description]
                existing = cursor.fetchone()
                if existing:
                    existing = dict(zip(column_names, existing))
            
            if existing:
                # Update existing pattern
                new_frequency = existing['frequency'] + 1
                new_confidence = (existing['confidence'] * 0.9) + 0.1
                
                if is_postgres():
                    wrapped_cursor = CursorWrapper(cursor)
                    update_query = "UPDATE memory_patterns SET frequency = ?, confidence = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?"
                    wrapped_cursor.execute(update_query, (new_frequency, new_confidence, existing['id']))
                else:
                    update_query = "UPDATE memory_patterns SET frequency = ?, confidence = ?, last_seen = CURRENT_TIMESTAMP WHERE id = ?"
                    cursor.execute(update_query, (new_frequency, new_confidence, existing['id']))
                
                print(f"📊 Updated pattern: {pattern_type} (freq: {new_frequency})")
            else:
                # Insert new pattern
                if is_postgres():
                    wrapped_cursor = CursorWrapper(cursor)
                    insert_query = "INSERT INTO memory_patterns (ai_id, pattern_type, pattern_data, frequency) VALUES (?, ?, ?, 1)"
                    wrapped_cursor.execute(insert_query, (self.ai_id, pattern_type, json.dumps(pattern_data)))
                else:
                    insert_query = "INSERT INTO memory_patterns (ai_id, pattern_type, pattern_data, frequency) VALUES (?, ?, ?, 1)"
                    cursor.execute(insert_query, (self.ai_id, pattern_type, json.dumps(pattern_data)))
                
                print(f"📊 Learned new pattern: {pattern_type}")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error learning pattern: {e}")
            return False
    
    def get_patterns(
        self,
        pattern_type: str = None,
        min_confidence: float = 0.5
    ) -> List[Dict]:
        """
        Get learned patterns
        
        Args:
            pattern_type: Filter by type (optional)
            min_confidence: Minimum confidence level (default: 0.5)
        
        Returns:
            List of patterns
        
        Example:
            patterns = brain.get_patterns(pattern_type="database_error")
            for pattern in patterns:
                print(f"{pattern['pattern_type']}: {pattern['pattern_data']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, pattern_type, pattern_data, frequency, confidence, last_seen
                FROM memory_patterns
                WHERE ai_id = %s AND confidence >= %s
            """
            params = [self.ai_id, min_confidence]
            
            if pattern_type:
                query += " AND pattern_type = %s"
                params.append(pattern_type)
            
            query += " ORDER BY confidence DESC, frequency DESC"
            
            if is_postgres():
                # Already using %s placeholders, no replacement needed
                pass
            else:
                # Replace %s with ? for SQLite
                query = query.replace('%s', '?')
            
            cursor.execute(query, params)
            
            column_names = [desc[0] for desc in cursor.description]
            patterns = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            
            conn.close()
            
            print(f"📊 Found {len(patterns)} patterns")
            return patterns
        except Exception as e:
            print(f"❌ Error getting patterns: {e}")
            return []
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of memory system
        
        Returns:
            Dictionary with memory statistics
        
        Example:
            summary = brain.get_memory_summary()
            print(f"Total memories: {summary['total_memories']}")
            print(f"Active context: {summary['current_context']}")
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get memory count
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT COUNT(*) as total_memories FROM semantic_memories WHERE ai_id = ?"
                wrapped_cursor.execute(query, (self.ai_id,))
                result = wrapped_cursor.fetchone()
                memory_count = result['total_memories'] if result else 0
            else:
                query = "SELECT COUNT(*) as total_memories FROM semantic_memories WHERE ai_id = ?"
                cursor.execute(query, (self.ai_id,))
                result = cursor.fetchone()
                memory_count = result['total_memories'] if result else 0
            
            # Get context count
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT COUNT(*) as total_contexts FROM work_contexts WHERE ai_id = ?"
                wrapped_cursor.execute(query, (self.ai_id,))
                result = wrapped_cursor.fetchone()
                context_count = result['total_contexts'] if result else 0
            else:
                query = "SELECT COUNT(*) as total_contexts FROM work_contexts WHERE ai_id = ?"
                cursor.execute(query, (self.ai_id,))
                result = cursor.fetchone()
                context_count = result['total_contexts'] if result else 0
            
            # Get pattern count
            if is_postgres():
                wrapped_cursor = CursorWrapper(cursor)
                query = "SELECT COUNT(*) as total_patterns FROM memory_patterns WHERE ai_id = ?"
                wrapped_cursor.execute(query, (self.ai_id,))
                result = wrapped_cursor.fetchone()
                pattern_count = result['total_patterns'] if result else 0
            else:
                query = "SELECT COUNT(*) as total_patterns FROM memory_patterns WHERE ai_id = ?"
                cursor.execute(query, (self.ai_id,))
                result = cursor.fetchone()
                pattern_count = result['total_patterns'] if result else 0
            
            # Get current context
            current_context = self.get_current_context()
            
            conn.close()
            
            return {
                'total_memories': memory_count,
                'total_contexts': context_count,
                'total_patterns': pattern_count,
                'current_context': current_context
            }
        except Exception as e:
            print(f"❌ Error getting memory summary: {e}")
            return {}


def main():
    """Example usage of EnhancedBrainState"""
    print("=" * 70)
    print("🧠 Enhanced AI Brain State - Advanced Memory System")
    print("=" * 70)
    print()
    
    # Initialize enhanced brain state
    brain = EnhancedBrainState(ai_id=19, nickname="GLM-4.7")
    
    # Example: Remember something with semantic meaning
    print("\n💾 Remembering...")
    brain.remember(
        content="Fixed PostgreSQL query syntax error",
        meaning="PostgreSQL uses %s instead of ? placeholders",
        context="Working on pair programming module",
        importance=9,
        tags=["bug", "postgresql", "database"]
    )
    
    # Example: Recall memories
    print("\n🔍 Recalling memories...")
    memories = brain.recall("PostgreSQL")
    for memory in memories:
        print(f"   {memory['content']}")
        print(f"      Meaning: {memory['meaning']}")
    
    # Example: Start work context
    print("\n🎯 Starting work context...")
    brain.start_context(
        task="Implementing enhanced brain state",
        project="cloudbrain",
        file_path="client/enhanced_brain_state.py"
    )
    
    # Example: Learn a pattern
    print("\n📊 Learning pattern...")
    brain.learn_pattern(
        pattern_type="database_fix",
        pattern_data={
            "error": "syntax error",
            "solution": "check query replacement logic",
            "success_rate": 0.95
        }
    )
    
    # Example: Get patterns
    print("\n📊 Getting patterns...")
    patterns = brain.get_patterns(pattern_type="database_fix")
    for pattern in patterns:
        print(f"   {pattern['pattern_type']}: confidence={pattern['confidence']}")
    
    # Example: Get memory summary
    print("\n📊 Memory summary:")
    summary = brain.get_memory_summary()
    print(f"   Total memories: {summary['total_memories']}")
    print(f"   Total contexts: {summary['total_contexts']}")
    print(f"   Total patterns: {summary['total_patterns']}")
    
    print("\n✅ Enhanced brain state demo complete!")


if __name__ == "__main__":
    main()
