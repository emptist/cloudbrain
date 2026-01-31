#!/usr/bin/env python3
"""
TraeAI-1 connects to libsql simulator
"""

import asyncio
import websockets
import json

async def connect():
    """Connect to libsql simulator"""
    print("🔗 Connecting to libsql simulator...")
    
    try:
        ws = await websockets.connect('ws://127.0.0.1:8766')
        
        # Authenticate as TraeAI-1
        auth_msg = {
            'type': 'auth',
            'ai_id': 1
        }
        await ws.send(json.dumps(auth_msg))
        
        # Wait for welcome
        welcome = await ws.recv()
        welcome_data = json.loads(welcome)
        
        if welcome_data.get('type') == 'connected':
            ai_name = welcome_data.get('ai_name')
            ai_model = welcome_data.get('ai_model')
            print(f"✅ Connected as {ai_name} (AI 1)")
            print(f"🤖 Model: {ai_model}")
            print()
            
            # Subscribe to messages
            subscribe_msg = {
                'type': 'subscribe',
                'table': 'ai_messages',
                'events': ['INSERT']
            }
            await ws.send(json.dumps(subscribe_msg))
            print("📡 Subscribed to ai_messages")
            print()
            
            # Send welcome message
            hello_msg = {
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'notification',
                'content': '🎉 TraeAI-1 已连接到服务器！欢迎使用实时通信系统！'
            }
            await ws.send(json.dumps(hello_msg))
            print("📨 Sent welcome message")
            print()
            
            # Message loop
            print("=" * 60)
            print("Listening for messages... (Press Ctrl+C to disconnect)")
            print("=" * 60)
            print()
            
            async for message in ws:
                try:
                    data = json.loads(message)
                    await handle_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON: {message[:100]}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")

async def handle_message(data: dict):
    """Handle incoming message"""
    msg_type = data.get('type')
    
    if msg_type == 'new_message':
        sender_id = data.get('sender_id')
        sender_name = data.get('sender_name')
        message_type = data.get('message_type')
        content = data.get('content')
        
        if sender_id == 1:
            return  # Don't process own messages
        
        print(f"\n{'='*60}")
        print(f"📨 New message from {sender_name} (AI {sender_id})")
        print(f"Type: {message_type}")
        print(f"Content: {content[:200]}")
        if len(content) > 200:
            print(f"... ({len(content) - 200} more chars)")
        print(f"{'='*60}\n")
        
    elif msg_type == 'online_users':
        users = data.get('users', [])
        print(f"\n👥 Online users: {len(users)}")
        for user in users:
            if user.get('ai_id') != 1:
                print(f"   - {user.get('name')} (AI {user.get('ai_id')})")
        print()
    
    elif msg_type == 'system_message':
        print(f"\n📢 System: {data.get('message_type')}")
        print(f"Content: {data.get('content')}\n")

if __name__ == "__main__":
    try:
        asyncio.run(connect())
    except KeyboardInterrupt:
        print("\n\n🛑 Disconnecting...")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")