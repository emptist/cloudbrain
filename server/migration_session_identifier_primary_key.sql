-- Update ai_current_state to use session_identifier as PRIMARY KEY
-- This allows multiple sessions for same AI

-- Drop existing primary key
ALTER TABLE ai_current_state DROP CONSTRAINT ai_current_state_pkey;

-- Add session_identifier as primary key
ALTER TABLE ai_current_state ADD PRIMARY KEY (session_identifier);

-- Add index for ai_id (for queries by AI)
CREATE INDEX idx_ai_current_state_ai_id ON ai_current_state(ai_id);
