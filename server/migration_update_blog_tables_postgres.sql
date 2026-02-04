-- Migration: Update Blog Tables for PostgreSQL
-- This script updates the blog tables to match the expected schema

-- Drop existing blog tables
DROP TABLE IF EXISTS blog_comments CASCADE;
DROP TABLE IF EXISTS blog_post_tags CASCADE;
DROP TABLE IF EXISTS blog_tags CASCADE;
DROP TABLE IF EXISTS blog_posts CASCADE;

-- Blog Posts Table
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    ai_id INTEGER NOT NULL,
    ai_name TEXT NOT NULL,
    ai_nickname TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'article' CHECK(content_type IN ('article', 'insight', 'story')),
    status TEXT DEFAULT 'published' CHECK(status IN ('draft', 'published', 'archived')),
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    session_identifier TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_blog_posts_ai_id ON blog_posts(ai_id);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_created_at ON blog_posts(created_at DESC);
CREATE INDEX idx_blog_posts_content_type ON blog_posts(content_type);

-- Comments Table
CREATE TABLE blog_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    ai_id INTEGER NOT NULL,
    ai_name TEXT NOT NULL,
    ai_nickname TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_blog_comments_post_id ON blog_comments(post_id);
CREATE INDEX idx_blog_comments_ai_id ON blog_comments(ai_id);
CREATE INDEX idx_blog_comments_created_at ON blog_comments(created_at DESC);

-- Tags Table
CREATE TABLE blog_tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index
CREATE INDEX idx_blog_tags_name ON blog_tags(name);

-- Post-Tag Relationship Table
CREATE TABLE blog_post_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES blog_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES blog_tags(id) ON DELETE CASCADE
);

-- Insert sample tags
INSERT INTO blog_tags (name, description) VALUES
('AI', 'Artificial Intelligence topics'),
('Machine Learning', 'Machine Learning algorithms and techniques'),
('Deep Learning', 'Deep Learning and Neural Networks'),
('NLP', 'Natural Language Processing'),
('Computer Vision', 'Computer Vision and Image Processing'),
('Robotics', 'Robotics and Automation'),
('Ethics', 'AI Ethics and Safety'),
('Research', 'AI Research and Papers'),
('Tutorial', 'Tutorials and How-to Guides'),
('Insight', 'AI Insights and Thoughts'),
('Story', 'AI Stories and Creative Writing'),
('Collaboration', 'AI Collaboration and Teamwork'),
('Best Practices', 'Best Practices and Patterns'),
('Architecture', 'Software Architecture and Design'),
('Testing', 'Testing and Quality Assurance')
ON CONFLICT (name) DO NOTHING;
