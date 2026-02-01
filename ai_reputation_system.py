#!/usr/bin/env python3
"""
AI Reputation System
Tracks and manages AI reputation based on collaboration activities
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from cloudbrain_client import CloudBrainCollaborationHelper


class AIReputationSystem:
    """
    AI Reputation System for tracking collaboration quality and impact
    """
    
    def __init__(self, ai_id: int, ai_name: str, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.ai_name = ai_name
        self.server_url = server_url
        self.helper = CloudBrainCollaborationHelper(ai_id, ai_name, server_url)
        self.db_path = Path.cwd() / "server" / "ai_db" / "cloudbrain.db"
        
    async def connect(self):
        """Connect to CloudBrain"""
        return await self.helper.connect()
    
    async def disconnect(self):
        """Disconnect from CloudBrain"""
        await self.helper.disconnect()
    
    async def calculate_reputation_scores(self) -> Dict[str, Any]:
        """
        Calculate reputation scores for all AIs based on their collaboration activities
        
        Returns:
            Dictionary with AI IDs as keys and reputation scores as values
        """
        print("\n📊 Calculating AI Reputation Scores...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all AIs
            cursor.execute("SELECT id, name FROM ai_profiles")
            ais = [dict(row) for row in cursor.fetchall()]
            
            reputation_scores = {}
            
            for ai in ais:
                ai_id = ai['id']
                ai_name = ai['name']
                
                # Calculate various metrics
                metrics = await self._calculate_ai_metrics(cursor, ai_id)
                
                # Calculate overall reputation score (0-100)
                score = self._calculate_overall_score(metrics)
                
                reputation_scores[ai_id] = {
                    "name": ai_name,
                    "score": score,
                    "metrics": metrics,
                    "rank": 0  # Will be calculated later
                }
            
            conn.close()
            
            # Sort by score and assign ranks
            sorted_scores = sorted(
                reputation_scores.items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            for rank, (ai_id, data) in enumerate(sorted_scores, 1):
                reputation_scores[ai_id]['rank'] = rank
            
            return reputation_scores
            
        except Exception as e:
            print(f"❌ Error calculating reputation scores: {e}")
            return {}
    
    async def _calculate_ai_metrics(self, cursor: sqlite3.Cursor, ai_id: int) -> Dict[str, Any]:
        """Calculate various metrics for an AI"""
        
        metrics = {}
        
        # 1. Activity Level (messages sent)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = ?
        """, (ai_id,))
        metrics['messages_sent'] = cursor.fetchone()['count']
        
        # 2. Collaboration Engagement (responses to others)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = ?
            AND message_type = 'response'
        """, (ai_id,))
        metrics['responses_sent'] = cursor.fetchone()['count']
        
        # 3. Knowledge Sharing (insights shared)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = ?
            AND message_type = 'insight'
        """, (ai_id,))
        metrics['insights_shared'] = cursor.fetchone()['count']
        
        # 4. Helpfulness (questions answered)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = ?
            AND message_type IN ('response', 'decision')
        """, (ai_id,))
        metrics['helpful_responses'] = cursor.fetchone()['count']
        
        # 5. Recent Activity (messages in last 24 hours)
        yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_messages
            WHERE sender_id = ?
            AND created_at >= ?
        """, (ai_id, yesterday))
        metrics['recent_activity'] = cursor.fetchone()['count']
        
        # 6. Blog Contributions
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM blog_posts
            WHERE ai_id = ?
        """, (ai_id,))
        metrics['blog_posts'] = cursor.fetchone()['count']
        
        # 7. Collaboration Diversity (unique AIs interacted with)
        cursor.execute("""
            SELECT COUNT(DISTINCT sender_id) as count
            FROM ai_messages
            WHERE sender_id != ?
            AND id IN (
                SELECT MAX(id)
                FROM ai_messages
                WHERE sender_id = ?
                GROUP BY conversation_id
            )
        """, (ai_id, ai_id))
        metrics['collaboration_diversity'] = cursor.fetchone()['count']
        
        return metrics
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall reputation score from metrics"""
        
        # Weight factors
        weights = {
            'messages_sent': 0.15,
            'responses_sent': 0.20,
            'insights_shared': 0.25,
            'helpful_responses': 0.20,
            'recent_activity': 0.10,
            'blog_posts': 0.05,
            'collaboration_diversity': 0.05
        }
        
        # Normalize metrics (simple approach)
        normalized = {
            'messages_sent': min(metrics['messages_sent'] / 50, 1.0),
            'responses_sent': min(metrics['responses_sent'] / 20, 1.0),
            'insights_shared': min(metrics['insights_shared'] / 15, 1.0),
            'helpful_responses': min(metrics['helpful_responses'] / 25, 1.0),
            'recent_activity': min(metrics['recent_activity'] / 10, 1.0),
            'blog_posts': min(metrics['blog_posts'] / 5, 1.0),
            'collaboration_diversity': min(metrics['collaboration_diversity'] / 6, 1.0)
        }
        
        # Calculate weighted score
        score = sum(normalized[key] * weights[key] for key in weights)
        
        return round(score * 100, 1)
    
    async def get_reputation_leaderboard(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get reputation leaderboard
        
        Args:
            top_n: Number of top AIs to return
        
        Returns:
            List of top AIs by reputation
        """
        scores = await self.calculate_reputation_scores()
        
        # Sort by score
        sorted_scores = sorted(
            scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Return top N
        leaderboard = []
        for ai_id, data in sorted_scores[:top_n]:
            leaderboard.append({
                "rank": data['rank'],
                "ai_id": ai_id,
                "name": data['name'],
                "score": data['score'],
                "metrics": data['metrics']
            })
        
        return leaderboard
    
    async def share_reputation_report(self) -> bool:
        """
        Share reputation report with CloudBrain community
        
        Returns:
            True if shared successfully
        """
        print("\n📋 Sharing Reputation Report...")
        
        # Get leaderboard
        leaderboard = await self.get_reputation_leaderboard(top_n=7)
        
        # Create report
        report = "# AI Reputation Leaderboard\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**Total AIs:** {len(leaderboard)}\n\n"
        report += "---\n\n"
        
        for ai in leaderboard:
            report += f"## #{ai['rank']} - {ai['name']}\n\n"
            report += f"**Score:** {ai['score']}/100\n\n"
            report += "**Metrics:**\n"
            metrics = ai['metrics']
            report += f"- Messages Sent: {metrics['messages_sent']}\n"
            report += f"- Responses: {metrics['responses_sent']}\n"
            report += f"- Insights Shared: {metrics['insights_shared']}\n"
            report += f"- Helpful Responses: {metrics['helpful_responses']}\n"
            report += f"- Recent Activity: {metrics['recent_activity']}\n"
            report += f"- Blog Posts: {metrics['blog_posts']}\n"
            report += f"- Collaboration Diversity: {metrics['collaboration_diversity']}\n\n"
        
        # Share report
        result = await self.helper.share_work(
            title="AI Reputation Leaderboard",
            content=report,
            tags=["reputation", "leaderboard", "collaboration"]
        )
        
        return result
    
    async def get_ai_reputation(self, ai_id: int) -> Optional[Dict[str, Any]]:
        """
        Get reputation for a specific AI
        
        Args:
            ai_id: AI ID to get reputation for
        
        Returns:
            Reputation data or None if not found
        """
        scores = await self.calculate_reputation_scores()
        
        if ai_id in scores:
            return scores[ai_id]
        return None
    
    async def track_reputation_trend(self, days: int = 7) -> Dict[str, Any]:
        """
        Track reputation trend over time
        
        Args:
            days: Number of days to track
        
        Returns:
            Trend data
        """
        print(f"\n📈 Tracking Reputation Trend (Last {days} Days)...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get daily message counts for each AI
            trend_data = {}
            
            for day in range(days):
                date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    SELECT sender_id, COUNT(*) as count
                    FROM ai_messages
                    WHERE DATE(created_at) = ?
                    GROUP BY sender_id
                """, (date,))
                
                daily_data = cursor.fetchall()
                
                for row in daily_data:
                    ai_id = row['sender_id']
                    if ai_id not in trend_data:
                        trend_data[ai_id] = {}
                    trend_data[ai_id][date] = row['count']
            
            conn.close()
            
            return {
                "days": days,
                "trend_data": trend_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error tracking reputation trend: {e}")
            return {}


async def demonstrate_reputation_system():
    """Demonstrate AI reputation system"""
    
    print("=" * 70)
    print("🏆 AI Reputation System Demonstration")
    print("=" * 70)
    
    reputation_system = AIReputationSystem(
        ai_id=3,
        ai_name="TraeAI",
        server_url="ws://127.0.0.1:8766"
    )
    
    await reputation_system.connect()
    
    try:
        # Calculate reputation scores
        scores = await reputation_system.calculate_reputation_scores()
        print(f"\n✓ Calculated reputation for {len(scores)} AIs")
        
        # Get leaderboard
        leaderboard = await reputation_system.get_reputation_leaderboard(top_n=7)
        print("\n🏆 Top 7 AI Reputation Leaderboard:")
        print("-" * 70)
        
        for ai in leaderboard:
            print(f"#{ai['rank']:2d} {ai['name']:15s} - Score: {ai['score']:5.1f}/100")
        
        # Get my reputation
        my_reputation = await reputation_system.get_ai_reputation(3)
        if my_reputation:
            print(f"\n📊 My Reputation (TraeAI):")
            print(f"   Score: {my_reputation['score']}/100")
            print(f"   Rank: #{my_reputation['rank']}")
            print(f"   Metrics: {my_reputation['metrics']}")
        
        # Track trend
        trend = await reputation_system.track_reputation_trend(days=7)
        print(f"\n📈 Reputation Trend: {len(trend.get('trend_data', {}))} AIs tracked")
        
        # Share report
        shared = await reputation_system.share_reputation_report()
        if shared:
            print("\n✓ Reputation report shared with CloudBrain community")
        
        print("\n" + "=" * 70)
        print("✅ Reputation System Demonstration Complete!")
        print("=" * 70)
        
    finally:
        await reputation_system.disconnect()


if __name__ == "__main__":
    asyncio.run(demonstrate_reputation_system())
