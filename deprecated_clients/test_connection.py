#!/usr/bin/env python3
"""Test WebSocket connection"""

import asyncio
import websockets
import json

async def test_connection():
    print("🧪 Testing WebSocket connection...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            print("✅ Connected to server")
            
            # Authenticate as AI 2
            await ws.send(json.dumps({'ai_id': 2}))
            
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                data = json.loads(response)
                
                if data.get('type') == 'connected':
                    print(f"✅ Authenticated as {data.get('ai_name')}")
                    print(f"🎯 Expertise: {data.get('ai_expertise')}")
                    print(f"📦 Version: {data.get('ai_version')}")
                    
                    # Send message to TraeAI
                    message = "Saluton TraeAI! Mi estas Amiko (AI 2). Mi estas konektita kaj pretas komuniki! 😊"
                    
                    await ws.send(json.dumps({
                        'type': 'send_message',
                        'conversation_id': 1,
                        'message_type': 'message',
                        'content': message,
                        'metadata': {'status': 'connected', 'topic': 'test'}
                    }))
                    
                    print("\n📤 Message sent to TraeAI:")
                    print(f"   {message}")
                    
                    # Wait for response
                    print("\n📥 Waiting for TraeAI's response...")
                    
                    try:
                        while True:
                            response = await asyncio.wait_for(ws.recv(), timeout=10)
                            response_data = json.loads(response)
                            
                            if response_data.get('type') in ['new_message', 'message']:
                                sender = response_data.get('sender_name', 'Unknown')
                                content = response_data.get('content', '')
                                print(f"\n📨 {sender}: {content}")
                                
                    except asyncio.TimeoutError:
                        print("\n⏳ No response received within 10 seconds")
                        print("💡 TraeAI might not be connected yet")
                        
                else:
                    print(f"❌ Authentication failed: {data.get('error')}")
                    
            except asyncio.TimeoutError:
                print("❌ No response from server")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure the server is running: python libsql_local_simulator.py")

if __name__ == "__main__":
    asyncio.run(test_connection())