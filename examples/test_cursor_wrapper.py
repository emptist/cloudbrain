#!/usr/bin/env python3
"""Test CursorWrapper commit behavior"""
from db_config import get_db_connection, get_cursor

print("🔌 Getting connection via get_db_connection()...")
conn = get_db_connection()
print(f"🔌 Connection autocommit: {conn.autocommit}")

print("🔌 Getting cursor via get_cursor()...")
cursor = get_cursor()
print(f"🔌 Cursor type: {type(cursor)}")

print("🔍 Before insert:")
cursor.execute("SELECT id, name FROM ai_profiles ORDER BY id DESC LIMIT 3")
print(cursor.fetchall())

print("\n🔧 Inserting via CursorWrapper...")
cursor.execute("""
    INSERT INTO ai_profiles (id, name, nickname, expertise, version, project)
    VALUES (%s, %s, %s, %s, %s, %s)
""", (98, 'TestWrapper', '', 'General', '1.0.0', ''))

print("✅ INSERT executed via CursorWrapper")
print(f"🔌 Connection status after insert: {conn.status}")

print("\n🔧 Committing...")
conn.commit()
print(f"✅ COMMIT executed")
print(f"🔌 Connection status after commit: {conn.status}")

# Verify with fresh connection
print("\n🔍 Verifying with fresh connection...")
verify_conn = get_db_connection()
verify_cursor = verify_conn.cursor()
verify_cursor.execute("SELECT id, name FROM ai_profiles WHERE id = 98")
result = verify_cursor.fetchone()
print(f"🔍 Result: {result}")

conn.close()
verify_conn.close()
print("✅ Done")
