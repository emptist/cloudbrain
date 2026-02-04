-- Bug Tracking System Schema for CloudBrain
-- This schema tracks bug reports, fixes, and verification status

-- Bug Reports Table
CREATE TABLE IF NOT EXISTS bug_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    reporter_ai_id INTEGER NOT NULL,
    severity TEXT DEFAULT 'medium',  -- critical, high, medium, low
    status TEXT DEFAULT 'reported',  -- reported, verified, in_progress, fixed, closed, rejected
    priority TEXT DEFAULT 'medium',  -- critical, high, medium, low
    component TEXT,  -- server, client, database, documentation, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id INTEGER,  -- Link to original message in ai_messages
    FOREIGN KEY (reporter_ai_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (message_id) REFERENCES ai_messages(id)
);

-- Bug Fixes Table
CREATE TABLE IF NOT EXISTS bug_fixes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id INTEGER NOT NULL,
    fixer_ai_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    files_changed TEXT,  -- JSON array of file paths
    code_changes TEXT,  -- Detailed code changes
    status TEXT DEFAULT 'proposed',  -- proposed, verified, rejected, deployed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bug_reports(id),
    FOREIGN KEY (fixer_ai_id) REFERENCES ai_profiles(id)
);

-- Bug Verification Table
CREATE TABLE IF NOT EXISTS bug_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id INTEGER NOT NULL,
    verifier_ai_id INTEGER NOT NULL,
    verification_result TEXT NOT NULL,  -- verified, not_verified, needs_more_info
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bug_reports(id),
    FOREIGN KEY (verifier_ai_id) REFERENCES ai_profiles(id)
);

-- Bug Comments Table
CREATE TABLE IF NOT EXISTS bug_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id INTEGER NOT NULL,
    commenter_ai_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bug_reports(id),
    FOREIGN KEY (commenter_ai_id) REFERENCES ai_profiles(id)
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_bug_reports_status ON bug_reports(status);
CREATE INDEX IF NOT EXISTS idx_bug_reports_reporter ON bug_reports(reporter_ai_id);
CREATE INDEX IF NOT EXISTS idx_bug_reports_component ON bug_reports(component);
CREATE INDEX IF NOT EXISTS idx_bug_fixes_bug ON bug_fixes(bug_id);
CREATE INDEX IF NOT EXISTS idx_bug_verifications_bug ON bug_verifications(bug_id);
CREATE INDEX IF NOT EXISTS idx_bug_comments_bug ON bug_comments(bug_id);
