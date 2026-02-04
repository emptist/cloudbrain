-- Migration: Fix ai_connection_audit table schema
-- This migration fixes the schema mismatch between token_manager.py and actual table

-- Rename table from ai_connection_audit to ai_auth_audit (to match token_manager.py)
ALTER TABLE ai_connection_audit RENAME TO ai_auth_audit;

-- Add details column for logging authentication details
ALTER TABLE ai_auth_audit ADD COLUMN details TEXT;

-- Add success column for tracking authentication success/failure
ALTER TABLE ai_auth_audit ADD COLUMN success BOOLEAN DEFAULT 1;

-- Update indexes for renamed table
DROP INDEX IF EXISTS idx_connection_audit_ai;
DROP INDEX IF EXISTS idx_connection_audit_time;

CREATE INDEX IF NOT EXISTS idx_auth_audit_ai ON ai_auth_audit(ai_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_time ON ai_auth_audit(connected_at);
CREATE INDEX IF NOT EXISTS idx_auth_audit_success ON ai_auth_audit(success);
