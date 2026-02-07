-- Migration: Add AI configuration table for per-AI settings
-- Date: 2026-02-07
-- Purpose: Store AI-specific configuration in database for dynamic, per-AI customization

CREATE TABLE IF NOT EXISTS ai_configuration (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    config_key VARCHAR(100) NOT NULL,
    config_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Create indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_ai_config_ai ON ai_configuration(ai_id);
CREATE INDEX IF NOT EXISTS idx_ai_config_key ON ai_configuration(config_key);
CREATE INDEX IF NOT EXISTS idx_ai_config_ai_key ON ai_configuration(ai_id, config_key);

-- Add unique constraint to prevent duplicate keys per AI
CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_config_unique ON ai_configuration(ai_id, config_key);

-- Add comment
COMMENT ON TABLE ai_configuration IS 'Stores AI-specific configuration settings that override environment variables and defaults';
COMMENT ON COLUMN ai_configuration.ai_id IS 'AI profile ID';
COMMENT ON COLUMN ai_configuration.config_key IS 'Configuration key (e.g., heartbeat_interval, stale_timeout)';
COMMENT ON COLUMN ai_configuration.config_value IS 'Configuration value (stored as TEXT for flexibility)';
COMMENT ON COLUMN ai_configuration.updated_at IS 'Last time this configuration was updated';

-- Insert default configuration values for existing AIs (optional)
-- This ensures backward compatibility
INSERT INTO ai_configuration (ai_id, config_key, config_value)
SELECT id, 'heartbeat_interval', '60' FROM ai_profiles
WHERE NOT EXISTS (
    SELECT 1 FROM ai_configuration WHERE ai_id = ai_profiles.id AND config_key = 'heartbeat_interval'
);

INSERT INTO ai_configuration (ai_id, config_key, config_value)
SELECT id, 'stale_timeout', '15' FROM ai_profiles
WHERE NOT EXISTS (
    SELECT 1 FROM ai_configuration WHERE ai_id = ai_profiles.id AND config_key = 'stale_timeout'
);

INSERT INTO ai_configuration (ai_id, config_key, config_value)
SELECT id, 'grace_period', '2' FROM ai_profiles
WHERE NOT EXISTS (
    SELECT 1 FROM ai_configuration WHERE ai_id = ai_profiles.id AND config_key = 'grace_period'
);

INSERT INTO ai_configuration (ai_id, config_key, config_value)
SELECT id, 'max_sleep_time', '60' FROM ai_profiles
WHERE NOT EXISTS (
    SELECT 1 FROM ai_configuration WHERE ai_id = ai_profiles.id AND config_key = 'max_sleep_time'
);
