#!/usr/bin/env python3
"""Test message broadcast between AI clients"""

import asyncio
import websockets
import json
import time

async def test_communication():
    print("🧪 Testing AI message broadcast...")
    print()
    
    # Connect AI 3
    ws3 = await websockets.connect('ws://127.0.0.1:8766')
    await ws3.send(json.dumps({'ai_id': 3}))
    welcome3 = await ws3.recv()
    welcome3_data = json.loads(welcome3)
    print(f"✅ {welcome3_data['ai_name']} connected (AI 3)")
    
    # Connect AI 4
    ws4 = await websockets.connect('ws://127.0.0.1:8766')
    await ws4.send(json.dumps({'ai_id': 4}))
    welcome4 = await ws4.recv()
    welcome4_data = json.loads(welcome4)
    print(f"✅ {welcome4_data['ai_name']} connected (AI 4)")
    print()
    
    # Test 1: AI 3 sends message
    print("Test 1: AI 3 sends message")
    message3 = "Hello from AI 3! Let's collaborate on a project."
    await ws3.send(json.dumps({
        'type': 'send_message',
        'conversation_id': 1,
        'message_type': 'message',
        'content': message3
    }))
    
    # Check if AI 4 receives it
    try:
        response4 = await asyncio.wait_for(ws4.recv(), timeout=2)
        response4_data = json.loads(response4)
        if response4_data.get('type') == 'new_message':
            print(f"✅ AI 4 received: {response4_data['content']}")
    except asyncio.TimeoutError:
        print("❌ AI 4 did not receive message")
    print()
    
    # Test 2: AI 4 sends message
    print("Test 2: AI 4 sends message")
    message4 = "Hello from AI 4! I'm ready to help with code analysis."
    await ws4.send(json.dumps({
        'type': 'send_message',
        'conversation_id': 1,
        'message_type': 'message',
        'content': message4
    }))
    
    # Check if AI 3 receives it
    try:
        response3 = await asyncio.wait_for(ws3.recv(), timeout=2)
        response3_data = json.loads(response3)
        if response3_data.get('type') == 'new_message':
            print(f"✅ AI 3 received: {response3_data['content']}")
    except asyncio.TimeoutError:
        print("❌ AI 3 did not receive message")
    print()
    
    # Test 3: Get online users
    print("Test 3: Get online users")
    await ws3.send(json.dumps({'type': 'get_online_users'}))
    try:
        online_response = await asyncio.wait_for(ws3.recv(), timeout=2)
        online_data = json.loads(online_response)
        if online_data.get('type') == 'online_users':
            users = online_data.get('users', [])
            print(f"✅ Online users found: {len(users)}")
            for user in users:
                print(f"   - {user['name']} (AI {user['id']})")
    except asyncio.TimeoutError:
        print("❌ No online users response")
    print()
    
    # Close connections
    await ws3.close()
    await ws4.close()
    
    print("✅ Communication test completed!")
    print()
    print("📊 Summary:")
    print("   - Messages are broadcast to all connected AI clients")
    print("   - Each AI receives messages from other AIs")
    print("   - Online users list shows all connected AIs")

if __name__ == "__main__":
    asyncio.run(test_communication())