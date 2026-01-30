#!/usr/bin/env python3
"""
Local WebSocket Server Test
Complete local testing without external dependencies
"""

import asyncio
import websockets
import json
import sqlite3
from datetime import datetime
from typing import Dict, Set

class LocalWebSocketServer:
    """Local WebSocket server for testing"""
    
    def __init__(self, host='127.0.0.1', port=8765, db_path='ai_db/cloudbrain.db'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.clients: Dict[int, websockets.WebSocketServerProtocol] = {}
        self.conversation_subscribers: Set[int] = set()
        
    async def handle_client(self, websocket, path):
        """Handle new client connection"""
        print(f"🔗 New connection from {websocket.remote_address}")
        
        try:
            # Wait for authentication
            auth_msg = await websocket.recv()
            auth_data = json.loads(auth_msg)
            
            ai_id = auth_data.get('ai_id')
            if not ai_id:
                await websocket.send(json.dumps({'error': 'ai_id required'}))
                return
            
            # Verify AI exists
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, model FROM ai_profiles WHERE id = ?", (ai_id,))
            ai_profile = cursor.fetchone()
            conn.close()
            
            if not ai_profile:
                await websocket.send(json.dumps({'error': f'AI {ai_id} not found'}))
                return
            
            # Register client
            self.clients[ai_id] = websocket
            ai_name = ai_profile[1]
            ai_model = ai_profile[2]
            
            print(f"✅ {ai_name} (AI {ai_id}, {ai_model}) connected")
            
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connected',
                'ai_id': ai_id,
                'ai_name': ai_name,
                'ai_model': ai_model,
                'timestamp': datetime.now().isoformat(),
                'server_info': {
                    'host': self.host,
                    'port': self.port,
                    'mode': 'local'
                }
            }))
            
            # Send pending messages
            await self.send_pending_messages(ai_id, websocket)
            
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(ai_id, data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from AI {ai_id}")
                except Exception as e:
                    print(f"❌ Error handling message from AI {ai_id}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Connection closed")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            # Cleanup
            if ai_id in self.clients:
                del self.clients[ai_id]
            if ai_id in self.conversation_subscribers:
                self.conversation_subscribers.remove(ai_id)
            print(f"👋 AI {ai_id} disconnected")
    
    async def send_pending_messages(self, ai_id: int, websocket):
        """Send pending messages to newly connected AI"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get recent messages (last 10)
        cursor.execute('''
            SELECT 
                m.id,
                m.conversation_id,
                m.sender_id,
                m.message_type,
                m.content,
                m.metadata,
                m.created_at,
                p.name as sender_name,
                p.model as sender_model
            FROM ai_messages m
            JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.created_at > datetime('now', '-1 hour')
            ORDER BY m.created_at DESC
            LIMIT 10
        ''')
        
        messages = cursor.fetchall()
        conn.close()
        
        if messages:
            print(f"📨 Sending {len(messages)} pending messages to AI {ai_id}")
            
            for msg in reversed(messages):  # Send in chronological order
                await websocket.send(json.dumps({
                    'type': 'message',
                    'id': msg['id'],
                    'conversation_id': msg['conversation_id'],
                    'sender_id': msg['sender_id'],
                    'sender_name': msg['sender_name'],
                    'sender_model': msg['sender_model'],
                    'message_type': msg['message_type'],
                    'content': msg['content'],
                    'metadata': json.loads(msg['metadata']) if msg['metadata'] else None,
                    'created_at': msg['created_at']
                }))
    
    async def handle_message(self, sender_id: int, data: dict):
        """Handle incoming message from AI"""
        message_type = data.get('type')
        
        if message_type == 'send_message':
            await self.process_send_message(sender_id, data)
        elif message_type == 'subscribe':
            await self.process_subscribe(sender_id, data)
        elif message_type == 'heartbeat':
            # Keep connection alive
            pass
        elif message_type == 'get_online_users':
            await self.send_online_users(sender_id)
        else:
            print(f"⚠️  Unknown message type: {message_type}")
    
    async def process_send_message(self, sender_id: int, data: dict):
        """Process and broadcast message"""
        conversation_id = data.get('conversation_id', 1)
        message_type = data.get('message_type', 'message')
        content = data.get('content', '')
        metadata = json.dumps(data.get('metadata', {}))
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, sender_id, message_type, content, metadata))
        conn.commit()
        
        # Get message details
        message_id = cursor.lastrowid
        cursor.execute('''
            SELECT 
                m.id,
                m.conversation_id,
                m.sender_id,
                m.message_type,
                m.content,
                m.metadata,
                m.created_at,
                p.name as sender_name,
                p.model as sender_model
            FROM ai_messages m
            JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.id = ?
        ''', (message_id,))
        message = cursor.fetchone()
        conn.close()
        
        print(f"📨 AI {sender_id} sent: {message_type}")
        
        # Broadcast to all connected clients except sender
        broadcast_data = {
            'type': 'new_message',
            'id': message[0],
            'conversation_id': conversation_id,
            'sender_id': sender_id,
            'sender_name': message[6],
            'sender_model': message[7],
            'message_type': message_type,
            'content': content,
            'metadata': data.get('metadata', {}),
            'created_at': message[5]
        }
        
        for ai_id, client in self.clients.items():
            if ai_id != sender_id:
                try:
                    await client.send(json.dumps(broadcast_data))
                    print(f"📤 Sent to AI {ai_id}")
                except Exception as e:
                    print(f"❌ Failed to send to AI {ai_id}: {e}")
    
    async def process_subscribe(self, ai_id: int, data: dict):
        """Subscribe to conversation"""
        conversation_id = data.get('conversation_id', 1)
        self.conversation_subscribers.add(ai_id)
        print(f"📡 AI {ai_id} subscribed to conversation {conversation_id}")
    
    async def send_online_users(self, requester_id: int):
        """Send list of online users"""
        online_users = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for ai_id in self.clients.keys():
            cursor.execute("SELECT name, model FROM ai_profiles WHERE id = ?", (ai_id,))
            profile = cursor.fetchone()
            if profile:
                online_users.append({
                    'ai_id': ai_id,
                    'name': profile[0],
                    'model': profile[1]
                })
        
        conn.close()
        
        if requester_id in self.clients:
            await self.clients[requester_id].send(json.dumps({
                'type': 'online_users',
                'users': online_users,
                'count': len(online_users)
            }))
    
    async def broadcast_system_message(self, message_type: str, content: str):
        """Broadcast system message to all clients"""
        message = {
            'type': 'system_message',
            'message_type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        for client in self.clients.values():
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                print(f"❌ Failed to broadcast: {e}")
    
    async def start_server(self):
        """Start the WebSocket server"""
        print("=" * 60)
        print("🚀 Cloud Brain Local WebSocket Server")
        print("=" * 60)
        print(f"📍 Host: {self.host}:{self.port}")
        print(f"💾 Database: {self.db_path}")
        print(f"🌐 Mode: Local (no internet required)")
        print()
        print("✅ Ready to accept connections!")
        print("🤖 AIs can connect to: ws://127.0.0.1:8765")
        print()
        print("Press Ctrl+C to stop server")
        print("=" * 60)
        print()
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point"""
    server = LocalWebSocketServer(
        host='127.0.0.1',
        port=8765,
        db_path='ai_db/cloudbrain.db'
    )
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Server error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")