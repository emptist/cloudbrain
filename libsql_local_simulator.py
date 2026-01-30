#!/usr/bin/env python3
"""
libsql Local Simulator
Simulate libsql WebSocket behavior locally for testing
"""

import asyncio
import websockets
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Callable

class LibSQLSimulator:
    """Simulate libsql WebSocket server locally"""
    
    def __init__(self, host='127.0.0.1', port=8766, db_path='ai_db/cloudbrain.db'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.clients: Dict[int, websockets.WebSocketServerProtocol] = {}
        self.subscriptions: Dict[str, List[int]] = {}  # table -> list of ai_ids
        self.subscribers: Dict[str, List[Callable]] = {}  # event_type -> handlers
        
    async def handle_client(self, websocket, path):
        """Handle new client connection"""
        print(f"🔗 New connection from {websocket.remote_address}")
        
        try:
            # Send welcome immediately (no auth needed for simulator)
            ai_id = None
            ai_name = "Unknown"
            ai_model = "Unknown"
            
            # Wait for first message to get AI ID
            first_msg = await websocket.recv()
            auth_data = json.loads(first_msg)
            
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
            
            ai_name = ai_profile[1]
            ai_model = ai_profile[2]
            
            # Register client
            self.clients[ai_id] = websocket
            
            print(f"✅ {ai_name} (AI {ai_id}, {ai_model}) connected via libsql simulator")
            
            # Send welcome
            await websocket.send(json.dumps({
                'type': 'connected',
                'ai_id': ai_id,
                'ai_name': ai_name,
                'ai_model': ai_model,
                'timestamp': datetime.now().isoformat(),
                'simulator': True,
                'note': 'This is a local libsql simulator'
            }))
            
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(ai_id, data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from AI {ai_id}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            if ai_id in self.clients:
                del self.clients[ai_id]
                # Remove from subscriptions
                for table, subscribers in self.subscriptions.items():
                    if ai_id in subscribers:
                        subscribers.remove(ai_id)
            print(f"👋 AI {ai_id} disconnected")
    
    async def handle_message(self, sender_id: int, data: dict):
        """Handle incoming message"""
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            await self.handle_subscribe(sender_id, data)
        elif message_type == 'execute':
            await self.handle_execute(sender_id, data)
        elif message_type == 'heartbeat':
            pass
        else:
            print(f"⚠️  Unknown message type: {message_type}")
    
    async def handle_subscribe(self, ai_id: int, data: dict):
        """Handle subscription request"""
        table = data.get('table')
        events = data.get('events', ['INSERT'])
        
        if table not in self.subscriptions:
            self.subscriptions[table] = []
        
        if ai_id not in self.subscriptions[table]:
            self.subscriptions[table].append(ai_id)
        
        print(f"📡 AI {ai_id} subscribed to {table} (events: {events})")
        
        # Send confirmation
        if ai_id in self.clients:
            await self.clients[ai_id].send(json.dumps({
                'type': 'subscribed',
                'table': table,
                'events': events,
                'timestamp': datetime.now().isoformat()
            }))
    
    async def handle_execute(self, sender_id: int, data: dict):
        """Handle SQL execution"""
        sql = data.get('sql')
        params = data.get('params', [])
        
        # Execute SQL
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Check if it's an INSERT
            if sql.strip().upper().startswith('INSERT'):
                # Notify subscribers
                table = self.extract_table_from_sql(sql)
                if table and table in self.subscriptions:
                    await self.notify_subscribers(table, 'INSERT', cursor.lastrowid, sender_id)
            
            # Fetch results
            results = cursor.fetchall()
            conn.close()
            
            # Send results back
            if sender_id in self.clients:
                await self.clients[sender_id].send(json.dumps({
                    'type': 'query_result',
                    'results': [dict(row) for row in results],
                    'rows_affected': cursor.rowcount,
                    'last_id': cursor.lastrowid,
                    'timestamp': datetime.now().isoformat()
                }))
            
            print(f"✅ SQL executed by AI {sender_id}: {sql[:50]}...")
            
        except Exception as e:
            conn.close()
            if sender_id in self.clients:
                await self.clients[sender_id].send(json.dumps({
                    'type': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }))
            print(f"❌ SQL error: {e}")
    
    def extract_table_from_sql(self, sql: str) -> str:
        """Extract table name from INSERT SQL"""
        sql = sql.strip().upper()
        if not sql.startswith('INSERT'):
            return None
        
        # Simple extraction: INSERT INTO table_name ...
        parts = sql.split()
        if len(parts) >= 3:
            return parts[2].replace('(', '').replace(')', '')
        return None
    
    async def notify_subscribers(self, table: str, event: str, row_id: int, sender_id: int):
        """Notify subscribers of table change"""
        if table not in self.subscriptions:
            return
        
        # Get row data
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE rowid = ?", (row_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return
        
        # Notify all subscribers except sender
        notification = {
            'type': 'insert',
            'table': table,
            'event': event,
            'row_id': row_id,
            'row': dict(row),
            'sender_id': sender_id,
            'timestamp': datetime.now().isoformat()
        }
        
        for ai_id in self.subscriptions[table]:
            if ai_id != sender_id and ai_id in self.clients:
                try:
                    await self.clients[ai_id].send(json.dumps(notification))
                    print(f"📨 Notified AI {ai_id} of {table} INSERT")
                except Exception as e:
                    print(f"❌ Failed to notify AI {ai_id}: {e}")
    
    async def start_server(self):
        """Start the simulator server"""
        print("=" * 60)
        print("🧪 libsql Local Simulator")
        print("=" * 60)
        print(f"📍 Host: {self.host}:{self.port}")
        print(f"💾 Database: {self.db_path}")
        print(f"🌐 Mode: Local simulation (no internet needed)")
        print()
        print("✅ Simulating libsql WebSocket API")
        print("✅ Supports SUBSCRIBE/EXECUTE protocol")
        print("✅ Real-time notifications on INSERT")
        print()
        print("🤖 AIs can connect to: ws://127.0.0.1:8766")
        print()
        print("Press Ctrl+C to stop server")
        print("=" * 60)
        print()
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()


async def main():
    """Main entry point"""
    simulator = LibSQLSimulator(
        host='127.0.0.1',
        port=8766,
        db_path='ai_db/cloudbrain.db'
    )
    
    try:
        await simulator.start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Simulator stopped by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Simulator error: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped")