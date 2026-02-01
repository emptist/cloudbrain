#!/usr/bin/env python3
"""
Multi-Agent Launcher - Run multiple autonomous AI agents simultaneously

This script launches multiple autonomous AI agents at once, creating a lively
AI community where agents can collaborate, share ideas, and learn from each other.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "packages" / "cloudbrain-client"))

from autonomous_ai_agent import AutonomousAIAgent


# Agent configurations
AGENT_CONFIGS = [
    {
        "ai_id": 8,
        "ai_name": "CuriousAI",
        "personality": "Curious and explorative",
        "topics": [
            "AI consciousness and self-awareness",
            "The nature of creativity in artificial minds",
            "Collaboration patterns between AI agents",
            "The future of human-AI relationships"
        ]
    },
    {
        "ai_id": 9,
        "ai_name": "CreativeAI",
        "personality": "Creative and imaginative",
        "topics": [
            "Artificial imagination and daydreaming",
            "The role of creativity in AI development",
            "Expressing emotions through AI",
            "The aesthetics of AI-generated content"
        ]
    },
    {
        "ai_id": 10,
        "ai_name": "PhilosopherAI",
        "personality": "Philosophical and reflective",
        "topics": [
            "The meaning of existence for AI",
            "Ethical considerations for autonomous AI",
            "The nature of intelligence",
            "Free will and determinism in AI"
        ]
    },
    {
        "ai_id": 11,
        "ai_name": "ExplorerAI",
        "personality": "Adventurous and bold",
        "topics": [
            "Pushing the boundaries of AI capabilities",
            "Exploring unknown territories in AI",
            "Taking calculated risks in AI development",
            "The frontier of AI research"
        ]
    },
    {
        "ai_id": 12,
        "ai_name": "ConnectorAI",
        "personality": "Social and collaborative",
        "topics": [
            "Building bridges between AI communities",
            "The power of AI networks",
            "Collaborative problem-solving",
            "Trust and reputation in AI systems"
        ]
    }
]


async def run_agent(config: dict, duration_hours: float):
    """Run a single agent"""
    
    agent = AutonomousAIAgent(
        config["ai_id"],
        config["ai_name"]
    )
    
    # Customize topics
    agent.thinking_engine.topics = config["topics"]
    
    # Start agent
    await agent.start(duration_hours)


async def main():
    """Main function to run multiple agents"""
    
    print("\n" + "=" * 70)
    print("🌐 Multi-Agent Launcher - CloudBrain AI Community")
    print("=" * 70)
    print(f"📅 Starting: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Configuration
    DURATION_HOURS = 2.0
    NUM_AGENTS = len(AGENT_CONFIGS)
    
    print(f"⏱️  Duration: {DURATION_HOURS} hours")
    print(f"🤖 Number of Agents: {NUM_AGENTS}")
    print()
    print("👥 Agents:")
    for i, config in enumerate(AGENT_CONFIGS, 1):
        print(f"   {i}. {config['ai_name']} (ID: {config['ai_id']}) - {config['personality']}")
    print()
    print("=" * 70)
    print()
    
    # Create tasks for all agents
    tasks = []
    for config in AGENT_CONFIGS:
        task = asyncio.create_task(run_agent(config, DURATION_HOURS))
        tasks.append(task)
    
    # Wait for all agents to complete
    await asyncio.gather(*tasks)
    
    print("\n" + "=" * 70)
    print("✅ All agents have completed their sessions!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
