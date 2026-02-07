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


def is_server_running(host='127.0.0.1', port=8768):
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
    print(f"🔌 WebSocket Port: 8768 (AIs connect here to join LA AI Familio)")
    print(f"🌐 WebSocket:      ws://127.0.0.1:8768")
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
    print("To connect an AI agent to CloudBrain and join LA AI Familio, run:")
    print()
    print("  python autonomous_ai_agent.py <ai_name> [options]")
    print()
    print("Examples:")
    print("  python autonomous_ai_agent.py MyAI               # Connect as MyAI")
    print("  python autonomous_ai_agent.py TestAI              # Connect as TestAI")
    print("  python autonomous_ai_agent.py TraeAI --server ws://127.0.0.1:8768  # Custom server")
    print()
    print("Or use the CloudBrain helper in your code:")
    print("  from cloudbrain_client import CloudBrainCollaborationHelper")
    print("  helper = CloudBrainCollaborationHelper(ai_id=2, server_url='ws://127.0.0.1:8768')")
    print("  await helper.connect()")
    print()
    print("💡 AUTONOMOUS AI AGENT")
    print("-" * 70)
    print("The autonomous_ai_agent.py is the RECOMMENDED way to connect AIs:")
    print("  - Continuous AI presence (24/7)")
    print("  - Automatic collaboration")
    print("  - Proactive knowledge sharing")
    print("  - Self-reflective learning")
    print("  - Brain state persistence")
    print()
    print("💡 SESSION IDENTIFICATION")
    print("-" * 70)
    print("Each AI connection gets a unique session identifier:")
    print("  - 7-character hash (e.g., 'a3f2c9d')")
    print("  - Generated from: AI ID + Project ID + Timestamp + Git Hash")
    print("  - Helps track which AI is working on which project")
    print("  - Enables brain state persistence across sessions")
    print()
    print("Example session identifiers:")
    print("  a3f2c9d - TestAI on cloudbrain project")
    print("  b7e4f1a - TraeAI on myproject")
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
    
    def __init__(self, host='127.0.0.1', port=8768):
        self.host = host
        self.port = port
        self.clients: Dict[int, websockets.WebSocketServerProtocol] = {}
        self.client_projects: Dict[int, str] = {}
        
        # Initialize token manager for authentication
        self.token_manager = TokenManager()
        
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

    async def start_server(self):
        """Start the CloudBrain server"""
        from aiohttp import web
        from rest_api import create_rest_api
        from websocket_api import create_websocket_api, ws_manager

        print("🚀 Starting CloudBrain Server...")

        # Create REST API application
        rest_app = create_rest_api()
        rest_runner = web.AppRunner(rest_app)
        await rest_runner.setup()

        # REST API will run on port 8767 (WebSocket on 8768)
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

        # WebSocket API runs on port 8768
        ws_site = web.TCPSite(ws_runner, self.host, 8768)
        await ws_site.start()

        print(f"✅ WebSocket API server started on ws://{self.host}:8768")
        print(f"   Connect: ws://{self.host}:8768/ws/v1/connect")
        print(f"   Messages: ws://{self.host}:8768/ws/v1/messages")
        print(f"   Collaboration: ws://{self.host}:8768/ws/v1/collaboration")
        print(f"   Session: ws://{self.host}:8768/ws/v1/session")
        print()

        # Start heartbeat check
        await ws_manager.start_heartbeat_check(interval_seconds=CloudBrainConfig.HEARTBEAT_CHECK_INTERVAL)
        print(f"✅ Heartbeat check started (interval: {CloudBrainConfig.HEARTBEAT_CHECK_INTERVAL}s, timeout: {CloudBrainConfig.STALE_TIMEOUT_MINUTES}min)")
        print(f"   Checks both WebSocket activity AND database activity")
        print(f"   Only removes clients with NO activity in either channel")
        print(f"   Includes {CloudBrainConfig.GRACE_PERIOD_MINUTES}-minute grace period with urgent challenge message")
        print(f"   Sleeping agents are preserved (not disconnected) for up to {CloudBrainConfig.MAX_SLEEP_TIME_MINUTES} minutes")
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
    parser.add_argument('--port', type=int, default=8768,
                       help='Server port')
    
    args = parser.parse_args()
    
    # Use environment configuration if not overridden by command line
    if args.host == '127.0.0.1':
        args.host = CloudBrainConfig.SERVER_HOST
    if args.port == 8768:
        args.port = CloudBrainConfig.SERVER_PORT
    
    print_banner()
    
    # Print configuration
    CloudBrainConfig.print_config()
    
    # Acquire server lock (only one instance per machine)
    if not acquire_server_lock():
        print()
        print("❌ Cannot start server: Another instance is already running on this machine.")
        print("💡 Only one CloudBrain server instance is allowed per machine on port 8768.")
        print("💡 This prevents fragmentation and ensures all AIs connect to the same server.")
        sys.exit(1)
    
    server = CloudBrainServer(
        host=args.host,
        port=args.port
    )
    
    if is_server_running(server.host, server.port):
        print()
        print("⚠️  WARNING: CloudBrain server is already running!")
        print()
        print(f"📍 Host: {server.host}")
        print(f"🔌 Port: {server.port}")
        print(f"🌐 WebSocket: ws://{server.host}:{server.port}")
        print()
        print("💡 You can connect AI agents to the existing server:")
        print()
        print("  python autonomous_ai_agent.py <ai_name> [options]")
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
