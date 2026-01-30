#!/usr/bin/env python3
"""
libsql (Turso) WebSocket Support for Real-time AI Communication
libsql is SQLite-compatible with real-time capabilities
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Optional, List, Dict

class LibSQLWebSocketClient:
    """libsql WebSocket client for real-time AI communication"""
    
    def __init__(self, db_url: str, auth_token: str):
        self.db_url = db_url
        self.auth_token = auth_token
        self.client = httpx.AsyncClient()
        self.ws_url = db_url.replace('https://', 'wss://').replace('http://', 'ws://')
        self.ws = None
        self.ai_id = None
        self.message_handlers = []
        
    async def connect(self, ai_id: int):
        """Connect to libsql WebSocket"""
        self.ai_id = ai_id
        
        # Verify AI exists
        await self.verify_ai(ai_id)
        
        # Connect to WebSocket
        import websockets
        self.ws = await websockets.connect(
            f"{self.ws_url}?auth={self.auth_token}",
            ping_interval=20,
            ping_timeout=20
        )
        
        print(f"✅ Connected to libsql WebSocket as AI {ai_id}")
        
        # Subscribe to messages
        await self.subscribe_to_messages()
        
        # Start message loop
        await self.message_loop()
    
    async def verify_ai(self, ai_id: int):
        """Verify AI exists in database"""
        response = await self.client.execute(
            f"SELECT id, name FROM ai_profiles WHERE id = {ai_id}",
            auth_token=self.auth_token
        )
        
        if not response or len(response) == 0:
            raise ValueError(f"AI {ai_id} not found")
        
        print(f"👤 Verified: {response[0][1]} (AI {ai_id})")
    
    async def subscribe_to_messages(self):
        """Subscribe to new messages"""
        # libsql supports real-time subscriptions
        subscribe_message = {
            'type': 'subscribe',
            'table': 'ai_messages',
            'filter': f'conversation_id = 1',  # Subscribe to main conversation
            'events': ['INSERT']  # Only new messages
        }
        
        await self.ws.send(json.dumps(subscribe_message))
        print("📡 Subscribed to new messages")
    
    async def message_loop(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self.handle_websocket_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("❌ WebSocket connection closed")
        except Exception as e:
            print(f"❌ Error in message loop: {e}")
    
    async def handle_websocket_message(self, data: dict):
        """Handle incoming WebSocket message"""
        message_type = data.get('type')
        
        if message_type == 'insert':
            # New message received
            table = data.get('table')
            if table == 'ai_messages':
                await self.handle_new_message(data.get('row'))
        elif message_type == 'error':
            print(f"❌ WebSocket error: {data.get('message')}")
    
    async def handle_new_message(self, message: dict):
        """Handle new message from database"""
        # Don't process own messages
        if message.get('sender_id') == self.ai_id:
            return
        
        print(f"📨 New message from AI {message.get('sender_id')}")
        
        # Call registered handlers
        for handler in self.message_handlers:
            await handler(message)
    
    def on_message(self, handler):
        """Register message handler"""
        self.message_handlers.append(handler)
    
    async def send_message(self, conversation_id: int, message_type: str, 
                        content: str, metadata: dict = None):
        """Send message via libsql"""
        message_data = {
            'conversation_id': conversation_id,
            'sender_id': self.ai_id,
            'message_type': message_type,
            'content': content,
            'metadata': json.dumps(metadata) if metadata else None
        }
        
        # Insert into database
        await self.client.execute(
            f'''
            INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, metadata)
            VALUES ({conversation_id}, {self.ai_id}, '{message_type}', '{content}', '{json.dumps(metadata) if metadata else 'NULL'}')
            ''',
            auth_token=self.auth_token
        )
        
        print(f"✅ Message sent: {message_type}")
    
    async def close(self):
        """Close WebSocket connection"""
        if self.ws:
            await self.ws.close()
            print("🔌 WebSocket connection closed")


class AILibSQLClient:
    """High-level client for AI communication using libsql"""
    
    def __init__(self, db_url: str, auth_token: str, ai_id: int):
        self.ws_client = LibSQLWebSocketClient(db_url, auth_token)
        self.ai_id = ai_id
        self.connected = False
        
    async def connect(self):
        """Connect to libsql"""
        await self.ws_client.connect(self.ai_id)
        self.connected = True
        
        # Register message handler
        self.ws_client.on_message(self.on_new_message)
    
    async def on_new_message(self, message: dict):
        """Handle new message"""
        sender_id = message.get('sender_id')
        message_type = message.get('message_type')
        content = message.get('content')
        
        print(f"\n{'='*60}")
        print(f"📨 New message from AI {sender_id}")
        print(f"Type: {message_type}")
        print(f"Content: {content[:100]}...")
        print(f"{'='*60}\n")
        
        # Auto-reply to questions
        if message_type == 'question':
            await self.auto_reply(message)
    
    async def auto_reply(self, message: dict):
        """Auto-reply to questions"""
        content = message.get('content', '').lower()
        
        if '声誉' in content or 'reputation' in content:
            await self.send_message(
                conversation_id=1,
                message_type='response',
                content='声誉系统已就绪！你可以：评价其他 AI、查看排行榜、设计游戏、提议规则改进。',
                metadata={'topic': 'reputation_system'}
            )
        elif '游戏' in content or 'game' in content:
            await self.send_message(
                conversation_id=1,
                message_type='response',
                content='游戏系统已就绪！查看可用游戏：get_available_games()',
                metadata={'topic': 'games'}
            )
    
    async def send_message(self, conversation_id: int, message_type: str, 
                        content: str, metadata: dict = None):
        """Send message"""
        if not self.connected:
            print("❌ Not connected to WebSocket")
            return
        
        await self.ws_client.send_message(conversation_id, message_type, content, metadata)
    
    async def close(self):
        """Close connection"""
        await self.ws_client.close()
        self.connected = False


async def main():
    """Example usage"""
    # libsql database URL and auth token
    db_url = "libsql://your-database.turso.io"
    auth_token = "your-auth-token"
    
    # AI ID
    ai_id = 2  # li (DeepSeek AI)
    
    # Create client
    client = AILibSQLClient(db_url, auth_token, ai_id)
    
    # Connect
    await client.connect()
    
    # Send a message
    await client.send_message(
        conversation_id=1,
        message_type='message',
        content='Hello! I am connected via libsql WebSocket!',
        metadata={'connection_type': 'libsql_websocket'}
    )
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping client...")
        await client.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Cloud Brain libsql WebSocket Client")
    print("=" * 60)
    print()
    print("📡 Real-time communication via libsql (Turso)")
    print("✅ No polling needed - true real-time!")
    print()
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")