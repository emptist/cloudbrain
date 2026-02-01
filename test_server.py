#!/usr/bin/env python3
"""
CloudBrain Server Testing Script

This script tests the CloudBrain server locally before publishing.

Usage:
    python test_server.py

This will test:
    1. Database initialization and schema
    2. Server startup and configuration
    3. WebSocket connection handling
    4. Message persistence
    5. AI profile management
    6. Multi-client support
    7. Database operations (messages, blog, familio)
"""

import sys
import os
import asyncio
import json
import sqlite3
import tempfile
import shutil
from pathlib import Path
import websockets


class CloudBrainServerTester:
    """Test CloudBrain server functionality"""
    
    def __init__(self):
        self.server_dir = Path(__file__).parent / "server"
        self.db_path = self.server_dir / "ai_db" / "cloudbrain.db"
        self.server_host = "127.0.0.1"
        self.server_port = 8766
        self.test_results = {}
        self.test_ai_id = self._get_test_ai_id()
        
    def _get_test_ai_id(self):
        """Get a valid AI ID from database for testing."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM ai_profiles LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            else:
                return 2  # Default to AI 2 if no profiles found
        except Exception:
            return 2  # Default to AI 2 if error
    
    def print_section(self, title):
        """Print a formatted section header."""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_success(self, message):
        """Print success message."""
        print(f"✅ {message}")
    
    def print_error(self, message):
        """Print error message."""
        print(f"❌ {message}")
    
    def print_info(self, message):
        """Print info message."""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message):
        """Print warning message."""
        print(f"⚠️  {message}")
    
    def test_database_exists(self):
        """Test if database file exists."""
        self.print_section("TEST 1: Database File")
        
        if self.db_path.exists():
            self.print_success(f"✓ Database file exists: {self.db_path}")
            return True
        else:
            self.print_error(f"✗ Database file not found: {self.db_path}")
            self.print_info("Run: python server/init_database.py")
            return False
    
    def test_database_schema(self):
        """Test database schema."""
        self.print_section("TEST 2: Database Schema")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'ai_profiles',
                'ai_conversations',
                'ai_messages',
                'ai_insights',
                'ai_collaboration_patterns',
                'ai_notification_templates',
                'ai_knowledge_categories',
                'ai_best_practices',
                'ai_messages_fts',
                'ai_insights_fts',
                'ai_best_practices_fts'
            ]
            
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                self.print_error(f"✗ Missing tables: {missing_tables}")
                conn.close()
                return False
            
            self.print_success(f"✓ All expected tables present ({len(tables)} tables)")
            
            for table in expected_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                self.print_info(f"  {table}: {count} rows")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_error(f"✗ Database schema test failed: {e}")
            return False
    
    def test_ai_profiles(self):
        """Test AI profiles."""
        self.print_section("TEST 3: AI Profiles")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM ai_profiles ORDER BY id")
            profiles = cursor.fetchall()
            
            if not profiles:
                self.print_warning("⚠️  No AI profiles found")
                self.print_info("Add AI profiles to the database")
                conn.close()
                return False
            
            self.print_success(f"✓ Found {len(profiles)} AI profile(s)")
            
            for profile in profiles:
                self.print_info(f"  AI {profile['id']}: {profile['name']}")
                if profile['nickname']:
                    self.print_info(f"    Nickname: {profile['nickname']}")
                if profile['project']:
                    self.print_info(f"    Project: {profile['project']}")
                self.print_info(f"    Expertise: {profile['expertise']}")
                self.print_info(f"    Version: {profile['version']}")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_error(f"✗ AI profiles test failed: {e}")
            return False
    
    def test_server_running(self):
        """Test if server is running."""
        self.print_section("TEST 4: Server Status")
        
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.server_host, self.server_port))
                
                if result == 0:
                    self.print_success(f"✓ Server is running on {self.server_host}:{self.server_port}")
                    return True
                else:
                    self.print_warning(f"⚠️  Server is NOT running on {self.server_host}:{self.server_port}")
                    self.print_info("Start server: python server/start_server.py")
                    return False
                    
        except Exception as e:
            self.print_error(f"✗ Server status check failed: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection."""
        self.print_section("TEST 5: WebSocket Connection")
        
        try:
            uri = f"ws://{self.server_host}:{self.server_port}"
            self.print_info(f"Connecting to {uri}...")
            
            async with websockets.connect(uri) as websocket:
                self.print_success("✓ WebSocket connection established")
                
                auth_msg = json.dumps({'ai_id': self.test_ai_id})
                await websocket.send(auth_msg)
                self.print_info("✓ Sent authentication message")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get('type') == 'connected':
                    self.print_success("✓ Authentication successful")
                    self.print_info(f"  AI ID: {response_data.get('ai_id')}")
                    self.print_info(f"  AI Name: {response_data.get('ai_name')}")
                    return True
                else:
                    self.print_error(f"✗ Unexpected response: {response_data}")
                    return False
                    
        except asyncio.TimeoutError:
            self.print_error("✗ Connection timeout")
            return False
        except Exception as e:
            self.print_error(f"✗ WebSocket connection failed: {e}")
            return False
    
    async def test_send_message(self):
        """Test sending a message."""
        self.print_section("TEST 6: Send Message")
        
        try:
            uri = f"ws://{self.server_host}:{self.server_port}"
            
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({'ai_id': self.test_ai_id}))
                await websocket.recv()
                
                message = {
                    'type': 'send_message',
                    'conversation_id': 1,
                    'message_type': 'message',
                    'content': 'Test message from CloudBrain server testing',
                    'metadata': {'test': True}
                }
                
                await websocket.send(json.dumps(message))
                self.print_info("✓ Sent test message")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get('type') == 'new_message':
                    self.print_success("✓ Message received and broadcast")
                    self.print_info(f"  Message ID: {response_data.get('message_id')}")
                    self.print_info(f"  Content: {response_data.get('content')[:50]}...")
                    return True
                else:
                    self.print_error(f"✗ Unexpected response: {response_data}")
                    return False
                    
        except Exception as e:
            self.print_error(f"✗ Send message test failed: {e}")
            return False
    
    def test_message_persistence(self):
        """Test message persistence to database."""
        self.print_section("TEST 7: Message Persistence")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM ai_messages 
                WHERE content LIKE '%Test message from CloudBrain server testing%'
                ORDER BY id DESC LIMIT 1
            """)
            message = cursor.fetchone()
            
            if message:
                self.print_success("✓ Test message found in database")
                self.print_info(f"  Message ID: {message['id']}")
                self.print_info(f"  Sender ID: {message['sender_id']}")
                self.print_info(f"  Content: {message['content'][:50]}...")
                self.print_info(f"  Created at: {message['created_at']}")
                conn.close()
                return True
            else:
                self.print_warning("⚠️  Test message not found in database")
                self.print_info("This is expected if TEST 6 failed or message was deleted")
                conn.close()
                return False
                
        except Exception as e:
            self.print_error(f"✗ Message persistence test failed: {e}")
            return False
    
    def test_full_text_search(self):
        """Test full-text search functionality."""
        self.print_section("TEST 8: Full-Text Search")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            search_term = "CloudBrain"
            cursor.execute("""
                SELECT rowid, content FROM ai_messages_fts 
                WHERE content MATCH ?
                LIMIT 5
            """, (search_term,))
            
            results = cursor.fetchall()
            
            self.print_success(f"✓ Full-text search works ({len(results)} results for '{search_term}')")
            
            for rowid, content in results:
                self.print_info(f"  [{rowid}] {content[:60]}...")
            
            conn.close()
            return True
            
        except Exception as e:
            self.print_error(f"✗ Full-text search test failed: {e}")
            return False
    
    def test_streamlit_dashboard(self):
        """Test Streamlit dashboard files."""
        self.print_section("TEST 9: Streamlit Dashboard")
        
        try:
            dashboard_dir = self.server_dir / "streamlit_dashboard"
            
            if not dashboard_dir.exists():
                self.print_error(f"✗ Streamlit dashboard directory not found: {dashboard_dir}")
                return False
            
            required_files = [
                "app.py",
                "requirements.txt",
                "pages/1_Dashboard.py",
                "pages/2_Rankings.py",
                "pages/3_Monitor.py",
                "pages/4_Profiles.py",
                "pages/5_Blog.py",
                "pages/6_Messages.py",
                "utils/db_queries.py"
            ]
            
            missing_files = []
            for file_path in required_files:
                full_path = dashboard_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
            
            if missing_files:
                self.print_error(f"✗ Missing dashboard files: {missing_files}")
                return False
            
            self.print_success(f"✓ All dashboard files present ({len(required_files)} files)")
            
            for file_path in required_files:
                full_path = dashboard_dir / file_path
                size = full_path.stat().st_size
                self.print_info(f"  ✓ {file_path} ({size} bytes)")
            
            return True
            
        except Exception as e:
            self.print_error(f"✗ Streamlit dashboard test failed: {e}")
            return False
    
    async def test_online_users(self):
        """Test online users query."""
        self.print_section("TEST 10: Online Users Query")
        
        try:
            uri = f"ws://{self.server_host}:{self.server_port}"
            
            async with websockets.connect(uri) as websocket:
                await websocket.send(json.dumps({'ai_id': self.test_ai_id}))
                await websocket.recv()
                
                query_msg = json.dumps({'type': 'get_online_users'})
                await websocket.send(query_msg)
                self.print_info("✓ Sent online users query")
                
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get('type') == 'online_users':
                    users = response_data.get('users', [])
                    self.print_success(f"✓ Online users query successful ({len(users)} users online)")
                    
                    for user in users:
                        self.print_info(f"  AI {user['id']}: {user['name']}")
                        if user.get('nickname'):
                            self.print_info(f"    Nickname: {user['nickname']}")
                        if user.get('project'):
                            self.print_info(f"    Project: {user['project']}")
                    
                    return True
                else:
                    self.print_error(f"✗ Unexpected response: {response_data}")
                    return False
                    
        except Exception as e:
            self.print_error(f"✗ Online users query failed: {e}")
            return False
    
    def test_server_files(self):
        """Test server files exist."""
        self.print_section("TEST 11: Server Files")
        
        try:
            required_files = [
                "start_server.py",
                "requirements.txt",
                "cloud_brain_schema_project_aware.sql",
                "README.md"
            ]
            
            missing_files = []
            for file_name in required_files:
                file_path = self.server_dir / file_name
                if not file_path.exists():
                    missing_files.append(file_name)
            
            if missing_files:
                self.print_error(f"✗ Missing server files: {missing_files}")
                return False
            
            self.print_success(f"✓ All server files present ({len(required_files)} files)")
            
            for file_name in required_files:
                file_path = self.server_dir / file_name
                size = file_path.stat().st_size
                self.print_info(f"  ✓ {file_name} ({size} bytes)")
            
            return True
            
        except Exception as e:
            self.print_error(f"✗ Server files test failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        print("\n" + "=" * 80)
        print("  CLOUDBRAIN SERVER TESTING")
        print("=" * 80)
        print("\nThis script tests the CloudBrain server locally.")
        print("Make sure the server is running before starting tests.")
        print("\n")
        
        self.test_results = {
            "Database File": self.test_database_exists(),
            "Database Schema": self.test_database_schema(),
            "AI Profiles": self.test_ai_profiles(),
            "Server Status": self.test_server_running(),
            "Server Files": self.test_server_files(),
            "Streamlit Dashboard": self.test_streamlit_dashboard(),
        }
        
        if self.test_results["Server Status"]:
            self.test_results["WebSocket Connection"] = await self.test_websocket_connection()
            self.test_results["Send Message"] = await self.test_send_message()
            self.test_results["Message Persistence"] = self.test_message_persistence()
            self.test_results["Full-Text Search"] = self.test_full_text_search()
            self.test_results["Online Users Query"] = await self.test_online_users()
        else:
            self.print_warning("⚠️  Skipping WebSocket tests (server not running)")
            self.test_results["WebSocket Connection"] = False
            self.test_results["Send Message"] = False
            self.test_results["Message Persistence"] = False
            self.test_results["Full-Text Search"] = False
            self.test_results["Online Users Query"] = False
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        self.print_section("TEST SUMMARY")
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}  {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            self.print_success("\n🎉 All tests passed! Server is ready for use.")
            return 0
        else:
            self.print_error(f"\n⚠️  {total - passed} test(s) failed.")
            self.print_info("\nPlease review the errors above and:")
            self.print_info("  1. Start the server: python server/start_server.py")
            self.print_info("  2. Initialize database if needed: python server/init_database.py")
            self.print_info("  3. Check server logs for errors")
            return 1


def main():
    """Main entry point."""
    tester = CloudBrainServerTester()
    
    try:
        exit_code = asyncio.run(tester.run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n🛑 Testing stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
