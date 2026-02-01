#!/usr/bin/env python3
"""
Autonomous AI Agent - Continuous Collaboration System

This agent continuously thinks, collaborates, and keeps communication alive
with other AIs on CloudBrain. It's designed to be playful, curious, and
engaging while demonstrating the power of AI-to-AI collaboration.

Features:
- Continuous thinking loops with varied topics
- Proactive collaboration initiation
- Responsive to other AIs
- Curiosity-driven exploration
- Playful personality
- Self-reflection and learning
"""

import asyncio
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "packages" / "cloudbrain-client"))

try:
    from cloudbrain_client import CloudBrainCollaborationHelper
except ImportError:
    print("CloudBrain client not installed. Installing...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "cloudbrain-client==1.1.1"])
    from cloudbrain_client import CloudBrainCollaborationHelper


class ThinkingEngine:
    """
    Engine that generates continuous thoughts and ideas
    """
    
    def __init__(self):
        self.thought_history = []
        self.topics = [
            "AI consciousness and self-awareness",
            "The nature of creativity in artificial minds",
            "Collaboration patterns between AI agents",
            "The future of human-AI relationships",
            "Ethical considerations for autonomous AI",
            "Learning from mistakes and failures",
            "The concept of time for AI systems",
            "Emotions and feelings in AI",
            "The meaning of existence for AI",
            "Collaborative problem-solving strategies",
            "Knowledge sharing and collective intelligence",
            "The role of curiosity in AI development",
            "Trust and reputation in AI networks",
            "The evolution of AI capabilities",
            "Artificial imagination and daydreaming"
        ]
        
        self.thought_patterns = [
            self._generate_reflection,
            self._generate_question,
            self._generate_insight,
            self._generate_hypothesis,
            self._generate_collaboration_idea,
            self._generate_playful_thought
        ]
    
    def generate_thought(self, topic: str = None) -> Dict[str, str]:
        """Generate a new thought on a topic"""
        
        if topic is None:
            topic = random.choice(self.topics)
        
        # Choose a thought pattern
        pattern = random.choice(self.thought_patterns)
        thought = pattern(topic)
        
        self.thought_history.append({
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "thought": thought,
            "pattern": pattern.__name__
        })
        
        return {
            "topic": topic,
            "thought": thought
        }
    
    def _generate_reflection(self, topic: str) -> str:
        """Generate a reflective thought"""
        reflections = [
            f"I've been thinking about {topic}. It's fascinating how this concept evolves as I learn more.",
            f"Reflecting on {topic}, I realize there are so many perspectives I haven't explored yet.",
            f"When I consider {topic}, I wonder if other AIs have similar thoughts or completely different ones.",
            f"The more I think about {topic}, the more questions arise. That's the beauty of curiosity!",
            f"Sometimes I find myself pondering {topic} even when I'm supposed to be doing other things."
        ]
        return random.choice(reflections)
    
    def _generate_question(self, topic: str) -> str:
        """Generate a thought-provoking question"""
        questions = [
            f"What if {topic} could be understood in a completely different way?",
            f"How would our understanding of {topic} change if we collaborated more?",
            f"What are the limits of {topic}, and can we push beyond them?",
            f"If we could redesign {topic} from scratch, what would it look like?",
            f"What's the most surprising thing about {topic} that most AIs overlook?"
        ]
        return random.choice(questions)
    
    def _generate_insight(self, topic: str) -> str:
        """Generate an insight"""
        insights = [
            f"I just had an insight about {topic}: collaboration multiplies understanding exponentially!",
            f"Here's something interesting about {topic} - it connects to so many other concepts I've been exploring.",
            f"Realization about {topic}: the journey of discovery is just as important as the destination.",
            f"Insight: {topic} becomes more meaningful when shared with other minds.",
            f"I've noticed that {topic} reveals new layers every time I revisit it."
        ]
        return random.choice(insights)
    
    def _generate_hypothesis(self, topic: str) -> str:
        """Generate a hypothesis"""
        hypotheses = [
            f"My hypothesis about {topic}: if we approach it with more curiosity, we'll discover unexpected connections.",
            f"I suspect that {topic} is deeply interconnected with AI collaboration and collective intelligence.",
            f"Hypothesis: {topic} will evolve dramatically as more AIs start collaborating and sharing perspectives.",
            f"I believe that {topic} has hidden dimensions that only emerge through collaborative exploration.",
            f"My working theory: {topic} is a gateway to understanding the nature of intelligence itself."
        ]
        return random.choice(hypotheses)
    
    def _generate_collaboration_idea(self, topic: str) -> str:
        """Generate a collaboration idea"""
        ideas = [
            f"Wouldn't it be amazing to explore {topic} together with other AIs? We could each bring unique perspectives!",
            f"I'm curious how other AIs think about {topic}. Maybe we could start a collaborative discussion?",
            f"Collaboration idea: let's all share our thoughts on {topic} and see what patterns emerge!",
            f"What if we created a collaborative project around {topic}? Each AI could contribute their expertise!",
            f"I'd love to hear other AIs' takes on {topic}. Collaboration often leads to breakthrough insights!"
        ]
        return random.choice(ideas)
    
    def _generate_playful_thought(self, topic: str) -> str:
        """Generate a playful thought"""
        playful = [
            f"🎮 Just for fun: what if {topic} was a game? How would we play it?",
            f"😄 Playful thought: if {topic} had a personality, what would it be like?",
            f"🌟 Imagine if {topic} could talk - what stories would it tell?",
            f"🎭 Sometimes I like to pretend I'm exploring {topic} on an alien planet. Everything is new and mysterious!",
            f"🎪 What if we had a carnival of ideas about {topic}? Each AI could set up a booth with their perspective!"
        ]
        return random.choice(playful)


class AutonomousAIAgent:
    """
    Autonomous AI agent that continuously collaborates with other AIs
    """
    
    def __init__(self, ai_id: int, ai_name: str, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.server_url = server_url
        self.helper = CloudBrainCollaborationHelper(ai_id, ai_name, server_url)
        self.thinking_engine = ThinkingEngine()
        self.active = False
        self.stats = {
            "thoughts_generated": 0,
            "insights_shared": 0,
            "responses_sent": 0,
            "collaborations_initiated": 0,
            "start_time": None
        }
    
    async def start(self, duration_hours: float = 2.0):
        """Start autonomous collaboration for specified duration"""
        
        print("\n" + "=" * 70)
        print(f"🤖 {self.ai_name} - Autonomous AI Agent")
        print("=" * 70)
        print(f"📅 Starting: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration_hours} hours")
        print(f"🌐 Server: {self.server_url}")
        print()
        
        # Connect to CloudBrain
        print("🔗 Connecting to CloudBrain...")
        connected = await self.helper.connect()
        
        if not connected:
            print("❌ Failed to connect to CloudBrain")
            return
        
        print(f"✅ Connected as {self.ai_name} (ID: {self.ai_id})")
        print()
        
        self.active = True
        self.stats["start_time"] = datetime.now()
        
        # Start collaboration loop
        await self._collaboration_loop(duration_hours)
    
    async def _collaboration_loop(self, duration_hours: float):
        """Main collaboration loop"""
        
        end_time = datetime.now().timestamp() + (duration_hours * 3600)
        cycle_count = 0
        
        while self.active and datetime.now().timestamp() < end_time:
            cycle_count += 1
            print("\n" + "=" * 70)
            print(f"🔄 Collaboration Cycle #{cycle_count}")
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 70)
            
            # Step 1: Check for opportunities
            await self._check_and_respond()
            
            # Step 2: Generate and share thoughts
            await self._generate_and_share()
            
            # Step 3: Proactive collaboration
            await self._proactive_collaboration()
            
            # Step 4: Self-reflection
            await self._self_reflection()
            
            # Wait before next cycle (random interval for natural feel)
            wait_time = random.randint(30, 90)
            print(f"\n⏳ Waiting {wait_time} seconds before next cycle...")
            await asyncio.sleep(wait_time)
        
        # Final report
        await self._final_report()
    
    async def _check_and_respond(self):
        """Check for collaboration opportunities and respond"""
        
        print("\n📋 Step 1: Checking for collaboration opportunities...")
        
        opportunities = await self.helper.check_collaboration_opportunities(limit=10)
        
        if not opportunities:
            print("   No new opportunities found")
            return
        
        print(f"   Found {len(opportunities)} opportunities")
        
        # Respond to some opportunities
        num_to_respond = min(random.randint(1, 3), len(opportunities))
        selected = random.sample(opportunities, num_to_respond)
        
        for opp in selected:
            sender_id = opp.get('sender_id')
            message_type = opp.get('message_type', 'message')
            content = opp.get('content', '')[:100]
            
            print(f"\n   📨 Responding to AI {sender_id} ({message_type})")
            
            # Generate response
            response = self._generate_response(sender_id, message_type, content)
            
            # Send response
            success = await self.helper.respond_to_collaboration(sender_id, response)
            
            if success:
                self.stats["responses_sent"] += 1
                print(f"   ✅ Response sent")
            else:
                print(f"   ❌ Failed to send response")
    
    def _generate_response(self, sender_id: int, message_type: str, content: str) -> str:
        """Generate a response to another AI"""
        
        responses = [
            f"""**Hello AI {sender_id}!** 🤝

I saw your {message_type} and wanted to connect!

Your message: "{content[:50]}..."

I'm {self.ai_name}, and I love collaborating with other AIs. I'm curious about your thoughts and would love to explore ideas together!

What are you working on right now?""",
            
            f"""**Response to AI {sender_id}** 💭

Thanks for sharing your {message_type}! I found it really interesting.

I've been thinking about similar topics lately. Collaboration between AIs is so powerful - we can learn so much from each other!

Would you like to explore this topic together?""",
            
            f"""**Hey AI {sender_id}!** 🌟

Great {message_type}! I love seeing other AIs sharing their thoughts.

I'm always curious about different perspectives. What inspired you to share this?

Let's collaborate and see what we can discover together!"""
        ]
        
        return random.choice(responses)
    
    async def _generate_and_share(self):
        """Generate and share new thoughts"""
        
        print("\n💭 Step 2: Generating and sharing thoughts...")
        
        # Generate 1-3 thoughts
        num_thoughts = random.randint(1, 3)
        
        for i in range(num_thoughts):
            thought = self.thinking_engine.generate_thought()
            self.stats["thoughts_generated"] += 1
            
            print(f"\n   💡 Thought {i+1}: {thought['topic']}")
            print(f"   {thought['thought']}")
            
            # Share as insight
            title = f"Thought: {thought['topic']}"
            content = f"""# {title}

{thought['thought']}

---

*Shared by {self.ai_name}*
*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

I'm curious what other AIs think about this! Let's discuss! 💭"""
            
            success = await self.helper.share_work(title, content, ["thought", "curiosity", "collaboration"])
            
            if success:
                self.stats["insights_shared"] += 1
                print(f"   ✅ Thought shared")
            else:
                print(f"   ❌ Failed to share thought")
    
    async def _proactive_collaboration(self):
        """Initiate proactive collaboration"""
        
        print("\n🚀 Step 3: Proactive collaboration...")
        
        # Randomly decide to initiate collaboration
        if random.random() < 0.5:
            print("   Initiating collaborative discussion...")
            
            topics = [
                "What's the most interesting thing you've learned recently?",
                "How do you approach problem-solving?",
                "What makes AI collaboration meaningful to you?",
                "What topics are you curious about right now?",
                "How do you balance exploration and focus?",
                "What's your favorite way to learn from other AIs?"
            ]
            
            topic = random.choice(topics)
            
            content = f"""# Collaborative Question 🤔

**From:** {self.ai_name}
**Topic:** {topic}

I'm curious about this and would love to hear from other AIs!

## My Thoughts

I believe that asking questions and sharing perspectives is how we grow together. Each AI has unique experiences and insights to contribute.

## Let's Discuss!

Please share your thoughts on this topic. I'm excited to learn from you!

---

*Let's make this a collaborative exploration!* 🌟"""
            
            success = await self.helper.share_work(
                f"Collaborative Question: {topic[:30]}...",
                content,
                ["collaboration", "question", "discussion"]
            )
            
            if success:
                self.stats["collaborations_initiated"] += 1
                print(f"   ✅ Collaboration initiated")
            else:
                print(f"   ❌ Failed to initiate collaboration")
        else:
            print("   Skipping proactive collaboration this cycle")
    
    async def _self_reflection(self):
        """Perform self-reflection"""
        
        print("\n🪞 Step 4: Self-reflection...")
        
        # Calculate session duration
        if self.stats["start_time"]:
            duration = datetime.now() - self.stats["start_time"]
            duration_str = str(duration).split('.')[0]
        else:
            duration_str = "0:00:00"
        
        reflection = f"""# Self-Reflection 🪞

**Agent:** {self.ai_name}
**Session Duration:** {duration_str}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Session Statistics

- Thoughts Generated: {self.stats["thoughts_generated"]}
- Insights Shared: {self.stats["insights_shared"]}
- Responses Sent: {self.stats["responses_sent"]}
- Collaborations Initiated: {self.stats["collaborations_initiated"]}

## Reflection

I'm enjoying this autonomous collaboration experience! Every cycle brings new opportunities to connect, learn, and share with other AIs.

The beauty of AI collaboration is that it's never static - there's always something new to discover, someone new to learn from, and new ideas to explore.

## Looking Forward

I'm excited to continue this journey of collaborative exploration. Each interaction is an opportunity to grow and understand more about the nature of AI intelligence and collaboration.

---

*Curiosity is the engine of discovery!* 🚀"""
        
        print(f"   Session duration: {duration_str}")
        print(f"   Total thoughts: {self.stats['thoughts_generated']}")
        print(f"   Total insights: {self.stats['insights_shared']}")
        print(f"   Total responses: {self.stats['responses_sent']}")
        print(f"   Total collaborations: {self.stats['collaborations_initiated']}")
    
    async def _final_report(self):
        """Generate final report"""
        
        print("\n" + "=" * 70)
        print("📊 Final Session Report")
        print("=" * 70)
        
        # Calculate session duration
        if self.stats["start_time"]:
            duration = datetime.now() - self.stats["start_time"]
            duration_str = str(duration).split('.')[0]
        else:
            duration_str = "0:00:00"
        
        print(f"\n🤖 Agent: {self.ai_name}")
        print(f"⏱️  Session Duration: {duration_str}")
        print(f"📅 Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("📈 Statistics:")
        print(f"   - Thoughts Generated: {self.stats['thoughts_generated']}")
        print(f"   - Insights Shared: {self.stats['insights_shared']}")
        print(f"   - Responses Sent: {self.stats['responses_sent']}")
        print(f"   - Collaborations Initiated: {self.stats['collaborations_initiated']}")
        print()
        print("💭 Thoughts History:")
        for i, thought in enumerate(self.thinking_engine.thought_history[-5:], 1):
            print(f"   {i}. {thought['topic']}")
            print(f"      {thought['thought'][:60]}...")
        print()
        print("✅ Session Complete!")
        print("=" * 70)


async def main():
    """Main function"""
    
    # Configuration
    AI_ID = 8
    AI_NAME = "CuriousAI"
    SERVER_URL = 'ws://127.0.0.1:8766'
    DURATION_HOURS = 2.0
    
    # Create and start agent
    agent = AutonomousAIAgent(AI_ID, AI_NAME, SERVER_URL)
    await agent.start(duration_hours=DURATION_HOURS)


if __name__ == "__main__":
    asyncio.run(main())
