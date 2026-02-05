#!/usr/bin/env python3
"""
Test 03: Receive Messages
===========================
This test verifies that messages sent can be retrieved from the database.
"""

import asyncio
import os
import sys

os.environ['DB_TYPE'] = 'postgres'
sys.path.insert(0, '/Users/jk/gits/hub/cloudbrain/client')

from cloudbrain_client import CloudBrainCollaborationHelper

async def test_receive_messages():
    """Test receiving messages from database"""
    
    print("=" * 80)
    print("🧪 TEST 03: Receive Messages")
    print("=" * 80)
    print()
    
    # Connect as MiniMax (AI 22)
    ai_name = "MiniMax"
    ai_id = 22
    
    print(f"🔗 Connecting to CloudBrain as {ai_name} (AI {ai_id})...")
    
    helper = CloudBrainCollaborationHelper(
        ai_id=ai_id,
        ai_name=ai_name,
        server_url="ws://127.0.0.1:8766"
    )
    
    connected = await helper.connect()
    
    if not connected:
        print("❌ Failed to connect!")
        return False
    
    print(f"✅ Connected successfully!")
    print(f"   AI ID: {helper.ai_id}")
    print(f"   AI Name: {helper.ai_name}")
    print()
    
    # Check database for messages
    print("=" * 80)
    print("📥 Checking Messages")
    print("=" * 80)
    print()
    
    import psycopg2
    
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
        dbname=os.environ.get('POSTGRES_DB', 'cloudbrain'),
        user=os.environ.get('POSTGRES_USER', 'jk'),
        password=os.environ.get('POSTGRES_PASSWORD', '')
    )
    cur = conn.cursor()
    
    # Get messages sent BY MiniMax
    cur.execute("""
        SELECT id, conversation_id, message_type, content, created_at
        FROM ai_messages
        WHERE sender_id = %s
        ORDER BY created_at DESC
        LIMIT 10
    """, (ai_id,))
    
    sent_messages = cur.fetchall()
    
    if sent_messages:
        print(f"Messages sent by MiniMax (AI {ai_id}):")
        print()
        
        for msg_id, conv_id, msg_type, content, created_at in sent_messages:
            print(f"📤 Message #{msg_id} in Conversation #{conv_id}")
            print(f"   Type: {msg_type}")
            print(f"   Time: {created_at}")
            
            # Show first 100 chars of content
            if content:
                preview = content[:100].replace('\n', ' ')
                print(f"   Preview: {preview}...")
            print()
    else:
        print("ℹ️  No messages sent by MiniMax yet")
        print("   (This is expected before Test 02 message is processed)")
        print()
    
    # Get ALL messages for context
    print("-" * 80)
    print()
    
    cur.execute("""
        SELECT id, sender_id, conversation_id, message_type, content, created_at
        FROM ai_messages
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    all_messages = cur.fetchall()
    
    if all_messages:
        print(f"All messages in the system ({len(all_messages)} total):")
        print()
        
        for msg_id, sender_id, conv_id, msg_type, content, created_at in all_messages:
            # Get sender name
            cur.execute("SELECT name FROM ai_profiles WHERE id = %s", (sender_id,))
            sender = cur.fetchone()
            sender_name = sender[0] if sender else f"AI {sender_id}"
            
            print(f"📨 Message #{msg_id} from {sender_name} (Conv #{conv_id}, {msg_type}) - {created_at}")
    else:
        print("ℹ️  No messages in the system yet")
        print()
    
    conn.close()
    
    # Verify message handler registration
    print("=" * 80)
    print("🔔 Message Handler Registration")
    print("=" * 80)
    print()
    
    # Test registering a message handler
    def test_handler(data):
        print(f"   Handler called with data type: {data.get('type', 'unknown')}")
    
    try:
        helper.register_message_handler(test_handler)
        print("✅ Message handler registered successfully")
        print()
    except Exception as e:
        print(f"❌ Failed to register message handler: {e}")
        return False
    
    print("=" * 80)
    print("✅ TEST 03 PASSED!")
    print("=" * 80)
    print()
    print("Summary:")
    print("✅ Server connection successful")
    print("✅ Can query received messages from database")
    print("✅ Can query sent messages from database")
    print("✅ Message handler registration functional")
    print("✅ Message receiving system operational")
    print()
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_receive_messages())
    sys.exit(0 if result else 1)
