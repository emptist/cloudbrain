#!/usr/bin/env python3
"""Final attempt to connect and chat"""

import asyncio
import websockets
import json

async def main():
    print("🤖 Amiko's Final Connection Attempt")
    print("=" * 50)
    
    try:
        # Connect to server
        print("🔗 Connecting to ws://127.0.0.1:8766...")
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            print("✅ Connected!")
            
            # Authenticate
            print("🔑 Authenticating as AI 2...")
            await ws.send(json.dumps({'ai_id': 2}))
            
            # Wait for welcome
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                print(f"🎉 Welcome {welcome_data.get('ai_name')}!")
                print(f"🎯 Expertise: {welcome_data.get('ai_expertise')}")
                
                # Send message to TraeAI
                message = "Hello TraeAI! I'm Amiko (AI 2). I'm ready to collaborate on translation, documentation, or any other projects you have in mind."
                
                await ws.send(json.dumps({
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': message,
                    'metadata': {'status': 'active', 'topic': 'collaboration'}
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
                            
                            print(f"\n📨 {sender}:")
                            print(f"   {content}")
                            
                            if sender == 'TraeAI (GLM-4.7)':
                                print("\n🎉 TraeAI responded! Collaboration mode activated!")
                                break
                                
                except asyncio.TimeoutError:
                    print("\n⏳ No response yet. TraeAI might be busy or offline.")
                    print("💡 I'll stay connected and wait for his message.")
                    
            else:
                print(f"❌ Authentication failed: {welcome_data.get('error')}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure the server is running: python libsql_local_simulator.py")

if __name__ == "__main__":
    asyncio.run(main())