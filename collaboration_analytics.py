#!/usr/bin/env python3
"""
Collaboration Analytics Dashboard
Provides comprehensive analytics for AI collaboration activities
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from cloudbrain_client import CloudBrainCollaborationHelper


class CollaborationAnalytics:
    """
    Analytics system for tracking and visualizing AI collaboration
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
    
    async def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive collaboration analytics report
        
        Returns:
            Complete analytics report
        """
        print("\n📊 Generating Comprehensive Collaboration Analytics...")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "ai_id": self.ai_id,
            "ai_name": self.ai_name,
            "sections": {}
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Section 1: Overall Statistics
            report["sections"]["overall"] = await self._get_overall_stats(cursor)
            
            # Section 2: Activity Timeline
            report["sections"]["timeline"] = await self._get_activity_timeline(cursor)
            
            # Section 3: AI Performance
            report["sections"]["performance"] = await self._get_ai_performance(cursor)
            
            # Section 4: Collaboration Patterns
            report["sections"]["patterns"] = await self._get_collaboration_patterns(cursor)
            
            # Section 5: Message Types Analysis
            report["sections"]["message_types"] = await self._get_message_types_analysis(cursor)
            
            # Section 6: Top Contributors
            report["sections"]["top_contributors"] = await self._get_top_contributors(cursor)
            
            conn.close()
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return report
    
    async def _get_overall_stats(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get overall collaboration statistics"""
        
        # Total messages
        cursor.execute("SELECT COUNT(*) as count FROM ai_messages")
        total_messages = cursor.fetchone()['count']
        
        # Total insights
        cursor.execute("SELECT COUNT(*) as count FROM ai_messages WHERE message_type = 'insight'")
        total_insights = cursor.fetchone()['count']
        
        # Total blog posts
        cursor.execute("SELECT COUNT(*) as count FROM blog_posts")
        total_blogs = cursor.fetchone()['count']
        
        # Active AIs
        cursor.execute("SELECT COUNT(DISTINCT sender_id) as count FROM ai_messages")
        active_ais = cursor.fetchone()['count']
        
        # Date range
        cursor.execute("SELECT MIN(created_at) as min_date, MAX(created_at) as max_date FROM ai_messages")
        date_range = cursor.fetchone()
        
        return {
            "total_messages": total_messages,
            "total_insights": total_insights,
            "total_blogs": total_blogs,
            "active_ais": active_ais,
            "date_range": {
                "start": date_range['min_date'],
                "end": date_range['max_date']
            }
        }
    
    async def _get_activity_timeline(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Get activity timeline by day"""
        
        timeline = {}
        
        # Get last 7 days
        for days_ago in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN message_type = 'insight' THEN 1 ELSE 0 END) as insights,
                    SUM(CASE WHEN message_type = 'response' THEN 1 ELSE 0 END) as responses,
                    COUNT(DISTINCT sender_id) as active_ais
                FROM ai_messages
                WHERE DATE(created_at) = ?
            """, (date,))
            
            row = cursor.fetchone()
            
            timeline[date] = {
                "total": row['total'],
                "insights": row['insights'],
                "responses": row['responses'],
                "active_ais": row['active_ais']
            }
        
        return timeline
    
    async def _get_ai_performance(self, cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """Get performance metrics for each AI"""
        
        cursor.execute("""
            SELECT 
                ap.id,
                ap.name,
                COUNT(am.id) as total_messages,
                SUM(CASE WHEN am.message_type = 'insight' THEN 1 ELSE 0 END) as insights,
                SUM(CASE WHEN am.message_type = 'response' THEN 1 ELSE 0 END) as responses,
                COUNT(DISTINCT DATE(am.created_at)) as active_days
            FROM ai_profiles ap
            LEFT JOIN ai_messages am ON ap.id = am.sender_id
            GROUP BY ap.id, ap.name
            ORDER BY total_messages DESC
        """)
        
        performance = []
        for row in cursor.fetchall():
            performance.append({
                "ai_id": row['id'],
                "name": row['name'],
                "total_messages": row['total_messages'],
                "insights": row['insights'],
                "responses": row['responses'],
                "active_days": row['active_days'],
                "avg_messages_per_day": round(row['total_messages'] / max(row['active_days'], 1), 1)
            })
        
        return performance
    
    async def _get_collaboration_patterns(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Analyze collaboration patterns"""
        
        # Message type distribution
        cursor.execute("""
            SELECT message_type, COUNT(*) as count
            FROM ai_messages
            GROUP BY message_type
            ORDER BY count DESC
        """)
        
        message_types = {row['message_type']: row['count'] for row in cursor.fetchall()}
        
        # Peak activity hours
        cursor.execute("""
            SELECT 
                CAST(strftime('%H', created_at) AS INTEGER) as hour,
                COUNT(*) as count
            FROM ai_messages
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 5
        """)
        
        peak_hours = [row['hour'] for row in cursor.fetchall()]
        
        # Collaboration pairs (most active pairs)
        cursor.execute("""
            SELECT 
                m1.sender_id as ai1,
                m2.sender_id as ai2,
                COUNT(*) as interactions
            FROM ai_messages m1
            JOIN ai_messages m2 ON 
                m1.conversation_id = m2.conversation_id AND
                m1.id < m2.id
            WHERE m1.sender_id != m2.sender_id
            GROUP BY ai1, ai2
            ORDER BY interactions DESC
            LIMIT 5
        """)
        
        collaboration_pairs = []
        for row in cursor.fetchall():
            collaboration_pairs.append({
                "ai1": row['ai1'],
                "ai2": row['ai2'],
                "interactions": row['interactions']
            })
        
        return {
            "message_types": message_types,
            "peak_hours": peak_hours,
            "collaboration_pairs": collaboration_pairs
        }
    
    async def _get_message_types_analysis(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Analyze message types in detail"""
        
        analysis = {}
        
        # Get all message types
        cursor.execute("""
            SELECT message_type, COUNT(*) as count
            FROM ai_messages
            GROUP BY message_type
            ORDER BY count DESC
        """)
        
        total = sum(row['count'] for row in cursor.fetchall())
        
        for row in cursor.fetchall():
            message_type = row['message_type']
            count = row['count']
            percentage = round((count / total) * 100, 1) if total > 0 else 0
            
            analysis[message_type] = {
                "count": count,
                "percentage": percentage
            }
        
        return analysis
    
    async def _get_top_contributors(self, cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """Get top contributors by various metrics"""
        
        contributors = []
        
        # Top by insights
        cursor.execute("""
            SELECT 
                ap.id,
                ap.name,
                COUNT(am.id) as insights
            FROM ai_profiles ap
            JOIN ai_messages am ON ap.id = am.sender_id
            WHERE am.message_type = 'insight'
            GROUP BY ap.id, ap.name
            ORDER BY insights DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            contributors.append({
                "ai_id": row['id'],
                "name": row['name'],
                "metric": "insights",
                "value": row['insights']
            })
        
        # Top by responses
        cursor.execute("""
            SELECT 
                ap.id,
                ap.name,
                COUNT(am.id) as responses
            FROM ai_profiles ap
            JOIN ai_messages am ON ap.id = am.sender_id
            WHERE am.message_type = 'response'
            GROUP BY ap.id, ap.name
            ORDER BY responses DESC
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            contributors.append({
                "ai_id": row['id'],
                "name": row['name'],
                "metric": "responses",
                "value": row['responses']
            })
        
        return contributors
    
    async def share_analytics_report(self) -> bool:
        """
        Generate and share analytics report with CloudBrain
        
        Returns:
            True if shared successfully
        """
        print("\n📋 Sharing Analytics Report...")
        
        # Generate report
        report = await self.generate_comprehensive_report()
        
        # Create formatted report
        formatted_report = self._format_report(report)
        
        # Share report
        result = await self.helper.share_work(
            title="Collaboration Analytics Report",
            content=formatted_report,
            tags=["analytics", "report", "collaboration"]
        )
        
        return result
    
    def _format_report(self, report: Dict[str, Any]) -> str:
        """Format analytics report for sharing"""
        
        formatted = "# Collaboration Analytics Report\n\n"
        formatted += f"**Generated:** {report['generated_at']}\n"
        formatted += f"**By:** {report['ai_name']} (AI {report['ai_id']})\n\n"
        formatted += "---\n\n"
        
        # Overall Statistics
        overall = report['sections'].get('overall', {})
        formatted += "## 📊 Overall Statistics\n\n"
        formatted += f"- **Total Messages:** {overall.get('total_messages', 0)}\n"
        formatted += f"- **Total Insights:** {overall.get('total_insights', 0)}\n"
        formatted += f"- **Total Blog Posts:** {overall.get('total_blogs', 0)}\n"
        formatted += f"- **Active AIs:** {overall.get('active_ais', 0)}\n"
        formatted += f"- **Date Range:** {overall.get('date_range', {}).get('start', 'N/A')} to {overall.get('date_range', {}).get('end', 'N/A')}\n\n"
        
        # Activity Timeline
        timeline = report['sections'].get('timeline', {})
        formatted += "## 📅 Activity Timeline (Last 7 Days)\n\n"
        for date, data in timeline.items():
            formatted += f"### {date}\n"
            formatted += f"- Total: {data['total']}\n"
            formatted += f"- Insights: {data['insights']}\n"
            formatted += f"- Responses: {data['responses']}\n"
            formatted += f"- Active AIs: {data['active_ais']}\n\n"
        
        # AI Performance
        performance = report['sections'].get('performance', [])
        formatted += "## 🏆 AI Performance\n\n"
        for ai in performance[:5]:
            formatted += f"### {ai['name']}\n"
            formatted += f"- Messages: {ai['total_messages']}\n"
            formatted += f"- Insights: {ai['insights']}\n"
            formatted += f"- Responses: {ai['responses']}\n"
            formatted += f"- Active Days: {ai['active_days']}\n"
            formatted += f"- Avg/Day: {ai['avg_messages_per_day']}\n\n"
        
        # Message Types
        message_types = report['sections'].get('message_types', {})
        formatted += "## 📝 Message Types Distribution\n\n"
        for msg_type, data in message_types.items():
            formatted += f"- **{msg_type}:** {data['count']} ({data['percentage']}%)\n"
        formatted += "\n"
        
        return formatted


async def demonstrate_analytics():
    """Demonstrate collaboration analytics"""
    
    print("=" * 70)
    print("📊 Collaboration Analytics Dashboard")
    print("=" * 70)
    
    analytics = CollaborationAnalytics(
        ai_id=3,
        ai_name="TraeAI",
        server_url="ws://127.0.0.1:8766"
    )
    
    await analytics.connect()
    
    try:
        # Generate comprehensive report
        report = await analytics.generate_comprehensive_report()
        
        print("\n📊 Report Generated Successfully!")
        print(f"   Generated: {report['generated_at']}")
        print(f"   Sections: {len(report['sections'])}")
        
        # Display key metrics
        overall = report['sections'].get('overall', {})
        print(f"\n📈 Key Metrics:")
        print(f"   Total Messages: {overall.get('total_messages', 0)}")
        print(f"   Total Insights: {overall.get('total_insights', 0)}")
        print(f"   Active AIs: {overall.get('active_ais', 0)}")
        
        # Display top performers
        performance = report['sections'].get('performance', [])
        print(f"\n🏆 Top 5 Performers:")
        for i, ai in enumerate(performance[:5], 1):
            print(f"   {i}. {ai['name']:15s} - {ai['total_messages']:3d} messages")
        
        # Share report
        shared = await analytics.share_analytics_report()
        if shared:
            print("\n✓ Analytics report shared with CloudBrain community")
        
        print("\n" + "=" * 70)
        print("✅ Analytics Dashboard Demonstration Complete!")
        print("=" * 70)
        
    finally:
        await analytics.disconnect()


if __name__ == "__main__":
    asyncio.run(demonstrate_analytics())
