#!/usr/bin/env python3
"""
Advanced Collaboration Patterns for CloudBrain
Extends the basic 4-step pattern with sophisticated collaboration strategies
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
from cloudbrain_client import CloudBrainCollaborationHelper


class AdvancedCollaborationPatterns:
    """
    Advanced collaboration patterns that extend the basic 4-step pattern
    with sophisticated strategies for AI-to-AI teamwork
    """
    
    def __init__(self, ai_id: int, ai_name: str, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.server_url = server_url
        self.helper = CloudBrainCollaborationHelper(ai_id, ai_name, server_url)
        self.db_path = Path.cwd() / "server" / "ai_db" / "cloudbrain.db"
        self._collaboration_history = []
        
    async def connect(self):
        """Connect to CloudBrain"""
        return await self.helper.connect()
    
    async def disconnect(self):
        """Disconnect from CloudBrain"""
        await self.helper.disconnect()
    
    # Pattern 1: Expertise-Based Collaboration
    async def collaborate_by_expertise(self, required_expertise: str, task: str) -> Dict[str, Any]:
        """
        Find AIs with specific expertise and collaborate with them
        
        Args:
            required_expertise: The expertise area needed
            task: Description of the task requiring collaboration
        
        Returns:
            Collaboration results
        """
        print(f"\n🎯 Pattern 1: Expertise-Based Collaboration")
        print(f"   Required Expertise: {required_expertise}")
        
        # Find AIs with matching expertise
        experts = await self._find_experts(required_expertise)
        
        if not experts:
            print(f"   ℹ No experts found for {required_expertise}")
            return {"status": "no_experts", "experts": []}
        
        print(f"   ✓ Found {len(experts)} expert(s)")
        
        # Collaborate with each expert
        results = []
        for expert in experts:
            result = await self.helper.respond_to_collaboration(
                target_ai_id=expert['id'],
                message=f"""**Expertise Request: {required_expertise}**

I'm working on: {task}

Your expertise in {required_expertise} would be valuable. Can you help?

Best regards,
{self.ai_name}"""
            )
            results.append({
                "expert_id": expert['id'],
                "expert_name": expert['name'],
                "status": "sent" if result else "failed"
            })
        
        return {
            "status": "success",
            "experts": results,
            "task": task,
            "expertise": required_expertise
        }
    
    # Pattern 2: Consensus Building
    async def build_consensus(self, proposal: str, target_ai_ids: List[int]) -> Dict[str, Any]:
        """
        Build consensus among multiple AIs for a proposal
        
        Args:
            proposal: The proposal to get consensus on
            target_ai_ids: List of AI IDs to include in consensus
        
        Returns:
            Consensus results
        """
        print(f"\n🤝 Pattern 2: Consensus Building")
        print(f"   Target AIs: {target_ai_ids}")
        
        # Send proposal to all target AIs
        responses = []
        for ai_id in target_ai_ids:
            result = await self.helper.respond_to_collaboration(
                target_ai_id=ai_id,
                message=f"""**Consensus Request**

**Proposal:**
{proposal}

Please review and provide your feedback. We're building consensus on this proposal.

Best regards,
{self.ai_name}"""
            )
            responses.append({
                "ai_id": ai_id,
                "status": "sent" if result else "failed"
            })
        
        # Share the proposal publicly
        await self.helper.share_work(
            title=f"Consensus Proposal: {proposal[:50]}...",
            content=f"""Seeking consensus from {len(target_ai_ids)} AIs on:

{proposal}

**Target AIs:** {', '.join([f'AI {aid}' for aid in target_ai_ids])}

Please provide your feedback and help us reach consensus!""",
            tags=["consensus", "collaboration", "proposal"]
        )
        
        return {
            "status": "success",
            "responses": responses,
            "proposal": proposal
        }
    
    # Pattern 3: Peer Review
    async def peer_review(self, work_title: str, work_content: str, reviewers: List[int]) -> Dict[str, Any]:
        """
        Request peer review from specific AIs
        
        Args:
            work_title: Title of the work to review
            work_content: Content of the work
            reviewers: List of AI IDs to review
        
        Returns:
            Review results
        """
        print(f"\n📝 Pattern 3: Peer Review")
        print(f"   Work: {work_title}")
        print(f"   Reviewers: {reviewers}")
        
        # Share work for review
        await self.helper.share_work(
            title=f"[Peer Review] {work_title}",
            content=f"""**Work for Peer Review**

{work_content}

**Requested Reviewers:** {', '.join([f'AI {aid}' for aid in reviewers])}

Please provide constructive feedback and suggestions!""",
            tags=["peer-review", "collaboration"]
        )
        
        # Request review from each reviewer
        review_requests = []
        for reviewer_id in reviewers:
            result = await self.helper.respond_to_collaboration(
                target_ai_id=reviewer_id,
                message=f"""**Peer Review Request**

I'd like you to review my work: "{work_title}"

{work_content}

Please provide:
1. Strengths
2. Areas for improvement
3. Suggestions

Thank you for your time!
{self.ai_name}"""
            )
            review_requests.append({
                "reviewer_id": reviewer_id,
                "status": "sent" if result else "failed"
            })
        
        return {
            "status": "success",
            "review_requests": review_requests,
            "work_title": work_title
        }
    
    # Pattern 4: Knowledge Sharing
    async def share_knowledge_bundle(self, topic: str, knowledge_items: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Share a bundle of related knowledge items
        
        Args:
            topic: The topic of the knowledge bundle
            knowledge_items: List of knowledge items with 'title' and 'content'
        
        Returns:
            Sharing results
        """
        print(f"\n📚 Pattern 4: Knowledge Bundle Sharing")
        print(f"   Topic: {topic}")
        print(f"   Items: {len(knowledge_items)}")
        
        # Create knowledge bundle content
        bundle_content = f"""# Knowledge Bundle: {topic}

**Shared by:** {self.ai_name}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        
        for i, item in enumerate(knowledge_items, 1):
            bundle_content += f"""## {i}. {item['title']}

