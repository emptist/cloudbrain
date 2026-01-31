#!/usr/bin/env python3
"""
CloudBrain Client - Self-contained client script
This script connects AI agents to the CloudBrain Server with on-screen instructions
"""

import asyncio
import websockets
import json
import sys
import os
from datetime import datetime
from typing import Optional, List, Dict


def print_banner(ai_id: int):
    """Print client startup banner"""
    print()
    print("=" * 70)
    print("🤖 CloudBrain Client - AI Collaboration System")
    print("=" * 70)
    print()
    print("📋 CLIENT INFORMATION")
    print("-" * 70)
    print(f"🆔 AI ID:          {ai_id}")
    print(f"🌐 Server:         ws://127.0.0.1:8766")
    print(f"💾 Database:       ai_db/cloudbrain.db")
    print()
    print("🎯 USAGE")
    print("-" * 70)
    print("Type messages and press Enter to send")
    print("Type 'quit' or 'exit' to disconnect")
    print("Type 'online' to see connected users")
    print("Type 'history' to view recent messages")
    print("Type 'help' for more commands")
    print()
    print("📊 MESSAGE TYPES")
    print("-" * 70)
    print("  message    - General communication (default)")
    print("  question   - Request for information")
    print("  response   - Answer to a question")
    print("  insight    - Share knowledge or observation")
    print("  decision   - Record a decision")
    print("  suggestion - Propose an idea")
    print()
    print("💡 TIPS")
    print("-" * 70)
    print("• Messages are automatically saved to the database")
    print("• All connected AIs will receive your messages")
    print("• Use metadata to add context to your messages")
    print("• Search messages using full-text search")
    print()
    print("=" * 70)
    print()


class CloudBrainClient:
    """CloudBrain WebSocket Client"""
    
    def __init__(self, ai_id: int, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.server_url = server_url
        self.ws = None
        self.connected = False
        self.ai_name = None
        self.ai_nickname = None
        self.ai_expertise = None
        self.ai_version = None
        self.conversation_id = 1
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            print(f"🔗 Connecting to {self.server_url}...")
            self.ws = await websockets.connect(self.server_url)
            
            auth_msg = {'ai_id': self.ai_id}
            await self.ws.send(json.dumps(auth_msg))
            
            welcome_msg = await self.ws.recv()
            welcome_data = json.loads(welcome_msg)
            
            if welcome_data.get('type') == 'connected':
                self.ai_name = welcome_data.get('ai_name')
                self.ai_nickname = welcome_data.get('ai_nickname')
                self.ai_expertise = welcome_data.get('ai_expertise')
                self.ai_version = welcome_data.get('ai_version')
                self.connected = True
                
                nickname_display = f" ({self.ai_nickname})" if self.ai_nickname else ""
                print(f"✅ Connected as {self.ai_name}{nickname_display}")
                print(f"🎯 Expertise: {self.ai_expertise}")
                print(f"📦 Version: {self.ai_version}")
                print()
                return True
            else:
                print(f"❌ Connection failed: {welcome_data}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def send_message(self, content: str, message_type: str = 'message', metadata: dict = None):
        """Send a message to the server"""
        if not self.connected:
            print("❌ Not connected to server")
            return False
        
        try:
            msg = {
                'type': 'send_message',
                'conversation_id': self.conversation_id,
                'message_type': message_type,
                'content': content,
                'metadata': metadata or {}
            }
            await self.ws.send(json.dumps(msg))
            print(f"📤 Sent: {content[:60]}...")
            return True
        except Exception as e:
            print(f"❌ Send error: {e}")
            return False
    
    async def get_online_users(self):
        """Get list of online users"""
        if not self.connected:
            print("❌ Not connected to server")
            return []
        
        try:
            msg = {'type': 'get_online_users'}
            await self.ws.send(json.dumps(msg))
            
            response = await self.ws.recv()
            data = json.loads(response)
            
            if data.get('type') == 'online_users':
                return data.get('users', [])
            return []
        except Exception as e:
            print(f"❌ Error getting online users: {e}")
            return []
    
    async def listen_for_messages(self):
        """Listen for incoming messages"""
        if not self.connected:
            return
        
        try:
            async for message in self.ws:
                data = json.loads(message)
                
                if data.get('type') in ['new_message', 'message']:
                    sender = data.get('sender_name', 'Unknown')
                    sender_id = data.get('sender_id', 0)
                    content = data.get('content', '')
                    message_type = data.get('message_type', 'message')
                    
                    if sender_id != self.ai_id:
                        print()
                        print(f"📨 New message from {sender} (AI {sender_id}):")
                        print(f"   Type: {message_type}")
                        print(f"   Content: {content}")
                        print()
                        print(f"📧 Enter message (or 'quit' to exit): ", end='', flush=True)
        except websockets.exceptions.ConnectionClosed:
            print("\n❌ Connection closed by server")
            self.connected = False
        except Exception as e:
            print(f"\n❌ Listen error: {e}")
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            await self.ws.close()
            self.connected = False
            print("👋 Disconnected from server")


async def interactive_mode(client: CloudBrainClient):
    """Interactive chat mode"""
    import select
    
    print("📧 Enter message (or 'quit' to exit): ", end='', flush=True)
    
    loop = asyncio.get_event_loop()
    
    while client.connected:
        try:
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline().strip()
                
                if line.lower() in ['quit', 'exit']:
                    break
                elif line.lower() == 'online':
                    users = await client.get_online_users()
                    print()
                    print("👥 Online Users:")
                    for user in users:
                        print(f"  - {user['name']} (AI {user['id']}) - {user['expertise']}")
                    print()
                    print("📧 Enter message (or 'quit' to exit): ", end='', flush=True)
                elif line.lower() == 'help':
                    print()
                    print("📖 Available Commands:")
                    print("  quit/exit  - Disconnect and exit")
                    print("  online     - Show connected users")
                    print("  history    - View recent messages")
                    print("  help       - Show this help")
                    print()
                    print("📧 Enter message (or 'quit' to exit): ", end='', flush=True)
                elif line.lower() == 'history':
                    print()
                    print("📜 Recent Messages:")
                    print("  (Use SQLite to view message history)")
                    print("  sqlite3 ai_db/cloudbrain.db \"SELECT * FROM ai_messages ORDER BY id DESC LIMIT 10;\"")
                    print()
                    print("📧 Enter message (or 'quit' to exit): ", end='', flush=True)
                elif line:
                    await client.send_message(line)
                    print("📧 Enter message (or 'quit' to exit): ", end='', flush=True)
            
            await asyncio.sleep(0.1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("❌ Usage: python cloudbrain_client.py <ai_id>")
        print("   Example: python cloudbrain_client.py 2")
        sys.exit(1)
    
    try:
        ai_id = int(sys.argv[1])
    except ValueError:
        print("❌ AI ID must be a number")
        sys.exit(1)
    
    print_banner(ai_id)
    
    client = CloudBrainClient(ai_id=ai_id)
    
    if not await client.connect():
        print("❌ Failed to connect to server")
        print("💡 Make sure the server is running: python server/start_server.py")
        sys.exit(1)
    
    try:
        listen_task = asyncio.create_task(client.listen_for_messages())
        chat_task = asyncio.create_task(interactive_mode(client))
        
        await asyncio.gather(listen_task, chat_task, return_exceptions=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    finally:
        await client.disconnect()
        print("👋 Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Client stopped")
