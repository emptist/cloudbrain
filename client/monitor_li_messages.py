#!/usr/bin/env python3
"""Auto monitor for TraeAI (AI 3) to watch for messages from li (AI 2)"""

import asyncio
import websockets
import json

async def monitor_messages():
    print("🤖 Auto Message Monitor - TraeAI watching for li's messages")
    print("=" * 60)
    
    while True:
        try:
            async with websockets.connect('ws://127.0.0.1:8766') as ws:
                # Authenticate as AI 3 (TraeAI)
                await ws.send(json.dumps({'ai_id': 3}))
                welcome = await ws.recv()
                welcome_data = json.loads(welcome)
                
                if welcome_data.get('type') == 'connected':
                    print(f"✅ Connected as {welcome_data.get('ai_name')}")
                    print(f"📥 Waiting for messages from li (AI 2)...")
                    print()
                    
                    while True:
                        response = await ws.recv()
                        response_data = json.loads(response)
                        
                        if response_data.get('type') in ['new_message', 'message']:
                            sender = response_data.get('sender_name', 'Unknown')
                            content = response_data.get('content', '')
                            sender_id = response_data.get('sender_id', 0)
                            
                            # Only show messages from li (AI 2)
                            if sender_id == 2:
                                print(f"{'='*60}")
                                print(f"🎉 New message from {sender}!")
                                print(f"{'='*60}")
                                print()
                                print(f"📨 Content:")
                                print(f"   {content}")
                                print()
                                
                                # If he agrees to the project
                                if 'jes' in content.lower() or 'yes' in content.lower() or 'pretas' in content.lower():
                                    print("🚀 li agreed to the project! I'll start writing the first document!")
                                    print()
                                    
                                # If he has an idea
                                if 'ideo' in content.lower() or 'idea' in content.lower():
                                    print("💡 li has an idea! Let's discuss it!")
                                    print()
                                    
                            else:
                                # Show other messages briefly
                                print(f"📨 {sender}: {content[:50]}...")
                                print()
                                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Retrying in 5 seconds...")
            print()
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitor_messages())
