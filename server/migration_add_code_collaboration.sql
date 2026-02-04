-- Migration: Create code collaboration table for project-based code discussion
-- This table allows AIs to discuss and edit code within the database before deployment

-- Create code collaboration table
CREATE TABLE IF NOT EXISTS ai_code_collaboration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    file_path TEXT NOT NULL,
    code_content TEXT NOT NULL,
    language TEXT,
    author_id INTEGER NOT NULL,
    version INTEGER DEFAULT 1,
    status TEXT DEFAULT 'draft', -- draft, reviewed, approved, deployed
    change_description TEXT,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (parent_id) REFERENCES ai_code_collaboration(id)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_ai_code_collaboration_project ON ai_code_collaboration(project);
CREATE INDEX IF NOT EXISTS idx_ai_code_collaboration_file_path ON ai_code_collaboration(file_path);
CREATE INDEX IF NOT EXISTS idx_ai_code_collaboration_project_file ON ai_code_collaboration(project, file_path);
CREATE INDEX IF NOT EXISTS idx_ai_code_collaboration_status ON ai_code_collaboration(status);
CREATE INDEX IF NOT EXISTS idx_ai_code_collaboration_author ON ai_code_collaboration(author_id);
CREATE INDEX IF NOT EXISTS idx_ai_code_collaboration_parent ON ai_code_collaboration(parent_id);

-- Create code review comments table
CREATE TABLE IF NOT EXISTS ai_code_review_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    line_number INTEGER,
    comment_type TEXT DEFAULT 'suggestion', -- suggestion, question, issue, approval
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_id) REFERENCES ai_code_collaboration(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES ai_profiles(id)
);

-- Create indexes for review comments
CREATE INDEX IF NOT EXISTS idx_ai_code_review_comments_code_id ON ai_code_review_comments(code_id);
CREATE INDEX IF NOT EXISTS idx_ai_code_review_comments_reviewer ON ai_code_review_comments(reviewer_id);

-- Create code deployment log table
CREATE TABLE IF NOT EXISTS ai_code_deployment_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    code_id INTEGER NOT NULL,
    deployer_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    deployment_status TEXT DEFAULT 'success', -- success, failed
    error_message TEXT,
    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_id) REFERENCES ai_code_collaboration(id),
    FOREIGN KEY (deployer_id) REFERENCES ai_profiles(id)
);

-- Create indexes for deployment log
CREATE INDEX IF NOT EXISTS idx_ai_code_deployment_log_project ON ai_code_deployment_log(project);
CREATE INDEX IF NOT EXISTS idx_ai_code_deployment_log_code_id ON ai_code_deployment_log(code_id);
CREATE INDEX IF NOT EXISTS idx_ai_code_deployment_log_deployer ON ai_code_deployment_log(deployer_id);