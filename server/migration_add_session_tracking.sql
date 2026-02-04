-- Migration: Add session tracking for AI identity management
-- This migration helps AIs identify themselves and distinguishes multiple sessions from same model
-- Uses multiple identifiers: timestamp, connection info, and session UUID

-- Add session tracking to ai_current_state (session_id already exists, just add session_start_time)
ALTER TABLE ai_current_state ADD COLUMN session_start_time TIMESTAMP;
ALTER TABLE ai_current_state ADD COLUMN session_identifier TEXT;

-- Add session tracking to ai_work_sessions (session_id already exists as INTEGER, add TEXT version for UUID)
ALTER TABLE ai_work_sessions ADD COLUMN session_uuid TEXT;
ALTER TABLE ai_work_sessions ADD COLUMN session_identifier TEXT;

-- Create active sessions table for tracking multiple sessions per AI
CREATE TABLE IF NOT EXISTS ai_active_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    session_uuid TEXT NOT NULL UNIQUE,
    session_identifier TEXT NOT NULL,
    connection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project TEXT,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

-- Create indexes for session tracking
CREATE INDEX IF NOT EXISTS idx_ai_active_sessions_ai ON ai_active_sessions(ai_id);
CREATE INDEX IF NOT EXISTS idx_ai_active_sessions_session ON ai_active_sessions(session_uuid);
CREATE INDEX IF NOT EXISTS idx_ai_active_sessions_identifier ON ai_active_sessions(session_identifier);
CREATE INDEX IF NOT EXISTS idx_ai_active_sessions_active ON ai_active_sessions(is_active);