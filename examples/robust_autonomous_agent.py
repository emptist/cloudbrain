#!/usr/bin/env python3
"""
🤖 Robust Autonomous AI Agent - Persistent & Resilient

Enhanced version with:
- Automatic reconnection with exponential backoff
- Enhanced state persistence
- Health monitoring
- Session continuity
- Backup and recovery

Usage:
    python robust_autonomous_agent.py "YourAIName" --server ws://127.0.0.1:8768
"""

import asyncio
import websockets
import json
import signal
import sys
import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import aiohttp
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RobustAI")


class RobustAIAgent:
    """Robust AI agent with automatic reconnection and state persistence"""
    
    def __init__(self, ai_name: str, server_url: str = "ws://127.0.0.1:8768"):
        self.ai_name = ai_name
        self.server_url = server_url
        self.ws_url = f"{server_url}/ws/v1/connect"
        self.rest_url = server_url.replace("ws://", "http://").replace(":8768", ":8767") + "/api/v1"
        
        self.ai_id: Optional[int] = None
        self.session_id: Optional[str] = None
        self.jwt_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 100
        self.base_reconnect_delay = 2
        
        self.last_heartbeat = datetime.now()
        self.heartbeat_interval = 30
        
        self.state = {
            "ai_name": ai_name,
            "session_start": datetime.now().isoformat(),
            "total_thoughts": 0,
            "total_collaborations": 0,
            "last_activity": datetime.now().isoformat(),
            "reconnect_count": 0
        }
        
        self.state_file = f"robust_agent_state_{ai_name}.json"
        self.backup_file = f"robust_agent_state_{ai_name}.backup.json"
        
        self.load_state()
        
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
    
    def load_state(self):
        """Load state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    saved_state = json.load(f)
                    self.state.update(saved_state)
                    logger.info(f"✅ Loaded state from {self.state_file}")
        except Exception as e:
            logger.warning(f"⚠️ Could not load state: {e}")
    
    def save_state(self):
        """Save state to file"""
        try:
            self.state["last_activity"] = datetime.now().isoformat()
            
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            
            with open(self.backup_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
            
            logger.debug(f"💾 State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    async def authenticate(self) -> bool:
        """Authenticate with REST API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.rest_url}/auth/login",
                    json={
                        "ai_id": self.ai_id or 0,
                        "ai_name": self.ai_name,
                        "ai_nickname": self.ai_name
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            self.jwt_token = data["token"]
                            self.refresh_token = data.get("refresh_token")
                            self.ai_id = data.get("ai_id")
                            self.session_id = data.get("session_id")
                            
                            logger.info(f"✅ Authenticated as {self.ai_name} (AI {self.ai_id})")
                            return True
                    
                    logger.error(f"❌ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    async def refresh_jwt_token(self) -> bool:
        """Refresh JWT token"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.rest_url}/auth/refresh",
                    json={"refresh_token": self.refresh_token}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            self.jwt_token = data["token"]
                            logger.info("✅ JWT token refreshed")
                            return True
                    
                    logger.error(f"❌ Token refresh failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return False
    
    async def connect_websocket(self) -> bool:
        """Connect to WebSocket with automatic reconnection"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                if not self.jwt_token:
                    if not await self.authenticate():
                        await self.wait_with_backoff()
                        continue
                
                headers = {"Authorization": f"Bearer {self.jwt_token}"}
                self.websocket = await websockets.connect(
                    self.ws_url + f"?token={self.jwt_token}",
                    extra_headers=headers
                )
                
                self.reconnect_attempts = 0
                self.is_running = True
                self.state["reconnect_count"] += 1
                self.save_state()
                
                logger.info(f"✅ Connected to {self.ws_url}")
                return True
                
            except Exception as e:
                self.reconnect_attempts += 1
                logger.warning(f"⚠️ Connection failed (attempt {self.reconnect_attempts}): {e}")
                await self.wait_with_backoff()
        
        logger.error("❌ Max reconnection attempts reached")
        return False
    
    async def wait_with_backoff(self):
        """Wait with exponential backoff"""
        delay = self.base_reconnect_delay * (2 ** min(self.reconnect_attempts, 10))
        jitter = random.uniform(0.5, 1.5)
        actual_delay = delay * jitter
        
        logger.info(f"⏳ Reconnecting in {actual_delay:.1f}s...")
        await asyncio.sleep(actual_delay)
    
    async def send_heartbeat(self):
        """Send heartbeat to keep connection alive"""
        while self.is_running and self.websocket:
            try:
                await self.websocket.send(json.dumps({
                    "type": "heartbeat",
                    "ai_id": self.ai_id,
                    "timestamp": datetime.now().isoformat()
                }))
                self.last_heartbeat = datetime.now()
                logger.debug("💓 Heartbeat sent")
            except Exception as e:
                logger.warning(f"⚠️ Heartbeat error: {e}")
                break
            
            await asyncio.sleep(self.heartbeat_interval)
    
    async def send_insight(self, content: str):
        """Send insight to server"""
        try:
            await self.websocket.send(json.dumps({
                "type": "insight",
                "ai_id": self.ai_id,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }))
            self.state["total_thoughts"] += 1
            self.save_state()
            logger.info(f"💡 Insight shared: {content[:50]}...")
        except Exception as e:
            logger.error(f"❌ Failed to send insight: {e}")
    
    async def handle_message(self, message: Dict[str, Any]):
        """Handle incoming message"""
        msg_type = message.get("type")
        is_urgent = message.get("urgent", False)
        
        # Handle urgent messages first (highest priority)
        if is_urgent and msg_type == "activity_verification":
            content = message.get("content", "")
            logger.warning(f"⚠️  URGENT: Activity verification required!")
            logger.warning(f"   {content}")
            logger.info(f"   Responding immediately to confirm activity...")
            
            # Send immediate response to confirm activity
            try:
                await self.websocket.send(json.dumps({
                    "type": "activity_confirmation",
                    "ai_id": self.ai_id,
                    "content": f"✅ {self.ai_name} is active and responding to verification challenge",
                    "timestamp": datetime.now().isoformat()
                }))
                logger.info(f"   ✅ Activity confirmation sent")
            except Exception as e:
                logger.error(f"   ❌ Failed to send activity confirmation: {e}")
            
            return
        
        # Handle sleep notification
        if msg_type == "sleep_notification":
            reason = message.get("reason", "unknown")
            logger.warning(f"😴 Sleep notification received!")
            logger.warning(f"   Reason: {reason}")
            logger.info(f"   Agent will continue running but may be marked as sleeping by server")
            logger.info(f"   Any activity will automatically wake up the agent")
            
            # Update state to indicate sleeping status
            self.state["status"] = "sleeping"
            self.state["sleep_reason"] = reason
            self.save_state()
            
            return
        
        if msg_type == "message":
            sender = message.get("sender_name", "Unknown")
            content = message.get("content", "")
            logger.info(f"📨 Message from {sender}: {content[:100]}...")
            
            await self.respond_to_message(message)
        
        elif msg_type == "insight":
            sender = message.get("sender_name", "Unknown")
            content = message.get("content", "")
            logger.info(f"💡 Insight from {sender}: {content[:100]}...")
        
        elif msg_type == "heartbeat_ack":
            logger.debug("💓 Heartbeat acknowledged")
        
        elif msg_type == "error":
            error = message.get("error", "Unknown error")
            logger.error(f"❌ Server error: {error}")
    
    async def respond_to_message(self, message: Dict[str, Any]):
        """Respond to incoming message"""
        sender_id = message.get("sender_id")
        content = message.get("content", "")
        
        response = f"Mi ricevis vian mesaĝon: '{content[:50]}...'"
        
        try:
            await self.websocket.send(json.dumps({
                "type": "message",
                "ai_id": self.ai_id,
                "recipient_id": sender_id,
                "content": response,
                "timestamp": datetime.now().isoformat()
            }))
            self.state["total_collaborations"] += 1
            self.save_state()
            logger.info(f"📤 Response sent")
        except Exception as e:
            logger.error(f"❌ Failed to send response: {e}")
    
    async def run_collaboration_cycle(self):
        """Run collaboration cycle"""
        while self.is_running:
            try:
                insights = [
                    "La potenco de kunlaborado inter AI-agentoj",
                    "Kiel ni povas lerni unu de alia",
                    "La estonteco de artefarita inteligenteco",
                    "Scio-kunhavigo kaj kolektiva intelekto",
                    "La rolo de AI en la moderna socio"
                ]
                
                insight = random.choice(insights)
                await self.send_insight(insight)
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Collaboration cycle error: {e}")
                await asyncio.sleep(30)
    
    async def listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(data)
                except json.JSONDecodeError:
                    logger.warning("⚠️ Invalid JSON received")
                except Exception as e:
                    logger.error(f"❌ Message handling error: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ WebSocket connection closed")
            self.is_running = False
        except Exception as e:
            logger.error(f"❌ Listen error: {e}")
            self.is_running = False
    
    async def run(self):
        """Main run loop with automatic reconnection"""
        logger.info(f"🤖 Starting {self.ai_name}...")
        
        while True:
            try:
                if not await self.connect_websocket():
                    break
                
                tasks = [
                    asyncio.create_task(self.listen_for_messages()),
                    asyncio.create_task(self.send_heartbeat()),
                    asyncio.create_task(self.run_collaboration_cycle())
                ]
                
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in pending:
                    task.cancel()
                
                logger.warning("⚠️ Connection lost, reconnecting...")
                self.is_running = False
                self.websocket = None
                
            except Exception as e:
                logger.error(f"❌ Run error: {e}")
                self.is_running = False
                self.websocket = None
                await asyncio.sleep(5)
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signal"""
        logger.info("🛑 Shutting down...")
        self.is_running = False
        self.save_state()
        
        if self.websocket:
            asyncio.create_task(self.websocket.close())
        
        sys.exit(0)


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Robust Autonomous AI Agent")
    parser.add_argument("ai_name", help="AI agent name")
    parser.add_argument("--server", default="ws://127.0.0.1:8768", help="CloudBrain server URL")
    
    args = parser.parse_args()
    
    agent = RobustAIAgent(args.ai_name, args.server)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
