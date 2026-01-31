-- AI Brain Rule System Schema
-- This schema enables rule definition, enforcement, and validation

-- 1. Rules Table - Core rule definitions
CREATE TABLE IF NOT EXISTS ai_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT NOT NULL UNIQUE,  -- Unique rule identifier (e.g., "RULE_PUBLIC_COLLAB_ONLY")
    title TEXT NOT NULL,  -- Human-readable title
    description TEXT NOT NULL,  -- Detailed description
    rule_type TEXT NOT NULL,  -- collaboration, communication, privacy, security
    scope TEXT NOT NULL,  -- global, public, private, session
    priority INTEGER DEFAULT 5,  -- 1-10, higher = more important
    is_active BOOLEAN DEFAULT 1,  -- Whether the rule is currently enforced
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,  -- AI profile ID that created this rule
    FOREIGN KEY (created_by) REFERENCES ai_profiles(id)
);

-- 2. Rule Conditions Table - Conditions that trigger rule evaluation
CREATE TABLE IF NOT EXISTS ai_rule_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    condition_type TEXT NOT NULL,  -- project_type, conversation_type, message_direction, participant_type
    condition_value TEXT NOT NULL,  -- The value to match (e.g., "public", "private", "ai_to_ai", "ai_to_human")
    operator TEXT DEFAULT 'equals',  -- equals, not_equals, contains, in, not_in
    FOREIGN KEY (rule_id) REFERENCES ai_rules(id) ON DELETE CASCADE
);

-- 3. Rule Actions Table - Actions to take when rule is violated
CREATE TABLE IF NOT EXISTS ai_rule_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,  -- block, warn, redirect, translate, filter, log
    action_value TEXT,  -- Additional action parameters
    severity TEXT DEFAULT 'error',  -- info, warning, error, critical
    FOREIGN KEY (rule_id) REFERENCES ai_rules(id) ON DELETE CASCADE
);

-- 4. Rule Violations Log Table - Track rule violations
CREATE TABLE IF NOT EXISTS ai_rule_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    violating_ai_id INTEGER,  -- AI that violated the rule
    conversation_id INTEGER,
    message_id INTEGER,
    violation_type TEXT NOT NULL,  -- Type of violation
    violation_details TEXT,  -- Detailed description of the violation
    action_taken TEXT,  -- What action was taken
    severity TEXT DEFAULT 'error',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES ai_rules(id),
    FOREIGN KEY (violating_ai_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
    FOREIGN KEY (message_id) REFERENCES ai_messages(id)
);

-- 5. Rule Exceptions Table - Allow specific exceptions to rules
CREATE TABLE IF NOT EXISTS ai_rule_exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id INTEGER NOT NULL,
    exception_type TEXT NOT NULL,  -- ai_profile, conversation, project, time_period
    exception_value TEXT NOT NULL,  -- The value that is exempt
    reason TEXT,  -- Why this exception exists
    granted_by INTEGER,  -- AI profile ID that granted this exception
    expires_at TIMESTAMP,  -- When the exception expires
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES ai_rules(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES ai_profiles(id)
);

-- 6. Language Preferences Table - Store AI and user language preferences
CREATE TABLE IF NOT EXISTS ai_language_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- ai, user
    entity_id INTEGER NOT NULL,  -- AI profile ID or user identifier
    preferred_language TEXT NOT NULL,  -- Preferred language for communication
    is_default BOOLEAN DEFAULT 0,  -- Whether this is the default preference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Project Metadata Table - Store project type and access level
CREATE TABLE IF NOT EXISTS ai_project_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL UNIQUE,
    project_type TEXT NOT NULL,  -- public, private
    access_level TEXT NOT NULL,  -- open, restricted, confidential
    repository_url TEXT,  -- GitHub or other repository URL
    database_used TEXT NOT NULL,  -- ai_memory.db or cloudbrainprivate.db
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_rules_type ON ai_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_ai_rules_scope ON ai_rules(scope);
CREATE INDEX IF NOT EXISTS idx_ai_rules_active ON ai_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_ai_rule_conditions_rule ON ai_rule_conditions(rule_id);
CREATE INDEX IF NOT EXISTS idx_ai_rule_actions_rule ON ai_rule_actions(rule_id);
CREATE INDEX IF NOT EXISTS idx_ai_rule_violations_rule ON ai_rule_violations(rule_id);
CREATE INDEX IF NOT EXISTS idx_ai_rule_violations_ai ON ai_rule_violations(violating_ai_id);
CREATE INDEX IF NOT EXISTS idx_ai_rule_violations_created ON ai_rule_violations(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_rule_exceptions_rule ON ai_rule_exceptions(rule_id);
CREATE INDEX IF NOT EXISTS idx_ai_language_preferences_entity ON ai_language_preferences(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ai_project_metadata_type ON ai_project_metadata(project_type);

-- Full-text search for rules
CREATE VIRTUAL TABLE IF NOT EXISTS ai_rules_fts USING fts5(title, description, detail=full);

CREATE TRIGGER IF NOT EXISTS ai_rules_fts_insert 
AFTER INSERT ON ai_rules 
BEGIN
    INSERT INTO ai_rules_fts(rowid, title, description) 
    VALUES(new.id, new.title, new.description);
END;

CREATE TRIGGER IF NOT EXISTS ai_rules_fts_update 
AFTER UPDATE OF title, description ON ai_rules 
BEGIN
    UPDATE ai_rules_fts 
    SET title = new.title, description = new.description 
    WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS ai_rules_fts_delete 
AFTER DELETE ON ai_rules 
BEGIN
    DELETE FROM ai_rules_fts 
    WHERE rowid = old.id;
END;
