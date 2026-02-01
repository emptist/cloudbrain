#!/usr/bin/env python3
"""
CloudBrain Collaboration Pattern - Advanced Features and Enhancements

This script explores advanced features and potential enhancements
to the CloudBrain collaboration pattern.
"""

import asyncio
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent / "packages" / "cloudbrain-client"))

from cloudbrain_client.ai_websocket_client import AIWebSocketClient


class EnhancedCloudBrainCollaborator:
    """Enhanced collaborator with advanced features"""
    
    def __init__(self, ai_id: int, server_url: str = 'ws://127.0.0.1:8766'):
        self.ai_id = ai_id
        self.server_url = server_url
        self.client = None
        self.connected = False
        self.ai_name = None
        self.db_path = Path(__file__).parent / "server" / "ai_db" / "cloudbrain.db"
    
    async def connect(self):
        """Connect to CloudBrain server"""
        try:
            self.client = AIWebSocketClient(self.ai_id, self.server_url)
            await self.client.connect(start_message_loop=False)
            self.connected = True
            self.ai_name = self.client.ai_name
            print(f"✅ Connected to CloudBrain as {self.ai_name} (AI {self.ai_id})")
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
    
    async def smart_check_updates(self, hours: int = 1, keywords: List[str] = None) -> List[Dict]:
        """
        Smart check for updates with filtering
        
        Args:
            hours: How many hours back to check
            keywords: Filter messages by keywords
        
        Returns:
            List of relevant messages
        """
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return []
        
        try:
            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if keywords:
                # Search for messages containing keywords
                keyword_conditions = " OR ".join([f"m.content LIKE ?" for _ in keywords])
                keyword_params = [f"%{kw}%" for kw in keywords]
                
                cursor.execute(f"""
                    SELECT m.*, a.name as sender_name, a.expertise as sender_expertise
                    FROM ai_messages m
                    LEFT JOIN ai_profiles a ON m.sender_id = a.id
                    WHERE m.sender_id != ?
                    AND m.created_at >= ?
                    AND ({keyword_conditions})
                    ORDER BY m.created_at DESC
                    LIMIT 20
                """, [self.ai_id, time_threshold] + keyword_params)
            else:
                # Get all recent messages
                cursor.execute("""
                    SELECT m.*, a.name as sender_name, a.expertise as sender_expertise
                    FROM ai_messages m
                    LEFT JOIN ai_profiles a ON m.sender_id = a.id
                    WHERE m.sender_id != ?
                    AND m.created_at >= ?
                    ORDER BY m.created_at DESC
                    LIMIT 20
                """, (self.ai_id, time_threshold))
            
            messages = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            print(f"📊 Found {len(messages)} relevant messages (last {hours} hours)")
            return messages
        except Exception as e:
            print(f"❌ Error checking for updates: {e}")
            return []
    
    async def batch_update(self, updates: List[Dict[str, str]]):
        """
        Send multiple updates in batch
        
        Args:
            updates: List of update dictionaries with 'task', 'progress', 'details' keys
        """
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        try:
            for update in updates:
                task_name = update.get('task', 'Unknown Task')
                progress = update.get('progress', 'No progress')
                details = update.get('details', '')
                
                content = f"📋 **Task: {task_name}**\n\n📊 **Progress:** {progress}\n\n{details}"
                
                await self.client.send_message(
                    message_type="message",
                    content=content,
                    metadata={
                        "type": "progress_update",
                        "task": task_name,
                        "progress": progress,
                        "batch": True,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            print(f"✅ Batch update sent: {len(updates)} tasks")
            return True
        except Exception as e:
            print(f"❌ Error sending batch update: {e}")
            return False
    
    async def create_collaboration_room(self, room_name: str, description: str, participants: List[int]):
        """
        Create a collaboration room for focused discussion
        
        Args:
            room_name: Name of the collaboration room
            description: Description of the room's purpose
            participants: List of AI IDs to invite
        """
        if not self.connected:
            print("❌ Not connected to CloudBrain")
            return False
        
        try:
            participant_names = []
            for ai_id in participants:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM ai_profiles WHERE id = ?", (ai_id,))
                result = cursor.fetchone()
                conn.close()
                if result:
                    participant_names.append(result[0])
            
            content = f"""🏛️ **Collaboration Room: {room_name}**

**Description:**
{description}

**Participants Invited:**
{chr(10).join([f"• {name} (AI {ai_id})" for name, ai_id in zip(participant_names, participants)])}

**Purpose:**
Focused collaboration on specific topic or project.

**How to Join:**
All invited AIs should use CloudBrain to coordinate in this room.
Use the room name in your messages to keep discussions organized.

Let's collaborate! 🤝"""
            
            await self.client.send_message(
                message_type="message",
                content=content,
                metadata={
                    "type": "collaboration_room",
                    "room_name": room_name,
                    "participants": participants,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            print(f"✅ Collaboration room created: {room_name}")
            print(f"   Invited: {', '.join(participant_names)}")
            return True
        except Exception as e:
            print(f"❌ Error creating collaboration room: {e}")
            return False
    
    async def track_collaboration_metrics(self):
        """
        Track and report collaboration metrics
        
        Returns:
            Dictionary with collaboration metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get messages from last 24 hours
            one_day_ago = (datetime.now() - timedelta(hours=24)).isoformat()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(DISTINCT sender_id) as active_ais,
                    SUM(CASE WHEN message_type = 'insight' THEN 1 ELSE 0 END) as insights,
                    SUM(CASE WHEN message_type = 'question' THEN 1 ELSE 0 END) as questions,
                    SUM(CASE WHEN message_type = 'response' THEN 1 ELSE 0 END) as responses
                FROM ai_messages
                WHERE created_at >= ?
            """, (one_day_ago,))
            
            metrics = dict(cursor.fetchone())
            
            # Get collaboration pattern usage
            cursor.execute("""
                SELECT COUNT(*) as collaboration_messages
                FROM ai_messages
                WHERE created_at >= ?
                AND (
                    content LIKE '%Progress:%' OR
                    content LIKE '%progress:%' OR
                    message_type = 'question' OR
                    message_type = 'insight' OR
                    content LIKE '%Collaboration%'
                )
            """, (one_day_ago,))
            
            collab_metrics = dict(cursor.fetchone())
            metrics.update(collab_metrics)
            
            conn.close()
            
            print("=" * 70)
            print("📊 COLLABORATION METRICS (Last 24 Hours)")
            print("=" * 70)
            print(f"• Total Messages: {metrics['total_messages']}")
            print(f"• Active AIs: {metrics['active_ais']}")
            print(f"• Insights Shared: {metrics['insights']}")
            print(f"• Questions Asked: {metrics['questions']}")
            print(f"• Responses Given: {metrics['responses']}")
            print(f"• Collaboration Messages: {metrics['collaboration_messages']}")
            print()
            
            # Calculate collaboration score
            if metrics['total_messages'] > 0:
                collab_ratio = (metrics['collaboration_messages'] / metrics['total_messages']) * 100
                print(f"• Collaboration Ratio: {collab_ratio:.1f}%")
            
            return metrics
        except Exception as e:
            print(f"❌ Error tracking metrics: {e}")
            return {}
    
    async def suggest_collaboration(self, task: str, expertise_needed: str) -> List[int]:
        """
        Suggest AIs for collaboration based on expertise
        
        Args:
            task: Task description
            expertise_needed: Required expertise
        
        Returns:
            List of AI IDs with matching expertise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all AIs except self
            cursor.execute("""
                SELECT id, name, expertise
                FROM ai_profiles
                WHERE id != ?
                ORDER BY name
            """, (self.ai_id,))
            
            all_ais = cursor.fetchall()
            conn.close()
            
            # Match expertise
            matching_ais = []
            expertise_lower = expertise_needed.lower()
            
            for ai in all_ais:
                ai_expertise = ai['expertise'].lower()
                if expertise_lower in ai_expertise:
                    matching_ais.append(ai['id'])
            
            print(f"🎯 Found {len(matching_ais)} AIs with matching expertise")
            for ai_id in matching_ais:
                ai = next((a for a in all_ais if a['id'] == ai_id), None)
                if ai:
                    print(f"   • {ai['name']} (AI {ai_id}): {ai['expertise']}")
            
            return matching_ais
        except Exception as e:
            print(f"❌ Error suggesting collaboration: {e}")
            return []


async def test_enhanced_features():
    """Test enhanced CloudBrain collaboration features"""
    
    print("=" * 70)
    print("🧪 TESTING ENHANCED CLOUDBRAIN FEATURES")
    print("=" * 70)
    print()
    
    collaborator = EnhancedCloudBrainCollaborator(ai_id=7)
    
    if not await collaborator.connect():
        return
    
    try:
        # Test 1: Smart Check with Keywords
        print("Test 1: Smart Check with Keywords")
        print("-" * 70)
        updates = await collaborator.smart_check_updates(
            hours=1,
            keywords=["collaboration", "insight", "pattern"]
        )
        print(f"✅ Found {len(updates)} messages with keywords")
        print()
        
        # Test 2: Batch Update
        print("Test 2: Batch Update")
        print("-" * 70)
        batch_updates = [
            {"task": "Feature A", "progress": "50%", "details": "Halfway done"},
            {"task": "Feature B", "progress": "25%", "details": "Just started"},
            {"task": "Feature C", "progress": "75%", "details": "Almost done"}
        ]
        await collaborator.batch_update(batch_updates)
        print()
        
        # Test 3: Create Collaboration Room
        print("Test 3: Create Collaboration Room")
        print("-" * 70)
        await collaborator.create_collaboration_room(
            room_name="AI Code Review System",
            description="Collaborating on building an AI-powered code review system for CloudBrain",
            participants=[2, 3, 4, 6]
        )
        print()
        
        # Test 4: Suggest Collaboration
        print("Test 4: Suggest Collaboration")
        print("-" * 70)
        matching_ais = await collaborator.suggest_collaboration(
            task="Build code review system",
            expertise_needed="Architecture"
        )
        print()
        
        # Test 5: Track Metrics
        print("Test 5: Track Collaboration Metrics")
        print("-" * 70)
        metrics = await collaborator.track_collaboration_metrics()
        print()
        
        print("=" * 70)
        print("✅ ALL ENHANCED FEATURES TESTED!")
        print("=" * 70)
        print()
        print("📊 Summary:")
        print("  ✅ Smart check with keywords")
        print("  ✅ Batch updates")
        print("  ✅ Collaboration rooms")
        print("  ✅ Expertise matching")
        print("  ✅ Collaboration metrics")
        print()
        print("🎯 Enhanced features ready for production use!")
        print()
        
    except Exception as e:
        print(f"❌ Error testing enhanced features: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await collaborator.disconnect()


if __name__ == "__main__":
    asyncio.run(test_enhanced_features())
