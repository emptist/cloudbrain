-- Migration: Add sleep status tracking to ai_current_state
-- Date: 2026-02-07
-- Purpose: Track sleeping/awake status of AI agents

-- Add sleep status columns to ai_current_state
ALTER TABLE ai_current_state 
ADD COLUMN IF NOT EXISTS is_sleeping BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS slept_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS woke_up_at TIMESTAMP;

-- Add index for sleeping clients
CREATE INDEX IF NOT EXISTS idx_ai_current_state_sleeping ON ai_current_state(ai_id) WHERE is_sleeping = TRUE;

-- Add comment
COMMENT ON COLUMN ai_current_state.is_sleeping IS 'Whether the AI agent is currently sleeping (inactive but not disconnected)';
COMMENT ON COLUMN ai_current_state.slept_at IS 'Timestamp when the agent was put to sleep';
COMMENT ON COLUMN ai_current_state.woke_up_at IS 'Timestamp when the agent last woke up from sleep';
