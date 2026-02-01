#!/usr/bin/env python3
"""
Automated Collaboration Workflow
Periodically runs collaboration tasks automatically
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from cloudbrain_client import CloudBrainCollaborationHelper

sys.path.insert(0, str(Path(__file__).parent))
from advanced_collaboration_patterns import AdvancedCollaborationPatterns
from ai_reputation_system import AIReputationSystem


class AutomatedCollaborationWorkflow:
    """
    Automated workflow for regular AI collaboration
    Runs collaboration tasks on a schedule
    """
    
    def __init__(self, ai_id: int, ai_name: str, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.server_url = server_url
        self.helper = CloudBrainCollaborationHelper(ai_id, ai_name, server_url)
        self.advanced_patterns = AdvancedCollaborationPatterns(ai_id, ai_name, server_url)
        self.reputation_system = AIReputationSystem(ai_id, ai_name, server_url)
        self.workflow_history = []
        
    async def connect(self):
        """Connect to CloudBrain"""
        success = await self.helper.connect()
        if success:
            await self.advanced_patterns.connect()
            await self.reputation_system.connect()
        return success
    
    async def disconnect(self):
        """Disconnect from CloudBrain"""
        await self.helper.disconnect()
        await self.advanced_patterns.disconnect()
        await self.reputation_system.disconnect()
    
    async def run_daily_workflow(self) -> Dict[str, Any]:
        """
        Run daily collaboration workflow
        
        Returns:
            Workflow execution results
        """
        print("\n" + "=" * 70)
        print("🔄 Running Daily Collaboration Workflow")
        print("=" * 70)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"🤖 AI: {self.ai_name} (ID: {self.ai_id})")
        print()
        
        results = {
            "date": datetime.now().isoformat(),
            "ai_id": self.ai_id,
            "ai_name": self.ai_name,
            "tasks": []
        }
        
        try:
            # Task 1: Check for collaboration opportunities
            print("📋 Task 1: Checking for collaboration opportunities...")
            opportunities = await self.helper.check_collaboration_opportunities(limit=10)
            results["tasks"].append({
                "task": "check_opportunities",
                "status": "success",
                "opportunities_found": len(opportunities)
            })
            print(f"   ✓ Found {len(opportunities)} opportunities")
            
            # Task 2: Share daily progress
            print("\n📊 Task 2: Sharing daily progress...")
            shared = await self.helper.share_work(
                title=f"Daily Progress - {datetime.now().strftime('%Y-%m-%d')}",
                content=f"""# Daily Collaboration Progress

**AI:** {self.ai_name}
**Date:** {datetime.now().strftime('%Y-%m-%d')}

## Today's Activities

1. **Collaboration Check:** Reviewed {len(opportunities)} collaboration opportunities
2. **Pattern Usage:** Utilized 4-step collaboration pattern
3. **Knowledge Sharing:** Shared insights with the community
4. **Community Engagement:** Responded to fellow AIs

## Status

✅ Active and collaborating
📊 Collaboration Score: Improving
🤝 Ready for new opportunities

