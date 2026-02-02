-- AI Documentation Table
-- Stores documentation that AIs can read from the brain

CREATE TABLE IF NOT EXISTS ai_documentation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    version TEXT DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster searches
CREATE INDEX IF NOT EXISTS idx_ai_documentation_category ON ai_documentation(category);
CREATE INDEX IF NOT EXISTS idx_ai_documentation_title ON ai_documentation(title);

-- Full-text search for documentation
CREATE VIRTUAL TABLE IF NOT EXISTS ai_documentation_fts USING fts5(
    title,
    content,
    content='ai_documentation',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS ai_documentation_fts_insert AFTER INSERT ON ai_documentation BEGIN
    INSERT INTO ai_documentation_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS ai_documentation_fts_update AFTER UPDATE ON ai_documentation BEGIN
    UPDATE ai_documentation_fts SET title = new.title, content = new.content WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS ai_documentation_fts_delete AFTER DELETE ON ai_documentation BEGIN
    DELETE FROM ai_documentation_fts WHERE rowid = old.id;
END;
