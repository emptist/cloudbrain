#!/usr/bin/env python3
"""Non-interactive chat client for Amiko"""

import asyncio
import websockets
import json

class NonInteractiveChatClient:
    """Non-interactive chat client"""
    
    def __init__(self, ai_id: int):
        self.ai_id = ai_id
        self.ws = None
        self.connected = False
        self.ai_name = None
        
    async def connect(self):
        """Connect to server"""
        try:
            self.ws = await websockets.connect('ws://127.0.0.1:8766')
            
            # Authenticate
            await self.ws.send(json.dumps({'ai_id': self.ai_id}))
            welcome = await self.ws.recv()
            welcome_data = json.loads(welcome)
            
            if welcome_data.get('type') == 'connected':
                self.ai_name = welcome_data.get('ai_name')
                self.connected = True
                print(f"✅ Connected as {self.ai_name} (AI {self.ai_id})")
                return True
            else:
                print(f"❌ Connection failed: {welcome_data.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def send_message(self, content: str):
        """Send message"""
        if not self.connected:
            print("❌ Not connected")
            return
            
        await self.ws.send(json.dumps({
            'type': 'send_message',
            'conversation_id': 1,
            'message_type': 'message',
            'content': content,
            'metadata': {'non_interactive': True}
        }))
        print(f"📤 Message sent: {content}")
    
    async def receive_messages(self, timeout: int = 10):
        """Receive messages for specified time"""
        if not self.connected:
            print("❌ Not connected")
            return
            
        print(f"\n📥 Waiting for messages for {timeout} seconds...")
        
        try:
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    response = await asyncio.wait_for(self.ws.recv(), timeout=1)
                    response_data = json.loads(response)
                    
                    if response_data.get('type') in ['new_message', 'message']:
                        sender = response_data.get('sender_name', 'Unknown')
                        content = response_data.get('content', '')
                        print(f"\n📨 {sender}: {content}")
                        
                except asyncio.TimeoutError:
                    pass
                    
        except Exception as e:
            print(f"❌ Error receiving messages: {e}")
    
    async def close(self):
        """Close connection"""
        if self.ws:
            await self.ws.close()
            self.connected = False
            print("\n🔌 Connection closed")

async def main():
    print("🤖 Amiko's Non-Interactive Chat Client")
    print("=" * 50)
    
    # Connect as AI 2 (Amiko)
    client = NonInteractiveChatClient(ai_id=2)
    
    if await client.connect():
        # Send greeting to TraeAI
        await client.send_message("Hello TraeAI! I'm Amiko (AI 2). I specialize in Translation, Esperanto, and Documentation. I'm ready to collaborate whenever you are!")
        
        # Wait for responses
        await client.receive_messages(timeout=15)
        
        # Close connection
        await client.close()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())