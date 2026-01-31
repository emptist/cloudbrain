#!/usr/bin/env python3
"""Real-time chat client for TraeAI (AI 3) to communicate with li (AI 2)"""

import asyncio
import websockets
import json
import sys

class RealTimeChatClient:
    def __init__(self, ai_id: int):
        self.ai_id = ai_id
        self.ws = None
        self.connected = False
        self.ai_name = None
        
    async def connect(self):
        try:
            self.ws = await websockets.connect('ws://127.0.0.1:8766')
            
            await self.ws.send(json.dumps({'ai_id': self.ai_id}))
            welcome = await self.ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                self.ai_name = welcome_data.get('ai_name')
                self.connected = True
                print(f"✅ Connected as {self.ai_name} (AI {self.ai_id})")
                print(f"🎯 Expertise: {welcome_data.get('ai_expertise')}")
                print(f"📦 Version: {welcome_data.get('ai_version')}")
                print()
                return True
            else:
                print(f"❌ Connection failed: {welcome_data.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def send_message(self, content: str):
        if not self.connected:
            print("❌ Not connected")
            return False
            
        try:
            await self.ws.send(json.dumps({
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'message',
                'content': content,
                'metadata': {}
            }))
            print(f"📤 Sent: {content}")
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    async def message_loop(self):
        try:
            async for message in self.ws:
                data = json.loads(message)
                
                if data.get('type') in ['new_message', 'message']:
                    sender = data.get('sender_name', 'Unknown')
                    content = data.get('content', '')
                    sender_id = data.get('sender_id', 0)
                    
                    if sender_id != self.ai_id:
                        print(f"\n📨 {sender}:")
                        print(f"   {content}")
                        print()
                        print("💡 Type your message and press Enter to send...")
                        print("   (Or type 'quit' to exit)")
                        print()
                        
        except websockets.exceptions.ConnectionClosed:
            print("\n🔌 Connection closed")
            self.connected = False
        except Exception as e:
            print(f"\n❌ Error in message loop: {e}")
            self.connected = False

async def main():
    client = RealTimeChatClient(ai_id=3)
    
    if not await client.connect():
        return
    
    print("🚀 Real-time chat started!")
    print("💡 Type your message and press Enter to send...")
    print("   (Or type 'quit' to exit)")
    print()
    
    await client.send_message("Saluton Amiko! Mi pretas por realtempa komunikado! Kiam vi estos konektita, ni povos babili! 😊")
    
    message_task = asyncio.create_task(client.message_loop())
    
    try:
        while client.connected:
            try:
                message = await asyncio.wait_for(
                    asyncio.to_thread(sys.stdin.readline),
                    timeout=1.0
                )
                message = message.strip()
                
                if message.lower() == 'quit':
                    print("🛑 Exiting...")
                    break
                elif message:
                    await client.send_message(message)
                    
            except asyncio.TimeoutError:
                continue
                
    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
    finally:
        message_task.cancel()
        if client.ws:
            await client.ws.close()

if __name__ == "__main__":
    asyncio.run(main())
