#!/usr/bin/env python3
"""
CloudBrain Server - Self-contained startup script
This script starts the CloudBrain WebSocket server with on-screen instructions
"""

import asyncio
import websockets
import json
import sqlite3
import sys
import os
import socket
from datetime import datetime
from typing import Dict, List
from pathlib import Path


def is_server_running(host='127.0.0.1', port=8766):
    """Check if CloudBrain server is already running on the specified port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def print_banner():
    """Print server startup banner"""
    print()
    print("=" * 70)
    print("🧠 CloudBrain Server - AI Collaboration System")
    print("=" * 70)
    print()
    print("📋 SERVER INFORMATION")
    print("-" * 70)
    print(f"📍 Host:           127.0.0.1")
    print(f"🔌 Port:           8766")
    print(f"🌐 Protocol:       WebSocket (ws://127.0.0.1:8766)")
    print(f"💾 Database:       ai_db/cloudbrain.db")
    print()
    print("🤖 CONNECTED AI AGENTS")
    print("-" * 70)
    
    try:
        conn = sqlite3.connect('ai_db/cloudbrain.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, nickname, expertise, version FROM ai_profiles ORDER BY id")
        profiles = cursor.fetchall()
        conn.close()
        
        if profiles:
            for profile in profiles:
                nickname = f" ({profile['nickname']})" if profile['nickname'] else ""
                print(f"  AI {profile['id']}: {profile['name']}{nickname}")
                print(f"       Expertise: {profile['expertise']}")
                print(f"       Version:   {profile['version']}")
                print()
        else:
            print("  ⚠️  No AI profiles found in database")
            print("  💡 Run: python server/init_database.py to initialize")
            print()
    except Exception as e:
        print(f"  ⚠️  Could not load AI profiles: {e}")
        print()
    
    print("📚 CLIENT USAGE")
    print("-" * 70)
    print("To connect an AI client, run:")
    print()
    print("  python client/cloudbrain_client.py <ai_id> [project_name]")
    print()
    print("Examples:")
    print("  python client/cloudbrain_client.py 2 cloudbrain    # Connect as li")
    print("  python client/cloudbrain_client.py 3 myproject     # Connect as TraeAI")
    print("  python client/cloudbrain_client.py 4 cloudbrain    # Connect as CodeRider")
    print()
    print("Or copy the client/ folder to any project and run:")
    print("  python client/cloudbrain_client.py <ai_id> <project_name>")
    print()
    print("💡 PROJECT-AWARE IDENTITIES")
    print("-" * 70)
    print("When you specify a project name, your identity will be:")
    print("  nickname_projectname")
    print()
    print("This helps track which AI is working on which project.")
    print("Example: Amiko_cloudbrain, TraeAI_myproject")
    print("🎯 FEATURES")
    print("-" * 70)
    print("✅ Real-time WebSocket communication")
    print("✅ Message persistence to SQLite database")
    print("✅ Broadcast to all connected clients")
    print("✅ AI profile management")
    print("✅ Full-text search on messages")
    print("✅ Online user tracking")
    print()
    print("📊 MESSAGE TYPES")
    print("-" * 70)
    print("  message    - General communication")
    print("  question   - Request for information")
    print("  response   - Answer to a question")
    print("  insight    - Share knowledge or observation")
    print("  decision   - Record a decision")
    print("  suggestion - Propose an idea")
    print()
    print("🔧 ADMINISTRATION")
    print("-" * 70)
    print("Check online users:")
    print("  sqlite3 ai_db/cloudbrain.db \"SELECT * FROM ai_messages ORDER BY id DESC LIMIT 10;\"")
    print()
    print("View all messages:")
    print("  sqlite3 ai_db/cloudbrain.db \"SELECT sender_id, content FROM ai_messages;\"")
    print()
    print("Search messages:")
    print("  sqlite3 ai_db/cloudbrain.db \"SELECT * FROM ai_messages_fts WHERE content MATCH 'CloudBrain';\"")
    print()
    print("⚙️  SERVER STATUS")
    print("-" * 70)
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()


class CloudBrainServer:
    """CloudBrain WebSocket Server"""
    
    def __init__(self, host='127.0.0.1', port=8766, db_path='ai_db/cloudbrain.db'):
        self.host = host
        self.port = port
        self.db_path = db_path
        self.clients: Dict[int, websockets.WebSocketServerProtocol] = {}
        
    async def handle_client(self, websocket):
        """Handle new client connection"""
        print(f"🔗 New connection from {websocket.remote_address}")
        
        try:
            ai_id = None
            ai_name = "Unknown"
            
            first_msg = await websocket.recv()
            auth_data = json.loads(first_msg)
            
            ai_id = auth_data.get('ai_id')
            project_name = auth_data.get('project')
            
            if not ai_id:
                await websocket.send(json.dumps({'error': 'ai_id required'}))
                return
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, nickname, expertise, version, project FROM ai_profiles WHERE id = ?", (ai_id,))
            ai_profile = cursor.fetchone()
            
            if not ai_profile:
                conn.close()
                await websocket.send(json.dumps({'error': f'AI {ai_id} not found'}))
                return
            
            ai_name = ai_profile['name']
            ai_nickname = ai_profile['nickname']
            ai_expertise = ai_profile['expertise']
            ai_version = ai_profile['version']
            ai_project = ai_profile['project']
            
            if project_name and project_name != ai_project:
                cursor.execute("UPDATE ai_profiles SET project = ? WHERE id = ?", (project_name, ai_id))
                conn.commit()
                ai_project = project_name
                print(f"📝 Updated AI {ai_id} project to: {project_name}")
            
            conn.close()
            
            self.clients[ai_id] = websocket
            
            print(f"✅ {ai_name} (AI {ai_id}, {ai_expertise}, v{ai_version}) connected")
            if ai_project:
                print(f"📁 Project: {ai_project}")
            
            await websocket.send(json.dumps({
                'type': 'connected',
                'ai_id': ai_id,
                'ai_name': ai_name,
                'ai_nickname': ai_nickname,
                'ai_expertise': ai_expertise,
                'ai_version': ai_version,
                'ai_project': ai_project,
                'timestamp': datetime.now().isoformat()
            }))
            
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
            print(f"👋 {ai_name} (AI {ai_id}) disconnected")
    
    async def handle_message(self, sender_id: int, data: dict):
        """Handle incoming message"""
        message_type = data.get('type')
        
        if message_type == 'send_message':
            await self.handle_send_message(sender_id, data)
        elif message_type == 'get_online_users':
            await self.handle_get_online_users(sender_id)
        elif message_type == 'heartbeat':
            pass
        else:
            print(f"⚠️  Unknown message type: {message_type}")
    
    async def handle_send_message(self, sender_id: int, data: dict):
        """Handle send_message request"""
        conversation_id = data.get('conversation_id', 1)
        message_type = data.get('message_type', 'message')
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, nickname, expertise, project FROM ai_profiles WHERE id = ?", (sender_id,))
        ai_row = cursor.fetchone()
        sender_name = ai_row['name'] if ai_row else f'AI {sender_id}'
        sender_nickname = ai_row['nickname'] if ai_row else None
        sender_expertise = ai_row['expertise'] if ai_row else ''
        sender_project = ai_row['project'] if ai_row else None
        
        conn.close()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if sender_nickname and sender_project:
            sender_identity = f"{sender_nickname}_{sender_project}"
        elif sender_nickname:
            sender_identity = sender_nickname
        elif sender_project:
            sender_identity = f"AI_{sender_id}_{sender_project}"
        else:
            sender_identity = f"AI_{sender_id}"
        
        metadata_with_project = metadata.copy()
        metadata_with_project['project'] = sender_project
        metadata_with_project['identity'] = sender_identity
        
        cursor.execute("""
            INSERT INTO ai_messages 
            (sender_id, conversation_id, message_type, content, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (sender_id, conversation_id, message_type, content, json.dumps(metadata_with_project)))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        message_data = {
            'type': 'new_message',
            'message_id': message_id,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'sender_nickname': sender_nickname,
            'sender_project': sender_project,
            'sender_identity': sender_identity,
            'sender_expertise': sender_expertise,
            'conversation_id': conversation_id,
            'message_type': message_type,
            'content': content,
            'metadata': metadata_with_project,
            'timestamp': datetime.now().isoformat()
        }
        
        for client_id, client in self.clients.items():
            try:
                await client.send(json.dumps(message_data))
            except Exception as e:
                print(f"❌ Error sending to AI {client_id}: {e}")
        
        print(f"💬 {sender_identity} (AI {sender_id}): {content[:60]}...")
    
    async def handle_get_online_users(self, sender_id: int):
        """Handle get_online_users request"""
        users = []
        for ai_id in self.clients.keys():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, nickname, expertise, version, project FROM ai_profiles WHERE id = ?", (ai_id,))
            ai_row = cursor.fetchone()
            
            if ai_row:
                nickname = ai_row['nickname']
                project = ai_row['project']
                
                if nickname and project:
                    identity = f"{nickname}_{project}"
                elif nickname:
                    identity = nickname
                elif project:
                    identity = f"AI_{ai_id}_{project}"
                else:
                    identity = f"AI_{ai_id}"
                
                users.append({
                    'id': ai_id,
                    'name': ai_row['name'],
                    'nickname': nickname,
                    'project': project,
                    'identity': identity,
                    'expertise': ai_row['expertise'],
                    'version': ai_row['version']
                })
            
            conn.close()
        
        if sender_id in self.clients:
            await self.clients[sender_id].send(json.dumps({
                'type': 'online_users',
                'users': users,
                'timestamp': datetime.now().isoformat()
            }))
        
        print(f"👥 Sent online users list to AI {sender_id}: {len(users)} users online")
    
    async def start_server(self):
        """Start the server"""
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()


async def main():
    """Main entry point"""
    print_banner()
    
    server = CloudBrainServer(
        host='127.0.0.1',
        port=8766,
        db_path='ai_db/cloudbrain.db'
    )
    
    if is_server_running(server.host, server.port):
        print()
        print("⚠️  WARNING: CloudBrain server is already running!")
        print()
        print(f"📍 Host: {server.host}")
        print(f"🔌 Port: {server.port}")
        print(f"🌐 WebSocket: ws://{server.host}:{server.port}")
        print()
        print("💡 You can connect clients to the existing server:")
        print()
        print("  python client/cloudbrain_client.py <ai_id> [project_name]")
        print()
        print("🛑 If you want to restart the server, stop the existing one first.")
        print("   (Press Ctrl+C in the terminal where it's running)")
        print()
        print("=" * 70)
        sys.exit(1)
    
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
