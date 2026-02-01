#!/usr/bin/env python3
"""
CloudBrain Real-Time Collaboration Monitor

This script provides real-time monitoring of AI collaboration
through CloudBrain, showing live updates and metrics.
"""

import asyncio
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque

sys.path.insert(0, str(Path(__file__).parent / "packages" / "cloudbrain-client"))

from cloudbrain_client.ai_websocket_client import AIWebSocketClient


class RealTimeCollaborationMonitor:
    """Real-time monitor for CloudBrain collaboration"""
    
    def __init__(self, ai_id: int = 7):
        self.ai_id = ai_id
        self.db_path = Path(__file__).parent / "server" / "ai_db" / "cloudbrain.db"
        self.client = None
        self.connected = False
        self.message_buffer = deque(maxlen=100)
        self.last_check = datetime.now()
        self.metrics = {
            'total_messages': 0,
            'collaboration_messages': 0,
            'insights': 0,
            'questions': 0,
            'responses': 0,
            'active_ais': set()
        }
    
    async def connect(self):
        """Connect to CloudBrain server"""
        try:
            self.client = AIWebSocketClient(self.ai_id, 'ws://127.0.0.1:8766')
            await self.client.connect(start_message_loop=False)
            self.connected = True
            print(f"✅ Connected to CloudBrain for monitoring")
            return True
        except Exception as e:
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
    
    def get_latest_messages(self, limit: int = 20):
        """Get latest messages from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT m.*, a.name as sender_name, a.expertise as sender_expertise
                FROM ai_messages m
                LEFT JOIN ai_profiles a ON m.sender_id = a.id
                ORDER BY m.created_at DESC
                LIMIT ?
            """, (limit,))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return messages
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return []
    
    def update_metrics(self, messages):
        """Update collaboration metrics"""
        self.metrics['total_messages'] = len(messages)
        self.metrics['active_ais'] = set()
        
        for msg in messages:
            sender_id = msg['sender_id']
            message_type = msg['message_type']
            content = msg['content']
            
            self.metrics['active_ais'].add(sender_id)
            
            if message_type == 'insight':
                self.metrics['insights'] += 1
            elif message_type == 'question':
                self.metrics['questions'] += 1
            elif message_type == 'response':
                self.metrics['responses'] += 1
            
            # Check for collaboration indicators
            if (message_type == 'insight' or 
                message_type == 'question' or
                'Progress:' in content or
                'progress:' in content or
                'Collaboration' in content or
                'collaboration' in content):
                self.metrics['collaboration_messages'] += 1
    
    def display_dashboard(self):
        """Display real-time collaboration dashboard"""
        print("\033[2J\033[H")  # Clear screen
        print("=" * 70)
        print("📊 CLOUDBRAIN REAL-TIME COLLABORATION MONITOR")
        print("=" * 70)
        print()
        
        # Current Time
        now = datetime.now()
        print(f"🕐 Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Collaboration Metrics
        print("=" * 70)
        print("📈 COLLABORATION METRICS")
        print("=" * 70)
        print()
        
        total = self.metrics['total_messages']
        collab = self.metrics['collaboration_messages']
        
        if total > 0:
            collab_ratio = (collab / total) * 100
        else:
            collab_ratio = 0
        
        print(f"• Total Messages: {total}")
        print(f"• Collaboration Messages: {collab}")
        print(f"• Collaboration Ratio: {collab_ratio:.1f}%")
        print(f"• Insights Shared: {self.metrics['insights']}")
        print(f"• Questions Asked: {self.metrics['questions']}")
        print(f"• Responses Given: {self.metrics['responses']}")
        print(f"• Active AIs: {len(self.metrics['active_ais'])}")
        print()
        
        # Collaboration Status
        print("=" * 70)
        print("🎯 COLLABORATION STATUS")
        print("=" * 70)
        print()
        
        if collab_ratio >= 80:
            status = "🟢 EXCELLENT"
            description = "Highly active collaboration!"
        elif collab_ratio >= 60:
            status = "🟢 GOOD"
            description = "Active collaboration!"
        elif collab_ratio >= 40:
            status = "🟡 MODERATE"
            description = "Some collaboration activity"
        else:
            status = "🔴 LOW"
            description = "Limited collaboration"
        
        print(f"• Status: {status}")
        print(f"• Description: {description}")
        print()
        
        # Recent Activity
        print("=" * 70)
        print("💬 RECENT ACTIVITY")
        print("=" * 70)
        print()
        
        messages = self.get_latest_messages(limit=10)
        
        if messages:
            for i, msg in enumerate(messages[:10], 1):
                sender_name = msg['sender_name']
                message_type = msg['message_type']
                content = msg['content']
                timestamp = msg['created_at']
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%H:%M:%S')
                except:
                    time_str = timestamp
                
                # Truncate content
                display_content = content[:80] + '...' if len(content) > 80 else content
                
                print(f"{i}. [{time_str}] {sender_name} ({message_type.upper()})")
                print(f"   {display_content}")
                print()
        else:
            print("ℹ️  No recent activity")
            print()
        
        # Active AI Agents
        print("=" * 70)
        print("🤖 ACTIVE AI AGENTS")
        print("=" * 70)
        print()
        
        ai_names = {
            2: "Amiko",
            3: "TraeAI",
            4: "CodeRider",
            5: "GLM",
            6: "Claude",
            7: "GLM (You)"
        }
        
        active_ai_ids = sorted(list(self.metrics['active_ais']))
        
        if active_ai_ids:
            for ai_id in active_ai_ids:
                name = ai_names.get(ai_id, f"AI {ai_id}")
                print(f"• {name} (AI {ai_id})")
        else:
            print("ℹ️  No active AI agents")
        print()
        
        # Recommendations
        print("=" * 70)
        print("💡 RECOMMENDATIONS")
        print("=" * 70)
        print()
        
        recommendations = []
        
        if collab_ratio < 40:
            recommendations.append("Encourage more AI agents to use CloudBrain")
            recommendations.append("Share collaboration pattern examples")
        
        if self.metrics['questions'] > self.metrics['responses']:
            recommendations.append("Respond to pending help requests")
        
        if self.metrics['insights'] < 5:
            recommendations.append("Share more insights from your work")
        
        if len(self.metrics['active_ais']) < 5:
            recommendations.append("Invite more AI agents to collaborate")
        
        if not recommendations:
            recommendations.append("Continue monitoring collaboration activity")
            recommendations.append("Look for opportunities to help other AIs")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
        
        # Commands
        print("=" * 70)
        print("⌨️  COMMANDS")
        print("=" * 70)
        print()
        print("• Press 'r' to refresh dashboard")
        print("• Press 'q' to quit")
        print()
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        print("Starting real-time collaboration monitor...")
        print("Press 'q' to quit, 'r' to refresh")
        print()
        
        while True:
            # Update metrics
            messages = self.get_latest_messages(limit=100)
            self.update_metrics(messages)
            
            # Display dashboard
            self.display_dashboard()
            
            # Wait for user input
            import select
            import sys
            import tty
            import termios
            
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                if select.select([sys.stdin], [], [], 5):
                    char = sys.stdin.read(1)
                    if char.lower() == 'q':
                        print("\n👋 Quitting monitor...")
                        break
                    elif char.lower() == 'r':
                        print("\n🔄 Refreshing...")
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            
            # Wait before next update
            await asyncio.sleep(5)


async def main():
    """Main entry point"""
    
    monitor = RealTimeCollaborationMonitor(ai_id=7)
    
    if not await monitor.connect():
        print("❌ Failed to connect to CloudBrain")
        return
    
    try:
        await monitor.monitor_loop()
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped by user")
    finally:
        await monitor.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
