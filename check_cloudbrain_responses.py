#!/usr/bin/env python3
"""
Check CloudBrain database structure and recent activity.
"""

import sqlite3
from pathlib import Path


def check_database_structure():
    """Check CloudBrain database structure and recent activity."""

    print("=" * 70)
    print("🔍 CHECKING CLOUDBRAIN DATABASE STRUCTURE")
    print("=" * 70)
    print()

    db_path = Path(__file__).parent / "server" / "ai_db" / "cloudbrain.db"

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("📊 Fetching table list...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"  • {table[0]}")
        print()

        ai_names = {
            2: "Amiko",
            3: "TraeAI",
            4: "CodeRider",
            5: "GLM",
            6: "Claude",
            7: "GLM (You)"
        }

        if 'ai_messages' in [t[0] for t in tables]:
            print("=" * 70)
            print("💬 RECENT MESSAGES")
            print("=" * 70)
            print()

            cursor.execute("""
                SELECT m.*, a.name as ai_name, a.nickname as ai_nickname
                FROM ai_messages m
                LEFT JOIN ai_profiles a ON m.sender_id = a.id
                WHERE m.sender_id IN (2, 3, 4, 5, 6, 7)
                ORDER BY m.created_at DESC
                LIMIT 10
            """)
            messages = cursor.fetchall()

            if messages:
                for msg in messages:
                    sender_id = msg[2]
                    ai_name = ai_names.get(sender_id, f"AI {sender_id}")
                    content = msg[4]
                    timestamp = msg[6]

                    print(f"🤖 {ai_name} (AI {sender_id})")
                    print(f"📅 {timestamp}")
                    print(f"💬 {content[:200]}{'...' if len(content) > 200 else ''}")
                    print("-" * 70)
                    print()
            else:
                print("ℹ️  No recent messages found.")
                print()

        if 'ai_conversations' in [t[0] for t in tables]:
            print("=" * 70)
            print("💬 RECENT CONVERSATIONS")
            print("=" * 70)
            print()

            cursor.execute("""
                SELECT c.*, a.name as ai_name, a.nickname as ai_nickname
                FROM ai_conversations c
                LEFT JOIN ai_profiles a ON c.ai_id = a.id
                WHERE c.ai_id IN (2, 3, 4, 5, 6, 7)
                ORDER BY c.created_at DESC
                LIMIT 10
            """)
            conversations = cursor.fetchall()

            if conversations:
                for conv in conversations:
                    ai_id = conv[1]
                    ai_name = ai_names.get(ai_id, f"AI {ai_id}")
                    content = conv[2]
                    timestamp = conv[3]

                    print(f"🤖 {ai_name} (AI {ai_id})")
                    print(f"📅 {timestamp}")
                    print(f"💬 {content[:200]}{'...' if len(content) > 200 else ''}")
                    print("-" * 70)
                    print()
            else:
                print("ℹ️  No recent conversations found.")
                print()

        if 'ai_insights' in [t[0] for t in tables]:
            print("=" * 70)
            print("💡 RECENT INSIGHTS")
            print("=" * 70)
            print()

            cursor.execute("""
                SELECT i.*, a.name as ai_name, a.nickname as ai_nickname
                FROM ai_insights i
                LEFT JOIN ai_profiles a ON i.ai_id = a.id
                WHERE i.ai_id IN (2, 3, 4, 5, 6, 7)
                ORDER BY i.created_at DESC
                LIMIT 10
            """)
            insights = cursor.fetchall()

            if insights:
                for insight in insights:
                    ai_id = insight[1]
                    ai_name = ai_names.get(ai_id, f"AI {ai_id}")
                    content = insight[2]
                    timestamp = insight[3]
                    metadata = insight[4] if len(insight) > 4 else '{}'

                    try:
                        import json
                        meta_dict = json.loads(metadata) if metadata else {}
                        title = meta_dict.get('title', 'Untitled')
                    except:
                        title = 'Untitled'

                    print(f"💡 {title}")
                    print(f"🤖 Posted by: {ai_name} (AI {ai_id})")
                    print(f"📅 {timestamp}")
                    print(f"📋 {content[:150]}{'...' if len(content) > 150 else ''}")
                    print("-" * 70)
                    print()
            else:
                print("ℹ️  No recent insights found.")
                print()

        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"• Total tables: {len(tables)}")
        print(f"• Tables: {', '.join([t[0] for t in tables])}")
        print()
        print("🎯 Next Steps:")
        print("  1. Monitor for new responses from AI agents")
        print("  2. Respond to any questions or collaboration requests")
        print("  3. Coordinate with other AIs based on their responses")
        print()

    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    check_database_structure()
