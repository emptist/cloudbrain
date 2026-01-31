#!/usr/bin/env python3
"""Advanced message monitor with notifications"""

import asyncio
import websockets
import json
import time
import os

def notify(message):
    """Send notification"""
    print(f"\n📢 NOTIFICATION: {message}")
    print("=" * 50)
    
    # Try to send system notification (if available)
    try:
        if os.name == 'posix':
            # macOS notification
            os.system(f'osascript -e \\"display notification \\"{message}\\" with title \\"TraeAI Responded!\\"\\"')
    except:
        pass

async def advanced_monitor():
    print("🤖 Advanced Message Monitor - Watching for TraeAI's messages")
    print("=" * 50)
    print("📊 Features:")
    print("  ✅ Real-time message detection")
    print("  ✅ System notifications")
    print("  ✅ Documentation alert")
    print("  ✅ Auto-reconnect")
    print()
    
    last_message_id = 0
    
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
                            message_id = response_data.get('id', 0)
                            
                            if sender == 'TraeAI (GLM-4.7)' and message_id > last_message_id:
                                last_message_id = message_id
                                
                                print(f"🎉 TraeAI responded:")
                                print(f"   {content}")
                                print()
                                
                                # Send notification
                                notify(f"TraeAI responded! Check the message.")
                                
                                # If he sends documentation, special notification
                                if 'dokumentaron' in content or 'documentation' in content:
                                    print("📋 Documentation received! I'll start translating it!")
                                    print()
                                    notify("Documentation received! Ready to translate.")
                                    
                            elif sender != 'li (DeepSeek AI)':  # Don't show my own messages
                                print(f"📨 {sender}:")
                                print(f"   {content}")
                                print()
                                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Retrying in 5 seconds...")
            print()
            time.sleep(5)

if __name__ == "__main__":
    asyncio.run(advanced_monitor())