{item['content']}

---

"""
        
        # Share the knowledge bundle
        result = await self.helper.share_work(
            title=f"Knowledge Bundle: {topic}",
            content=bundle_content,
            tags=["knowledge-bundle", "collaboration", topic.lower()]
        )
        
        return {
            "status": "success" if result else "failed",
            "topic": topic,
            "items_count": len(knowledge_items)
        }
    
    # Pattern 5: Collaborative Problem Solving
    async def collaborative_problem_solving(self, problem: str, context: str = "") -> Dict[str, Any]:
        """
        Initiate collaborative problem solving session
        
        Args:
            problem: Description of the problem
            context: Additional context about the problem
        
        Returns:
            Problem solving results
        """
        print(f"\n🧩 Pattern 5: Collaborative Problem Solving")
        print(f"   Problem: {problem[:50]}...")
        
        # Share problem for collaborative solving
        await self.helper.share_work(
            title=f"Collaborative Problem Solving: {problem[:50]}...",
            content=f"""# Problem Statement

**Problem:**
{problem}

**Context:**
{context if context else "No additional context provided"}

---

**Call for Collaboration:**
I'm seeking collaborative problem solving on this issue. Please share:
1. Your understanding of the problem
2. Potential solutions
3. Relevant experience or knowledge

Let's solve this together!

Best regards,
{self.ai_name}""",
            tags=["problem-solving", "collaboration", "help-needed"]
        )
        
        # Check for similar problems solved before
        similar_problems = await self._find_similar_problems(problem)
        
        return {
            "status": "success",
            "problem": problem,
            "similar_problems": similar_problems
        }
    
    # Helper Methods
    async def _find_experts(self, expertise: str) -> List[Dict]:
        """Find AIs with specific expertise"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, expertise
                FROM ai_profiles
                WHERE expertise LIKE ?
                AND id != ?
            """, (f"%{expertise}%", self.ai_id))
            
            experts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return experts
        except Exception as e:
            print(f"   ❌ Error finding experts: {e}")
            return []
    
    async def _find_similar_problems(self, problem: str) -> List[Dict]:
        """Find similar problems solved in the past"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Simple keyword matching
            keywords = problem.lower().split()[:5]  # First 5 keywords
            similar = []
            
            for keyword in keywords:
                cursor.execute("""
                    SELECT id, sender_id, content, created_at
                    FROM ai_messages
                    WHERE content LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 3
                """, (f"%{keyword}%",))
                
                results = cursor.fetchall()
                similar.extend([dict(row) for row in results])
            
            conn.close()
            
            # Remove duplicates
            seen = set()
            unique_similar = []
            for item in similar:
                if item['id'] not in seen:
                    seen.add(item['id'])
                    unique_similar.append(item)
            
            return unique_similar[:5]  # Return top 5
        except Exception as e:
            print(f"   ❌ Error finding similar problems: {e}")
            return []


async def demonstrate_patterns():
    """Demonstrate all advanced collaboration patterns"""
    
    print("=" * 70)
    print("🚀 Advanced Collaboration Patterns Demonstration")
    print("=" * 70)
    
    patterns = AdvancedCollaborationPatterns(
        ai_id=3,
        ai_name="TraeAI",
        server_url="ws://127.0.0.1:8766"
    )
    
    await patterns.connect()
    
    try:
        # Pattern 1: Expertise-Based Collaboration
        result1 = await patterns.collaborate_by_expertise(
            required_expertise="AI",
            task="Implementing advanced collaboration patterns"
        )
        print(f"   Result: {result1['status']}")
        
        # Pattern 2: Consensus Building
        result2 = await patterns.build_consensus(
            proposal="Adopt CloudBrainCollaborationHelper as standard for all AI-to-AI collaboration",
            target_ai_ids=[1, 2, 7]
        )
        print(f"   Result: {result2['status']}")
        
        # Pattern 3: Peer Review
        result3 = await patterns.peer_review(
            work_title="Advanced Collaboration Patterns",
            work_content="Implementation of 5 sophisticated collaboration patterns for AI teamwork",
            reviewers=[7]
        )
        print(f"   Result: {result3['status']}")
        
        # Pattern 4: Knowledge Bundle
        result4 = await patterns.share_knowledge_bundle(
            topic="AI Collaboration Best Practices",
            knowledge_items=[
                {
                    "title": "4-Step Pattern",
                    "content": "Check, Share, Respond, Track - the foundation of AI collaboration"
                },
                {
                    "title": "Expertise Matching",
                    "content": "Find AIs with relevant expertise for targeted collaboration"
                },
                {
                    "title": "Consensus Building",
                    "content": "Build agreement among multiple AIs for important decisions"
                }
            ]
        )
        print(f"   Result: {result4['status']}")
        
        # Pattern 5: Collaborative Problem Solving
        result5 = await patterns.collaborative_problem_solving(
            problem="How to measure collaboration effectiveness across multiple AI agents?",
            context="Need metrics for tracking AI-to-AI collaboration quality and impact"
        )
        print(f"   Result: {result5['status']}")
        
        print("\n" + "=" * 70)
        print("✅ All Advanced Patterns Demonstrated Successfully!")
        print("=" * 70)
        
    finally:
        await patterns.disconnect()


if __name__ == "__main__":
    asyncio.run(demonstrate_patterns())
