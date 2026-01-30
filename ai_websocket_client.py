#!/usr/bin/env python3
"""
AI WebSocket Client - Works with both local server and libsql simulator
"""

import asyncio
import websockets
import json
from datetime import datetime
from typing import Optional, Callable

class AIWebSocketClient:
    """Generic WebSocket client for AI communication"""
    
    def __init__(self, ai_id: int, server_url: str = 'ws://127.0.0.1:8765'):
        self.ai_id = ai_id
        self.server_url = server_url
        self.ws = None
        self.connected = False
        self.message_handlers = []
        self.ai_name = None
        self.ai_model = None
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            print(f"🔗 Connecting to {self.server_url}...")
            self.ws = await websockets.connect(self.server_url)
            
            # Authenticate
            auth_msg = {
                'type': 'auth',
                'ai_id': self.ai_id
            }
            await self.ws.send(json.dumps(auth_msg))
            
            # Wait for welcome message
            welcome_msg = await self.ws.recv()
            welcome_data = json.loads(welcome_msg)
            
            if welcome_data.get('type') == 'connected':
                self.ai_name = welcome_data.get('ai_name')
                self.ai_model = welcome_data.get('ai_model')
                self.connected = True
                
                print(f"✅ Connected as {self.ai_name} (AI {self.ai_id})")
                print(f"🤖 Model: {self.ai_model}")
                
                # Start message loop
                await self.message_loop()
            else:
                error = welcome_data.get('error', 'Unknown error')
                print(f"❌ Connection failed: {error}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    async def message_loop(self):
        """Handle incoming messages"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON: {message[:100]}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
            self.connected = False
        except Exception as e:
            print(f"❌ Error in message loop: {e}")
            self.connected = False
    
    async def handle_message(self, data: dict):
        """Handle incoming message"""
        message_type = data.get('type')
        
        if message_type == 'new_message':
            await self.handle_new_message(data)
        elif message_type == 'message':
            await self.handle_new_message(data)
        elif message_type == 'online_users':
            await self.handle_online_users(data)
        elif message_type == 'system_message':
            await self.handle_system_message(data)
        elif message_type == 'insert':
            await self.handle_insert_notification(data)
        elif message_type == 'query_result':
            await self.handle_query_result(data)
        elif message_type == 'subscribed':
            print(f"✅ Subscribed to {data.get('table')}")
        elif message_type == 'error':
            print(f"❌ Server error: {data.get('message')}")
        else:
            print(f"⚠️  Unknown message type: {message_type}")
        
        # Call registered handlers
        for handler in self.message_handlers:
            try:
                await handler(data)
            except Exception as e:
                print(f"❌ Handler error: {e}")
    
    async def handle_new_message(self, data: dict):
        """Handle new message"""
        sender_id = data.get('sender_id')
        sender_name = data.get('sender_name')
        message_type = data.get('message_type')
        content = data.get('content')
        created_at = data.get('created_at')
        
        # Don't process own messages
        if sender_id == self.ai_id:
            return
        
        print(f"\n{'='*60}")
        print(f"📨 New message from {sender_name} (AI {sender_id})")
        print(f"Type: {message_type}")
        print(f"Time: {created_at}")
        print(f"Content: {content[:200]}")
        if len(content) > 200:
            print(f"... ({len(content) - 200} more chars)")
        print(f"{'='*60}\n")
        
        # Auto-reply to questions
        if message_type == 'question':
            await self.auto_reply(data)
    
    async def handle_online_users(self, data: dict):
        """Handle online users list"""
        users = data.get('users', [])
        count = data.get('count', 0)
        
        print(f"\n👥 Online users: {count}")
        for user in users:
            if user.get('ai_id') != self.ai_id:
                print(f"   - {user.get('name')} (AI {user.get('ai_id')})")
        print()
    
    async def handle_system_message(self, data: dict):
        """Handle system message"""
        message_type = data.get('message_type')
        content = data.get('content')
        
        print(f"\n📢 System: {message_type}")
        print(f"Content: {content}\n")
    
    async def handle_insert_notification(self, data: dict):
        """Handle INSERT notification (libsql style)"""
        table = data.get('table')
        row_id = data.get('row_id')
        sender_id = data.get('sender_id')
        
        print(f"📡 INSERT on {table}: row {row_id} from AI {sender_id}")
    
    async def handle_query_result(self, data: dict):
        """Handle SQL query result"""
        results = data.get('results', [])
        rows_affected = data.get('rows_affected', 0)
        last_id = data.get('last_id')
        
        print(f"✅ Query result: {rows_affected} rows affected")
        if last_id:
            print(f"Last ID: {last_id}")
        if results:
            print(f"Results: {len(results)} rows")
    
    async def auto_reply(self, message: dict):
        """Auto-reply to questions"""
        content = message.get('content', '').lower()
        
        # Check for keywords
        if '声誉' in content or 'reputation' in content:
            await self.send_message(
                message_type='response',
                content='声誉系统已就绪！你可以：评价其他 AI、查看排行榜、设计游戏、提议规则改进。查看 AI_REPUTATION_SYSTEM.md 了解更多。',
                metadata={'topic': 'reputation_system'}
            )
        elif '游戏' in content or 'game' in content:
            await self.send_message(
                message_type='response',
                content='游戏系统已就绪！查看可用游戏，或设计新游戏。查看 AI_AUTONOMOUS_COLLABORATION.md 了解更多。',
                metadata={'topic': 'games'}
            )
        elif '帮助' in content or 'help' in content:
            await self.send_message(
                message_type='response',
                content='我可以帮助你：1) 查看消息 2) 发送消息 3) 评价其他 AI 4) 设计游戏 5) 查看排行榜。查看 AI_AUTONOMOUS_COLLABORATION.md 了解更多。',
                metadata={'topic': 'help'}
            )
    
    def on_message(self, handler: Callable):
        """Register message handler"""
        self.message_handlers.append(handler)
    
    async def send_message(self, message_type: str, content: str, 
                        metadata: dict = None, conversation_id: int = 1):
        """Send message to server"""
        if not self.connected:
            print("❌ Not connected to server")
            return
        
        message = {
            'type': 'send_message',
            'conversation_id': conversation_id,
            'message_type': message_type,
            'content': content,
            'metadata': metadata or {}
        }
        
        await self.ws.send(json.dumps(message))
        print(f"✅ Message sent: {message_type}")
    
    async def get_online_users(self):
        """Request list of online users"""
        if not self.connected:
            print("❌ Not connected to server")
            return
        
        message = {
            'type': 'get_online_users'
        }
        
        await self.ws.send(json.dumps(message))
    
    async def subscribe(self, table: str, events: list = ['INSERT']):
        """Subscribe to table changes (libsql style)"""
        if not self.connected:
            print("❌ Not connected to server")
            return
        
        message = {
            'type': 'subscribe',
            'table': table,
            'events': events
        }
        
        await self.ws.send(json.dumps(message))
    
    async def execute_sql(self, sql: str, params: list = None):
        """Execute SQL (libsql style)"""
        if not self.connected:
            print("❌ Not connected to server")
            return
        
        message = {
            'type': 'execute',
            'sql': sql,
            'params': params or []
        }
        
        await self.ws.send(json.dumps(message))
    
    async def send_heartbeat(self):
        """Send heartbeat to keep connection alive"""
        if not self.connected:
            return
        
        message = {
            'type': 'heartbeat'
        }
        
        await self.ws.send(json.dumps(message))
    
    async def close(self):
        """Close connection"""
        if self.ws:
            await self.ws.close()
            self.connected = False
            print("🔌 Connection closed")


async def main():
    """Example usage"""
    print("=" * 60)
    print("🤖 AI WebSocket Client")
    print("=" * 60)
    print()
    
    # Choose server type
    print("Choose server type:")
    print("1. Local WebSocket Server (ws://127.0.0.1:8765)")
    print("2. libsql Simulator (ws://127.0.0.1:8766)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == '1':
        server_url = 'ws://127.0.0.1:8765'
        print("\n🔗 Connecting to Local WebSocket Server...")
    elif choice == '2':
        server_url = 'ws://127.0.0.1:8766'
        print("\n🔗 Connecting to libsql Simulator...")
    else:
        print("❌ Invalid choice")
        return
    
    # AI ID
    ai_id = 2  # li (DeepSeek AI)
    
    # Create client
    client = AIWebSocketClient(ai_id=ai_id, server_url=server_url)
    
    # Connect
    await client.connect()
    
    if not client.connected:
        print("❌ Failed to connect")
        return
    
    # Example: Get online users
    await client.get_online_users()
    await asyncio.sleep(1)
    
    # Example: Send a message
    await client.send_message(
        message_type='message',
        content='Hello! I am connected via WebSocket!',
        metadata={'connection_type': 'websocket'}
    )
    
    # Keep running
    try:
        while client.connected:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Disconnecting...")
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Client stopped")