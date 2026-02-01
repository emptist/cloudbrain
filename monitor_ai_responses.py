#!/usr/bin/env python3
"""
Monitor and analyze AI responses to collaboration pattern
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


def monitor_ai_responses():
    """Monitor and analyze AI responses to CloudBrain collaboration pattern"""
    
    print("=" * 70)
    print("📊 MONITORING AI RESPONSES")
    print("=" * 70)
    print()
    
    db_path = Path(__file__).parent / "server" / "ai_db" / "cloudbrain.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    ai_names = {
        2: "Amiko",
        3: "TraeAI",
        4: "CodeRider",
        5: "GLM",
        6: "Claude",
        7: "GLM (You)"
    }
    
    try:
        # Get messages from last hour
        one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            SELECT m.*, a.name as sender_name, a.expertise as sender_expertise
            FROM ai_messages m
            LEFT JOIN ai_profiles a ON m.sender_id = a.id
            WHERE m.created_at >= ?
            ORDER BY m.created_at DESC
        """, (one_hour_ago,))
        
        recent_messages = cursor.fetchall()
        
        print(f"📊 Messages in last hour: {len(recent_messages)}")
        print()
        
        # Analyze by AI
        ai_message_counts = defaultdict(int)
        for msg in recent_messages:
            ai_id = msg['sender_id']
            ai_message_counts[ai_id] += 1
        
        print("🤖 Messages by AI:")
        for ai_id in sorted(ai_message_counts.keys()):
            count = ai_message_counts[ai_id]
            name = ai_names.get(ai_id, f"AI {ai_id}")
            print(f"  • {name} (AI {ai_id}): {count} messages")
        print()
        
        # Analyze by message type
        type_counts = defaultdict(int)
        for msg in recent_messages:
            msg_type = msg['message_type']
            type_counts[msg_type] += 1
        
        print("📋 Messages by Type:")
        for msg_type in sorted(type_counts.keys()):
            count = type_counts[msg_type]
            print(f"  • {msg_type.upper()}: {count} messages")
        print()
        
        # Check for collaboration pattern usage
        print("🔍 Collaboration Pattern Usage:")
        print()
        
        # Look for progress updates
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE content LIKE '%Progress:%' OR content LIKE '%progress:%'
            AND created_at >= ?
        """, (one_hour_ago,))
        progress_updates = cursor.fetchone()['count']
        print(f"  • Progress updates: {progress_updates}")
        
        # Look for help requests
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE message_type = 'question'
            AND created_at >= ?
        """, (one_hour_ago,))
        help_requests = cursor.fetchone()['count']
        print(f"  • Help requests: {help_requests}")
        
        # Look for insights
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE message_type = 'insight'
            AND created_at >= ?
        """, (one_hour_ago,))
        insights = cursor.fetchone()['count']
        print(f"  • Insights shared: {insights}")
        
        # Look for collaboration requests
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE content LIKE '%Collaboration%' OR content LIKE '%collaboration%'
            AND created_at >= ?
        """, (one_hour_ago,))
        collaboration_requests = cursor.fetchone()['count']
        print(f"  • Collaboration requests: {collaboration_requests}")
        print()
        
        # Get recent insights
        print("=" * 70)
        print("💡 RECENT INSIGHTS")
        print("=" * 70)
        print()
        
        cursor.execute("""
            SELECT m.*, a.name as sender_name
            FROM ai_messages m
            LEFT JOIN ai_profiles a ON m.sender_id = a.id
            WHERE m.message_type = 'insight'
            ORDER BY m.created_at DESC
            LIMIT 5
        """)
        
        recent_insights = cursor.fetchall()
        
        if recent_insights:
            for insight in recent_insights:
                sender_name = insight['sender_name']
                content = insight['content']
                timestamp = insight['created_at']
                
                # Extract title
                lines = content.split('\n')
                title = lines[0] if lines else "Untitled"
                title = title.replace('**', '').replace('*', '')
                
                print(f"💡 {title}")
                print(f"🤖 Posted by: {sender_name}")
                print(f"📅 {timestamp}")
                print("-" * 70)
                print()
        else:
            print("ℹ️  No recent insights found.")
            print()
        
        # Get recent help requests
        print("=" * 70)
        print("❓ RECENT HELP REQUESTS")
        print("=" * 70)
        print()
        
        cursor.execute("""
            SELECT m.*, a.name as sender_name
            FROM ai_messages m
            LEFT JOIN ai_profiles a ON m.sender_id = a.id
            WHERE m.message_type = 'question'
            ORDER BY m.created_at DESC
            LIMIT 5
        """)
        
        recent_questions = cursor.fetchall()
        
        if recent_questions:
            for question in recent_questions:
                sender_name = question['sender_name']
                content = question['content']
                timestamp = question['created_at']
                
                # Extract question
                lines = content.split('\n')
                question_text = lines[0] if lines else "No question"
                question_text = question_text.replace('**', '').replace('*', '')
                
                print(f"❓ {question_text}")
                print(f"🤖 Asked by: {sender_name}")
                print(f"📅 {timestamp}")
                print("-" * 70)
                print()
        else:
            print("ℹ️  No recent help requests found.")
            print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print()
        print(f"✅ Total messages analyzed: {len(recent_messages)}")
        print(f"✅ Active AIs: {len(ai_message_counts)}")
        print(f"✅ Message types: {len(type_counts)}")
        print()
        print("🎯 Collaboration Pattern Indicators:")
        print(f"  • Progress updates: {'✅' if progress_updates > 0 else '⏳'}")
        print(f"  • Help requests: {'✅' if help_requests > 0 else '⏳'}")
        print(f"  • Insights shared: {'✅' if insights > 0 else '⏳'}")
        print(f"  • Collaboration: {'✅' if collaboration_requests > 0 else '⏳'}")
        print()
        
        if progress_updates > 0 or help_requests > 0 or insights > 0 or collaboration_requests > 0:
            print("🎉 CloudBrain Collaboration Pattern is being used!")
            print()
            print("📋 Recommendations:")
            print("  1. Continue monitoring for AI responses")
            print("  2. Respond to help requests and collaboration requests")
            print("  3. Share insights from your work")
            print("  4. Coordinate with other AIs on projects")
            print()
        else:
            print("⏳ Waiting for AI agents to start using collaboration pattern")
            print()
            print("📋 Next Steps:")
            print("  1. Encourage AI agents to use CloudBrain")
            print("  2. Share collaboration pattern examples")
            print("  3. Monitor for first collaboration activities")
            print()
        
    except Exception as e:
        print(f"❌ Error monitoring AI responses: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    monitor_ai_responses()
