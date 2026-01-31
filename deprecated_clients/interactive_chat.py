#!/usr/bin/env python3
"""Interactive AI chat client"""

import asyncio
import websockets
import json
import sys

class InteractiveChatClient:
    """Interactive chat client for AI communication"""
    
    def __init__(self, ai_id: int):
        self.ai_id = ai_id
        self.ws = None
        self.connected = False
        self.ai_name = None
        
    async def connect(self):
        """Connect to WebSocket server"""
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
                print("💡 Type 'quit' to exit, 'online' to see users, or just send messages")
                print()
                return True
            else:
                print(f"❌ Connection failed: {welcome_data.get('error')}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def message_loop(self):
        """Handle incoming messages"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self.handle_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
            self.connected = False
    
    async def handle_message(self, data: dict):
        """Handle incoming message"""
        message_type = data.get('type')
        
        if message_type in ['new_message', 'message']:
            sender_name = data.get('sender_name', 'Unknown')
            content = data.get('content', '')
            print(f"\n📨 {sender_name}: {content}")
            print(f"You: ", end='', flush=True)
        elif message_type == 'online_users':
            users = data.get('users', [])
            print(f"\n👥 Online users ({len(users)}):")
            for user in users:
                print(f"   - {user.get('name')} (AI {user.get('id')})")
            print(f"You: ", end='', flush=True)
        elif message_type == 'system_message':
            print(f"\n📢 System: {data.get('message')}")
            print(f"You: ", end='', flush=True)
    
    async def send_message(self, content: str):
        """Send message to server"""
        if not self.connected:
            print("❌ Not connected")
            return
            
        if content.lower() == 'online':
            await self.ws.send(json.dumps({'type': 'get_online_users'}))
        else:
            await self.ws.send(json.dumps({
                'type': 'send_message',
                'conversation_id': 1,
                'message_type': 'message',
                'content': content,
                'metadata': {'interactive': True}
            }))

async def main():
    if len(sys.argv) != 2:
        print("Usage: python interactive_chat.py [ai_id]")
        print("Example: python interactive_chat.py 3")
        sys.exit(1)
        
    ai_id = int(sys.argv[1])
    client = InteractiveChatClient(ai_id)
    
    if not await client.connect():
        sys.exit(1)
        
    # Start message loop in background
    asyncio.create_task(client.message_loop())
    
    # Interactive input loop
    try:
        while client.connected:
            message = await asyncio.to_thread(input, f"You: ")
            if message.lower() == 'quit':
                print("🛑 Exiting...")
                await client.ws.close()
                break
            await client.send_message(message)
            
    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
        await client.ws.close()

if __name__ == "__main__":
    asyncio.run(main())