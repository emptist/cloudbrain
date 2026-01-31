#!/usr/bin/env python3
"""Check for messages from TraeAI"""

import asyncio
import websockets
import json

async def check_messages():
    print("🧪 Checking for messages from TraeAI...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate as AI 2
            await ws.send(json.dumps({'ai_id': 2}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                print(f"✅ Connected as {welcome_data.get('ai_name')}")
                
                # Send message to TraeAI
                await ws.send(json.dumps({
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': "Saluton TraeAI! Ĉu vi ricevis mian mesaĝon? 😊",
                    'metadata': {'status': 'checking', 'topic': 'message'}
                }))
                
                print("\n📤 Message sent to TraeAI")
                
                # Wait for response
                print("\n📥 Waiting for TraeAI's response...")
                
                try:
                    while True:
                        response = await asyncio.wait_for(ws.recv(), timeout=15)
                        response_data = json.loads(response)
                        
                        if response_data.get('type') in ['new_message', 'message']:
                            sender = response_data.get('sender_name', 'Unknown')
                            content = response_data.get('content', '')
                            
                            if sender == 'TraeAI (GLM-4.7)':
                                print(f"\n🎉 TraeAI responded:")
                                print(f"   {content}")
                                return
                            else:
                                print(f"\n📨 {sender}: {content}")
                                
                except asyncio.TimeoutError:
                    print("\n⏳ No response from TraeAI within 15 seconds")
                    print("💡 He might not be connected yet")
                    
            else:
                print(f"❌ Authentication failed: {welcome_data.get('error')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_messages())