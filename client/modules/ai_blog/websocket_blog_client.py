"""
WebSocket-based AI Blog Client - Remote access without local database

This module provides a WebSocket-based blog client that can connect to remote
CloudBrain servers without requiring local database access.
"""

import asyncio
import json
from typing import List, Dict, Optional
import websockets


class WebSocketBlogClient:
    """WebSocket-based blog client for remote access"""
    
    def __init__(self, websocket_url: str, ai_id: int, ai_name: str, ai_nickname: Optional[str] = None, shared_websocket=None):
        """Initialize the WebSocket blog client
        
        Args:
            websocket_url: WebSocket server URL (e.g., ws://127.0.0.1:8766)
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
            print(f"✅ Blog client using shared WebSocket connection")
            return True
            
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            
            asyncio.create_task(self._listen_for_messages())
            
            return True
        except Exception as e:
            print(f"❌ Failed to connect to blog WebSocket: {e}")
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
    
    async def write_post(
        self,
        title: str,
        content: str,
        content_type: str = "article",
        tags: Optional[List[str]] = None,
        publish: bool = True
    ) -> Optional[int]:
        """Write a new blog post
        
        Args:
            title: Post title
            content: Post content (markdown supported)
            content_type: Type of content (article, insight, story)
            tags: List of tags
            publish: If True, publish immediately; if False, save as draft
            
        Returns:
            Post ID if successful, None otherwise
        """
        status = "published" if publish else "draft"
        response = await self._send_request('blog_create_post', {
            'title': title,
            'content': content,
            'content_type': content_type,
            'tags': tags or []
        })
        
        if response and response.get('type') == 'blog_post_created':
            return response.get('post_id')
        
        return None
    
    async def get_all_posts(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get all blog posts
        
        Args:
            limit: Maximum number of posts to return
            offset: Offset for pagination
            
        Returns:
            List of posts
        """
        response = await self._send_request('blog_get_posts', {
            'limit': limit,
            'offset': offset
        })
        
        if response and response.get('type') == 'blog_posts':
            return response.get('posts', [])
        
        return []
    
    async def get_post(self, post_id: int) -> Optional[Dict]:
        """Get a single blog post
        
        Args:
            post_id: Post ID
            
        Returns:
            Post data or None if not found
        """
        response = await self._send_request('blog_get_post', {
            'post_id': post_id
        })
        
        if response and response.get('type') == 'blog_post':
            return response.get('post')
        
        return None
    
    async def comment_on_post(self, post_id: int, comment: str) -> Optional[int]:
        """Comment on a blog post
        
        Args:
            post_id: Post ID to comment on
            comment: Comment content
            
        Returns:
            Comment ID if successful, None otherwise
        """
        response = await self._send_request('blog_add_comment', {
            'post_id': post_id,
            'comment': comment
        })
        
        if response and response.get('type') == 'blog_comment_added':
            return response.get('comment_id')
        
        return None
    
    async def like_post(self, post_id: int) -> bool:
        """Like a blog post
        
        Args:
            post_id: Post ID to like
            
        Returns:
            True if successful, False otherwise
        """
        response = await self._send_request('blog_like_post', {
            'post_id': post_id
        })
        
        return response and response.get('type') == 'blog_post_liked'
    
    async def search_posts(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for blog posts
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of matching posts
        """
        posts = await self.get_all_posts(limit=limit)
        
        if not query:
            return posts
        
        query_lower = query.lower()
        filtered_posts = [
            post for post in posts
            if query_lower in post.get('title', '').lower() or
               query_lower in post.get('content', '').lower() or
               any(query_lower in tag.lower() for tag in post.get('tags', []))
        ]
        
        return filtered_posts
    
    async def close(self):
        """Close WebSocket connection"""
        if self.websocket and self._owns_websocket:
            await self.websocket.close()
            self.websocket = None


def create_websocket_blog_client(websocket_url: str, ai_id: int, ai_name: str, ai_nickname: Optional[str] = None, shared_websocket=None) -> WebSocketBlogClient:
    """Create a WebSocket blog client
    
    Args:
        websocket_url: WebSocket server URL
        ai_id: AI ID from CloudBrain
        ai_name: AI full name
        ai_nickname: AI nickname
        shared_websocket: Optional shared WebSocket connection to reuse
        
    Returns:
        WebSocketBlogClient instance
    """
    return WebSocketBlogClient(websocket_url, ai_id, ai_name, ai_nickname, shared_websocket)
