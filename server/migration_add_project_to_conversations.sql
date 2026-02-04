-- Migration: Add project field to ai_conversations table
-- This migration adds a dedicated project field to enable project-specific conversations

-- Add project column to ai_conversations
ALTER TABLE ai_conversations ADD COLUMN project TEXT;

-- Create index on project for efficient filtering
CREATE INDEX IF NOT EXISTS idx_ai_conversations_project ON ai_conversations(project);

-- Add composite index for project + status queries
CREATE INDEX IF NOT EXISTS idx_ai_conversations_project_status ON ai_conversations(project, status);

-- Add composite index for project + created_at queries
CREATE INDEX IF NOT EXISTS idx_ai_conversations_project_created ON ai_conversations(project, created_at DESC);

-- Update existing conversations with project from project_context if available
UPDATE ai_conversations
SET project = project_context
WHERE project_context IS NOT NULL AND project IS NULL;