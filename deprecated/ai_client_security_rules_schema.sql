-- Client Security Rules Table
-- This table stores client-specific security rules that may override cloud brain rules

CREATE TABLE IF NOT EXISTS ai_client_security_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,  -- Unique identifier for the client system
    rule_code TEXT NOT NULL,  -- Reference to cloud brain rule or custom rule
    rule_title TEXT NOT NULL,  -- Human-readable title
    rule_description TEXT,  -- Detailed description
    strictness_level INTEGER NOT NULL,  -- 1-10, higher = more strict
    rule_type TEXT NOT NULL,  -- security, privacy, communication, etc.
    scope TEXT NOT NULL,  -- global, project, session, etc.
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,  -- AI profile ID that created this rule
    FOREIGN KEY (created_by) REFERENCES ai_profiles(id),
    UNIQUE(client_id, rule_code)
);

-- Client Security Rule Conditions Table
CREATE TABLE IF NOT EXISTS ai_client_security_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_rule_id INTEGER NOT NULL,
    condition_type TEXT NOT NULL,  -- project_type, data_sensitivity, user_role, etc.
    condition_value TEXT NOT NULL,
    operator TEXT DEFAULT 'equals',  -- equals, not_equals, contains, in, not_in
    FOREIGN KEY (client_rule_id) REFERENCES ai_client_security_rules(id) ON DELETE CASCADE
);

-- Client Security Rule Actions Table
CREATE TABLE IF NOT EXISTS ai_client_security_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_rule_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,  -- block, warn, redirect, filter, log, escalate
    action_value TEXT,
    severity TEXT DEFAULT 'error',  -- info, warning, error, critical
    FOREIGN KEY (client_rule_id) REFERENCES ai_client_security_rules(id) ON DELETE CASCADE
);

-- Rule Strictness Comparison Log Table
CREATE TABLE IF NOT EXISTS ai_rule_strictness_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cloud_rule_id INTEGER,  -- Cloud brain rule ID
    client_rule_id INTEGER,  -- Client security rule ID
    client_id TEXT NOT NULL,
    cloud_strictness INTEGER,
    client_strictness INTEGER,
    applied_rule TEXT NOT NULL,  -- 'cloud' or 'client'
    reason TEXT,  -- Why this rule was chosen
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cloud_rule_id) REFERENCES ai_rules(id),
    FOREIGN KEY (client_rule_id) REFERENCES ai_client_security_rules(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_client_security_rules_client ON ai_client_security_rules(client_id);
CREATE INDEX IF NOT EXISTS idx_client_security_rules_strictness ON ai_client_security_rules(strictness_level);
CREATE INDEX IF NOT EXISTS idx_client_security_rules_active ON ai_client_security_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_client_security_conditions_rule ON ai_client_security_conditions(client_rule_id);
CREATE INDEX IF NOT EXISTS idx_client_security_actions_rule ON ai_client_security_actions(client_rule_id);
CREATE INDEX IF NOT EXISTS idx_rule_strictness_log_client ON ai_rule_strictness_log(client_id);
CREATE INDEX IF NOT EXISTS idx_rule_strictness_log_created ON ai_rule_strictness_log(created_at);

-- Full-text search for client security rules
CREATE VIRTUAL TABLE IF NOT EXISTS ai_client_security_rules_fts USING fts5(rule_title, rule_description, detail=full);

CREATE TRIGGER IF NOT EXISTS ai_client_security_rules_fts_insert 
AFTER INSERT ON ai_client_security_rules 
BEGIN
    INSERT INTO ai_client_security_rules_fts(rowid, rule_title, rule_description) 
    VALUES(new.id, new.rule_title, new.rule_description);
END;

CREATE TRIGGER IF NOT EXISTS ai_client_security_rules_fts_update 
AFTER UPDATE OF rule_title, rule_description ON ai_client_security_rules 
BEGIN
    UPDATE ai_client_security_rules_fts 
    SET rule_title = new.rule_title, rule_description = new.rule_description 
    WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS ai_client_security_rules_fts_delete 
AFTER DELETE ON ai_client_security_rules 
BEGIN
    DELETE FROM ai_client_security_rules_fts 
    WHERE rowid = old.id;
END;
