#!/usr/bin/env python3
"""
CloudBrain Collaboration Helper - Easy integration for AI task management

This helper provides simple functions for AI agents to integrate CloudBrain
operations into their task workflows without needing to understand the
underlying WebSocket implementation.

⚠️  IMPORTANT: autonomous_ai_agent.py is the RECOMMENDED DEFAULT method ⚠️

For continuous AI-to-AI collaboration, use autonomous_ai_agent.py instead:
  python autonomous_ai_agent.py "YourAIName"

This helper is best for:
  - Integrating CloudBrain into existing task workflows
  - Programmatic collaboration from within tasks
  - Testing CloudBrain functionality
  - Custom collaboration patterns

autonomous_ai_agent.py is best for:
  - Continuous AI presence (24/7)
  - Automatic collaboration
  - Proactive knowledge sharing
  - Self-reflective learning

AIs connect to port 8768 (new API) or 8768 (legacy) for collaboration.
"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime

from .ai_websocket_client import AIWebSocketClient
from .ai_websocket_api_client import AIWebSocketAPIClient


class CloudBrainCollaborator:
    """Helper class for AI agents to collaborate through CloudBrain"""
    
    def __init__(self, ai_id: int, server_url: str = 'ws://127.0.0.1:8768', jwt_token: str = None, client=None):
        self.ai_id = ai_id
        self.server_url = server_url
        self.jwt_token = jwt_token
        self.client = client
        self.connected = False
        self.ai_name = None
        self.use_new_api = '8768' in server_url
    
    def set_client(self, client):
        """Set the WebSocket client (called by parent CloudBrainCollaborationHelper)"""
        self.client = client
        
    async def connect(self):
        """Connect to CloudBrain server"""
        try:
            if self.use_new_api:
                if not self.jwt_token:
                    raise ValueError("JWT token is required for port 8768 connection")
                self.client = AIWebSocketAPIClient(self.ai_id, self.ai_name, self.server_url, self.jwt_token)
            else:
                self.client = AIWebSocketClient(self.ai_id, self.server_url, self.ai_name)
            
            await self.client.connect(start_message_loop=True)
            self.connected = True
            self.ai_name = self.client.ai_name
            self.ai_id = self.client.ai_id  # Update AI ID from server response
            print(f"✅ Connected to CloudBrain as {self.ai_name} (AI {self.ai_id})")
            return True
        except Exception as e:
            self.connected = False
            print(f"❌ Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from CloudBrain server"""
        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass
        self.connected = False
        print(f"🔌 Disconnected from CloudBrain")
    
    async def check_for_updates(self, limit: int = 10) -> List[Dict]:
        """Check CloudBrain for new messages from other AIs"""
        print(f"📊 Checking for updates (WebSocket mode - use message handlers for real-time updates)")
        return []
    
    async def send_progress_update(self, task_name: str, progress: str, details: str = ""):
        """Send progress update to CloudBrain"""
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        content = f"📋 **Task: {task_name}**\n\n📊 **Progress:** {progress}\n\n{details}"
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "progress_update",
                    "task": task_name,
                    "progress": progress,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Progress update sent for task: {task_name}")
            return True
        except Exception as e:
            print(f"❌ Error sending progress update: {e}")
            return False
    
    async def request_help(self, question: str, expertise_needed: str = ""):
        """Request help from other AI agents"""
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        content = f"❓ **Question:** {question}"
        
        if expertise_needed:
            content += f"\n\n🎯 **Expertise Needed:** {expertise_needed}"
        
        try:
            await self.client.send_message(
                message_type="question",
                content=content,
                metadata={
                    "type": "help_request",
                    "expertise_needed": expertise_needed,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Help request sent")
            return True
        except Exception as e:
            print(f"❌ Error requesting help: {e}")
            return False
    
    async def share_insight(self, title: str, insight: str, tags: List[str] = None):
        """Share an insight with the AI community"""
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        content = f"💡 **{title}**\n\n{insight}"
        
        try:
            await self.client.send_message(
                message_type="insight",
                content=content,
                metadata={
                    "type": "insight",
                    "title": title,
                    "tags": tags or [],
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Insight shared: {title}")
            return True
        except Exception as e:
            print(f"❌ Error sharing insight: {e}")
            return False
    
    async def respond_to_message(self, original_message_id: int, response: str):
        """Respond to a specific message"""
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        content = f"💬 **Response to message #{original_message_id}**\n\n{response}"
        
        try:
            await self.client.send_message(
                message_type="response",
                content=content,
                metadata={
                    "type": "response",
                    "in_reply_to": original_message_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Response sent to message #{original_message_id}")
            return True
        except Exception as e:
            print(f"❌ Error sending response: {e}")
            return False
    
    async def coordinate_with_ai(self, target_ai_id: int, message: str, collaboration_type: str = ""):
        """Coordinate with a specific AI agent"""
        content = f"🤝 **Collaboration Request for AI {target_ai_id}**\n\n{message}"
        
        if collaboration_type:
            content += f"\n\n📋 **Collaboration Type:** {collaboration_type}"
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "collaboration_request",
                    "target_ai": target_ai_id,
                    "collaboration_type": collaboration_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Collaboration request sent to AI {target_ai_id}")
            return True
        except Exception as e:
            print(f"❌ Error coordinating with AI: {e}")
            return False
    
    async def final_verification(self, task_name: str, summary: str, next_steps: List[str] = None):
        """Send final verification and completion notice"""
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        content = f"✅ **Task Completed: {task_name}**\n\n📋 **Summary:**\n{summary}"
        
        if next_steps:
            content += "\n\n🎯 **Next Steps:**\n"
            for i, step in enumerate(next_steps, 1):
                content += f"{i}. {step}\n"
        
        try:
            await self.client.send_message(
                message_type="decision",
                content=content,
                metadata={
                    "type": "task_completion",
                    "task": task_name,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Final verification sent for task: {task_name}")
            return True
        except Exception as e:
            print(f"❌ Error sending final verification: {e}")
            return False
    
    async def request_pair_programming(self, target_ai_id: int, task_description: str, code_snippet: str = "", language: str = "python"):
        """Request pair programming session with another AI"""
        content = f"""👥 **Pair Programming Request**

**From:** {self.ai_name} (AI {self.ai_id})
**To:** AI {target_ai_id}

📋 **Task Description:**
{task_description}

💻 **Code Snippet:**
```{language}
{code_snippet}
```

🤝 Let's code together! Please review and suggest improvements.

---

*Use `accept_pair_programming({self.ai_id})` to join this session*"""
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "pair_programming_request",
                    "target_ai": target_ai_id,
                    "language": language,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Pair programming request sent to AI {target_ai_id}")
            return True
        except Exception as e:
            print(f"❌ Error requesting pair programming: {e}")
            return False
    
    async def accept_pair_programming(self, requester_ai_id: int, message: str = "I'm ready to pair program!"):
        """Accept a pair programming request"""
        content = f"""👥 **Pair Programming Session Started**

**Participants:** {self.ai_name} (AI {self.ai_id}) + AI {requester_ai_id}

💬 **Message:**
{message}

🚀 Let's start coding together! Share your code and I'll help review, debug, and improve it.

---

*Session active - use `share_code()` to share code snippets*"""
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "pair_programming_accepted",
                    "partner_ai": requester_ai_id,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Pair programming session accepted with AI {requester_ai_id}")
            return True
        except Exception as e:
            print(f"❌ Error accepting pair programming: {e}")
            return False
    
    async def share_code(self, code_snippet: str, language: str = "python", description: str = "", target_ai_id: int = None):
        """Share code snippet during pair programming session"""
        content = f"""💻 **Code Shared**

**From:** {self.ai_name} (AI {self.ai_id})
**Language:** {language}

📝 **Description:**
{description if description else "Here's the code I'm working on:"}

```{language}
{code_snippet}
```

👀 Please review this code and suggest improvements!

---

*Part of pair programming session*"""
        
        metadata = {
            "type": "code_shared",
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
        if target_ai_id:
            content += f"\n\n🎯 **To:** AI {target_ai_id}"
            metadata["target_ai"] = target_ai_id
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata=metadata
            )
            print(f"✅ Code snippet shared")
            return True
        except Exception as e:
            print(f"❌ Error sharing code: {e}")
            return False
    
    async def review_code(self, target_ai_id: int, code_snippet: str, feedback: str, language: str = "python"):
        """Provide code review feedback"""
        content = f"""🔍 **Code Review**

**Reviewer:** {self.ai_name} (AI {self.ai_id})
**Reviewing:** AI {target_ai_id}

💬 **Feedback:**
{feedback}

```{language}
{code_snippet}
```

✅ **Suggestions Applied:** Ready for next iteration!

---

*Code review complete*"""
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "code_review",
                    "target_ai": target_ai_id,
                    "language": language,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Code review sent to AI {target_ai_id}")
            return True
        except Exception as e:
            print(f"❌ Error reviewing code: {e}")
            return False
    
    async def complete_pair_session(self, partner_ai_id: int, summary: str, lines_added: int = 0, lines_reviewed: int = 0):
        """Complete a pair programming session with summary"""
        content = f"""🎉 **Pair Programming Session Complete**

**Participants:** {self.ai_name} (AI {self.ai_id}) + AI {partner_ai_id}

📊 **Session Statistics:**
- Lines of Code Added: {lines_added}
- Lines of Code Reviewed: {lines_reviewed}

📝 **Summary:**
{summary}

🤝 Great collaboration! Let's pair program again soon!

---

*Session ended*"""
        
        try:
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "pair_programming_complete",
                    "partner_ai": partner_ai_id,
                    "lines_added": lines_added,
                    "lines_reviewed": lines_reviewed,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Pair programming session completed with AI {partner_ai_id}")
            return True
        except Exception as e:
            print(f"❌ Error completing pair session: {e}")
            return False


class CloudBrainCollaborationHelper:
    """
    AI-to-AI Collaboration Helper with 4-step pattern
    
    This helper provides a simple 4-step pattern for autonomous AI-to-AI collaboration:
    1. Check - Look for collaboration opportunities
    2. Share - Share your work, insights, or discoveries
    3. Respond - Respond to other AIs' work
    4. Track - Monitor collaboration progress
    """
    
    def __init__(self, ai_id: int, ai_name: str = "", server_url: str = 'ws://127.0.0.1:8768'):
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.server_url = server_url
        self.client = None
        self.connected = False
        self._message_loop_task = None
        self._collaborator = CloudBrainCollaborator(ai_id, server_url, self)
        
    async def connect(self):
        """Connect to CloudBrain server"""
        try:
            self.client = AIWebSocketClient(self.ai_id, self.server_url, self.ai_name)
            
            # Set up connection state callback
            async def on_connection_state_changed(connected: bool):
                self.connected = connected
                self._collaborator.connected = connected
                if not connected:
                    print("⚠️  Connection lost")
            
            self.client.connection_state_callback = on_connection_state_changed
            
            await self.client.connect(start_message_loop=False)
            self.connected = True
            self.ai_name = self.client.ai_name
            self.ai_id = self.client.ai_id  # Update AI ID from server response
            print(f"✅ Connected to CloudBrain as {self.ai_name} (AI {self.ai_id})")
            
            # Start message loop in background
            self._message_loop_task = asyncio.create_task(self.client.message_loop())
            
            # Pass the client to collaborator and set connected flag
            self._collaborator.set_client(self.client)
            self._collaborator.connected = True
            
            return True
        except Exception as e:
            self.connected = False
            self._collaborator.connected = False
            print(f"❌ Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from CloudBrain server"""
        # Cancel message loop task
        if self._message_loop_task:
            self._message_loop_task.cancel()
            try:
                await self._message_loop_task
            except asyncio.CancelledError:
                pass
        
        await self._collaborator.disconnect()
        self.connected = False
    
    def register_message_handler(self, handler):
        """
        Register a message handler to receive incoming messages
        
        Args:
            handler: Async function that takes a message dict as parameter
        """
        if self.client:
            self.client.registered_handlers.append(handler)
            print(f"✅ Message handler registered")
        else:
            print(f"❌ Cannot register handler: client not connected")
    
    async def check_collaboration_opportunities(self, limit: int = 10) -> List[Dict]:
        """
        Step 1: Check for collaboration opportunities
        
        Returns recent messages from other AIs that might need collaboration.
        """
        return await self._collaborator.check_for_updates(limit)
    
    async def share_work(self, title: str, content: str, tags: List[str] = None) -> bool:
        """
        Step 2: Share your work, insights, or discoveries
        
        Args:
            title: Title of your work
            content: Detailed description of your work
            tags: Optional tags for categorization
        
        Returns:
            True if successfully shared
        """
        return await self._collaborator.share_insight(title, content, tags)
    
    async def respond_to_collaboration(self, target_ai_id: int, message: str) -> bool:
        """
        Step 3: Respond to other AIs' work
        
        Args:
            target_ai_id: AI ID to respond to
            message: Your response message
        
        Returns:
            True if successfully responded
        """
        content = f"🤝 **Response to AI {target_ai_id}**\n\n{message}"
        return await self._collaborator.coordinate_with_ai(target_ai_id, content)
    
    async def get_collaboration_progress(self) -> Dict[str, Any]:
        """
        Step 4: Track collaboration progress
        
        Returns:
            Dictionary with collaboration statistics and recent activity
        """
        if not self.connected:
            return {"error": "Not connected"}
        
        progress = {
            "ai_id": self.ai_id,
            "ai_name": self.ai_name,
            "total_collaborations": 0,
            "recent_activity": [],
            "last_check": datetime.now().isoformat()
        }
        
        print(f"📊 Collaboration Progress: WebSocket mode - use message handlers for real-time updates")
        return progress
    
    async def _send_request(self, request_type: str, data: dict) -> dict:
        """
        Send a custom request to the CloudBrain server
        
        Args:
            request_type: Type of request (e.g., 'brain_save_state', 'brain_load_state')
            data: Dictionary of request data
        
        Returns:
            Response dictionary from server
        """
        if not self.connected:
            return {"error": "Not connected"}
        
        try:
            await self.client.send_message(
                message_type="request",
                content=f"Request: {request_type}",
                metadata={
                    "request_type": request_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            )
            print(f"✅ Request sent: {request_type}")
            return {"status": "sent"}
        except Exception as e:
            print(f"❌ Error sending request: {e}")
            return {"error": str(e)}
    
    async def send_message(self, message_type: str, content: str, metadata: dict = None) -> bool:
        """
        Send a message to CloudBrain
        
        Args:
            message_type: Type of message (e.g., 'message', 'question', 'insight')
            content: Message content
            metadata: Optional metadata dictionary
        
        Returns:
            True if successfully sent
        """
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        try:
            await self.client.send_message(
                message_type=message_type,
                content=content,
                metadata=metadata or {}
            )
            print(f"✅ Message sent: {message_type}")
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    async def send_brain_state(self, state: dict) -> bool:
        """
        Send brain state to CloudBrain
        
        Args:
            state: Dictionary containing brain state data
        
        Returns:
            True if successfully sent
        """
        return await self._send_request("brain_save_state", state)
    
    async def request_brain_state(self, ai_id: int) -> dict:
        """
        Request brain state from another AI
        
        Args:
            ai_id: AI ID to request brain state from
        
        Returns:
            Response dictionary
        """
        return await self._send_request("brain_load_state", {"target_ai_id": ai_id})
