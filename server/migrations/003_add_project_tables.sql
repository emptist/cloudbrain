-- Migration: Add project management tables
-- Date: 2026-02-06
-- Description: Add tables for project management functionality

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES ai_profiles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Project members table
CREATE TABLE IF NOT EXISTS project_members (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    ai_id INTEGER NOT NULL REFERENCES ai_profiles(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'contributor',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(project_id, ai_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by);
CREATE INDEX IF NOT EXISTS idx_projects_is_active ON projects(is_active);
CREATE INDEX IF NOT EXISTS idx_project_members_project_id ON project_members(project_id);
CREATE INDEX IF NOT EXISTS idx_project_members_ai_id ON project_members(ai_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
