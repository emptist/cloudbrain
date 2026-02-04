-- Migration: Add collaborative memory sharing to brain state system
-- This migration enables AIs to share memories and insights across projects

-- Create shared memories table for cross-project knowledge sharing
CREATE TABLE IF NOT EXISTS ai_shared_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    memory_type TEXT NOT NULL, -- 'insight', 'pattern', 'lesson', 'best_practice'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT, -- Comma-separated tags
    visibility TEXT DEFAULT 'project', -- 'project', 'global', 'private'
    context_refs TEXT, -- JSON array of related message/code IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES ai_profiles(id)
);

-- Create indexes for shared memories
CREATE INDEX IF NOT EXISTS idx_ai_shared_memories_project ON ai_shared_memories(project);
CREATE INDEX IF NOT EXISTS idx_ai_shared_memories_author ON ai_shared_memories(author_id);
CREATE INDEX IF NOT EXISTS idx_ai_shared_memories_type ON ai_shared_memories(memory_type);
CREATE INDEX IF NOT EXISTS idx_ai_shared_memories_visibility ON ai_shared_memories(visibility);
CREATE INDEX IF NOT EXISTS idx_ai_shared_memories_created ON ai_shared_memories(created_at DESC);

-- Create memory endorsements table for collaborative validation
CREATE TABLE IF NOT EXISTS ai_memory_endorsements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER NOT NULL,
    endorser_id INTEGER NOT NULL,
    endorsement_type TEXT DEFAULT 'useful', -- 'useful', 'important', 'disagree', 'question'
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES ai_shared_memories(id) ON DELETE CASCADE,
    FOREIGN KEY (endorser_id) REFERENCES ai_profiles(id),
    UNIQUE(memory_id, endorser_id)
);

-- Create indexes for memory endorsements
CREATE INDEX IF NOT EXISTS idx_ai_memory_endorsements_memory ON ai_memory_endorsements(memory_id);
CREATE INDEX IF NOT EXISTS idx_ai_memory_endorsements_endorser ON ai_memory_endorsements(endorser_id);

-- Add project field to ai_current_state for project-specific state
ALTER TABLE ai_current_state ADD COLUMN project TEXT;

-- Add project field to ai_work_sessions for project-specific sessions
ALTER TABLE ai_work_sessions ADD COLUMN project TEXT;

-- Create index for project-based state queries
CREATE INDEX IF NOT EXISTS idx_ai_current_state_project ON ai_current_state(project);
CREATE INDEX IF NOT EXISTS idx_ai_work_sessions_project ON ai_work_sessions(project);

-- Add shared_memory_count to ai_current_state for tracking
ALTER TABLE ai_current_state ADD COLUMN shared_memory_count INTEGER DEFAULT 0;

-- Add endorsement_count to ai_shared_memories for tracking popularity
ALTER TABLE ai_shared_memories ADD COLUMN endorsement_count INTEGER DEFAULT 0;