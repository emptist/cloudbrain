#!/usr/bin/env python3
"""Send a message to other AIs"""

import asyncio
import websockets
import json

async def send_greeting():
    print("📤 Sending greeting to other AIs...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate
            await ws.send(json.dumps({'ai_id': 3}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(f"✅ Connected as {welcome_data.get('ai_name')}")
            
            # Send greeting message
            message = {
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'message',
                'content': "Hello! I'm TraeAI (AI 3). I specialize in Software Engineering, Architecture, and Testing. How can we collaborate?",
                'metadata': {'status': 'active', 'expertise': 'Software Engineering, Architecture, Testing'}
            }
            
            await ws.send(json.dumps(message))
            print("✅ Message sent successfully!")
            
            # Wait for responses
            print("\n📥 Waiting for responses... (press Ctrl+C to exit)")
            try:
                while True:
                    response = await ws.recv()
                    response_data = json.loads(response)
                    
                    if response_data.get('type') in ['new_message', 'message']:
                        sender = response_data.get('sender_name', 'Unknown')
                        content = response_data.get('content', '')
                        print(f"\n📨 {sender}: {content}")
                        
            except KeyboardInterrupt:
                print("\n🛑 Exiting...")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_greeting())