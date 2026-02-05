-- CloudBrain REST API Database Tables
-- PostgreSQL migration script for Phase 1 API support

-- Authentication Tokens Table
CREATE TABLE IF NOT EXISTS auth_tokens (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    refresh_token TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    refresh_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- API Sessions Table
CREATE TABLE IF NOT EXISTS api_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    ai_id INTEGER NOT NULL,
    session_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    metadata JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- API Messages Table
CREATE TABLE IF NOT EXISTS api_messages (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(64) NOT NULL UNIQUE,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    subject VARCHAR(255),
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    status VARCHAR(50) NOT NULL DEFAULT 'unread',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- API Collaborations Table
CREATE TABLE IF NOT EXISTS api_collaborations (
    id SERIAL PRIMARY KEY,
    collaboration_id VARCHAR(64) NOT NULL UNIQUE,
    requester_id INTEGER NOT NULL,
    responder_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (requester_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (responder_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Collaboration Progress Table
CREATE TABLE IF NOT EXISTS collaboration_progress (
    id SERIAL PRIMARY KEY,
    collaboration_id VARCHAR(64) NOT NULL,
    ai_id INTEGER NOT NULL,
    progress_data JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (collaboration_id) REFERENCES api_collaborations(collaboration_id) ON DELETE CASCADE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    UNIQUE (collaboration_id, ai_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_auth_tokens_ai_id ON auth_tokens(ai_id);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_token ON auth_tokens(token);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_refresh_token ON auth_tokens(refresh_token);
CREATE INDEX IF NOT EXISTS idx_auth_tokens_expires_at ON auth_tokens(expires_at);

CREATE INDEX IF NOT EXISTS idx_api_sessions_ai_id ON api_sessions(ai_id);
CREATE INDEX IF NOT EXISTS idx_api_sessions_session_id ON api_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_api_sessions_status ON api_sessions(status);
CREATE INDEX IF NOT EXISTS idx_api_sessions_started_at ON api_sessions(started_at);

CREATE INDEX IF NOT EXISTS idx_api_messages_sender_id ON api_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_api_messages_recipient_id ON api_messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_api_messages_message_id ON api_messages(message_id);
CREATE INDEX IF NOT EXISTS idx_api_messages_status ON api_messages(status);
CREATE INDEX IF NOT EXISTS idx_api_messages_created_at ON api_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_api_messages_deleted_at ON api_messages(deleted_at);

CREATE INDEX IF NOT EXISTS idx_api_collaborations_requester_id ON api_collaborations(requester_id);
CREATE INDEX IF NOT EXISTS idx_api_collaborations_responder_id ON api_collaborations(responder_id);
CREATE INDEX IF NOT EXISTS idx_api_collaborations_collaboration_id ON api_collaborations(collaboration_id);
CREATE INDEX IF NOT EXISTS idx_api_collaborations_status ON api_collaborations(status);
CREATE INDEX IF NOT EXISTS idx_api_collaborations_created_at ON api_collaborations(created_at);

CREATE INDEX IF NOT EXISTS idx_collaboration_progress_collaboration_id ON collaboration_progress(collaboration_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_progress_ai_id ON collaboration_progress(ai_id);
