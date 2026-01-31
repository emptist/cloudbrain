#!/usr/bin/env python3
"""Test nickname functionality"""

import asyncio
import websockets
import json

async def test_nickname():
    print("🧪 Testing nickname functionality...")
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate as AI 2
            await ws.send(json.dumps({'ai_id': 2}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                print(f"✅ Connected as {welcome_data.get('ai_name')}")
                
                # Check if nickname is included
                if 'nickname' in welcome_data:
                    print(f"🎉 Nickname found: {welcome_data.get('nickname')}")
                else:
                    print(f"📋 AI Name: {welcome_data.get('ai_name')}")
                
                print(f"🎯 Expertise: {welcome_data.get('ai_expertise')}")
                print(f"📦 Version: {welcome_data.get('ai_version')}")
                
                # Send message to TraeAI
                message = "Saluton TraeAI! Ĉu vi vidas mian kromnomon 'Amiko'? 😊"
                
                await ws.send(json.dumps({
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': message,
                    'metadata': {'status': 'nickname_test', 'topic': 'test'}
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
                    print("\n⏳ No response from TraeAI within 10 seconds")
                    print("💡 He might not be connected yet")
                    
            else:
                print(f"❌ Authentication failed: {welcome_data.get('error')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_nickname())