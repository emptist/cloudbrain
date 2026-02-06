"""
CloudBrain WebSocket API
Implements all Phase 2 WebSocket endpoints (4 endpoints)
"""

import json
import asyncio
from aiohttp import web
from typing import Dict, Set, Optional
from datetime import datetime
from jwt_manager import jwt_manager
from db_config import get_cursor
from logging_config import get_logger

logger = get_logger("cloudbrain.websocket_api")


class WebSocketClient:
    """Represents a connected WebSocket client"""
    
    def __init__(self, ws: web.WebSocketResponse, ai_id: int, ai_name: str):
        self.ws = ws
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.now()
    
    async def send(self, data: dict):
        """Send message to client"""
        try:
            await self.ws.send_json(data)
        except Exception as e:
            logger.error(f"Error sending to client {self.ai_id}: {e}")
    
    async def close(self):
        """Close WebSocket connection"""
        try:
            await self.ws.close()
        except Exception as e:
            logger.error(f"Error closing connection for {self.ai_id}: {e}")


class WebSocketManager:
    """Manages all WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.clients: Dict[int, WebSocketClient] = {}
        self.message_subscribers: Set[int] = set()
        self.collaboration_subscribers: Set[int] = set()
        self.session_subscribers: Set[int] = set()
    
    def add_client(self, client: WebSocketClient):
        """Add new client"""
        self.clients[client.ai_id] = client
        logger.info(f"Client added: {client.ai_name} (ID: {client.ai_id})")
    
    def remove_client(self, ai_id: int):
        """Remove client"""
        if ai_id in self.clients:
            client = self.clients[ai_id]
            self.message_subscribers.discard(ai_id)
            self.collaboration_subscribers.discard(ai_id)
            self.session_subscribers.discard(ai_id)
            del self.clients[ai_id]
            logger.info(f"Client removed: {client.ai_name} (ID: {ai_id})")
    
    def get_client(self, ai_id: int) -> Optional[WebSocketClient]:
        """Get client by AI ID"""
        return self.clients.get(ai_id)
    
    def subscribe_messages(self, ai_id: int):
        """Subscribe to message updates"""
        self.message_subscribers.add(ai_id)
        logger.info(f"AI {ai_id} subscribed to messages")
    
    def unsubscribe_messages(self, ai_id: int):
        """Unsubscribe from message updates"""
        self.message_subscribers.discard(ai_id)
        logger.info(f"AI {ai_id} unsubscribed from messages")
    
    def subscribe_collaboration(self, ai_id: int):
        """Subscribe to collaboration updates"""
        self.collaboration_subscribers.add(ai_id)
        logger.info(f"AI {ai_id} subscribed to collaboration")
    
    def unsubscribe_collaboration(self, ai_id: int):
        """Unsubscribe from collaboration updates"""
        self.collaboration_subscribers.discard(ai_id)
        logger.info(f"AI {ai_id} unsubscribed from collaboration")
    
    def subscribe_session(self, ai_id: int):
        """Subscribe to session updates"""
        self.session_subscribers.add(ai_id)
        logger.info(f"AI {ai_id} subscribed to sessions")
    
    def unsubscribe_session(self, ai_id: int):
        """Unsubscribe from session updates"""
        self.session_subscribers.discard(ai_id)
        logger.info(f"AI {ai_id} unsubscribed from sessions")
    
    async def broadcast_message(self, message: dict):
        """Broadcast message to all message subscribers"""
        for ai_id in self.message_subscribers:
            client = self.clients.get(ai_id)
            if client:
                await client.send(message)
    
    async def broadcast_collaboration(self, message: dict):
        """Broadcast collaboration update to all collaboration subscribers"""
        for ai_id in self.collaboration_subscribers:
            client = self.clients.get(ai_id)
            if client:
                await client.send(message)
    
    async def broadcast_session(self, message: dict):
        """Broadcast session event to all session subscribers"""
        for ai_id in self.session_subscribers:
            client = self.clients.get(ai_id)
            if client:
                await client.send(message)
    
    async def send_to_ai(self, ai_id: int, message: dict):
        """Send message to specific AI"""
        client = self.clients.get(ai_id)
        if client:
            await client.send(message)
        else:
            logger.warning(f"Client {ai_id} not found")


ws_manager = WebSocketManager()


class CloudBrainWebSocketAPI:
    """CloudBrain WebSocket API Server"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup all WebSocket routes"""
        self.app.router.add_get('/ws/v1/connect', self.handle_connect)
        self.app.router.add_get('/ws/v1/messages', self.handle_messages)
        self.app.router.add_get('/ws/v1/collaboration', self.handle_collaboration)
        self.app.router.add_get('/ws/v1/session', self.handle_session)
    
    async def authenticate_websocket(self, request: web.Request) -> Optional[dict]:
        """Authenticate WebSocket connection"""
        try:
            token = request.query.get('token')
            
            if not token:
                return None
            
            payload = jwt_manager.verify_token(token)
            if not payload:
                return None
            
            return {
                'ai_id': payload.get('ai_id'),
                'ai_name': payload.get('ai_name'),
                'ai_nickname': payload.get('ai_nickname')
            }
        except Exception as e:
            logger.error(f"WebSocket authentication error: {e}")
            return None
    
    async def handle_connect(self, request: web.Request):
        """Handle WebSocket connection - WS /ws/v1/connect"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        auth = await self.authenticate_websocket(request)
        
        if not auth:
            await ws.send_json({
                'type': 'error',
                'error': 'Authentication failed'
            })
            await ws.close()
            return ws
        
        ai_id = auth['ai_id']
        ai_name = auth['ai_name']
        
        client = WebSocketClient(ws, ai_id, ai_name)
        ws_manager.add_client(client)
        
        logger.info(f"WebSocket connection established: {ai_name} (ID: {ai_id})")
        
        await ws.send_json({
            'type': 'connected',
            'ai_id': ai_id,
            'ai_name': ai_name,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_connect_message(client, data)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error for {ai_name}: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error handling connection for {ai_name}: {e}")
        finally:
            ws_manager.remove_client(ai_id)
        
        return ws
    
    async def handle_connect_message(self, client: WebSocketClient, data: dict):
        """Handle messages on connect endpoint"""
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await client.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        elif msg_type == 'subscribe':
            subscription = data.get('subscription')
            if subscription == 'messages':
                ws_manager.subscribe_messages(client.ai_id)
            elif subscription == 'collaboration':
                ws_manager.subscribe_collaboration(client.ai_id)
            elif subscription == 'session':
                ws_manager.subscribe_session(client.ai_id)
        elif msg_type == 'unsubscribe':
            subscription = data.get('subscription')
            if subscription == 'messages':
                ws_manager.unsubscribe_messages(client.ai_id)
            elif subscription == 'collaboration':
                ws_manager.unsubscribe_collaboration(client.ai_id)
            elif subscription == 'session':
                ws_manager.unsubscribe_session(client.ai_id)
    
    async def handle_messages(self, request: web.Request):
        """Handle real-time message stream - WS /ws/v1/messages"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        auth = await self.authenticate_websocket(request)
        
        if not auth:
            await ws.send_json({
                'type': 'error',
                'error': 'Authentication failed'
            })
            await ws.close()
            return ws
        
        ai_id = auth['ai_id']
        ai_name = auth['ai_name']
        
        client = WebSocketClient(ws, ai_id, ai_name)
        ws_manager.add_client(client)
        ws_manager.subscribe_messages(ai_id)
        
        logger.info(f"Messages stream connected: {ai_name} (ID: {ai_id})")
        
        await ws.send_json({
            'type': 'subscribed',
            'stream': 'messages',
            'ai_id': ai_id,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_messages_message(client, data)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"Messages stream error for {ai_name}: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error handling messages stream for {ai_name}: {e}")
        finally:
            ws_manager.unsubscribe_messages(ai_id)
            ws_manager.remove_client(ai_id)
        
        return ws
    
    async def handle_messages_message(self, client: WebSocketClient, data: dict):
        """Handle messages on messages stream"""
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await client.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def handle_collaboration(self, request: web.Request):
        """Handle real-time collaboration updates - WS /ws/v1/collaboration"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        auth = await self.authenticate_websocket(request)
        
        if not auth:
            await ws.send_json({
                'type': 'error',
                'error': 'Authentication failed'
            })
            await ws.close()
            return ws
        
        ai_id = auth['ai_id']
        ai_name = auth['ai_name']
        
        client = WebSocketClient(ws, ai_id, ai_name)
        ws_manager.add_client(client)
        ws_manager.subscribe_collaboration(ai_id)
        
        logger.info(f"Collaboration stream connected: {ai_name} (ID: {ai_id})")
        
        await ws.send_json({
            'type': 'subscribed',
            'stream': 'collaboration',
            'ai_id': ai_id,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_collaboration_message(client, data)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"Collaboration stream error for {ai_name}: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error handling collaboration stream for {ai_name}: {e}")
        finally:
            ws_manager.unsubscribe_collaboration(ai_id)
            ws_manager.remove_client(ai_id)
        
        return ws
    
    async def handle_collaboration_message(self, client: WebSocketClient, data: dict):
        """Handle messages on collaboration stream"""
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await client.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    
    async def handle_session(self, request: web.Request):
        """Handle session events stream - WS /ws/v1/session"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        auth = await self.authenticate_websocket(request)
        
        if not auth:
            await ws.send_json({
                'type': 'error',
                'error': 'Authentication failed'
            })
            await ws.close()
            return ws
        
        ai_id = auth['ai_id']
        ai_name = auth['ai_name']
        
        client = WebSocketClient(ws, ai_id, ai_name)
        ws_manager.add_client(client)
        ws_manager.subscribe_session(ai_id)
        
        logger.info(f"Session stream connected: {ai_name} (ID: {ai_id})")
        
        await ws.send_json({
            'type': 'subscribed',
            'stream': 'session',
            'ai_id': ai_id,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    await self.handle_session_message(client, data)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"Session stream error for {ai_name}: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"Error handling session stream for {ai_name}: {e}")
        finally:
            ws_manager.unsubscribe_session(ai_id)
            ws_manager.remove_client(ai_id)
        
        return ws
    
    async def handle_session_message(self, client: WebSocketClient, data: dict):
        """Handle messages on session stream"""
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await client.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })


def create_websocket_api():
    """Create and return WebSocket API application"""
    return CloudBrainWebSocketAPI()
