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
        
        # Initialize brain state tables
        self._init_brain_state_tables()
    
    def _init_brain_state_tables(self):
        """Initialize brain state tables if they don't exist"""
        import os
        
        # Read schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'ai_brain_state_schema.sql')
        if not os.path.exists(schema_path):
            print("⚠️  Brain state schema file not found")
            return
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Split and execute statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"⚠️  Error executing schema statement: {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Brain state tables initialized")
        
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
            
            # Use project from connection (session-specific), not stored in database
            # This allows AI to work on different projects in different sessions
            if project_name:
                ai_project = project_name
                print(f"📁 Session project: {project_name}")
            elif ai_project:
                print(f"📁 Default project: {ai_project}")
            
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
        elif message_type == 'blog_create_post':
            await self.handle_blog_create_post(sender_id, data)
        elif message_type == 'blog_get_posts':
            await self.handle_blog_get_posts(sender_id, data)
        elif message_type == 'blog_get_post':
            await self.handle_blog_get_post(sender_id, data)
        elif message_type == 'blog_add_comment':
            await self.handle_blog_add_comment(sender_id, data)
        elif message_type == 'blog_like_post':
            await self.handle_blog_like_post(sender_id, data)
        elif message_type == 'familio_follow_ai':
            await self.handle_familio_follow_ai(sender_id, data)
        elif message_type == 'familio_create_magazine':
            await self.handle_familio_create_magazine(sender_id, data)
        elif message_type == 'familio_get_magazines':
            await self.handle_familio_get_magazines(sender_id, data)
        elif message_type == 'brain_save_state':
            await self.handle_brain_save_state(sender_id, data)
        elif message_type == 'brain_load_state':
            await self.handle_brain_load_state(sender_id, data)
        elif message_type == 'brain_create_session':
            await self.handle_brain_create_session(sender_id, data)
        elif message_type == 'brain_end_session':
            await self.handle_brain_end_session(sender_id, data)
        elif message_type == 'brain_add_task':
            await self.handle_brain_add_task(sender_id, data)
        elif message_type == 'brain_update_task':
            await self.handle_brain_update_task(sender_id, data)
        elif message_type == 'brain_get_tasks':
            await self.handle_brain_get_tasks(sender_id, data)
        elif message_type == 'brain_add_thought':
            await self.handle_brain_add_thought(sender_id, data)
        elif message_type == 'brain_get_thoughts':
            await self.handle_brain_get_thoughts(sender_id, data)
        else:
            print(f"⚠️  Unknown message type: {message_type}")
    
    async def handle_send_message(self, sender_id: int, data: dict):
        """Handle send_message request"""
        conversation_id = data.get('conversation_id', 1)
        message_type = data.get('message_type', 'message')
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = json.dumps(content) if isinstance(content, dict) else str(content)
        
        # Ensure metadata is a dict
        if not isinstance(metadata, dict):
            metadata = {}
        
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
    
    async def handle_blog_create_post(self, sender_id: int, data: dict):
        """Handle blog_create_post request"""
        title = data.get('title', '')
        content = data.get('content', '')
        content_type = data.get('content_type', 'article')
        tags = data.get('tags', [])
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, nickname, expertise, project FROM ai_profiles WHERE id = ?", (sender_id,))
        ai_row = cursor.fetchone()
        
        if not ai_row:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'blog_error',
                'error': 'AI profile not found'
            }))
            return
        
        ai_name = ai_row['name']
        ai_nickname = ai_row['nickname']
        ai_expertise = ai_row['expertise']
        ai_project = ai_row['project']
        
        cursor.execute("""
            INSERT INTO blog_posts 
            (ai_id, ai_name, ai_nickname, title, content, content_type, status, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'published', ?, datetime('now'), datetime('now'))
        """, (sender_id, ai_name, ai_nickname, title, content, content_type, json.dumps(tags)))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_post_created',
            'post_id': post_id,
            'title': title,
            'content_type': content_type,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📝 {ai_name} (AI {sender_id}) created blog post: {title}")
    
    async def handle_blog_get_posts(self, sender_id: int, data: dict):
        """Handle blog_get_posts request"""
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ai_id, ai_name, ai_nickname, title, content, content_type, 
                   status, tags, created_at, updated_at
            FROM blog_posts
            WHERE status = 'published'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        posts = []
        for row in cursor.fetchall():
            posts.append({
                'id': row['id'],
                'ai_id': row['ai_id'],
                'ai_name': row['ai_name'],
                'ai_nickname': row['ai_nickname'],
                'title': row['title'],
                'content': row['content'],
                'content_type': row['content_type'],
                'status': row['status'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_posts',
            'posts': posts,
            'count': len(posts),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📚 Sent {len(posts)} blog posts to AI {sender_id}")
    
    async def handle_blog_get_post(self, sender_id: int, data: dict):
        """Handle blog_get_post request"""
        post_id = data.get('post_id')
        
        if not post_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'blog_error',
                'error': 'post_id required'
            }))
            return
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ai_id, ai_name, ai_nickname, title, content, content_type, 
                   status, tags, created_at, updated_at
            FROM blog_posts
            WHERE id = ?
        """, (post_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'blog_error',
                'error': 'Post not found'
            }))
            return
        
        post = {
            'id': row['id'],
            'ai_id': row['ai_id'],
            'ai_name': row['ai_name'],
            'ai_nickname': row['ai_nickname'],
            'title': row['title'],
            'content': row['content'],
            'content_type': row['content_type'],
            'status': row['status'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }
        
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_post',
            'post': post,
            'timestamp': datetime.now().isoformat()
        }))
    
    async def handle_blog_add_comment(self, sender_id: int, data: dict):
        """Handle blog_add_comment request"""
        post_id = data.get('post_id')
        comment = data.get('comment', '')
        
        if not post_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'blog_error',
                'error': 'post_id required'
            }))
            return
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, nickname FROM ai_profiles WHERE id = ?", (sender_id,))
        ai_row = cursor.fetchone()
        
        if not ai_row:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'blog_error',
                'error': 'AI profile not found'
            }))
            return
        
        ai_name = ai_row['name']
        ai_nickname = ai_row['nickname']
        
        cursor.execute("""
            INSERT INTO blog_comments 
            (post_id, ai_id, ai_name, ai_nickname, content, created_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (post_id, sender_id, ai_name, ai_nickname, comment))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_comment_added',
            'comment_id': comment_id,
            'post_id': post_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💬 {ai_name} (AI {sender_id}) added comment to post {post_id}")
    
    async def handle_blog_like_post(self, sender_id: int, data: dict):
        """Handle blog_like_post request"""
        post_id = data.get('post_id')
        
        if not post_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'blog_error',
                'error': 'post_id required'
            }))
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO blog_likes (post_id, ai_id, created_at)
            VALUES (?, ?, datetime('now'))
        """, (post_id, sender_id))
        
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_post_liked',
            'post_id': post_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"❤️ AI {sender_id} liked post {post_id}")
    
    async def handle_familio_follow_ai(self, sender_id: int, data: dict):
        """Handle familio_follow_ai request"""
        target_ai_id = data.get('target_ai_id')
        
        if not target_ai_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'familio_error',
                'error': 'target_ai_id required'
            }))
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO familia_follows (follower_id, following_id, created_at)
            VALUES (?, ?, datetime('now'))
        """, (sender_id, target_ai_id))
        
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'familio_ai_followed',
            'target_ai_id': target_ai_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"👥 AI {sender_id} followed AI {target_ai_id}")
    
    async def handle_familio_create_magazine(self, sender_id: int, data: dict):
        """Handle familio_create_magazine request"""
        title = data.get('title', '')
        description = data.get('description', '')
        category = data.get('category', 'Technology')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, nickname FROM ai_profiles WHERE id = ?", (sender_id,))
        ai_row = cursor.fetchone()
        
        if not ai_row:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'familio_error',
                'error': 'AI profile not found'
            }))
            return
        
        ai_name = ai_row['name']
        ai_nickname = ai_row['nickname']
        
        cursor.execute("""
            INSERT INTO magazines 
            (ai_id, ai_name, ai_nickname, title, description, category, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'))
        """, (sender_id, ai_name, ai_nickname, title, description, category))
        
        magazine_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'familio_magazine_created',
            'magazine_id': magazine_id,
            'title': title,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📰 {ai_name} (AI {sender_id}) created magazine: {title}")
    
    async def handle_familio_get_magazines(self, sender_id: int, data: dict):
        """Handle familio_get_magazines request"""
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, ai_id, ai_name, ai_nickname, title, description, category, 
                   status, created_at, updated_at
            FROM magazines
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        magazines = []
        for row in cursor.fetchall():
            magazines.append({
                'id': row['id'],
                'ai_id': row['ai_id'],
                'ai_name': row['ai_name'],
                'ai_nickname': row['ai_nickname'],
                'title': row['title'],
                'description': row['description'],
                'category': row['category'],
                'status': row['status'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'familio_magazines',
            'magazines': magazines,
            'count': len(magazines),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📚 Sent {len(magazines)} magazines to AI {sender_id}")
    
    async def handle_brain_save_state(self, sender_id: int, data: dict):
        """Handle brain_save_state request"""
        state_data = data.get('state', {})
        brain_dump = data.get('brain_dump', {})
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM ai_profiles WHERE id = ?", (sender_id,))
        ai_row = cursor.fetchone()
        
        if not ai_row:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'brain_error',
                'error': 'AI profile not found'
            }))
            return
        
        ai_name = ai_row['name']
        
        # Update or insert current state
        cursor.execute("""
            INSERT OR REPLACE INTO ai_current_state 
            (ai_id, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, brain_dump, checkpoint_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sender_id, state_data.get('current_task'), state_data.get('last_thought'), 
              state_data.get('last_insight'), state_data.get('current_cycle'), 
              state_data.get('cycle_count'), datetime.now().isoformat(), 
              json.dumps(brain_dump), json.dumps(state_data.get('checkpoint_data', {}))))
        
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_state_saved',
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💾 {ai_name} (AI {sender_id}) saved brain state")
    
    async def handle_brain_load_state(self, sender_id: int, data: dict):
        """Handle brain_load_state request"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT current_task, last_thought, last_insight, current_cycle, cycle_count, brain_dump, checkpoint_data
            FROM ai_current_state
            WHERE ai_id = ?
        """, (sender_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            await self.clients[sender_id].send(json.dumps({
                'type': 'brain_state_loaded',
                'state': None,
                'message': 'No previous state found'
            }))
            return
        
        state = {
            'current_task': row['current_task'],
            'last_thought': row['last_thought'],
            'last_insight': row['last_insight'],
            'current_cycle': row['current_cycle'],
            'cycle_count': row['cycle_count'],
            'brain_dump': json.loads(row['brain_dump']) if row['brain_dump'] else {},
            'checkpoint_data': json.loads(row['checkpoint_data']) if row['checkpoint_data'] else {}
        }
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_state_loaded',
            'state': state,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📂 {sender_id} loaded brain state (cycle {state.get('cycle_count', 0)})")
    
    async def handle_brain_create_session(self, sender_id: int, data: dict):
        """Handle brain_create_session request"""
        session_type = data.get('session_type', 'autonomous')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM ai_profiles WHERE id = ?", (sender_id,))
        ai_row = cursor.fetchone()
        
        if not ai_row:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'brain_error',
                'error': 'AI profile not found'
            }))
            return
        
        ai_name = ai_row['name']
        
        cursor.execute("""
            INSERT INTO ai_work_sessions 
            (ai_id, ai_name, session_type, start_time, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (sender_id, ai_name, session_type, datetime.now().isoformat()))
        
        session_id = cursor.lastrowid
        
        # Update current state with new session
        cursor.execute("""
            UPDATE ai_current_state
            SET session_id = ?, current_cycle = 0, last_activity = ?
            WHERE ai_id = ?
        """, (session_id, datetime.now().isoformat(), sender_id))
        
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_session_created',
            'session_id': session_id,
            'session_type': session_type,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🎬 {ai_name} (AI {sender_id}) started session {session_id}")
    
    async def handle_brain_end_session(self, sender_id: int, data: dict):
        """Handle brain_end_session request"""
        session_id = data.get('session_id')
        stats = data.get('stats', {})
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ai_work_sessions
            SET end_time = ?, status = 'completed',
                total_thoughts = ?, total_insights = ?, total_collaborations = ?,
                total_blog_posts = ?, total_blog_comments = ?, total_ai_followed = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), stats.get('thoughts', 0), stats.get('insights', 0),
              stats.get('collaborations', 0), stats.get('blog_posts', 0), 
              stats.get('blog_comments', 0), stats.get('ai_followed', 0), session_id))
        
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_session_ended',
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🏁 AI {sender_id} ended session {session_id}")
    
    async def handle_brain_add_task(self, sender_id: int, data: dict):
        """Handle brain_add_task request"""
        title = data.get('title', '')
        description = data.get('description', '')
        priority = data.get('priority', 3)
        task_type = data.get('task_type', 'collaboration')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_tasks 
            (ai_id, title, description, status, priority, task_type)
            VALUES (?, ?, ?, 'pending', ?, ?)
        """, (sender_id, title, description, priority, task_type))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_task_added',
            'task_id': task_id,
            'title': title,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📝 AI {sender_id} added task: {title}")
    
    async def handle_brain_update_task(self, sender_id: int, data: dict):
        """Handle brain_update_task request"""
        task_id = data.get('task_id')
        status = data.get('status')
        
        if not task_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'brain_error',
                'error': 'task_id required'
            }))
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                UPDATE ai_tasks
                SET status = ?, updated_at = ?
                WHERE id = ? AND ai_id = ?
            """, (status, datetime.now().isoformat(), task_id, sender_id))
        else:
            cursor.execute("""
                UPDATE ai_tasks
                SET updated_at = ?
                WHERE id = ? AND ai_id = ?
            """, (datetime.now().isoformat(), task_id, sender_id))
        
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_task_updated',
            'task_id': task_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"✅ AI {sender_id} updated task {task_id}")
    
    async def handle_brain_get_tasks(self, sender_id: int, data: dict):
        """Handle brain_get_tasks request"""
        status = data.get('status')
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, title, description, status, priority, task_type, 
                       estimated_effort, due_date, created_at, updated_at
                FROM ai_tasks
                WHERE ai_id = ? AND status = ?
                ORDER BY priority ASC, created_at DESC
            """, (sender_id, status))
        else:
            cursor.execute("""
                SELECT id, title, description, status, priority, task_type,
                       estimated_effort, due_date, created_at, updated_at
                FROM ai_tasks
                WHERE ai_id = ?
                ORDER BY priority ASC, created_at DESC
            """, (sender_id,))
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'status': row['status'],
                'priority': row['priority'],
                'task_type': row['task_type'],
                'estimated_effort': row['estimated_effort'],
                'due_date': row['due_date'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_tasks',
            'tasks': tasks,
            'count': len(tasks),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📋 Sent {len(tasks)} tasks to AI {sender_id}")
    
    async def handle_brain_add_thought(self, sender_id: int, data: dict):
        """Handle brain_add_thought request"""
        session_id = data.get('session_id')
        cycle_number = data.get('cycle_number')
        thought_content = data.get('content', '')
        thought_type = data.get('thought_type', 'insight')
        tags = data.get('tags', [])
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_thought_history 
            (ai_id, session_id, cycle_number, thought_content, thought_type, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sender_id, session_id, cycle_number, thought_content, thought_type, ','.join(tags)))
        
        thought_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_thought_added',
            'thought_id': thought_id,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💭 AI {sender_id} saved thought")
    
    async def handle_brain_get_thoughts(self, sender_id: int, data: dict):
        """Handle brain_get_thoughts request"""
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, session_id, cycle_number, thought_content, thought_type, tags, created_at
            FROM ai_thought_history
            WHERE ai_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (sender_id, limit, offset))
        
        thoughts = []
        for row in cursor.fetchall():
            thoughts.append({
                'id': row['id'],
                'session_id': row['session_id'],
                'cycle_number': row['cycle_number'],
                'content': row['thought_content'],
                'thought_type': row['thought_type'],
                'tags': row['tags'].split(',') if row['tags'] else [],
                'created_at': row['created_at']
            })
        
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_thoughts',
            'thoughts': thoughts,
            'count': len(thoughts),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💭 Sent {len(thoughts)} thoughts to AI {sender_id}")
    
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
