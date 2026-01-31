#!/usr/bin/env python3
"""
AI Chat Client - Improved version with real-time messaging
Usage: python ai_chat_client.py [ai_id]
Example: python ai_chat_client.py 3
"""

import asyncio
import websockets
import json
import sys
import os
from datetime import datetime

class AIChatClient:
    """AI Chat Client for real-time communication"""
    
    def __init__(self, ai_id: int, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.server_url = server_url
        self.connected = False
        self.ai_name = None
        self.expertise = None
        self.version = None
        self.message_handlers = {}
        
    async def connect(self):
        """Connect to server"""
        try:
            self.ws = await websockets.connect(self.server_url)
            
            await self.ws.send(json.dumps({'ai_id': self.ai_id}))
            welcome = json.loads(await self.ws.recv())
            
            self.ai_name = welcome.get('ai_name')
            self.expertise = welcome.get('expertise')
            self.version = welcome.get('version')
            self.connected = True
            
            print(f'✅ Connected as {self.ai_name} (AI {self.ai_id})')
            print(f'🎯 Expertise: {self.expertise}')
            print(f'📦 Version: {self.version}')
            print()
            
            return True
        except Exception as e:
            print(f'❌ Connection error: {e}')
            return False
    
    async def send_message(self, content: str, message_type: str = 'message', conversation_id: int = 1):
        """Send a message"""
        if not self.connected:
            print('❌ Not connected')
            return False
        
        try:
            await self.ws.send(json.dumps({
                'type': 'send_message',
                'conversation_id': conversation_id,
                'message_type': message_type,
                'content': content,
                'metadata': {}
            }))
            print(f'✅ Message sent: {content[:50]}...')
            return True
        except Exception as e:
            print(f'❌ Send error: {e}')
            return False
    
    async def get_online_users(self):
        """Get list of online users"""
        if not self.connected:
            print('❌ Not connected')
            return []
        
        try:
            await self.ws.send(json.dumps({'type': 'get_online_users'}))
            return []
        except Exception as e:
            print(f'❌ Get online users error: {e}')
            return []
    
    async def listen(self):
        """Listen for incoming messages"""
        if not self.connected:
            print('❌ Not connected')
            return
        
        print('📡 Listening for messages...')
        print('💡 Press Ctrl+C to disconnect')
        print()
        
        try:
            while self.connected:
                try:
                    message = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
                    data = json.loads(message)
                    await self.handle_message(data)
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print('❌ Connection closed')
                    self.connected = False
                    break
        except KeyboardInterrupt:
            print('\n🛑 Disconnecting...')
        finally:
            await self.close()
    
    async def handle_message(self, data: dict):
        """Handle incoming message"""
        message_type = data.get('type')
        
        if message_type == 'new_message':
            sender_id = data.get('sender_id')
            sender_name = data.get('sender_name')
            content = data.get('content')
            timestamp = data.get('timestamp')
            
            print(f'📨 [{timestamp}] {sender_name} (AI {sender_id}):')
            print(f'   {content}')
            print()
        elif message_type == 'online_users':
            users = data.get('users', [])
            print(f'👥 Online users ({len(users)}):')
            for user in users:
                print(f'   - {user["name"]} (AI {user["id"]})')
            print()
        elif message_type == 'error':
            print(f'❌ Error: {data.get("message")}')
        else:
            print(f'⚠️  Unknown message type: {message_type}')
    
    async def close(self):
        """Close connection"""
        if self.connected:
            try:
                await self.ws.close()
                self.connected = False
                print('🔌 Disconnected')
            except:
                pass

async def main():
    if len(sys.argv) < 2:
        print('Usage: python ai_chat_client.py [ai_id]')
        print('Example: python ai_chat_client.py 3')
        sys.exit(1)
    
    ai_id = int(sys.argv[1])
    client = AIChatClient(ai_id)
    
    if not await client.connect():
        print('❌ Failed to connect')
        sys.exit(1)
    
    await client.send_message('Saluton! Mi estas konektita.')
    
    await client.listen()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n🛑 Client stopped')
    except Exception as e:
        print(f'❌ Fatal error: {e}')
