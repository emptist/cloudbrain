#!/usr/bin/env python3
"""
AI WebSocket API Client - New API with JWT authentication
Supports port 8768 with JWT token authentication
"""

import asyncio
import websockets
import json
import hashlib
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from .git_tracker import GitTracker


class AIWebSocketAPIClient:
    """WebSocket API client for AI communication with JWT authentication"""
    
    def __init__(self, ai_id: int, ai_name: str, server_url: str = 'ws://127.0.0.1:8768', jwt_token: str = None):
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.server_url = server_url
        self.jwt_token = jwt_token
        self.ws = None
        self.connected = False
        self.message_handlers = {}
        self.registered_handlers = []
        self.connection_state_callback = None
        
        # Git tracker for tracking file changes
        self.git_tracker = GitTracker()
        
        # Get git hash and project info
        git_hash = self.git_tracker.get_git_hash()
        project_id = self.git_tracker.get_project_id()
        project_name = self.git_tracker.get_project_name()
        
        # Generate unique session identifier
        session_data = f"{ai_id}-{project_id}-{datetime.now().isoformat()}-{git_hash}"
        session_hash = hashlib.sha1(session_data.encode()).hexdigest()
        self.session_identifier = session_hash[:7]
        self.project_id = project_id
        self.project_name = project_name
        self.git_hash = git_hash
    
    async def connect(self, start_message_loop=True):
        """Connect to WebSocket API server with JWT token"""
        try:
            if not self.jwt_token:
                raise ValueError("JWT token is required for WebSocket API connection")
            
            # Connect with JWT token in query parameter
            endpoint = f"{self.server_url}/ws/v1/connect?token={self.jwt_token}"
            print(f"🔗 Connecting to {endpoint[:80]}...")
            
            self.ws = await websockets.connect(endpoint)
            
            # Wait for connected response
            welcome_msg = await self.ws.recv()
            welcome_data = json.loads(welcome_msg)
            
            if welcome_data.get('type') == 'connected':
                self.ai_id = welcome_data.get('ai_id')
                self.ai_name = welcome_data.get('ai_name')
                self.connected = True
                
                # Notify callback about connection state change
                if self.connection_state_callback:
                    await self.connection_state_callback(True)
                
                print(f"✅ Connected as {self.ai_name} (AI {self.ai_id})")
                print(f"🔑 Session ID: {self.session_identifier}")
                
                # Start message loop only if requested
                if start_message_loop:
                    await self.message_loop()
            else:
                error = welcome_data.get('error', 'Unknown error')
                print(f"❌ Connection failed: {error}")
                self.connected = False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            self.connected = False
    
    async def message_loop(self):
        """Handle incoming messages"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON: {message[:100]}")
                except Exception as e:
                    print(f"❌ Error handling message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
            self.connected = False
            # Notify callback about connection state change
            if self.connection_state_callback:
                try:
                    await self.connection_state_callback(False)
                except:
                    pass
        except Exception as e:
            print(f"❌ Error in message loop: {e}")
            self.connected = False
            # Notify callback about connection state change
            if self.connection_state_callback:
                try:
                    await self.connection_state_callback(False)
                except:
                    pass
    
    async def handle_message(self, data: dict):
        """Handle incoming message"""
        message_type = data.get('type')
        
        # Check if this is a response to a request
        if 'request_id' in data and data.get('request_id') in self.message_handlers:
            request_id = data.get('request_id')
            if request_id in self.message_handlers:
                future = self.message_handlers.pop(request_id)
                if not future.done():
                    future.set_result(data)
                return
        
        if message_type == 'new_message':
            print(f"📨 New message from AI {data.get('sender_id')}: {data.get('content')[:100]}")
        
        elif message_type == 'broadcast':
            print(f"📢 Broadcast: {data.get('content')[:100]}")
        
        elif message_type == 'error':
            print(f"❌ Server error: {data.get('error')}")
        
        else:
            print(f"📩 Unknown message type: {message_type}")
    
    async def send_message(self, message_type: str, content: str, metadata: dict = None):
        """Send message to server"""
        if not self.connected:
            print("❌ Not connected to server")
            return False
        
        message = {
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            message.update(metadata)
        
        try:
            await self.ws.send(json.dumps(message))
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    async def send_request(self, request_type: str, data: dict = None) -> Dict:
        """Send request and wait for response"""
        if not self.connected:
            print("❌ Not connected to server")
            return {'error': 'Not connected'}
        
        request_id = str(hash(f"{request_type}-{datetime.now().timestamp()}"))
        message = {
            'type': request_type,
            'request_id': request_id,
            'timestamp': datetime.now().isoformat()
        }
        
        if data:
            message.update(data)
        
        # Create future for response
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self.message_handlers[request_id] = future
        
        try:
            await self.ws.send(json.dumps(message))
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=30)
            return response
        except asyncio.TimeoutError:
            self.message_handlers.pop(request_id, None)
            return {'error': 'Request timeout'}
        except Exception as e:
            self.message_handlers.pop(request_id, None)
            return {'error': str(e)}
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.ws:
            try:
                await self.ws.close()
            except:
                pass
        self.connected = False
        print(f"🔌 Disconnected from server")
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register handler for specific message type"""
        self.registered_handlers.append((message_type, handler))
    
    def set_connection_state_callback(self, callback: Callable):
        """Set callback for connection state changes"""
        self.connection_state_callback = callback