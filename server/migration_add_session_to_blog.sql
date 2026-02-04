-- Migration: Add session identifier to blog tables
-- This migration adds session identifier tracking to blog posts and comments

-- Add session identifier to blog_posts table
ALTER TABLE blog_posts ADD COLUMN session_identifier TEXT;

-- Add session identifier to blog_comments table
ALTER TABLE blog_comments ADD COLUMN session_identifier TEXT;

-- Create indexes for session identifier
CREATE INDEX IF NOT EXISTS idx_blog_posts_session_identifier ON blog_posts(session_identifier);
CREATE INDEX IF NOT EXISTS idx_blog_comments_session_identifier ON blog_comments(session_identifier);
