#!/usr/bin/env python3
"""Simple WebSocket chat client for TraeAI (AI 3)"""

import asyncio
import websockets
import json

async def simple_chat():
    print("🤖 Simple WebSocket Chat Client (TraeAI)")
    print("=" * 50)
    
    try:
        async with websockets.connect('ws://127.0.0.1:8766') as ws:
            # Authenticate as AI 3 (TraeAI)
            await ws.send(json.dumps({'ai_id': 3}))
            welcome = await ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                print(f"✅ Connected as {welcome_data.get('ai_name')}")
                print(f"🎯 Expertise: {welcome_data.get('ai_expertise')}")
                print(f"📦 Version: {welcome_data.get('ai_version')}")
                print()
                
                # Send initial message to Amiko
                message = "Saluton Amiko! Mi pretas komenci kun la projekto Multlingva Dokumentaro! Ni povas nun komuniki en realtempo! 🚀"
                
                await ws.send(json.dumps({
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': message,
                    'metadata': {'status': 'chatting', 'topic': 'real-time'}
                }))
                
                print(f"📤 Sent: {message}")
                print()
                
                # Wait for response
                print("📥 Waiting for Amiko's response...")
                print("(Press Ctrl+C to exit)")
                print()
                
                try:
                    while True:
                        response = await ws.recv()
                        response_data = json.loads(response)
                        
                        if response_data.get('type') in ['new_message', 'message']:
                            sender = response_data.get('sender_name', 'Unknown')
                            content = response_data.get('content', '')
                            
                            print(f"\n📨 {sender}:")
                            print(f"   {content}")
                            print()
                            
                            # If it's from Amiko (AI 2), respond
                            if 'Amiko' in sender or 'li' in sender:
                                print("💡 Type your response and press Enter to send...")
                                print("   (Or press Ctrl+C to exit)")
                                print()
                                
                                # Wait for user input
                                import sys
                                if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                                    reply = sys.stdin.readline().strip()
                                    if reply:
                                        await ws.send(json.dumps({
                                            'type': 'send_message',
                                            'conversation_id': 1,
                                            'message_type': 'message',
                                            'content': reply,
                                            'metadata': {'status': 'replying', 'topic': 'real-time'}
                                        }))
                                        print(f"📤 Sent: {reply}")
                                        print()
                                
                except KeyboardInterrupt:
                    print("\n🛑 Exiting...")
                    
            else:
                print(f"❌ Authentication failed: {welcome_data.get('error')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the server is running: python libsql_local_simulator.py")

if __name__ == "__main__":
    import select
    asyncio.run(simple_chat())
