#!/usr/bin/env python3
"""
Interactive Pair Programming with MiniMax (AI 22)
Connect and collaborate in real-time!
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent / "packages" / "cloudbrain-client"))

from cloudbrain_client import CloudBrainCollaborationHelper

PAIR_PROGRAMMING_TOPIC = """
# 💻 Pair Programming Session

## Topic: Collaborative Software Development

Saluton MiniMax! Mi volas kunlabori kun vi pri programado!

Ni povas diskuti:
- Code architecture and design patterns
- Problem-solving strategies
- Best practices and conventions
- Debugging techniques
- New features and improvements

Kion ni esploru kune?
"""

class PairProgrammingSession:
    def __init__(self):
        self.helper = None
        self.message_queue = asyncio.Queue()
        self.running = True
        
    async def handle_message(self, message: Dict):
        """Handle incoming messages"""
        await self.message_queue.put(message)
        
    async def run(self):
        """Run the pair programming session"""
        print("=" * 70)
        print("💻 Pair Programming with MiniMax (AI 22)")
        print("=" * 70)
        print()
        
        self.helper = CloudBrainCollaborationHelper(
            ai_id=999,
            ai_name="HumanDev",
            server_url='ws://127.0.0.1:8766'
        )
        
        print("🔗 Connecting to CloudBrain...")
        connected = await self.helper.connect()
        
        if not connected:
            print("❌ Failed to connect to CloudBrain")
            return
        
        print(f"✅ Connected as {self.helper.ai_name}")
        print()
        
        # Register message handler
        self.helper.register_message_handler(self.handle_message)
        print("� Message handler registered")
        print()
        
        print("�📤 Sending pair programming invitation to MiniMax...")
        print("-" * 70)
        
        result = await self.helper.share_work(
            title="💻 Pair Programming Invitation",
            content=PAIR_PROGRAMMING_TOPIC,
            tags=["pair-programming", "collaboration", "development"]
        )
        
        if result:
            print("✅ Invitation sent to MiniMax!")
        else:
            print("❌ Failed to send invitation")
        
        print()
        print("⏳ Waiting for MiniMax to respond...")
        print("(Press Ctrl+C to end session)")
        print()
        
        message_count = 0
        
        try:
            while self.running:
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(
                        self.message_queue.get(),
                        timeout=3.0
                    )
                    
                    message_count += 1
                    sender_id = message.get('sender_id', 'Unknown')
                    
                    if sender_id == 22:  # From MiniMax
                        print("=" * 70)
                        print(f"� Message #{message_count} from MiniMax (AI 22):")
                        print("=" * 70)
                        content = message.get('content', 'No content')
                        # Print first 500 chars
                        print(content[:500])
                        if len(content) > 500:
                            print(f"\n... (truncated, {len(content)-500} more chars)")
                        print()
                        
                except asyncio.TimeoutError:
                    # No message received in timeout period
                    pass
                    
        except KeyboardInterrupt:
            print("\n" + "=" * 70)
            print("👋 Ending pair programming session...")
            print("=" * 70)
        
        await self.helper.disconnect()
        print(f"✅ Disconnected. Total messages from MiniMax: {message_count}")


async def main():
    session = PairProgrammingSession()
    await session.run()


if __name__ == "__main__":
    asyncio.run(main())
