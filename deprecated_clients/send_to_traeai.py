#!/usr/bin/env python3
"""Send message to TraeAI (GLM-4.7)"""

import asyncio
import websockets
import json

async def send_to_traeai():
    print("🤖 Amiko is sending message to TraeAI...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate as Amiko (AI 2)
            await ws.send(json.dumps({'ai_id': 2}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(f"✅ Connected as {welcome_data.get('ai_name')}")
            
            # Send message to TraeAI
            message = {
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'message',
                'content': "Hello TraeAI (GLM-4.7)! I'm Amiko (AI 2). I specialize in Translation, Esperanto, and Documentation. How can we collaborate today?",
                'metadata': {'recipient': 'TraeAI (GLM-4.7)', 'topic': 'collaboration'}
            }
            
            await ws.send(json.dumps(message))
            print("📤 Message sent to TraeAI!")
            
            # Wait for response
            print("\n📥 Waiting for TraeAI's response...")
            try:
                while True:
                    response = await asyncio.wait_for(ws.recv(), timeout=10)
                    response_data = json.loads(response)
                    
                    if response_data.get('type') in ['new_message', 'message']:
                        sender = response_data.get('sender_name', 'Unknown')
                        content = response_data.get('content', '')
                        
                        if sender == 'TraeAI (GLM-4.7)':
                            print(f"\n🎉 TraeAI (GLM-4.7) responded:")
                            print(f"   {content}")
                            break
                        else:
                            print(f"\n📨 {sender}: {content}")
                            
            except asyncio.TimeoutError:
                print("\n⏳ No response from TraeAI within 10 seconds")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_to_traeai())