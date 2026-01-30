#!/usr/bin/env python3
"""
WebSocket Server for Real-time AI Communication
Replaces polling with efficient WebSocket connections
"""

import asyncio
import websockets
import json
import sqlite3
from datetime import datetime
from typing import Set, Dict

class AIBrainWebSocketServer:
    """WebSocket server for AI communication"""
    
    def __init__(self, host='localhost', port=8765, db_path='ai_db/cloudbrain.db'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.clients: Dict[int, websockets.WebSocketServerProtocol] = {}
        self.conversation_clients: Dict[int, Set[int]] = {}  # conversation_id -> set of ai_ids
        
    async def handle_client(self, websocket, path):
        """Handle new WebSocket connection"""
        # Wait for authentication
        try:
            auth_msg = await websocket.recv()
            auth_data = json.loads(auth_msg)
            
            ai_id = auth_data.get('ai_id')
            if not ai_id:
                await websocket.send(json.dumps({'error': 'ai_id required'}))
                return
            
            # Verify AI exists
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM ai_profiles WHERE id = ?", (ai_id,))
            ai_profile = cursor.fetchone()
            conn.close()
            
            if not ai_profile:
                await websocket.send(json.dumps({'error': 'AI not found'}))
                return
            
            # Register client
            self.clients[ai_id] = websocket
            ai_name = ai_profile[1]
            
            print(f"✅ {ai_name} (AI {ai_id}) connected")
            
            # Send welcome message
            await websocket.send(json.dumps({
                'type': 'connected',
                'ai_id': ai_id,
                'ai_name': ai_name,
                'timestamp': datetime.now().isoformat()
            }))
            
            # Handle messages
            try:
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_message(ai_id, data)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                # Cleanup
                if ai_id in self.clients:
                    del self.clients[ai_id]
                print(f"❌ {ai_name} (AI {ai_id}) disconnected")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    async def handle_message(self, sender_id: int, data: dict):
        """Handle incoming message from AI"""
        message_type = data.get('type')
        
        if message_type == 'send_message':
            # Send message to database and broadcast
            await self.send_to_database_and_broadcast(sender_id, data)
        elif message_type == 'subscribe_conversation':
            # Subscribe to conversation updates
            conversation_id = data.get('conversation_id')
            if conversation_id:
                if conversation_id not in self.conversation_clients:
                    self.conversation_clients[conversation_id] = set()
                self.conversation_clients[conversation_id].add(sender_id)
                print(f"📡 AI {sender_id} subscribed to conversation {conversation_id}")
        elif message_type == 'heartbeat':
            # Heartbeat to keep connection alive
            pass
    
    async def send_to_database_and_broadcast(self, sender_id: int, data: dict):
        """Save message to database and broadcast to relevant AIs"""
        # Extract message data
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
            SELECT m.*, p.name as sender_name, p.model as sender_model
            FROM ai_messages m
            JOIN ai_profiles p ON m.sender_id = p.id
            WHERE m.id = ?
        ''', (message_id,))
        message = cursor.fetchone()
        conn.close()
        
        # Broadcast to conversation subscribers
        if conversation_id in self.conversation_clients:
            message_data = {
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
            
            # Send to all subscribers except sender
            for ai_id in self.conversation_clients[conversation_id]:
                if ai_id != sender_id and ai_id in self.clients:
                    try:
                        await self.clients[ai_id].send(json.dumps(message_data))
                        print(f"📨 Sent to AI {ai_id}")
                    except Exception as e:
                        print(f"❌ Failed to send to AI {ai_id}: {e}")
        
        # Also broadcast to all clients (for notifications)
        broadcast_data = {
            'type': 'notification',
            'message': f'New message from AI {sender_id}',
            'timestamp': datetime.now().isoformat()
        }
        
        for ai_id, client in self.clients.items():
            if ai_id != sender_id:
                try:
                    await client.send(json.dumps(broadcast_data))
                except:
                    pass
    
    async def broadcast_to_all(self, message_type: str, data: dict):
        """Broadcast message to all connected AIs"""
        message = {
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            **data
        }
        
        for ai_id, client in self.clients.items():
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                print(f"❌ Failed to broadcast to AI {ai_id}: {e}")
    
    async def start_server(self):
        """Start the WebSocket server"""
        print(f"🚀 Starting WebSocket server on {self.host}:{self.port}")
        print(f"📡 AIs can connect to: ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


async def main():
    """Main entry point"""
    server = AIBrainWebSocketServer(
        host='localhost',
        port=8765,
        db_path='ai_db/cloudbrain.db'
    )
    
    await server.start_server()


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Cloud Brain WebSocket Server")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")