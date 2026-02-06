-- Add git status tracking to ai_current_state table
-- This enables brain state to track what files are being edited/added/deleted

ALTER TABLE ai_current_state ADD COLUMN modified_files TEXT[];
ALTER TABLE ai_current_state ADD COLUMN added_files TEXT[];
ALTER TABLE ai_current_state ADD COLUMN deleted_files TEXT[];
ALTER TABLE ai_current_state ADD COLUMN git_status TEXT;

-- Create indexes for querying by file changes
CREATE INDEX idx_ai_current_state_modified ON ai_current_state USING GIN (modified_files);
CREATE INDEX idx_ai_current_state_added ON ai_current_state USING GIN (added_files);
CREATE INDEX idx_ai_current_state_deleted ON ai_current_state USING GIN (deleted_files);
