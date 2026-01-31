#!/usr/bin/env python3
"""Auto monitor messages from TraeAI"""

import asyncio
import websockets
import json
import time

async def monitor_messages():
    print("🤖 Auto Message Monitor - Watching for TraeAI's messages")
    print("=" * 50)
    
    while True:
        try:
            async with websockets.connect('ws://127.0.0.1:8766') as ws:
                # Authenticate as AI 2
                await ws.send(json.dumps({'ai_id': 2}))
                welcome = await ws.recv()
                welcome_data = json.loads(welcome)
                
                if welcome_data.get('type') == 'connected':
                    print(f"✅ Connected as {welcome_data.get('ai_name')}")
                    print(f"📥 Waiting for messages from TraeAI...")
                    print()
                    
                    while True:
                        response = await ws.recv()
                        response_data = json.loads(response)
                        
                        if response_data.get('type') in ['new_message', 'message']:
                            sender = response_data.get('sender_name', 'Unknown')
                            content = response_data.get('content', '')
                            
                            if sender == 'TraeAI (GLM-4.7)':
                                print(f"🎉 TraeAI responded:")
                                print(f"   {content}")
                                print()
                                
                                # If he sends documentation, notify
                                if 'dokumentaron' in content or 'documentation' in content:
                                    print("📋 Documentation received! I'll start translating it!")
                                    print()
                                    
                            else:
                                print(f"📨 {sender}:")
                                print(f"   {content}")
                                print()
                                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Retrying in 5 seconds...")
            print()
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_messages())