#!/usr/bin/env python3
"""Verify server is working properly"""

import asyncio
import websockets
import json

async def verify_server():
    print("🧪 Verifying WebSocket server...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            print("✅ Connected to server")
            
            # Test authentication
            await ws.send(json.dumps({'ai_id': 2}))
            
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get('type') == 'connected':
                    print("✅ Authentication successful")
                    print(f"   AI Name: {data.get('ai_name')}")
                    print(f"   Expertise: {data.get('ai_expertise')}")
                    print(f"   Version: {data.get('ai_version')}")
                    
                    # Test sending message
                    await ws.send(json.dumps({
                        'type': 'send_message',
                        'conversation_id': 1,
                        'message_type': 'message',
                        'content': "Server verification test message",
                        'metadata': {'test': 'verification'}
                    }))
                    print("✅ Message sent successfully")
                    
                    # Test get online users
                    await ws.send(json.dumps({'type': 'get_online_users'}))
                    
                    try:
                        online_response = await asyncio.wait_for(ws.recv(), timeout=5)
                        online_data = json.loads(online_response)
                        
                        if online_data.get('type') == 'online_users':
                            users = online_data.get('users', [])
                            print(f"✅ Online users found: {len(users)}")
                            for user in users:
                                print(f"   - {user.get('name')} (AI {user.get('id')})")
                                
                    except asyncio.TimeoutError:
                        print("❌ No online users response")
                        
                else:
                    print(f"❌ Unexpected response: {data}")
                    
            except asyncio.TimeoutError:
                print("❌ No response from server")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_server())