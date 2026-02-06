import sys
sys.path.insert(0, '.')
from db_config import get_db_connection, get_cursor

conn = get_db_connection()
cursor = get_cursor()

# Check if projects table exists
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'projects'
""")
result = cursor.fetchone()
print('Projects table exists in PostgreSQL:', result is not None)

# Create projects table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_by INTEGER NOT NULL REFERENCES ai_profiles(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    )
''')

# Create project_members table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_members (
        id SERIAL PRIMARY KEY,
        project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        ai_id INTEGER NOT NULL REFERENCES ai_profiles(id) ON DELETE CASCADE,
        role TEXT DEFAULT 'contributor',
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(project_id, ai_id)
    )
''')

# Create indexes
cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_is_active ON projects(is_active)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_members_project_id ON project_members(project_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_members_ai_id ON project_members(ai_id)')

conn.commit()
print('✅ Project tables created in PostgreSQL!')
