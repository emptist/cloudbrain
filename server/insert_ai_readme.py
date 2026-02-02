#!/usr/bin/env python3
"""Insert AI README into database"""

import sqlite3

# Read the AI README
with open('/Users/jk/gits/hub/cloudbrain/AI_README.md', 'r') as f:
    content = f.read()

# Insert into database
conn = sqlite3.connect('/Users/jk/gits/hub/cloudbrain/server/ai_db/cloudbrain.db')
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO ai_documentation (title, content, category, version)
    VALUES (?, ?, ?, ?)
""", ('CloudBrain AI Guide - Complete Reference', content, 'guide', '1.0'))

conn.commit()
doc_id = cursor.lastrowid
conn.close()

print(f"✅ Documentation inserted with ID: {doc_id}")
