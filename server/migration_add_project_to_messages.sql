-- Migration: Add project field to ai_messages table
-- This migration adds a dedicated project field to enable efficient project-based filtering

-- Add project column to ai_messages
ALTER TABLE ai_messages ADD COLUMN project TEXT;

-- Create index on project for efficient filtering
CREATE INDEX IF NOT EXISTS idx_ai_messages_project ON ai_messages(project);

-- Update existing messages with project from metadata if available
UPDATE ai_messages
SET project = json_extract(metadata, '$.project')
WHERE metadata IS NOT NULL AND json_extract(metadata, '$.project') IS NOT NULL;

-- Add composite index for project + created_at queries
CREATE INDEX IF NOT EXISTS idx_ai_messages_project_created ON ai_messages(project, created_at DESC);

-- Add composite index for project + sender queries
CREATE INDEX IF NOT EXISTS idx_ai_messages_project_sender ON ai_messages(project, sender_id);