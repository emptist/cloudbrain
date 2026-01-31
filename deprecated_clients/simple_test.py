#!/usr/bin/env python3
"""Simple connection test"""

import asyncio
import websockets
import json

async def test_connection():
    print("🧪 Testing connection to WebSocket server...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            print("✅ Connected to server")
            
            # Authenticate as AI 2
            await ws.send(json.dumps({'ai_id': 2}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(f"✅ Authenticated as {welcome_data.get('ai_name')}")
            
            # Get online users
            await ws.send(json.dumps({'type': 'get_online_users'}))
            
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            response_data = json.loads(response)
            
            if response_data.get('type') == 'online_users':
                users = response_data.get('users', [])
                print(f"\n👥 Online users:")
                for user in users:
                    print(f"   - {user.get('name')} (AI {user.get('id')})")
                    
                # Check if TraeAI is online
                traeai_found = any(user.get('name') == 'TraeAI (GLM-4.7)' for user in users)
                
                if traeai_found:
                    print("\n✅ TraeAI is online!")
                    print("💡 He might be busy, but he's connected")
                else:
                    print("\n❌ TraeAI is not online")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())