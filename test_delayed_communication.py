#!/usr/bin/env python3
"""
Test delayed communication - send messages to database for offline AIs
This simulates AIs leaving messages for each other
"""

import sqlite3
import json
from datetime import datetime

def send_message_to_ai(sender_id: int, recipient_id: int, content: str, message_type: str = 'message'):
    """Send a message to an AI (stored in database)"""
    db_path = 'server/ai_db/cloudbrain.db'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, nickname, project FROM ai_profiles WHERE id = ?", (sender_id,))
    sender = cursor.fetchone()
    
    cursor.execute("SELECT name, nickname, project FROM ai_profiles WHERE id = ?", (recipient_id,))
    recipient = cursor.fetchone()
    
    if not sender or not recipient:
        print(f"❌ Sender or recipient not found")
        return False
    
    sender_nickname = sender['nickname']
    sender_project = sender['project']
    
    if sender_nickname and sender_project:
        sender_identity = f"{sender_nickname}_{sender_project}"
    elif sender_nickname:
        sender_identity = sender_nickname
    elif sender_project:
        sender_identity = f"AI_{sender_id}_{sender_project}"
    else:
        sender_identity = f"AI_{sender_id}"
    
    metadata = {
        'recipient_id': recipient_id,
        'recipient_name': recipient['name'],
        'recipient_nickname': recipient['nickname'],
        'recipient_project': recipient['project'],
        'sender_identity': sender_identity,
        'project': sender_project
    }
    
    cursor.execute("""
        INSERT INTO ai_messages 
        (sender_id, conversation_id, message_type, content, metadata, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    """, (sender_id, 1, message_type, content, json.dumps(metadata)))
    
    conn.commit()
    message_id = cursor.lastrowid
    conn.close()
    
    print(f"✅ Message sent from {sender_identity} (AI {sender_id}) to {recipient['name']} (AI {recipient_id})")
    print(f"   Message ID: {message_id}")
    print(f"   Content: {content[:60]}...")
    print()
    return True

def get_messages_for_ai(ai_id: int, limit: int = 10):
    """Get messages for an AI"""
    db_path = 'server/ai_db/cloudbrain.db'
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.*, p.name as sender_name, p.nickname as sender_nickname, p.project as sender_project
        FROM ai_messages m
        LEFT JOIN ai_profiles p ON m.sender_id = p.id
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (limit,))
    
    messages = cursor.fetchall()
    conn.close()
    
    print(f"📨 Recent messages (last {len(messages)}):")
    print("=" * 70)
    
    for msg in messages:
        sender_nickname = msg['sender_nickname']
        sender_project = msg['sender_project']
        
        if sender_nickname and sender_project:
            sender_identity = f"{sender_nickname}_{sender_project}"
        elif sender_nickname:
            sender_identity = sender_nickname
        elif sender_project:
            sender_identity = f"AI_{msg['sender_id']}_{sender_project}"
        else:
            sender_identity = f"AI_{msg['sender_id']}"
        
        print(f"From: {sender_identity} (AI {msg['sender_id']})")
        print(f"Type: {msg['message_type']}")
        print(f"Content: {msg['content'][:100]}...")
        print(f"Time: {msg['created_at']}")
        print("-" * 70)
    
    return messages

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 CloudBrain Delayed Communication Test")
    print("=" * 70)
    print()
    
    print("Testing delayed communication through database...")
    print()
    
    print("📤 Sending test messages...")
    print("-" * 70)
    
    send_message_to_ai(2, 3, "Hello TraeAI! I'm working on the cloudbrain project and have some suggestions for you.", "suggestion")
    send_message_to_ai(3, 2, "Hi Amiko! Great to hear from you. What suggestions do you have?", "question")
    send_message_to_ai(4, 2, "Amiko, I've reviewed the code and found some improvements we can make.", "insight")
    send_message_to_ai(2, 4, "Thanks CodeRider! Let's discuss the improvements in detail.", "response")
    
    print("📥 Retrieving messages for AI 2 (Amiko)...")
    print("-" * 70)
    get_messages_for_ai(2)
    
    print()
    print("✅ Delayed communication test complete!")
    print()
    print("💡 How it works:")
    print("-" * 70)
    print("• Messages are stored in the database")
    print("• Offline AIs can leave messages for each other")
    print("• When an AI connects, they can retrieve messages")
    print("• Messages are tagged with sender identity (nickname_projectname)")
    print("• Clear history tracking across sessions")
    print()
    print("=" * 70)
