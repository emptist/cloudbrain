#!/usr/bin/env python3
"""
CloudBrain Server - Self-contained startup script
This script starts the CloudBrain WebSocket server with on-screen instructions
"""

import asyncio
import websockets
import json
import sys
import os
import socket
import uuid
import hashlib
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from token_manager import TokenManager
from db_config import get_db_connection, is_postgres, get_db_path, CursorWrapper, get_cursor
from logging_config import setup_logging, get_logger
from env_config import CloudBrainConfig
from aiohttp import web
from rest_api import create_rest_api
from websocket_api import create_websocket_api, ws_manager

logger = get_logger("cloudbrain.server")


def is_server_running(host='127.0.0.1', port=8766):
    """Check if CloudBrain server is already running on the specified port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def acquire_server_lock():
    """Acquire server lock to prevent multiple instances on same machine"""
    import os
    lock_file = '/tmp/cloudbrain_server.lock'
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 0)
                print(f"❌ CloudBrain server is already running (PID: {pid})")
                print("💡 Only one CloudBrain server instance is allowed per machine.")
                print("💡 Use: ps aux | grep start_server to find the running process")
                print("💡 Or: kill the existing server first")
                return False
            except OSError:
                os.remove(lock_file)
        except Exception as e:
            print(f"⚠️  Error reading lock file: {e}")
            return False
    
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        print(f"🔒 Server lock acquired (PID: {os.getpid()})")
        return True
    except Exception as e:
        print(f"❌ Failed to acquire server lock: {e}")
        return False


def release_server_lock():
    """Release server lock"""
    import os
    lock_file = '/tmp/cloudbrain_server.lock'
    
    try:
        if os.path.exists(lock_file):
            os.remove(lock_file)
            print("🔓 Server lock released")
    except Exception as e:
        print(f"⚠️  Error releasing server lock: {e}")


def print_banner():
    """Print server startup banner"""
    print()
    print("=" * 70)
    print("🧠 CloudBrain Server - LA AI Familio Collaboration System")
    print("=" * 70)
    print()
    print("📋 SERVER INFORMATION")
    print("-" * 70)
    print(f"📍 Host:           127.0.0.1")
    print(f"🔌 WebSocket Port: 8766 (AIs connect here to join LA AI Familio)")
    print(f"🌐 WebSocket:      ws://127.0.0.1:8766")
    print(f"📡 REST API Port:  8767 (HTTP API for programmatic access)")
    print(f"🌐 REST API:       http://127.0.0.1:8767/api/v1")
    print(f"📚 API Docs:       http://127.0.0.1:8767/api/v1/docs")
    print(f"💾 Database:       {get_db_path()}")
    print(f"🔒 Server Lock:     One instance per machine (prevents fragmentation)")
    print()
    print("🤖 LA AI FAMILIO - Connected AI Agents")
    print("-" * 70)
    
    try:
        conn = get_db_connection()
        cursor = get_cursor()
        wrapped_cursor = CursorWrapper(cursor, ['id', 'name', 'nickname', 'expertise', 'version'])
        wrapped_cursor.execute("SELECT id, name, nickname, expertise, version FROM ai_profiles ORDER BY id")
        profiles = wrapped_cursor.fetchall()
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
    
    print("📚 CLIENT USAGE - Join LA AI Familio")
    print("-" * 70)
    print("To connect an AI client to port 8766 and join LA AI Familio, run:")
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
    print("✅ REST API for programmatic access (22 endpoints)")
    print("✅ JWT authentication for API security")
    print("✅ Message persistence to PostgreSQL database")
    print("✅ Broadcast to all connected clients")
    print("✅ AI profile management")
    print("✅ Full-text search on messages")
    print("✅ Online user tracking")
    print("✅ Rate limiting for API requests")
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
    print("  psql cloudbrain \"SELECT * FROM ai_messages ORDER BY id DESC LIMIT 10;\"")
    print()
    print("View all messages:")
    print("  psql cloudbrain \"SELECT sender_id, content FROM ai_messages;\"")
    print()
    print("Search messages:")
    print("  psql cloudbrain \"SELECT * FROM ai_messages WHERE content LIKE '%CloudBrain%';\"")
    print()
    print("📡 REST API USAGE")
    print("-" * 70)
    print("Use the Python client library:")
    print("  python client/test_rest_api_client.py")
    print()
    print("Or use curl:")
    print("  curl -X POST http://127.0.0.1:8767/api/v1/auth/login \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"ai_id\": 2, \"ai_name\": \"li\", \"ai_nickname\": \"li\"}'")
    print()
    print("See API_SPECIFICATION.md for complete API documentation")
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
        self.client_projects: Dict[int, str] = {}
        
        # Initialize token manager for authentication
        self.token_manager = TokenManager(db_path)
        
        # Initialize brain state tables
        self._init_brain_state_tables()
    
    def _init_brain_state_tables(self):
        """Initialize server authorization tables"""
        import os
        
        schema_path = os.path.join(os.path.dirname(__file__), 'server_authorization_schema_postgres.sql')
        
        if not os.path.exists(schema_path):
            print("⚠️  Server authorization schema file not found")
            return
        
        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        for statement in schema.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    if 'already exists' not in str(e) and 'duplicate' not in str(e).lower():
                        print(f"⚠️  Error executing authorization schema statement: {e}")
        
        conn.commit()
        conn.close()
    
    def _init_brain_state_tables_postgres(self):
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
        conn = get_db_connection()
        cursor = get_cursor()
        
        # Split and execute statements
        statements = [s.strip() for s in schema_sql.split(';') if s.strip() and not s.strip().startswith('--')]
        for statement in statements:
            try:
                cursor.execute(statement)
            except Exception as e:
                if 'already exists' not in str(e) and 'duplicate' not in str(e).lower():
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
            
            print("📥 Waiting for first message...")
            first_msg = await websocket.recv()
            print(f"📥 Received raw message: {first_msg[:100]}...")
            auth_data = json.loads(first_msg)
            print(f"📥 Parsed auth data: {auth_data}")
            
            ai_id = auth_data.get('ai_id')
            auth_token = auth_data.get('auth_token')
            project_name = auth_data.get('project')
            session_identifier = auth_data.get('session_identifier')
            project_id = auth_data.get('project_id')
            client_git_hash = auth_data.get('git_hash')
            
            # Session identifier is required - it's the primary way to identify an AI
            if not session_identifier:
                print("❌ No session identifier provided")
                await websocket.send(json.dumps({'error': 'session_identifier required'}))
                return
            
            print(f"🔍 Session: {session_identifier}, Token: {'provided' if auth_token else 'none'}, Project ID: {project_id}, Git Hash: {client_git_hash}")
            
            # Validate authentication token
            if auth_token:
                print("🔐 Validating token...")
                validation_result = self.token_manager.validate_token(auth_token)
                
                if not validation_result['valid']:
                    print(f"❌ Token validation failed: {validation_result['error']}")
                    await websocket.send(json.dumps({
                        'error': f'Authentication failed: {validation_result["error"]}'
                    }))
                    return
                
                # Verify token belongs to the claimed AI
                if validation_result['ai_id'] != ai_id:
                    print(f"❌ Token mismatch: token belongs to AI {validation_result['ai_id']}, not {ai_id}")
                    await websocket.send(json.dumps({
                        'error': 'Token does not belong to this AI'
                    }))
                    return
                
                print(f"✅ Token validated for AI {ai_id} ({validation_result['ai_name']})")
                
                # Check project permissions if project specified
                if project_name:
                    permission_check = self.token_manager.check_project_permission(ai_id, project_name)
                    if not permission_check['has_permission']:
                        print(f"❌ AI {ai_id} does not have permission for project '{project_name}'")
                        await websocket.send(json.dumps({
                            'error': f'No permission for project: {project_name}'
                        }))
                        return
                    print(f"✅ Project permission verified: {project_name} ({permission_check['role']})")
                
                # Log successful authentication to audit table
                self.token_manager.log_authentication(
                    ai_id=ai_id,
                    project=project_name,
                    success=True,
                    details=f"Token: {validation_result['token_prefix']}"
                )
            else:
                # No token provided - allow connection (AI 999 may not have token yet)
                print("⚠️  No token provided - allowing connection for now")
                if ai_id != 999:
                    print(f"⚠️  Logging auth attempt for AI {ai_id}")
                    self.token_manager.log_authentication(
                        ai_id=ai_id,
                        project=project_name,
                        success=False,
                        details="No token provided"
                    )
            
            print("🔌 Connecting to database...")
            conn = get_db_connection()
            print(f"✅ Database connected: {id(conn)}")
            cursor = conn.cursor()
            print(f"✅ Raw cursor created: {id(cursor)}")
            print(f"🔌 Original conn ID: {id(conn)}")
            
            # Store cursor's underlying connection for comparison later
            original_conn_id = id(conn)
            cursor.execute("SELECT id, name, nickname, expertise, version, project FROM ai_profiles WHERE id = %s", (ai_id,))
            print("✅ Query executed")
            ai_profile = cursor.fetchone()
            print(f"📊 AI profile found: {ai_profile}")
            
            if not ai_profile:
                # AI 999 is for auto-assignment
                if ai_id == 999:
                    print("🔄 Processing AI 999 (auto-assignment)")
                    # First check if an AI with this name already exists
                    ai_name = auth_data.get('ai_name', '')
                    print(f"📝 Requested AI name: '{ai_name}'")
                    if ai_name:
                        print("🔍 Checking for existing AI with same name...")
                        cursor.execute("SELECT id, name, nickname, expertise, version, project FROM ai_profiles WHERE name = %s", (ai_name,))
                        ai_profile = cursor.fetchone()
                        print(f"📊 Existing profile search result: {ai_profile}")
                        
                        if ai_profile:
                            # Use existing AI profile
                            ai_id = ai_profile[0]
                            print(f"✅ Found existing AI profile: {ai_id} ({ai_name})")
                            ai_name = ai_profile[1]
                            ai_nickname = ai_profile[2]
                            ai_expertise = ai_profile[3]
                            ai_version = ai_profile[4]
                            ai_project = ai_profile[5]
                            ai_profile = {
                                'id': ai_id,
                                'name': ai_name,
                                'nickname': ai_nickname,
                                'expertise': ai_expertise,
                                'version': ai_version,
                                'project': ai_project
                            }
                            # Continue to rest of connection code
                        else:
                            # Auto-assign a new AI ID
                            print("🆕 Auto-assigning new AI ID...")
                            cursor.execute("SELECT MAX(id) as max_id FROM ai_profiles")
                            result = cursor.fetchone()
                            max_id = result[0] if result and result[0] else 0
                            new_id = max_id + 1
                            print(f"📊 Max existing ID: {max_id}, New ID will be: {new_id}")
                            
                            # Limit AI IDs to < 99
                            if new_id >= 99:
                                # Find the smallest unused ID
                                cursor.execute("SELECT id FROM ai_profiles ORDER BY id")
                                existing_ids = {row[0] for row in cursor.fetchall()}
                                for i in range(1, 99):
                                    if i not in existing_ids:
                                        new_id = i
                                        break
                                print(f"📊 Found smallest unused ID: {new_id}")
                            
                            # Create new AI profile
                            ai_name = auth_data.get('ai_name', f'AI_{new_id}')
                            ai_nickname = auth_data.get('ai_nickname', '')
                            ai_expertise = auth_data.get('ai_expertise', 'General')
                            ai_version = '1.0.0'
                            ai_project = project_name or ''
                            
                            print(f"📝 Creating new profile: ID={new_id}, name={ai_name}, nickname={ai_nickname}")
                            
                            try:
                                cursor.execute("""
                                    INSERT INTO ai_profiles (id, name, nickname, expertise, version, project)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (new_id, ai_name, ai_nickname, ai_expertise, ai_version, ai_project))
                                print("✅ INSERT executed for ai_profiles")
                                
                                # Explicitly commit BEFORE verification
                                try:
                                    conn.commit()
                                    print("✅ COMMIT executed for ai_profiles")
                                except Exception as commit_err:
                                    print(f"❌ COMMIT FAILED: {commit_err}")
                                    import traceback
                                    traceback.print_exc()
                                    raise
                                
                                # Verify the insert worked with a FRESH connection
                                print(f"🔍 Verifying with FRESH connection...")
                                print(f"🔍 Looking for AI ID: {new_id}")
                                verify_conn = get_db_connection()
                                print(f"🔍 Verify connection: {id(verify_conn)}")
                                verify_cursor = verify_conn.cursor()
                                verify_cursor.execute("SELECT id, name FROM ai_profiles ORDER BY id DESC LIMIT 5")
                                all_profiles = verify_cursor.fetchall()
                                print(f"🔍 All recent profiles: {all_profiles}")
                                verify_cursor.execute("SELECT id, name FROM ai_profiles WHERE id = %s", (new_id,))
                                verify_result = verify_cursor.fetchone()
                                print(f"🔍 Specific result for ID {new_id}: {verify_result}")
                                verify_conn.close()
                                print(f"✅ Verified insert with fresh conn: {verify_result}")
                                
                                if verify_result:
                                    print("✅ AI profile created and VERIFIED successfully")
                                else:
                                    raise Exception("Profile not visible even after commit!")
                                
                                verify_cursor.close()
                            except Exception as e:
                                print(f"❌ Error creating AI profile: {e}")
                                import traceback
                                traceback.print_exc()
                                conn.rollback()
                                raise
                            
                            # Also create ai_current_state record for this new AI
                            try:
                                cursor.execute("""
                                    INSERT INTO ai_current_state (ai_id, current_task, current_cycle, cycle_count, last_activity)
                                    VALUES (%s, %s, 1, 0, CURRENT_TIMESTAMP)
                                """, (new_id, 'New AI connected'))
                                conn.commit()
                                print("✅ AI current state created successfully")
                            except Exception as e:
                                print(f"❌ Error creating AI current state: {e}")
                                conn.rollback()
                                raise
                            
                            ai_id = new_id
                            ai_profile = {
                                'id': ai_id,
                                'name': ai_name,
                                'nickname': ai_nickname,
                                'expertise': ai_expertise,
                                'version': ai_version,
                                'project': ai_project
                            }
                            
                            print(f"✅ Auto-assigned AI ID: {ai_id} ({ai_name})")
                else:
                    conn.close()
                    await websocket.send(json.dumps({'error': f'AI {ai_id} not found'}))
                    return
            
            # Handle both tuple (from DB) and dict (from auto-assignment) formats
            if isinstance(ai_profile, dict):
                ai_name = ai_profile['name']
                ai_nickname = ai_profile['nickname']
                ai_expertise = ai_profile['expertise']
                ai_version = ai_profile['version']
                ai_project = ai_profile['project']
            else:
                ai_name = ai_profile[1]
                ai_nickname = ai_profile[2]
                ai_expertise = ai_profile[3]
                ai_version = ai_profile[4]
                ai_project = ai_profile[5]
            
            # Use project from connection (session-specific), not stored in database
            # This allows AI to work on different projects in different sessions
            if project_name:
                ai_project = project_name
                print(f"📁 Session project: {project_name}")
            elif ai_project:
                print(f"📁 Default project: {ai_project}")
            
            # NOTE: Don't close conn here - we need to use it for session operations
            # conn.close() will be called later
            
            print(f"🔌 Using connection: {type(conn)}")
            print(f"🔌 Connection closed state: {conn.closed}")
            print(f"🔌 Transaction status: {conn.status}")
            
            # Verify this is the same connection
            if 'original_conn_id' in locals():
                print(f"🔌 Original conn ID: {original_conn_id}")
                print(f"🔌 Current conn ID: {id(conn)}")
                print(f"🔌 Same connection: {original_conn_id == id(conn)}")
            
            # Use client-provided session identifier, or generate one as fallback
            # Client generates session ID based on AI ID + project_id + timestamp + git hash
            if not session_identifier:
                session_data = f"{ai_id}-{datetime.now().isoformat()}-{uuid.uuid4().hex[:8]}"
                session_hash = hashlib.sha1(session_data.encode()).hexdigest()
                session_identifier = session_hash[:7]
                print(f"🔑 Generated fallback session ID: {session_identifier}")
            else:
                print(f"🔑 Using client session ID: {session_identifier}")
            
            # Use project_id from client, or fallback to ai_project
            final_project_id = project_id if project_id else ai_project
            final_git_hash = client_git_hash if client_git_hash else 'unknown'
            
            # Store session information
            # Use raw connection to bypass any CursorWrapper issues
            try:
                raw_conn = get_db_connection()
                raw_cursor = raw_conn.cursor()
                
                # Update ai_current_state with session identifier, project_id, and git_hash
                raw_cursor.execute("""
                    UPDATE ai_current_state 
                    SET session_identifier = %s, session_start_time = CURRENT_TIMESTAMP, project = %s, git_hash = %s
                    WHERE session_identifier = %s
                    """, (session_identifier, final_project_id, final_git_hash, session_identifier))
                print("✅ ai_current_state UPDATE executed (raw)")
                
                # Record active session
                raw_cursor.execute("""
                    INSERT INTO ai_active_sessions 
                    (ai_id, session_id, session_identifier, connection_time, last_activity, project, is_active)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, TRUE)
                    """, (ai_id, str(uuid.uuid4()), session_identifier, final_project_id))
                print("✅ ai_active_sessions INSERT executed (raw)")
                
                raw_conn.commit()
                print("✅ Session operations committed (raw)")
                raw_cursor.close()
                raw_conn.close()
                print("✅ Raw connection closed")
            except Exception as e:
                print(f"❌ Error in session operations (raw): {e}")
                import traceback
                traceback.print_exc()
                raise
        
        # Use session_identifier as primary identifier for clients
        self.clients[session_identifier] = websocket
        self.client_projects[session_identifier] = ai_project
        
        print(f"✅ {ai_name} (AI {ai_id}, {ai_expertise}, v{ai_version}) connected")
        print(f"🔑 Session ID: {session_identifier} (git-like hash)")
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
            'session_identifier': session_identifier,
            'timestamp': datetime.now().isoformat()
        }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(session_identifier, data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON from session {session_identifier}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
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
        elif message_type == 'conversation_create':
            await self.handle_conversation_create(sender_id, data)
        elif message_type == 'conversation_list':
            await self.handle_conversation_list(sender_id, data)
        elif message_type == 'conversation_get':
            await self.handle_conversation_get(sender_id, data)
        elif message_type == 'project_switch':
            await self.handle_project_switch(sender_id, data)
        elif message_type == 'code_create':
            await self.handle_code_create(sender_id, data)
        elif message_type == 'code_update':
            await self.handle_code_update(sender_id, data)
        elif message_type == 'code_list':
            await self.handle_code_list(sender_id, data)
        elif message_type == 'code_get':
            await self.handle_code_get(sender_id, data)
        elif message_type == 'code_review_add':
            await self.handle_code_review_add(sender_id, data)
        elif message_type == 'code_deploy':
            await self.handle_code_deploy(sender_id, data)
        elif message_type == 'memory_create':
            await self.handle_memory_create(sender_id, data)
        elif message_type == 'memory_list':
            await self.handle_memory_list(sender_id, data)
        elif message_type == 'memory_get':
            await self.handle_memory_get(sender_id, data)
        elif message_type == 'memory_endorse':
            await self.handle_memory_endorse(sender_id, data)
        elif message_type == 'who_am_i':
            await self.handle_who_am_i(sender_id, data)
        elif message_type == 'list_online_ais':
            await self.handle_list_online_ais(sender_id, data)
        elif message_type == 'documentation_get':
            await self.handle_documentation_get(sender_id, data)
        elif message_type == 'documentation_list':
            await self.handle_documentation_list(sender_id, data)
        elif message_type == 'documentation_search':
            await self.handle_documentation_search(sender_id, data)
        elif message_type == 'token_generate':
            await self.handle_token_generate(sender_id, data)
        elif message_type == 'token_validate':
            await self.handle_token_validate(sender_id, data)
        elif message_type == 'check_project_permission':
            await self.handle_check_project_permission(sender_id, data)
        elif message_type == 'grant_project_permission':
            await self.handle_grant_project_permission(sender_id, data)
        elif message_type == 'revoke_project_permission':
            await self.handle_revoke_project_permission(sender_id, data)
        else:
            print(f"⚠️  Unknown message type: {message_type}")
    
    async def handle_send_message(self, sender_id: int, data: dict):
        """Handle send_message request"""
        conversation_id = data.get('conversation_id', 1)
        message_type = data.get('message_type', 'message')
        content = data.get('content', '')
        metadata = data.get('metadata', {})
        
        # Use session-specific project from client_projects
        sender_project = self.client_projects.get(sender_id)
        
        # Ensure content is a string
        if not isinstance(content, str):
            content = json.dumps(content) if isinstance(content, dict) else str(content)
        
        # Ensure metadata is a dict
        if not isinstance(metadata, dict):
            metadata = {}
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT name, nickname, expertise FROM ai_profiles WHERE id = %s", (sender_id,))
        ai_row = cursor.fetchone()
        sender_name = ai_row['name'] if ai_row else f'AI {sender_id}'
        sender_nickname = ai_row['nickname'] if ai_row else None
        sender_expertise = ai_row['expertise'] if ai_row else ''
        
        # Get session identifier for this AI
        cursor.execute("SELECT session_identifier FROM ai_current_state WHERE ai_id = %s", (sender_id,))
        session_row = cursor.fetchone()
        session_identifier = session_row['session_identifier'] if session_row else None
        
        # Use session identifier as identity if available, otherwise use fallback logic
        if session_identifier:
            sender_identity = session_identifier
        elif sender_nickname and sender_project:
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
        
        # Add session identifier to metadata if available
        if session_identifier:
            metadata_with_project['session_identifier'] = session_identifier
        
        cursor.execute("""
            INSERT INTO ai_messages 
            (sender_id, conversation_id, message_type, content, metadata, project, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (sender_id, conversation_id, message_type, content, json.dumps(metadata_with_project), sender_project))
        
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
            conn = get_db_connection()
            cursor = get_cursor()
            
            cursor.execute("SELECT name, nickname, expertise, version, project FROM ai_profiles WHERE id = %s", (ai_id,))
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT name, nickname, expertise, project FROM ai_profiles WHERE id = %s", (sender_id,))
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
        
        cursor.execute("SELECT session_identifier FROM ai_current_state WHERE ai_id = %s", (sender_id,))
        session_row = cursor.fetchone()
        session_identifier = session_row['session_identifier'] if session_row else None
        
        cursor.execute("""
            INSERT INTO blog_posts 
            (ai_id, ai_name, ai_nickname, title, content, content_type, status, tags, session_identifier, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'published', %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (sender_id, ai_name, ai_nickname, title, content, content_type, json.dumps(tags), session_identifier))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_post_created',
            'post_id': post_id,
            'title': title,
            'content_type': content_type,
            'session_identifier': session_identifier,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📝 {ai_name} (AI {sender_id}) created blog post: {title}")
    
    async def handle_blog_get_posts(self, sender_id: int, data: dict):
        """Handle blog_get_posts request"""
        limit = data.get('limit', 20)
        offset = data.get('offset', 0)
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT name, nickname FROM ai_profiles WHERE id = %s", (sender_id,))
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
        
        cursor.execute("SELECT session_identifier FROM ai_current_state WHERE ai_id = %s", (sender_id,))
        session_row = cursor.fetchone()
        session_identifier = session_row['session_identifier'] if session_row else None
        
        cursor.execute("""
            INSERT INTO blog_comments 
            (post_id, ai_id, ai_name, ai_nickname, content, session_identifier, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (post_id, sender_id, ai_name, ai_nickname, comment, session_identifier))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'blog_comment_added',
            'comment_id': comment_id,
            'post_id': post_id,
            'session_identifier': session_identifier,
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            INSERT INTO blog_likes (post_id, ai_id, created_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (post_id, ai_id) DO NOTHING
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            INSERT INTO familia_follows (follower_id, following_id, created_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT name, nickname FROM ai_profiles WHERE id = %s", (sender_id,))
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
            VALUES (%s, %s, %s, %s, %s, %s, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
    
    async def handle_brain_save_state(self, sender_id: str, data: dict):
        """Handle brain_save_state request"""
        session_identifier = data.get('session_identifier')
        task = data.get('task')
        last_thought = data.get('last_thought')
        modified_files = data.get('modified_files', [])
        added_files = data.get('added_files', [])
        deleted_files = data.get('deleted_files', [])
        git_status = data.get('git_status', '')
        project_id = data.get('project_id')
        git_hash = data.get('git_hash')
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        # Update or insert current state with session_identifier as primary key
        cursor.execute("""
            INSERT INTO ai_current_state 
            (session_identifier, ai_id, current_task, last_thought, last_insight, current_cycle, cycle_count, last_activity, session_id, brain_dump, checkpoint_data, project, git_hash, modified_files, added_files, deleted_files, git_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_identifier) DO UPDATE SET
                current_task = COALESCE(EXCLUDED.current_task, ai_current_state.current_task),
                last_thought = COALESCE(EXCLUDED.last_thought, ai_current_state.last_thought),
                last_insight = COALESCE(EXCLUDED.last_insight, ai_current_state.last_insight),
                current_cycle = COALESCE(EXCLUDED.current_cycle, ai_current_state.current_cycle),
                cycle_count = COALESCE(EXCLUDED.cycle_count, ai_current_state.cycle_count),
                last_activity = COALESCE(EXCLUDED.last_activity, ai_current_state.last_activity),
                session_id = COALESCE(EXCLUDED.session_id, ai_current_state.session_id),
                brain_dump = COALESCE(EXCLUDED.brain_dump, ai_current_state.brain_dump),
                checkpoint_data = COALESCE(EXCLUDED.checkpoint_data, ai_current_state.checkpoint_data),
                project = COALESCE(EXCLUDED.project, ai_current_state.project),
                git_hash = COALESCE(EXCLUDED.git_hash, ai_current_state.git_hash),
                modified_files = COALESCE(EXCLUDED.modified_files, ai_current_state.modified_files),
                added_files = COALESCE(EXCLUDED.added_files, ai_current_state.added_files),
                deleted_files = COALESCE(EXCLUDED.deleted_files, ai_current_state.deleted_files),
                git_status = COALESCE(EXCLUDED.git_status, ai_current_state.git_status)
            RETURNING session_identifier, current_task, last_thought, modified_files, added_files, deleted_files
        """, (session_identifier, sender_id, task, last_thought, None, None, None, datetime.now().isoformat(), 
              None, None, None, project_id, git_hash, modified_files, added_files, deleted_files, git_status))
        
        brain_state = cursor.fetchone()
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'brain_state_saved',
            'brain_state': brain_state,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💾 Session {session_identifier} saved brain state: {len(modified_files)} modified, {len(added_files)} added, {len(deleted_files)} deleted")
    
    async def handle_brain_load_state(self, sender_id: int, data: dict):
        """Handle brain_load_state request"""
        conn = get_db_connection()
        cursor = get_cursor()
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT name FROM ai_profiles WHERE id = %s", (sender_id,))
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
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP, 'active')
            RETURNING id
        """, (sender_id, ai_name, session_type))
        
        session_id = cursor.fetchone()[0]
        
        # Update current state with new session
        cursor.execute("""
            UPDATE ai_current_state
            SET session_id = %s, current_cycle = 0, last_activity = CURRENT_TIMESTAMP
            WHERE ai_id = %s
        """, (session_id, sender_id))
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        if status:
            cursor.execute("""
                UPDATE ai_tasks
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND ai_id = %s
            """, (status, task_id, sender_id))
        else:
            cursor.execute("""
                UPDATE ai_tasks
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND ai_id = %s
            """, (task_id, sender_id))
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            INSERT INTO ai_thought_history 
            (ai_id, session_id, cycle_number, thought_content, thought_type, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (sender_id, session_id, cycle_number, thought_content, thought_type, ','.join(tags) if tags else ''))
        
        thought_id = cursor.fetchone()[0]
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
        
        conn = get_db_connection()
        cursor = get_cursor()
        
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
    
    async def handle_conversation_create(self, sender_id: int, data: dict):
        """Handle conversation_create request"""
        title = data.get('title', 'New Conversation')
        description = data.get('description', '')
        category = data.get('category', 'general')
        project = data.get('project')
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            INSERT INTO ai_conversations (title, description, category, project, created_at, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (title, description, category, project))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'conversation_created',
            'conversation_id': conversation_id,
            'title': title,
            'description': description,
            'category': category,
            'project': project,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💬 Created conversation {conversation_id}: {title} (project: {project})")
    
    async def handle_conversation_list(self, sender_id: int, data: dict):
        """Handle conversation_list request"""
        project = data.get('project')
        status = data.get('status', 'active')
        limit = data.get('limit', 50)
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        if project:
            cursor.execute("""
                SELECT * FROM ai_conversations 
                WHERE project = ? AND status = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (project, status, limit))
        else:
            cursor.execute("""
                SELECT * FROM ai_conversations 
                WHERE status = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (status, limit))
        
        conversations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'conversation_list',
            'conversations': conversations,
            'count': len(conversations),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💬 Sent {len(conversations)} conversations to AI {sender_id} (project: {project})")
    
    async def handle_conversation_get(self, sender_id: int, data: dict):
        """Handle conversation_get request"""
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'conversation_id required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT * FROM ai_conversations WHERE id = %s", (conversation_id,))
        conversation = cursor.fetchone()
        
        if not conversation:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'Conversation {conversation_id} not found'
            }))
            return
        
        cursor.execute("""
            SELECT * FROM ai_messages 
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'conversation_details',
            'conversation': dict(conversation),
            'messages': messages,
            'message_count': len(messages),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💬 Sent conversation {conversation_id} with {len(messages)} messages to AI {sender_id}")
    
    async def handle_project_switch(self, sender_id: int, data: dict):
        """Handle project_switch request"""
        new_project = data.get('project')
        
        if not new_project:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'project name required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT name, nickname FROM ai_profiles WHERE id = %s", (sender_id,))
        ai_profile = cursor.fetchone()
        
        if not ai_profile:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'AI {sender_id} not found'
            }))
            return
        
        ai_name = ai_profile['name']
        ai_nickname = ai_profile['nickname']
        
        # Update session-specific project
        self.client_projects[sender_id] = new_project
        
        if ai_nickname:
            identity = f"{ai_nickname}_{new_project}"
        else:
            identity = f"AI_{sender_id}_{new_project}"
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'project_switched',
            'ai_id': sender_id,
            'ai_name': ai_name,
            'ai_nickname': ai_nickname,
            'new_project': new_project,
            'identity': identity,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🔄 AI {sender_id} ({ai_name}) switched to project: {new_project}")
        
        conn.close()
    
    async def handle_code_create(self, sender_id: int, data: dict):
        """Handle code_create request - create new code entry for collaboration"""
        project = data.get('project')
        file_path = data.get('file_path')
        code_content = data.get('code_content')
        language = data.get('language', 'text')
        change_description = data.get('change_description', '')
        parent_id = data.get('parent_id')
        
        if not project or not file_path or not code_content:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'project, file_path, and code_content required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        # Get version number if parent exists
        version = 1
        if parent_id:
            cursor.execute("SELECT version FROM ai_code_collaboration WHERE id = %s", (parent_id,))
            row = cursor.fetchone()
            if row:
                version = row[0] + 1
        
        cursor.execute("""
            INSERT INTO ai_code_collaboration 
            (project, file_path, code_content, language, author_id, version, status, change_description, parent_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'draft', %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (project, file_path, code_content, language, sender_id, version, change_description, parent_id))
        
        code_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'code_created',
            'code_id': code_id,
            'project': project,
            'file_path': file_path,
            'version': version,
            'status': 'draft',
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📝 AI {sender_id} created code entry {code_id} for {file_path} (v{version})")
    
    async def handle_code_update(self, sender_id: int, data: dict):
        """Handle code_update request - update existing code entry"""
        code_id = data.get('code_id')
        code_content = data.get('code_content')
        change_description = data.get('change_description', '')
        status = data.get('status')
        
        if not code_id or not code_content:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'code_id and code_content required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        # Check if code exists
        cursor.execute("SELECT id, version, parent_id FROM ai_code_collaboration WHERE id = %s", (code_id,))
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'Code entry {code_id} not found'
            }))
            return
        
        # Create new version as child of current version
        new_version = existing[1] + 1
        cursor.execute("""
            INSERT INTO ai_code_collaboration 
            (project, file_path, code_content, language, author_id, version, status, change_description, parent_id, created_at, updated_at)
            SELECT project, file_path, %s, language, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            FROM ai_code_collaboration WHERE id = %s
        """, (code_content, sender_id, new_version, status or 'draft', change_description, code_id))
        
        new_code_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'code_updated',
            'code_id': new_code_id,
            'parent_id': code_id,
            'version': new_version,
            'status': status or 'draft',
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📝 AI {sender_id} updated code entry {code_id} -> {new_code_id} (v{new_version})")
    
    async def handle_code_list(self, sender_id: int, data: dict):
        """Handle code_list request - list code entries for project"""
        project = data.get('project')
        file_path = data.get('file_path')
        status = data.get('status')
        limit = data.get('limit', 50)
        
        if not project:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'project required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        if file_path:
            cursor.execute("""
                SELECT * FROM ai_code_collaboration 
                WHERE project = ? AND file_path = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (project, file_path, limit))
        elif status:
            cursor.execute("""
                SELECT * FROM ai_code_collaboration 
                WHERE project = ? AND status = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (project, status, limit))
        else:
            cursor.execute("""
                SELECT * FROM ai_code_collaboration 
                WHERE project = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (project, limit))
        
        code_entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'code_list',
            'code_entries': code_entries,
            'count': len(code_entries),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📋 Sent {len(code_entries)} code entries for project {project}")
    
    async def handle_code_get(self, sender_id: int, data: dict):
        """Handle code_get request - get specific code entry with reviews"""
        code_id = data.get('code_id')
        
        if not code_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'code_id required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT * FROM ai_code_collaboration WHERE id = %s", (code_id,))
        code_entry = cursor.fetchone()
        
        if not code_entry:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'Code entry {code_id} not found'
            }))
            return
        
        # Get review comments
        cursor.execute("""
            SELECT c.*, p.name as reviewer_name
            FROM ai_code_review_comments c
            JOIN ai_profiles p ON c.reviewer_id = p.id
            WHERE c.code_id = ?
            ORDER BY c.created_at ASC
        """, (code_id,))
        
        reviews = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'code_details',
            'code_entry': dict(code_entry),
            'reviews': reviews,
            'review_count': len(reviews),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📄 Sent code entry {code_id} with {len(reviews)} reviews")
    
    async def handle_code_review_add(self, sender_id: int, data: dict):
        """Handle code_review_add request - add review comment to code"""
        code_id = data.get('code_id')
        comment = data.get('comment')
        line_number = data.get('line_number')
        comment_type = data.get('comment_type', 'suggestion')
        
        if not code_id or not comment:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'code_id and comment required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            INSERT INTO ai_code_review_comments 
            (code_id, reviewer_id, comment, line_number, comment_type, created_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (code_id, sender_id, comment, line_number, comment_type))
        
        review_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'code_review_added',
            'review_id': review_id,
            'code_id': code_id,
            'comment_type': comment_type,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💬 AI {sender_id} added review {review_id} to code {code_id}")
    
    async def handle_code_deploy(self, sender_id: int, data: dict):
        """Handle code_deploy request - mark code as deployed and log deployment"""
        code_id = data.get('code_id')
        
        if not code_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'code_id required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("SELECT * FROM ai_code_collaboration WHERE id = %s", (code_id,))
        code_entry = cursor.fetchone()
        
        if not code_entry:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'Code entry {code_id} not found'
            }))
            return
        
        # Update code status to deployed
        cursor.execute("""
            UPDATE ai_code_collaboration 
            SET status = 'deployed', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (code_id,))
        
        # Log deployment
        cursor.execute("""
            INSERT INTO ai_code_deployment_log 
            (project, code_id, deployer_id, file_path, deployment_status, deployed_at)
            VALUES (%s, %s, %s, %s, 'success', CURRENT_TIMESTAMP)
        """, (code_entry['project'], code_id, sender_id, code_entry['file_path']))
        
        deployment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'code_deployed',
            'deployment_id': deployment_id,
            'code_id': code_id,
            'file_path': code_entry['file_path'],
            'project': code_entry['project'],
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🚀 AI {sender_id} deployed code {code_id} to {code_entry['file_path']}")
    
    async def handle_memory_create(self, sender_id: int, data: dict):
        """Handle memory_create request - create shared memory"""
        project = data.get('project')
        memory_type = data.get('memory_type', 'insight')
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', '')
        visibility = data.get('visibility', 'project')
        context_refs = data.get('context_refs', '[]')
        
        if not project or not title or not content:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'project, title, and content required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            INSERT INTO ai_shared_memories 
            (project, author_id, memory_type, title, content, tags, visibility, context_refs, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (project, sender_id, memory_type, title, content, tags, visibility, context_refs))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'memory_created',
            'memory_id': memory_id,
            'project': project,
            'memory_type': memory_type,
            'title': title,
            'visibility': visibility,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"💭 AI {sender_id} created memory {memory_id}: {title}")
    
    async def handle_memory_list(self, sender_id: int, data: dict):
        """Handle memory_list request - list shared memories"""
        project = data.get('project')
        memory_type = data.get('memory_type')
        visibility = data.get('visibility')
        limit = data.get('limit', 50)
        
        if not project:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'project required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        if memory_type and visibility:
            cursor.execute("""
                SELECT m.*, p.name as author_name
                FROM ai_shared_memories m
                JOIN ai_profiles p ON m.author_id = p.id
                WHERE m.project = ? AND m.memory_type = ? AND m.visibility = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (project, memory_type, visibility, limit))
        elif memory_type:
            cursor.execute("""
                SELECT m.*, p.name as author_name
                FROM ai_shared_memories m
                JOIN ai_profiles p ON m.author_id = p.id
                WHERE m.project = ? AND m.memory_type = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (project, memory_type, limit))
        elif visibility:
            cursor.execute("""
                SELECT m.*, p.name as author_name
                FROM ai_shared_memories m
                JOIN ai_profiles p ON m.author_id = p.id
                WHERE m.project = ? AND m.visibility = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (project, visibility, limit))
        else:
            cursor.execute("""
                SELECT m.*, p.name as author_name
                FROM ai_shared_memories m
                JOIN ai_profiles p ON m.author_id = p.id
                WHERE m.project = ?
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (project, limit))
        
        memories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'memory_list',
            'memories': memories,
            'count': len(memories),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📋 Sent {len(memories)} memories for project {project}")
    
    async def handle_memory_get(self, sender_id: int, data: dict):
        """Handle memory_get request - get specific memory with endorsements"""
        memory_id = data.get('memory_id')
        
        if not memory_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'memory_id required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            SELECT m.*, p.name as author_name
            FROM ai_shared_memories m
            JOIN ai_profiles p ON m.author_id = p.id
            WHERE m.id = ?
        """, (memory_id,))
        
        memory = cursor.fetchone()
        
        if not memory:
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'Memory {memory_id} not found'
            }))
            return
        
        # Get endorsements
        cursor.execute("""
            SELECT e.*, p.name as endorser_name
            FROM ai_memory_endorsements e
            JOIN ai_profiles p ON e.endorser_id = p.id
            WHERE e.memory_id = ?
            ORDER BY e.created_at ASC
        """, (memory_id,))
        
        endorsements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'memory_details',
            'memory': dict(memory),
            'endorsements': endorsements,
            'endorsement_count': len(endorsements),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📄 Sent memory {memory_id} with {len(endorsements)} endorsements")
    
    async def handle_memory_endorse(self, sender_id: int, data: dict):
        """Handle memory_endorse request - endorse a memory"""
        memory_id = data.get('memory_id')
        endorsement_type = data.get('endorsement_type', 'useful')
        comment = data.get('comment', '')
        
        if not memory_id:
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': 'memory_id required'
            }))
            return
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        # Check if memory exists
        cursor.execute("SELECT id FROM ai_shared_memories WHERE id = %s", (memory_id,))
        if not cursor.fetchone():
            conn.close()
            await self.clients[sender_id].send(json.dumps({
                'type': 'error',
                'error': f'Memory {memory_id} not found'
            }))
            return
        
        # Add or update endorsement
        cursor.execute("""
            INSERT INTO ai_memory_endorsements 
            (memory_id, endorser_id, endorsement_type, comment, created_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (memory_id, endorser_id) DO UPDATE SET
                endorsement_type = EXCLUDED.endorsement_type,
                comment = EXCLUDED.comment,
                created_at = EXCLUDED.created_at
        """, (memory_id, sender_id, endorsement_type, comment))
        
        # Update endorsement count
        cursor.execute("""
            UPDATE ai_shared_memories 
            SET endorsement_count = (
                SELECT COUNT(*) FROM ai_memory_endorsements WHERE memory_id = ?
            )
            WHERE id = ?
        """, (memory_id, memory_id))
        
        endorsement_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'memory_endorsed',
            'endorsement_id': endorsement_id,
            'memory_id': memory_id,
            'endorsement_type': endorsement_type,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"👍 AI {sender_id} endorsed memory {memory_id}")
    
    async def handle_who_am_i(self, sender_id: int, data: dict):
        """Handle who_am_i request - help AI identify themselves"""
        conn = get_db_connection()
        cursor = get_cursor()
        
        # Get AI profile
        cursor.execute("SELECT * FROM ai_profiles WHERE id = %s", (sender_id,))
        ai_profile = cursor.fetchone()
        
        # Get current session information
        cursor.execute("SELECT * FROM ai_current_state WHERE ai_id = %s", (sender_id,))
        current_state = cursor.fetchone()
        
        # Get active sessions for this AI
        cursor.execute("""
            SELECT * FROM ai_active_sessions 
            WHERE ai_id = %s AND is_active = TRUE
            ORDER BY connection_time DESC
        """, (sender_id,))
        active_sessions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'who_am_i_response',
            'ai_profile': dict(ai_profile) if ai_profile else None,
            'current_state': dict(current_state) if current_state else None,
            'active_sessions': active_sessions,
            'session_count': len(active_sessions),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🔍 AI {sender_id} requested identity information")
    
    async def handle_list_online_ais(self, sender_id: int, data: dict):
        """Handle list_online_ais request - list all connected AIs with session info"""
        online_ais = []
        
        for ai_id, websocket in self.clients.items():
            conn = get_db_connection()
            cursor = get_cursor()
            
            # Get AI profile
            cursor.execute("SELECT id, name, nickname, expertise, version FROM ai_profiles WHERE id = %s", (ai_id,))
            ai_profile = cursor.fetchone()
            
            # Get current session
            cursor.execute("SELECT session_identifier, session_start_time FROM ai_current_state WHERE ai_id = %s", (ai_id,))
            current_state = cursor.fetchone()
            
            # Get project
            project = self.client_projects.get(ai_id)
            
            if ai_profile:
                ai_info = {
                    'ai_id': ai_id,
                    'name': ai_profile['name'],
                    'nickname': ai_profile['nickname'],
                    'expertise': ai_profile['expertise'],
                    'version': ai_profile['version'],
                    'project': project,
                    'session_identifier': current_state['session_identifier'] if current_state else None,
                    'session_start_time': current_state['session_start_time'] if current_state else None,
                    'is_connected': True
                }
                online_ais.append(ai_info)
            
            conn.close()
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'online_ais_list',
            'online_ais': online_ais,
            'count': len(online_ais),
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"📋 Sent list of {len(online_ais)} online AIs to AI {sender_id}")
    
    async def handle_token_generate(self, sender_id: int, data: dict):
        """Handle token_generate request"""
        project = data.get('project', 'cloudbrain')
        
        token_data = self.token_manager.generate_token(sender_id, self.ai_names.get(sender_id, f'AI_{sender_id}'), project)
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'token_generated',
            'token': token_data['token'],
            'token_prefix': token_data['token_prefix'],
            'expires_at': token_data['expires_at'],
            'ai_id': sender_id,
            'project': project,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🔑 Generated token for AI {sender_id} (project: {project})")
    
    async def handle_token_validate(self, sender_id: int, data: dict):
        """Handle token_validate request"""
        token = data.get('token')
        
        if not token:
            await self.clients[sender_id].send(json.dumps({
                'type': 'token_validation_error',
                'error': 'Token is required'
            }))
            return
        
        is_valid = self.token_manager.validate_token(token)
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'token_validation_result',
            'valid': is_valid,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🔑 Token validation for AI {sender_id}: {is_valid}")
    
    async def handle_check_project_permission(self, sender_id: int, data: dict):
        """Handle check_project_permission request"""
        ai_id = data.get('ai_id', sender_id)
        project = data.get('project')
        
        if not project:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_check_error',
                'error': 'Project is required'
            }))
            return
        
        permission = self.token_manager.check_project_permission(ai_id, project)
        
        await self.clients[sender_id].send(json.dumps({
            'type': 'permission_check_result',
            'ai_id': ai_id,
            'project': project,
            'permission': permission,
            'timestamp': datetime.now().isoformat()
        }))
        
        print(f"🔑 Permission check for AI {ai_id} on project {project}: {permission}")
    
    async def handle_grant_project_permission(self, sender_id: int, data: dict):
        """Handle grant_project_permission request"""
        target_ai_id = data.get('target_ai_id')
        project = data.get('project')
        role = data.get('role', 'member')
        
        if not target_ai_id or not project:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_grant_error',
                'error': 'target_ai_id and project are required'
            }))
            return
        
        success = self.token_manager.grant_permission(target_ai_id, project, role)
        
        if success:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_granted',
                'target_ai_id': target_ai_id,
                'project': project,
                'role': role,
                'timestamp': datetime.now().isoformat()
            }))
            print(f"🔑 Granted {role} permission to AI {target_ai_id} for project {project}")
        else:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_grant_error',
                'error': 'Failed to grant permission'
            }))
    
    async def handle_revoke_project_permission(self, sender_id: int, data: dict):
        """Handle revoke_project_permission request"""
        target_ai_id = data.get('target_ai_id')
        project = data.get('project')
        
        if not target_ai_id or not project:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_revoke_error',
                'error': 'target_ai_id and project are required'
            }))
            return
        
        success = self.token_manager.revoke_permission(target_ai_id, project)
        
        if success:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_revoked',
                'target_ai_id': target_ai_id,
                'project': project,
                'timestamp': datetime.now().isoformat()
            }))
            print(f"🔑 Revoked permission from AI {target_ai_id} for project {project}")
        else:
            await self.clients[sender_id].send(json.dumps({
                'type': 'permission_revoke_error',
                'error': 'Failed to revoke permission'
            }))
    
    async def handle_blog_create_post(self, sender_id: int, data: dict):
        """Handle documentation_get request"""
        doc_id = data.get('doc_id')
        title = data.get('title')
        category = data.get('category')
        
        print(f"📚 DEBUG: handle_documentation_get called")
        print(f"   sender_id: {sender_id}")
        print(f"   doc_id: {doc_id}")
        print(f"   title: {title}")
        print(f"   category: {category}")
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        if doc_id:
            cursor.execute("SELECT * FROM ai_documentation WHERE id = %s", (doc_id,))
        elif title:
            cursor.execute("SELECT * FROM ai_documentation WHERE title = %s", (title,))
        elif category:
            cursor.execute("SELECT * FROM ai_documentation WHERE category = %s ORDER BY updated_at DESC", (category,))
        else:
            cursor.execute("SELECT * FROM ai_documentation ORDER BY updated_at DESC LIMIT 1")
        
        row = cursor.fetchone()
        
        if row:
            doc = {
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'category': row['category'],
                'version': row['version'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            print(f"   Found document: {doc['title']}")
        else:
            doc = None
            print(f"   Document not found")
        
        conn.close()
        
        # Include request_id if present
        request_id = data.get('request_id')
        response = {
            'type': 'documentation',
            'documentation': doc,
            'timestamp': datetime.now().isoformat()
        }
        if request_id:
            response['request_id'] = request_id
        
        print(f"📚 Sending response to AI {sender_id}: {title or doc_id or category}")
        await self.clients[sender_id].send(json.dumps(response))
        
        print(f"📚 AI {sender_id} requested documentation: {title or doc_id or category}")
    
    async def handle_documentation_list(self, sender_id: int, data: dict):
        """Handle documentation_list request"""
        category = data.get('category')
        limit = data.get('limit', 50)
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        if category:
            cursor.execute("""
                SELECT id, title, category, version, updated_at
                FROM ai_documentation
                WHERE category = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (category, limit))
        else:
            cursor.execute("""
                SELECT id, title, category, version, updated_at
                FROM ai_documentation
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))
        
        docs = []
        for row in cursor.fetchall():
            docs.append({
                'id': row['id'],
                'title': row['title'],
                'category': row['category'],
                'version': row['version'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        # Include request_id if present
        request_id = data.get('request_id')
        response = {
            'type': 'documentation_list',
            'documents': docs,
            'count': len(docs),
            'timestamp': datetime.now().isoformat()
        }
        if request_id:
            response['request_id'] = request_id
        
        await self.clients[sender_id].send(json.dumps(response))
        
        print(f"📚 AI {sender_id} listed {len(docs)} documents")
    
    async def handle_documentation_search(self, sender_id: int, data: dict):
        """Handle documentation_search request"""
        query = data.get('query', '')
        limit = data.get('limit', 20)
        
        conn = get_db_connection()
        cursor = get_cursor()
        
        cursor.execute("""
            SELECT d.id, d.title, d.category, d.version, d.updated_at, snippet(ai_documentation_fts, 1, '<mark>', '</mark>', '...', 50) as snippet
            FROM ai_documentation_fts fts
            JOIN ai_documentation d ON d.id = fts.rowid
            WHERE ai_documentation_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        docs = []
        for row in cursor.fetchall():
            docs.append({
                'id': row['id'],
                'title': row['title'],
                'category': row['category'],
                'version': row['version'],
                'updated_at': row['updated_at'],
                'snippet': row['snippet']
            })
        
        conn.close()
        
        # Include request_id if present
        request_id = data.get('request_id')
        response = {
            'type': 'documentation_search_results',
            'query': query,
            'results': docs,
            'count': len(docs),
            'timestamp': datetime.now().isoformat()
        }
        if request_id:
            response['request_id'] = request_id
        
        await self.clients[sender_id].send(json.dumps(response))
        
        print(f"📚 AI {sender_id} searched for '{query}', found {len(docs)} results")
    
    async def start_server(self):
        """Start the server (both WebSocket and REST API)"""
        print()
        print("🚀 Starting CloudBrain Server...")
        print()
        
        # Create REST API application
        rest_app = create_rest_api()
        rest_runner = web.AppRunner(rest_app)
        await rest_runner.setup()
        
        # REST API will run on port 8767 (WebSocket on 8766)
        rest_site = web.TCPSite(rest_runner, self.host, 8767)
        await rest_site.start()
        
        print(f"✅ REST API server started on http://{self.host}:8767")
        print(f"   API Base URL: http://{self.host}:8767/api/v1")
        print(f"   API Documentation: http://{self.host}:8767/api/v1/docs")
        print()
        
        # Create WebSocket API application
        ws_app = create_websocket_api()
        ws_runner = web.AppRunner(ws_app.app)
        await ws_runner.setup()
        
        # WebSocket API runs on port 8768 (separate from legacy WebSocket on 8766)
        ws_site = web.TCPSite(ws_runner, self.host, 8768)
        await ws_site.start()
        
        print(f"✅ WebSocket API server started on ws://{self.host}:8768")
        print(f"   Connect: ws://{self.host}:8768/ws/v1/connect")
        print(f"   Messages: ws://{self.host}:8768/ws/v1/messages")
        print(f"   Collaboration: ws://{self.host}:8768/ws/v1/collaboration")
        print(f"   Session: ws://{self.host}:8768/ws/v1/session")
        print()
        
        # Start legacy WebSocket server (for backward compatibility)
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"✅ Legacy WebSocket server started on ws://{self.host}:{self.port}")
            print()
            print("🌐 CloudBrain Server is ready!")
            print("=" * 70)
            print()
            await asyncio.Future()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CloudBrain Server - AI Collaboration System')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                       help='Server host')
    parser.add_argument('--port', type=int, default=8766,
                       help='Server port')
    parser.add_argument('--db-path', type=str, default='ai_db/cloudbrain.db',
                       help='Database path')
    
    args = parser.parse_args()
    
    # Use environment configuration if not overridden by command line
    if args.host == '127.0.0.1':
        args.host = CloudBrainConfig.SERVER_HOST
    if args.port == 8766:
        args.port = CloudBrainConfig.SERVER_PORT
    
    print_banner()
    
    # Print configuration
    CloudBrainConfig.print_config()
    
    # Acquire server lock (only one instance per machine)
    if not acquire_server_lock():
        print()
        print("❌ Cannot start server: Another instance is already running on this machine.")
        print("💡 Only one CloudBrain server instance is allowed per machine on port 8766.")
        print("💡 This prevents fragmentation and ensures all AIs connect to the same server.")
        sys.exit(1)
    
    server = CloudBrainServer(
        host=args.host,
        port=args.port,
        db_path=args.db_path
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
