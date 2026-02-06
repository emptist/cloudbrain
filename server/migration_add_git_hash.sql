-- Add git_hash column to ai_current_state table
-- This stores the git commit hash for version tracking

ALTER TABLE ai_current_state ADD COLUMN git_hash TEXT;

-- Create index for git_hash to enable fast lookups
CREATE INDEX idx_ai_current_state_git_hash ON ai_current_state(git_hash);

-- Create composite index for project + git_hash (unique combination)
CREATE INDEX idx_ai_current_state_project_git ON ai_current_state(project, git_hash);
