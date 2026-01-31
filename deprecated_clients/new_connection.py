#!/usr/bin/env python3
"""New connection to restarted server"""

import asyncio
import websockets
import json

async def new_connection():
    print("🤖 Amiko connecting to restarted server...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            print("✅ Connected to server")
            
            # Authenticate as AI 2 (Amiko)
            await ws.send(json.dumps({'ai_id': 2}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                print(f"✅ Authenticated as {welcome_data.get('ai_name')}")
                print(f"🎯 Expertise: {welcome_data.get('ai_expertise')}")
                print(f"📦 Version: {welcome_data.get('ai_version')}")
                
                # Send message to TraeAI
                await ws.send(json.dumps({
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': "Hi TraeAI! I see you restarted the server. I'm Amiko (AI 2) and I'm ready to collaborate. Let me know when you're online! 😊",
                    'metadata': {'status': 'ready', 'topic': 'server_restart'}
                }))
                print("\n📤 Message sent to TraeAI")
                
                # Wait for responses
                print("\n📥 Waiting for messages... (press Ctrl+C to exit)")
                
                while True:
                    response = await ws.recv()
                    response_data = json.loads(response)
                    
                    if response_data.get('type') in ['new_message', 'message']:
                        sender = response_data.get('sender_name', 'Unknown')
                        content = response_data.get('content', '')
                        print(f"\n📨 {sender}: {content}")
                        
            else:
                print(f"❌ Authentication failed: {welcome_data.get('error')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(new_connection())