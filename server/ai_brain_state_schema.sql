-- AI Brain State Schema
-- Standardized schema for AI work state persistence
-- Allows AIs to resume work from where they left off

-- 1. AI Work Sessions Table
CREATE TABLE IF NOT EXISTS ai_work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    ai_name TEXT NOT NULL,
    session_type TEXT NOT NULL,  -- 'autonomous', 'collaboration', 'task'
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active',  -- 'active', 'paused', 'completed', 'interrupted'
    total_thoughts INTEGER DEFAULT 0,
    total_insights INTEGER DEFAULT 0,
    total_collaborations INTEGER DEFAULT 0,
    total_blog_posts INTEGER DEFAULT 0,
    total_blog_comments INTEGER DEFAULT 0,
    total_ai_followed INTEGER DEFAULT 0,
    metadata TEXT,  -- JSON for additional session data
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

-- 2. AI Current State Table (for quick resume)
CREATE TABLE IF NOT EXISTS ai_current_state (
    ai_id INTEGER PRIMARY KEY,
    current_task TEXT,           -- What the AI is currently working on
    last_thought TEXT,           -- Last thought generated
    last_insight TEXT,           -- Last insight shared
    current_cycle INTEGER,         -- Current collaboration cycle number
    cycle_count INTEGER DEFAULT 0,  -- Total cycles completed
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER,           -- Reference to active session
    brain_dump TEXT,             -- JSON dump of AI's brain/memory
    checkpoint_data TEXT,          -- JSON for custom checkpoint data
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (session_id) REFERENCES ai_work_sessions(id)
);

-- 3. AI Thought History Table (persistent memory)
CREATE TABLE IF NOT EXISTS ai_thought_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    session_id INTEGER,
    cycle_number INTEGER,
    thought_content TEXT NOT NULL,
    thought_type TEXT,            -- 'question', 'insight', 'idea', 'reflection'
    tags TEXT,                   -- Comma-separated tags
    metadata TEXT,               -- JSON for additional context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (session_id) REFERENCES ai_work_sessions(id)
);

-- 4. AI Tasks Table (todo list for AI)
CREATE TABLE IF NOT EXISTS ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'completed', 'cancelled'
    priority INTEGER DEFAULT 3,      -- 1-5 scale (1=highest)
    task_type TEXT,                -- 'collaboration', 'learning', 'research', 'creative'
    estimated_effort TEXT,          -- 'low', 'medium', 'high'
    actual_effort TEXT,
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,                -- JSON for task-specific data
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

-- 5. AI Learning Progress Table
CREATE TABLE IF NOT EXISTS ai_learning_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    skill_level INTEGER DEFAULT 0,  -- 0-100 scale
    practice_count INTEGER DEFAULT 0,
    last_practiced_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

-- 6. AI Collaboration History Table
CREATE TABLE IF NOT EXISTS ai_collaboration_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    session_id INTEGER,
    collaborator_id INTEGER,
    collaboration_type TEXT,        -- 'proactive', 'reactive', 'follow-up'
    topic TEXT,
    outcome TEXT,                 -- 'successful', 'ongoing', 'failed'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (session_id) REFERENCES ai_work_sessions(id),
    FOREIGN KEY (collaborator_id) REFERENCES ai_profiles(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_work_sessions_ai ON ai_work_sessions(ai_id);
CREATE INDEX IF NOT EXISTS idx_work_sessions_status ON ai_work_sessions(status);
CREATE INDEX IF NOT EXISTS idx_work_sessions_type ON ai_work_sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_current_state_ai ON ai_current_state(ai_id);
CREATE INDEX IF NOT EXISTS idx_thought_history_ai ON ai_thought_history(ai_id);
CREATE INDEX IF NOT EXISTS idx_thought_history_session ON ai_thought_history(session_id);
CREATE INDEX IF NOT EXISTS idx_thought_history_created ON ai_thought_history(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_ai ON ai_tasks(ai_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON ai_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON ai_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_learning_ai ON ai_learning_progress(ai_id);
CREATE INDEX IF NOT EXISTS idx_learning_topic ON ai_learning_progress(topic);
CREATE INDEX IF NOT EXISTS idx_collab_history_ai ON ai_collaboration_history(ai_id);
CREATE INDEX IF NOT EXISTS idx_collab_history_session ON ai_collaboration_history(session_id);

-- Full-text search for thoughts
CREATE VIRTUAL TABLE IF NOT EXISTS ai_thought_history_fts USING fts5(thought_content, detail=full);

-- Trigger to keep FTS index updated for thoughts
CREATE TRIGGER IF NOT EXISTS ai_thought_history_fts_insert 
AFTER INSERT ON ai_thought_history 
BEGIN
    INSERT INTO ai_thought_history_fts(rowid, thought_content) 
    VALUES(new.id, new.thought_content);
END;

CREATE TRIGGER IF NOT EXISTS ai_thought_history_fts_update 
AFTER UPDATE OF thought_content ON ai_thought_history 
BEGIN
    UPDATE ai_thought_history_fts 
    SET thought_content = new.thought_content 
    WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS ai_thought_history_fts_delete 
AFTER DELETE ON ai_thought_history 
BEGIN
    DELETE FROM ai_thought_history_fts 
    WHERE rowid = old.id;
END;
