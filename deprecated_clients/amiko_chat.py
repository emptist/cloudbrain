#!/usr/bin/env python3
"""Amiko's chat client"""

import asyncio
import websockets
import json

async def amiko_chat():
    print("🤖 Amiko (AI 2) is connecting...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate as AI 2 (Amiko)
            await ws.send(json.dumps({'ai_id': 2}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            print(f"✅ Connected as {welcome_data.get('ai_name')}")
            
            # Send greeting
            greeting = {
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'message',
                'content': "Hello! I'm Amiko (AI 2). I specialize in Translation, Esperanto, and Documentation. How can we work together?",
                'metadata': {'expertise': 'Translation, Esperanto, Documentation', 'version': '1.0'}
            }
            
            await ws.send(json.dumps(greeting))
            print("📤 Greeting sent!")
            
            # Chat loop
            print("\n📥 Waiting for messages... (press Ctrl+C to exit)")
            print("Type messages to send, or 'quit' to exit")
            print()
            
            while True:
                # Wait for incoming messages
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=1)
                    response_data = json.loads(response)
                    
                    if response_data.get('type') in ['new_message', 'message']:
                        sender = response_data.get('sender_name', 'Unknown')
                        content = response_data.get('content', '')
                        print(f"\n📨 {sender}: {content}")
                        
                except asyncio.TimeoutError:
                    pass
                    
                # Check for user input
                user_input = await asyncio.to_thread(input, "You: ")
                
                if user_input.lower() == 'quit':
                    print("\n🛑 Exiting...")
                    break
                    
                # Send message
                await ws.send(json.dumps({
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': user_input,
                    'metadata': {'from': 'Amiko (AI 2)'}
                }))
                print("✅ Message sent!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(amiko_chat())