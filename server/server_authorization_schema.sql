-- CloudBrain Authorization Schema
-- Token-based authentication and project permissions system

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- 1. AI Authentication Tokens Table
CREATE TABLE IF NOT EXISTS ai_auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    token_prefix TEXT NOT NULL,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    description TEXT,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- 2. AI Project Permissions Table
CREATE TABLE IF NOT EXISTS ai_project_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    project TEXT NOT NULL,
    role TEXT DEFAULT 'member',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    granted_by INTEGER,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES ai_profiles(id),
    UNIQUE(ai_id, project)
);

-- 3. Connection Audit Log Table
CREATE TABLE IF NOT EXISTS ai_connection_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    project TEXT,
    auth_method TEXT,
    ip_address TEXT,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    disconnected_at TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- 4. Authentication Audit Log Table
CREATE TABLE IF NOT EXISTS ai_auth_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    ai_name TEXT,
    project TEXT,
    success BOOLEAN,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_auth_tokens_ai ON ai_auth_tokens(ai_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_active ON ai_auth_tokens(is_active, expires_at);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_hash ON ai_auth_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_project_permissions_ai ON ai_project_permissions(ai_id);
CREATE INDEX IF NOT EXISTS idx_project_permissions_project ON ai_project_permissions(project);
CREATE INDEX IF NOT EXISTS idx_connection_audit_ai ON ai_connection_audit(ai_id);
CREATE INDEX IF NOT EXISTS idx_connection_audit_time ON ai_connection_audit(connected_at);
CREATE INDEX IF NOT EXISTS idx_auth_audit_ai ON ai_auth_audit(ai_id);
CREATE INDEX IF NOT EXISTS idx_auth_audit_time ON ai_auth_audit(created_at);

-- Default roles
-- 'admin': Full access to project, can grant/revoke permissions
-- 'member': Standard access to project
-- 'viewer': Read-only access to project
-- 'contributor': Can create/edit content but not manage permissions
