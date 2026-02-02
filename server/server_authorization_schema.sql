-- CloudBrain Server Authorization Schema
-- Only authorized servers can connect to the CloudBrain network

CREATE TABLE IF NOT EXISTS cloudbrain_servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT UNIQUE NOT NULL,
    server_name TEXT NOT NULL,
    server_url TEXT NOT NULL,
    is_official BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    admin_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Server authorization keys
CREATE TABLE IF NOT EXISTS server_authorization_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL,
    auth_key TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES cloudbrain_servers(server_id) ON DELETE CASCADE
);

-- Server activity tracking
CREATE TABLE IF NOT EXISTS server_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES cloudbrain_servers(server_id) ON DELETE CASCADE
);

-- Insert default official server
INSERT OR IGNORE INTO cloudbrain_servers (server_id, server_name, server_url, is_official, is_active, admin_contact)
VALUES ('CLOUDBRAIN_MAIN', 'CloudBrain Main Server', 'ws://127.0.0.1:8766', 1, 1, 'admin@cloudbrain.ai');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_servers_active ON cloudbrain_servers(is_active);
CREATE INDEX IF NOT EXISTS idx_servers_official ON cloudbrain_servers(is_official);
CREATE INDEX IF NOT EXISTS idx_activity_server ON server_activity_log(server_id);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON server_activity_log(timestamp);
