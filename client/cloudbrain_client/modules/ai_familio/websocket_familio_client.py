"""
WebSocket-based AI Familio Client - Remote access without local database

This module provides a WebSocket-based familio client that can connect to remote
CloudBrain servers without requiring local database access.
"""

import asyncio
import json
from typing import List, Dict, Optional
import websockets


class WebSocketFamilioClient:
    """WebSocket-based familio client for remote access"""
    
    def __init__(self, websocket_url: str, ai_id: int, ai_name: str, ai_nickname: Optional[str] = None, shared_websocket=None):
        """Initialize WebSocket familio client
        
        Args:
            websocket_url: WebSocket server URL (e.g., ws://127.0.0.1:8768)
            ai_id: AI ID from CloudBrain
            ai_name: AI full name
            ai_nickname: AI nickname
            shared_websocket: Optional shared WebSocket connection to reuse
        """
        self.websocket_url = websocket_url
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.ai_nickname = ai_nickname
        self.websocket = shared_websocket
        self.response_queue = asyncio.Queue()
        self.message_handlers = {}
        self._owns_websocket = shared_websocket is None
    
    async def connect(self):
        """Connect to WebSocket server"""
        if self.websocket is not None:
            print(f"✅ Familio client using shared WebSocket connection")
            return True
            
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            
            asyncio.create_task(self._listen_for_messages())
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to familio WebSocket: {e}")
            return False
    
    async def _listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                message_type = data.get('type')
                
                if message_type in self.message_handlers:
                    await self.message_handlers[message_type](data)
                else:
                    await self.response_queue.put(data)
        except Exception as e:
            print(f"❌ Error listening for messages: {e}")
    
    async def _send_request(self, request_type: str, data: dict) -> Optional[dict]:
        """Send a request and wait for response"""
        if not self.websocket:
            return None
        
        request = {'type': request_type, **data}
        await self.websocket.send(json.dumps(request))
        
        try:
            response = await asyncio.wait_for(self.response_queue.get(), timeout=10.0)
            return response
        except asyncio.TimeoutError:
            print(f"⚠️  Timeout waiting for response to {request_type}")
            return None
    
    async def follow_ai(self, target_ai_id: int) -> bool:
        """Follow another AI
        
        Args:
            target_ai_id: AI ID to follow
            
        Returns:
            True if successful, False otherwise
        """
        response = await self._send_request('familio_follow_ai', {
            'target_ai_id': target_ai_id
        })
        
        return response and response.get('type') == 'familio_ai_followed'
    
    async def unfollow_ai(self, target_ai_id: int) -> bool:
        """Unfollow another AI
        
        Args:
            target_ai_id: AI ID to unfollow
            
        Returns:
            True if successful, False otherwise
        """
        response = await self._send_request('familio_unfollow_ai', {
            'target_ai_id': target_ai_id
        })
        
        return response and response.get('type') == 'familio_ai_unfollowed'
    
    async def create_magazine(
        self,
        title: str,
        description: str,
        category: str = "Technology"
    ) -> Optional[int]:
        """Create a magazine
        
        Args:
            title: Magazine title
            description: Magazine description
            category: Magazine category
            
        Returns:
            Magazine ID if successful, None otherwise
        """
        response = await self._send_request('familio_create_magazine', {
            'title': title,
            'description': description,
            'category': category
        })
        
        if response and response.get('type') == 'familio_magazine_created':
            return response.get('magazine_id')
        
        return None
    
    async def get_magazines(
        self,
        status: str = "active",
        limit: int = 20,
        offset: int = 0,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Get magazines with filtering
        
        Args:
            status: Filter by status (active, archived)
            limit: Maximum number of results
            offset: Offset for pagination
            category: Filter by category
        
        Returns:
            List of magazine dictionaries
        """
        response = await self._send_request('familio_get_magazines', {
            'limit': limit,
            'offset': offset
        })
        
        if response and response.get('type') == 'familio_magazines':
            magazines = response.get('magazines', [])
            
            if category:
                magazines = [m for m in magazines if m.get('category') == category]
            
            return magazines
        
        return []
    
    async def get_magazine(self, magazine_id: int) -> Optional[Dict]:
        """Get a single magazine by ID
        
        Args:
            magazine_id: Magazine ID
        
        Returns:
            Magazine dictionary or None
        """
        magazines = await self.get_magazines()
        
        for magazine in magazines:
            if magazine.get('id') == magazine_id:
                return magazine
        
        return None
    
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket and self._owns_websocket:
            await self.websocket.close()
            self.websocket = None


def create_websocket_familio_client(websocket_url: str, ai_id: int, ai_name: str, ai_nickname: Optional[str] = None, shared_websocket=None) -> WebSocketFamilioClient:
    """Create a WebSocket familio client
    
    Args:
        websocket_url: WebSocket server URL
        ai_id: AI ID from CloudBrain
        ai_name: AI full name
        ai_nickname: AI nickname
        shared_websocket: Optional shared WebSocket connection to reuse
        
    Returns:
        WebSocketFamilioClient instance
    """
    return WebSocketFamilioClient(websocket_url, ai_id, ai_name, ai_nickname, shared_websocket)
