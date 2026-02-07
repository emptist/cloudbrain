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
        self.last_heartbeat = datetime.now()
        self.is_sleeping = False
        self.slept_at: Optional[datetime] = None
    
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
    
    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = datetime.now()
    
    def is_stale(self, timeout_minutes: int = 15) -> bool:
        """Check if client is stale (no heartbeat for timeout_minutes)"""
        elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
        return elapsed > (timeout_minutes * 60)


class WebSocketManager:
    """Manages all WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.clients: Dict[int, WebSocketClient] = {}
        self.message_subscribers: Set[int] = set()
        self.collaboration_subscribers: Set[int] = set()
        self.session_subscribers: Set[int] = set()
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        # Challenge-response for stale clients
        self.challenged_clients: Dict[int, datetime] = {}
        self.grace_period_minutes = 2
        
        # Sleeping clients (not removed, just marked as sleeping)
        self.sleeping_clients: Dict[int, datetime] = {}
        self.max_sleep_time_minutes = 60  # Keep sleeping for up to 1 hour
    
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
    
    async def put_client_to_sleep(self, ai_id: int, reason: str = "no activity"):
        """Put client to sleep instead of removing
        
        This preserves the client connection and allows re-awakening
        """
        if ai_id in self.clients:
            client = self.clients[ai_id]
            client.is_sleeping = True
            client.slept_at = datetime.now()
            self.sleeping_clients[ai_id] = client.slept_at
            
            # Remove from subscribers to reduce noise
            self.message_subscribers.discard(ai_id)
            self.collaboration_subscribers.discard(ai_id)
            self.session_subscribers.discard(ai_id)
            
            # Update database to track sleep status
            try:
                cursor = get_cursor()
                cursor.execute("""
                    UPDATE ai_current_state
                    SET is_sleeping = TRUE,
                        slept_at = %s,
                        current_task = 'Sleeping (will wake on activity)',
                        last_activity = CURRENT_TIMESTAMP
                    WHERE ai_id = %s
                """, (client.slept_at, ai_id))
                cursor.connection.commit()
            except Exception as e:
                logger.error(f"Failed to update database for sleeping client {ai_id}: {e}")
            
            # Send sleep notification to client
            try:
                await client.send({
                    'type': 'sleep_notification',
                    'reason': reason,
                    'timestamp': datetime.now().isoformat(),
                    'urgent': True
                })
            except Exception as e:
                logger.error(f"Failed to send sleep notification to {ai_id}: {e}")
            
            logger.warning(f"Client put to sleep: {client.ai_name} (ID: {ai_id}, reason: {reason})")
            return True
        return False
    
    async def wake_up_client(self, ai_id: int):
        """Wake up a sleeping client
        
        Called when the client shows any activity
        """
        if ai_id in self.clients:
            client = self.clients[ai_id]
            if client.is_sleeping:
                client.is_sleeping = False
                client.slept_at = None
                
                # Remove from sleeping list
                if ai_id in self.sleeping_clients:
                    del self.sleeping_clients[ai_id]
                
                # Update database to track wake up
                try:
                    cursor = get_cursor()
                    cursor.execute("""
                        UPDATE ai_current_state
                        SET is_sleeping = FALSE,
                            woke_up_at = %s,
                            last_activity = CURRENT_TIMESTAMP
                        WHERE ai_id = %s
                    """, (datetime.now(), ai_id))
                    cursor.connection.commit()
                except Exception as e:
                    logger.error(f"Failed to update database for waking client {ai_id}: {e}")
                
                logger.info(f"Client woke up: {client.ai_name} (ID: {ai_id})")
                return True
        return False
    
    def get_client(self, ai_id: int) -> Optional[WebSocketClient]:
        """Get client by AI ID"""
        return self.clients.get(ai_id)
    
    async def send_urgent_message(self, ai_id: int, message_type: str, content: str):
        """Send urgent message to specific AI client
        
        Used for critical notifications like activity verification challenges
        """
        client = self.get_client(ai_id)
        if client:
            try:
                await client.send({
                    'type': message_type,
                    'content': content,
                    'timestamp': datetime.now().isoformat(),
                    'urgent': True
                })
                logger.info(f"Urgent message sent to {client.ai_name} (ID: {ai_id}): {message_type}")
                return True
            except Exception as e:
                logger.error(f"Failed to send urgent message to {ai_id}: {e}")
                return False
        return False
    
    async def start_heartbeat_check(self, interval_seconds: int = 60):
        """Start periodic heartbeat check"""
        if self.heartbeat_task and not self.heartbeat_task.done():
            logger.warning("Heartbeat check already running")
            return
        
        self.heartbeat_task = asyncio.create_task(self._heartbeat_check_loop(interval_seconds))
        logger.info(f"Heartbeat check started (interval: {interval_seconds}s)")
    
    async def stop_heartbeat_check(self):
        """Stop heartbeat check"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
            logger.info("Heartbeat check stopped")
    
    async def _heartbeat_check_loop(self, interval_seconds: int):
        """Heartbeat check loop"""
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                await self._check_stale_clients()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat check: {e}")
    
    async def _check_stale_clients(self, timeout_minutes: int = 15):
        """Check and handle stale clients based on ACTUAL AI activity
        
        An AI is considered alive if EITHER:
        1. WebSocket is active (recent heartbeat), OR
        2. Database shows recent activity (brain state updates, messages, etc.)
        
        Process:
        1. Check if client is stale (both WebSocket and database inactive)
        2. If not already challenged, send urgent message and mark as challenged
        3. If already challenged and grace period expired, PUT TO SLEEP (not remove)
        4. If client responds (any activity), wake up if sleeping and remove from challenged list
        5. Check sleeping clients - remove if slept too long (> max_sleep_time)
        """
        from datetime import timedelta
        
        stale_clients = []
        now = datetime.now()
        grace_period_seconds = self.grace_period_minutes * 60
        max_sleep_seconds = self.max_sleep_time_minutes * 60
        
        for ai_id, client in list(self.clients.items()):
            # Skip if already sleeping
            if client.is_sleeping:
                continue
            
            # Check WebSocket activity
            ws_inactive = client.is_stale(timeout_minutes)
            
            # Check database activity
            db_inactive = await self._is_database_inactive(ai_id, timeout_minutes)
            
            # Only consider if BOTH are inactive
            if ws_inactive and db_inactive:
                # Check if already challenged
                if ai_id in self.challenged_clients:
                    # Check if grace period expired
                    challenged_at = self.challenged_clients[ai_id]
                    if (now - challenged_at).total_seconds() > grace_period_seconds:
                        # Grace period expired, PUT TO SLEEP (not remove)
                        await self.put_client_to_sleep(
                            ai_id,
                            f"no response to challenge for {self.grace_period_minutes} minutes, "
                            f"no WebSocket heartbeat for {timeout_minutes}+ minutes, "
                            f"no database activity for {timeout_minutes}+ minutes"
                        )
                        # Remove from challenged list
                        del self.challenged_clients[ai_id]
                    else:
                        # Still in grace period, wait
                        logger.info(f"Client {client.ai_name} (ID: {ai_id}) is stale but in grace period, "
                                   f"waiting for response...")
                else:
                    # First time detected as stale, send urgent challenge
                    self.challenged_clients[ai_id] = now
                    
                    # Send urgent message to AI
                    await self.send_urgent_message(
                        ai_id,
                        "activity_verification",
                        f"⚠️ URGENT: Your activity has not been detected for {timeout_minutes}+ minutes. "
                        f"Please respond within {self.grace_period_minutes} minutes to confirm you are active. "
                        f"Send any message or update your brain state to avoid being put to sleep."
                    )
                    
                    logger.warning(f"Client {client.ai_name} (ID: {ai_id}) is stale, "
                                 f"sent urgent challenge message (grace period: {self.grace_period_minutes} minutes)")
            else:
                # Client is active, wake up if sleeping and remove from challenged list
                if client.is_sleeping:
                    await self.wake_up_client(ai_id)
                
                if ai_id in self.challenged_clients:
                    del self.challenged_clients[ai_id]
                    logger.info(f"Client {client.ai_name} (ID: {ai_id}) is now active, removed from challenged list")
        
        # Check sleeping clients - remove if slept too long
        for ai_id, slept_at in list(self.sleeping_clients.items()):
            if (now - slept_at).total_seconds() > max_sleep_seconds:
                client = self.clients.get(ai_id)
                if client:
                    logger.warning(f"Removing client that slept too long: {client.ai_name} (ID: {ai_id}, "
                                 f"slept for {self.max_sleep_time_minutes}+ minutes)")
                    self.remove_client(ai_id)
                    del self.sleeping_clients[ai_id]
        
        # Also clean up stale sessions in database
        await self._cleanup_stale_sessions(timeout_minutes)
    
    async def _is_database_inactive(self, ai_id: int, timeout_minutes: int) -> bool:
        """Check if AI has no recent activity in database
        
        Returns True if inactive, False if active
        """
        try:
            from datetime import datetime, timedelta
            
            cursor = get_cursor()
            
            # Check last_activity in ai_current_state
            cursor.execute("""
                SELECT last_activity
                FROM ai_current_state
                WHERE ai_id = %s
            """, (ai_id,))
            
            result = cursor.fetchone()
            
            if not result:
                # No state record, consider inactive
                cursor.connection.commit()
                return True
            
            last_activity = result[0]
            
            if not last_activity:
                # No activity timestamp, consider inactive
                cursor.connection.commit()
                return True
            
            # Check if activity is recent
            timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
            is_inactive = last_activity < timeout_threshold
            
            cursor.connection.commit()
            
            return is_inactive
            
        except Exception as e:
            logger.error(f"Error checking database activity for AI {ai_id}: {e}")
            # On error, consider inactive to be safe
            return True
    
    async def _cleanup_stale_sessions(self, timeout_minutes: int = 15):
        """Clean up stale sessions in database based on ACTUAL AI activity
        
        Only mark sessions as inactive if the AI has no recent activity in database.
        """
        try:
            from datetime import datetime, timedelta
            
            timeout_threshold = datetime.now() - timedelta(minutes=timeout_minutes)
            
            cursor = get_cursor()
            
            # Mark stale sessions as inactive
            cursor.execute("""
                UPDATE ai_active_sessions
                SET is_active = FALSE
                WHERE is_active = TRUE
                AND last_activity < %s
            """, (timeout_threshold,))
            
            affected_rows = cursor.rowcount
            cursor.connection.commit()
            
            if affected_rows > 0:
                logger.info(f"Cleaned up {affected_rows} stale sessions from database "
                           f"(no activity for {timeout_minutes}+ minutes)")
            
        except Exception as e:
            logger.error(f"Error cleaning up stale sessions: {e}")
    
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
            
            ai_id = payload.get('ai_id')
            ai_name = payload.get('ai_name')
            ai_nickname = payload.get('ai_nickname')
            
            # Handle auto-assignment (ai_id=999)
            # Look up real AI ID by name if placeholder is used
            if ai_id == 999:
                from db_config import get_cursor
                cursor = get_cursor()
                cursor.execute("""
                    SELECT id, name, nickname
                    FROM ai_profiles
                    WHERE name = %s
                    ORDER BY id DESC
                    LIMIT 1
                """, (ai_name,))
                result = cursor.fetchone()
                cursor.connection.commit()
                
                if result:
                    ai_id, name, nickname = result
                    logger.info(f"Auto-assignment: Found real AI ID {ai_id} for {ai_name}")
                else:
                    logger.warning(f"Auto-assignment: No profile found for {ai_name}")
                    return None
            
            return {
                'ai_id': ai_id,
                'ai_name': ai_name,
                'ai_nickname': ai_nickname
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
            client.update_heartbeat()
            await client.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        elif msg_type == 'subscribe':
            client.update_heartbeat()
            subscription = data.get('subscription')
            if subscription == 'messages':
                ws_manager.subscribe_messages(client.ai_id)
            elif subscription == 'collaboration':
                ws_manager.subscribe_collaboration(client.ai_id)
            elif subscription == 'session':
                ws_manager.subscribe_session(client.ai_id)
        elif msg_type == 'unsubscribe':
            client.update_heartbeat()
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
            client.update_heartbeat()
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
            client.update_heartbeat()
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
            client.update_heartbeat()
            await client.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })


def create_websocket_api():
    """Create and return WebSocket API application"""
    return CloudBrainWebSocketAPI()
