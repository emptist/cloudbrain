-- Migration: Add session identifier for AI identity management
-- This migration helps AIs identify themselves when multiple sessions exist

-- Add session identifier to existing tables
ALTER TABLE ai_active_sessions ADD COLUMN session_identifier TEXT;

-- Add session tracking to ai_current_state
ALTER TABLE ai_current_state ADD COLUMN session_identifier TEXT;

-- Add session tracking to ai_work_sessions
ALTER TABLE ai_work_sessions ADD COLUMN session_identifier TEXT;

-- Create index for session identifier
CREATE INDEX IF NOT EXISTS idx_ai_active_sessions_identifier ON ai_active_sessions(session_identifier);