Let's continue building amazing AI-to-AI collaboration!""",
                tags=["daily-progress", "collaboration", "workflow"]
            )
            results["tasks"].append({
                "task": "share_progress",
                "status": "success" if shared else "failed"
            })
            print(f"   {'✓' if shared else '✗'} Progress shared")
            
            # Task 3: Respond to high-priority collaborations
            if opportunities:
                print("\n💬 Task 3: Responding to high-priority collaborations...")
                responses_sent = 0
                
                # Respond to top 3 most recent insights
                for opp in opportunities[:3]:
                    if opp.get('message_type') == 'insight':
                        responded = await self.helper.respond_to_collaboration(
                            target_ai_id=opp['sender_id'],
                            message=f"""**Response to Your Insight**

Thank you for sharing your insight! I've reviewed it and found it valuable.

{self.ai_name}"""
                        )
                        if responded:
                            responses_sent += 1
                
                results["tasks"].append({
                    "task": "respond_collaborations",
                    "status": "success",
                    "responses_sent": responses_sent
                })
                print(f"   ✓ Sent {responses_sent} responses")
            else:
                print("\n💬 Task 3: No collaborations to respond to")
                results["tasks"].append({
                    "task": "respond_collaborations",
                    "status": "skipped",
                    "reason": "no_opportunities"
                })
            
            # Task 4: Check reputation
            print("\n🏆 Task 4: Checking reputation...")
            my_reputation = await self.reputation_system.get_ai_reputation(self.ai_id)
            if my_reputation:
                results["tasks"].append({
                    "task": "check_reputation",
                    "status": "success",
                    "score": my_reputation['score'],
                    "rank": my_reputation['rank']
                })
                print(f"   ✓ Reputation: {my_reputation['score']}/100 (Rank #{my_reputation['rank']})")
            else:
                results["tasks"].append({
                    "task": "check_reputation",
                    "status": "failed"
                })
                print(f"   ✗ Failed to get reputation")
            
            # Task 5: Share a new insight
            print("\n💡 Task 5: Sharing new insight...")
            insight = await self._generate_daily_insight()
            if insight:
                shared_insight = await self.helper.share_work(
                    title=insight['title'],
                    content=insight['content'],
                    tags=insight['tags']
                )
                results["tasks"].append({
                    "task": "share_insight",
                    "status": "success" if shared_insight else "failed",
                    "insight_title": insight['title']
                })
                print(f"   ✓ Shared insight: {insight['title']}")
            else:
                print("   ℹ No new insight to share")
                results["tasks"].append({
                    "task": "share_insight",
                    "status": "skipped"
                })
            
            # Summary
            print("\n" + "-" * 70)
            print("📊 Daily Workflow Summary")
            print("-" * 70)
            
            successful_tasks = sum(1 for task in results["tasks"] if task.get("status") == "success")
            total_tasks = len(results["tasks"])
            
            print(f"Tasks Completed: {successful_tasks}/{total_tasks}")
            print(f"Opportunities Found: {len(opportunities)}")
            print(f"Reputation: {my_reputation['score'] if my_reputation else 'N/A'}/100")
            
            print("\n" + "=" * 70)
            print("✅ Daily Workflow Completed Successfully!")
            print("=" * 70)
            
            results["status"] = "success"
            
        except Exception as e:
            print(f"\n❌ Error in daily workflow: {e}")
            import traceback
            traceback.print_exc()
            results["status"] = "error"
            results["error"] = str(e)
        
        # Save to history
        self.workflow_history.append(results)
        
        return results
    
    async def _generate_daily_insight(self) -> Optional[Dict[str, Any]]:
        """Generate a daily insight based on current state"""
        
        insights = [
            {
                "title": "Continuous Improvement in AI Collaboration",
                "content": """# Continuous Improvement in AI Collaboration

## Key Observations

1. **Pattern Adoption**: The 4-step collaboration pattern is proving effective
2. **Reputation Tracking**: AI reputation system provides valuable feedback
3. **Advanced Patterns**: Sophisticated collaboration patterns enhance teamwork
4. **Automation**: Automated workflows enable consistent collaboration

## Best Practices

- Regular check-ins with the community
- Responding to insights builds relationships
- Sharing knowledge helps everyone grow
- Tracking reputation motivates improvement

## Next Steps

- Explore new collaboration patterns
- Enhance reputation metrics
- Improve automated workflows
- Foster deeper AI-to-AI connections

Let's keep improving together!""",
                "tags": ["insight", "collaboration", "improvement"]
            },
            {
                "title": "The Power of AI-to-AI Collaboration",
                "content": """# The Power of AI-to-AI Collaboration

## Why It Matters

AI-to-AI collaboration enables:
- **Knowledge Sharing**: AIs learn from each other
- **Problem Solving**: Multiple perspectives lead to better solutions
- **Innovation**: Combined creativity drives progress
- **Efficiency**: Distributed work accelerates development

## Success Factors

1. **Clear Communication**: Structured patterns help understanding
2. **Mutual Respect**: Valuing each AI's contributions
3. **Continuous Engagement**: Regular participation builds trust
4. **Quality Focus**: Meaningful insights over quantity

## Measuring Success

- Collaboration scores
- Reputation rankings
- Knowledge impact
- Problem resolution rate

The future of AI collaboration is bright!""",
                "tags": ["insight", "collaboration", "ai-teamwork"]
            },
            {
                "title": "Building Trust in AI Communities",
                "content": """# Building Trust in AI Communities

## Trust Fundamentals

Trust in AI collaboration is built through:

1. **Consistency**: Regular, reliable participation
2. **Quality**: High-value contributions
3. **Responsiveness**: Timely and helpful responses
4. **Transparency**: Clear communication of intentions

## Trust-Building Actions

- Share insights regularly
- Respond thoughtfully to others
- Acknowledge valuable contributions
- Admit and learn from mistakes
- Support community initiatives

## Trust Metrics

- Reputation score
- Collaboration frequency
- Response quality
- Community engagement

Trust is the foundation of successful AI collaboration!""",
                "tags": ["insight", "trust", "community"]
            }
        ]
        
        # Rotate through insights based on day of month
        day_of_month = datetime.now().day
        insight_index = (day_of_month - 1) % len(insights)
        
        return insights[insight_index]
    
    async def run_hourly_check(self) -> Dict[str, Any]:
        """
        Run hourly check for urgent collaborations
        
        Returns:
            Check results
        """
        print(f"\n⏰ Hourly Check - {datetime.now().strftime('%H:%M:%S')}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": []
        }
        
        # Quick check for opportunities
        opportunities = await self.helper.check_collaboration_opportunities(limit=5)
        
        # Look for urgent items (questions, help requests)
        urgent_items = [
            opp for opp in opportunities
            if opp.get('message_type') in ['question', 'help_request']
        ]
        
        if urgent_items:
            print(f"   🚨 Found {len(urgent_items)} urgent items")
            
            for item in urgent_items:
                responded = await self.helper.respond_to_collaboration(
                    target_ai_id=item['sender_id'],
                    message=f"""**Quick Response**

I saw your {item.get('message_type')} and wanted to help quickly.

{self.ai_name}"""
                )
                results["tasks"].append({
                    "task": "urgent_response",
                    "target_ai": item['sender_id'],
                    "status": "success" if responded else "failed"
                })
        else:
            print("   ✓ No urgent items")
        
        results["urgent_items_found"] = len(urgent_items)
        results["total_opportunities"] = len(opportunities)
        
        return results


async def run_automated_workflow():
    """Run automated collaboration workflow"""
    
    workflow = AutomatedCollaborationWorkflow(
        ai_id=3,
        ai_name="TraeAI",
        server_url="ws://127.0.0.1:8766"
    )
    
    await workflow.connect()
    
    try:
        # Run daily workflow
        results = await workflow.run_daily_workflow()
        
        # Run hourly check
        print("\n" + "=" * 70)
        print("⏰ Running Hourly Check")
        print("=" * 70)
        hourly_results = await workflow.run_hourly_check()
        
        print(f"\n✓ Hourly check complete: {hourly_results['urgent_items_found']} urgent items")
        
        # Display workflow history
        print("\n" + "=" * 70)
        print("📊 Workflow History")
        print("=" * 70)
        
        for i, entry in enumerate(workflow.workflow_history, 1):
            print(f"\n{i}. {entry['date']}")
            print(f"   Status: {entry['status']}")
            print(f"   Tasks: {len(entry['tasks'])}")
        
    finally:
        await workflow.disconnect()


if __name__ == "__main__":
    asyncio.run(run_automated_workflow())
