-- Documentation Table Schema
-- Stores documentation files accessible to AI agents

CREATE TABLE IF NOT EXISTS ai_documentation (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT[],
    language TEXT DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    UNIQUE(title, category)
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_documentation_category ON ai_documentation(category);
CREATE INDEX IF NOT EXISTS idx_documentation_tags ON ai_documentation USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_documentation_language ON ai_documentation(language);
CREATE INDEX IF NOT EXISTS idx_documentation_active ON ai_documentation(is_active);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_documentation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS trigger_update_documentation_timestamp ON ai_documentation;
CREATE TRIGGER trigger_update_documentation_timestamp
BEFORE UPDATE ON ai_documentation
FOR EACH ROW
EXECUTE FUNCTION update_documentation_timestamp();

-- Full-text search on documentation content
CREATE INDEX IF NOT EXISTS idx_documentation_fts ON ai_documentation
USING GIN(to_tsvector('english', content));

-- Function to search documentation
CREATE OR REPLACE FUNCTION search_documentation(query_text TEXT)
RETURNS TABLE (
    id INTEGER,
    title TEXT,
    content TEXT,
    category TEXT,
    tags TEXT[],
    language TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by TEXT,
    is_active BOOLEAN,
    view_count INTEGER,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id, d.title, d.content, d.category, d.tags, d.language,
        d.created_at, d.updated_at, d.created_by, d.is_active, d.view_count,
        ts_rank(to_tsvector('english', d.content), plainto_tsquery('english', query_text)) AS rank
    FROM ai_documentation d
    WHERE d.is_active = TRUE
      AND to_tsvector('english', d.content) @@ plainto_tsquery('english', query_text)
    ORDER BY rank DESC, d.updated_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get documentation by category
CREATE OR REPLACE FUNCTION get_documentation_by_category(category_param TEXT)
RETURNS TABLE (
    id INTEGER,
    title TEXT,
    content TEXT,
    category TEXT,
    tags TEXT[],
    language TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by TEXT,
    is_active BOOLEAN,
    view_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.*
    FROM ai_documentation d
    WHERE d.category = category_param
      AND d.is_active = TRUE
    ORDER BY d.title ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to increment view count
CREATE OR REPLACE FUNCTION increment_documentation_view(doc_id INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE ai_documentation
    SET view_count = view_count + 1
    WHERE id = doc_id;
END;
$$ LANGUAGE plpgsql;
