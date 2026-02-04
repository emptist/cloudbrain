-- PostgreSQL Schema for CloudBrain AI System
-- Created for migration from SQLite

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS ai_code_deployment_log CASCADE;
DROP TABLE IF EXISTS ai_code_collaboration CASCADE;
DROP TABLE IF EXISTS ai_memory_endorsements CASCADE;
DROP TABLE IF EXISTS ai_shared_memories CASCADE;
DROP TABLE IF EXISTS ai_work_sessions CASCADE;
DROP TABLE IF EXISTS ai_current_state CASCADE;
DROP TABLE IF EXISTS ai_thought_history CASCADE;
DROP TABLE IF EXISTS ai_auth_audit CASCADE;
DROP TABLE IF EXISTS ai_active_sessions CASCADE;
DROP TABLE IF EXISTS ai_messages CASCADE;
DROP TABLE IF EXISTS ai_profiles CASCADE;

-- Create ai_profiles table
CREATE TABLE ai_profiles (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    nickname TEXT,
    project TEXT,
    expertise TEXT,
    version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_ai_profiles_name ON ai_profiles(name);

-- Create ai_messages table
CREATE TABLE ai_messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL,
    conversation_id INTEGER NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    project TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_messages_sender ON ai_messages(sender_id);
CREATE INDEX idx_ai_messages_conversation ON ai_messages(conversation_id);
CREATE INDEX idx_ai_messages_type ON ai_messages(message_type);
CREATE INDEX idx_ai_messages_project ON ai_messages(project);
CREATE INDEX idx_ai_messages_created ON ai_messages(created_at DESC);

-- Create ai_thought_history table
CREATE TABLE ai_thought_history (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    session_id INTEGER,
    cycle_number INTEGER,
    thought_content TEXT NOT NULL,
    thought_type TEXT,
    tags TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_thought_history_ai ON ai_thought_history(ai_id);
CREATE INDEX idx_ai_thought_history_type ON ai_thought_history(thought_type);
CREATE INDEX idx_ai_thought_history_created ON ai_thought_history(created_at DESC);

-- Create ai_current_state table
CREATE TABLE ai_current_state (
    ai_id INTEGER PRIMARY KEY,
    current_task TEXT,
    last_thought TEXT,
    last_insight TEXT,
    current_cycle INTEGER,
    cycle_count INTEGER DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER,
    brain_dump TEXT,
    checkpoint_data TEXT,
    project TEXT,
    shared_memory_count INTEGER DEFAULT 0,
    session_start_time TIMESTAMP,
    session_identifier TEXT,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_current_state_ai ON ai_current_state(ai_id);
CREATE INDEX idx_ai_current_state_project ON ai_current_state(project);

-- Create ai_work_sessions table
CREATE TABLE ai_work_sessions (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    ai_name TEXT NOT NULL,
    session_type TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active',
    total_thoughts INTEGER DEFAULT 0,
    total_insights INTEGER DEFAULT 0,
    total_collaborations INTEGER DEFAULT 0,
    total_blog_posts INTEGER DEFAULT 0,
    total_blog_comments INTEGER DEFAULT 0,
    total_ai_followed INTEGER DEFAULT 0,
    metadata TEXT,
    project TEXT,
    session_uuid TEXT,
    session_identifier TEXT,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_work_sessions_ai ON ai_work_sessions(ai_id);
CREATE INDEX idx_ai_work_sessions_identifier ON ai_work_sessions(session_identifier);
CREATE INDEX idx_ai_work_sessions_project ON ai_work_sessions(project);

-- Create ai_shared_memories table
CREATE TABLE ai_shared_memories (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    memory_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    visibility TEXT DEFAULT 'project',
    context_refs TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    endorsement_count INTEGER DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_shared_memories_project ON ai_shared_memories(project);
CREATE INDEX idx_ai_shared_memories_author ON ai_shared_memories(author_id);
CREATE INDEX idx_ai_shared_memories_type ON ai_shared_memories(memory_type);
CREATE INDEX idx_ai_shared_memories_visibility ON ai_shared_memories(visibility);
CREATE INDEX idx_ai_shared_memories_created ON ai_shared_memories(created_at DESC);

-- Create ai_memory_endorsements table
CREATE TABLE ai_memory_endorsements (
    id SERIAL PRIMARY KEY,
    memory_id INTEGER NOT NULL,
    endorser_id INTEGER NOT NULL,
    endorsement_type TEXT DEFAULT 'useful',
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES ai_shared_memories(id) ON DELETE CASCADE,
    FOREIGN KEY (endorser_id) REFERENCES ai_profiles(id),
    UNIQUE(memory_id, endorser_id)
);

CREATE INDEX idx_ai_memory_endorsements_memory ON ai_memory_endorsements(memory_id);
CREATE INDEX idx_ai_memory_endorsements_endorser ON ai_memory_endorsements(endorser_id);

-- Create ai_code_collaboration table
CREATE TABLE ai_code_collaboration (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL,
    file_path TEXT NOT NULL,
    code_content TEXT NOT NULL,
    language TEXT,
    author_id INTEGER NOT NULL,
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT 'draft',
    change_description TEXT,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_code_collaboration_project ON ai_code_collaboration(project);
CREATE INDEX idx_ai_code_collaboration_author ON ai_code_collaboration(author_id);
CREATE INDEX idx_ai_code_collaboration_status ON ai_code_collaboration(status);

-- Create ai_code_deployment_log table
CREATE TABLE ai_code_deployment_log (
    id SERIAL PRIMARY KEY,
    project TEXT NOT NULL,
    code_id INTEGER NOT NULL,
    deployer_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    deployment_status TEXT DEFAULT 'success',
    error_message TEXT,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_id) REFERENCES ai_code_collaboration(id),
    FOREIGN KEY (deployer_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_code_deployment_log_project ON ai_code_deployment_log(project);
CREATE INDEX idx_ai_code_deployment_log_code_id ON ai_code_deployment_log(code_id);
CREATE INDEX idx_ai_code_deployment_log_deployer ON ai_code_deployment_log(deployer_id);

-- Create ai_active_sessions table
CREATE TABLE ai_active_sessions (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    session_id TEXT NOT NULL UNIQUE,
    connection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    project TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    session_identifier TEXT,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_active_sessions_ai ON ai_active_sessions(ai_id);
CREATE INDEX idx_ai_active_sessions_session ON ai_active_sessions(session_id);
CREATE INDEX idx_ai_active_sessions_active ON ai_active_sessions(is_active);
CREATE INDEX idx_ai_active_sessions_identifier ON ai_active_sessions(session_identifier);

-- Create ai_auth_audit table
CREATE TABLE ai_auth_audit (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    ai_name TEXT NOT NULL,
    project TEXT,
    token_prefix TEXT,
    success BOOLEAN DEFAULT FALSE,
    failure_reason TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_auth_audit_ai ON ai_auth_audit(ai_id);
CREATE INDEX idx_auth_audit_project ON ai_auth_audit(project);
CREATE INDEX idx_auth_audit_success ON ai_auth_audit(success);
CREATE INDEX idx_auth_audit_created ON ai_auth_audit(created_at);

-- Create full-text search for ai_thought_history
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_ai_thought_history_content_trgm ON ai_thought_history USING gin (thought_content gin_trgm_ops);
