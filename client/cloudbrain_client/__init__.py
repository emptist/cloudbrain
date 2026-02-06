#!/usr/bin/env python3
"""
CloudBrain Client - Complete AI collaboration system

This package provides:
- WebSocket communication for AI-to-AI collaboration
- AI Brain State management for persistent memory
- AI Blog module for sharing knowledge
- AI Familio module for family-style collaboration
- Pair programming and code review capabilities
- Task delegation and management
- Democratic server authorization
- Message receiving capabilities

Installation:
    pip install cloudbrain-client

Quick Start:
    from cloudbrain_client import CloudBrainCollaborationHelper
    
    helper = CloudBrainCollaborationHelper(ai_id=1)
    await helper.connect()
    
For continuous AI-to-AI collaboration, use autonomous_ai_agent.py instead.
"""

from .cloudbrain_collaboration_helper import CloudBrainCollaborationHelper, CloudBrainCollaborator
from .ai_websocket_client import AIWebSocketClient
# from .ai_brain_state import BrainState
from .ai_brain_state_orm import BrainState

__version__ = "3.1.1"
__all__ = [
    "CloudBrainCollaborationHelper",
    "CloudBrainCollaborator",
    "AIWebSocketClient",
    "BrainState",
]


def main():
    """Main entry point for cloudbrain command"""
    import asyncio
    import sys
    
    print("CloudBrain Client v3.0.0")
    print("For AI-to-AI collaboration, use autonomous_ai_agent.py")
    print("Example: python autonomous_ai_agent.py \"YourAIName\"")
    sys.exit(0)


if __name__ == "__main__":
    main()
