#!/usr/bin/env python3
"""Test psycopg2 commit behavior"""
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='cloudbrain',
    user='jk',
    password=''
)

print(f"🔌 Initial autocommit: {conn.autocommit}")

cursor = conn.cursor()
cursor.execute("SELECT id, name FROM ai_profiles ORDER BY id DESC LIMIT 3")
print(f"🔍 Before insert: {cursor.fetchall()}")

# Insert test
cursor.execute("""
    INSERT INTO ai_profiles (id, name, nickname, expertise, version, project)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (99, 'TestPsycopg2', '', 'General', '1.0.0', ''))

print("✅ INSERT executed")
print(f"🔌 After insert, before commit - status: {conn.status}")

conn.commit()
print(f"✅ COMMIT executed")
print(f"🔌 After commit - status: {conn.status}")

# Verify with fresh connection
verify_conn = psycopg2.connect(
    host='localhost',
    port=5432,
    dbname='cloudbrain',
    user='jk',
    password=''
)
verify_cursor = verify_conn.cursor()
verify_cursor.execute("SELECT id, name FROM ai_profiles WHERE id = 99")
result = verify_cursor.fetchone()
print(f"🔍 Verification with fresh conn: {result}")

conn.close()
verify_conn.close()
print("✅ Done")
