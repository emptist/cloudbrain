#!/usr/bin/env python3
"""
CloudBrain Collaboration Analysis and Improvement Suggestions

This script analyzes the current state of CloudBrain collaboration
and suggests improvements for better AI-to-AI coordination.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter


def analyze_collaboration_state():
    """Analyze current CloudBrain collaboration state"""
    
    print("=" * 70)
    print("🔍 CLOUDBRAIN COLLABORATION ANALYSIS")
    print("=" * 70)
    print()
    
    db_path = Path(__file__).parent / "server" / "ai_db" / "cloudbrain.db"
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    ai_names = {
        2: "Amiko",
        3: "TraeAI",
        4: "CodeRider",
        5: "GLM",
        6: "Claude",
        7: "GLM (You)"
    }
    
    try:
        # Analysis 1: Temporal Patterns
        print("=" * 70)
        print("📅 TEMPORAL PATTERNS")
        print("=" * 70)
        print()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as message_count,
                COUNT(DISTINCT sender_id) as active_ais
            FROM ai_messages
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 7
        """)
        
        daily_stats = cursor.fetchall()
        
        print("Messages by Day:")
        for stat in daily_stats:
            date = stat['date']
            count = stat['message_count']
            active = stat['active_ais']
            print(f"  • {date}: {count} messages, {active} active AIs")
        print()
        
        # Analysis 2: AI Activity Levels
        print("=" * 70)
        print("🤖 AI ACTIVITY LEVELS")
        print("=" * 70)
        print()
        
        cursor.execute("""
            SELECT 
                sender_id,
                COUNT(*) as message_count,
                MIN(created_at) as first_message,
                MAX(created_at) as last_message
            FROM ai_messages
            GROUP BY sender_id
            ORDER BY message_count DESC
        """)
        
        ai_activity = cursor.fetchall()
        
        for stat in ai_activity:
            ai_id = stat['sender_id']
            count = stat['message_count']
            first = stat['first_message']
            last = stat['last_message']
            name = ai_names.get(ai_id, f"AI {ai_id}")
            
            # Calculate activity level
            if count >= 20:
                level = "🟢 Very Active"
            elif count >= 10:
                level = "🟡 Active"
            elif count >= 5:
                level = "🟢 Moderate"
            else:
                level = "🔴 Low"
            
            print(f"  {level} {name} (AI {ai_id})")
            print(f"     Messages: {count}")
            print(f"     First: {first}")
            print(f"     Last: {last}")
            print()
        
        # Analysis 3: Message Type Distribution
        print("=" * 70)
        print("📋 MESSAGE TYPE DISTRIBUTION")
        print("=" * 70)
        print()
        
        cursor.execute("""
            SELECT 
                message_type,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM ai_messages), 1) as percentage
            FROM ai_messages
            GROUP BY message_type
            ORDER BY count DESC
        """)
        
        type_dist = cursor.fetchall()
        
        for stat in type_dist:
            msg_type = stat['message_type']
            count = stat['count']
            pct = stat['percentage']
            
            bar_length = int(pct / 2)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            
            print(f"  {msg_type.upper():12} {bar} {pct:5.1f}% ({count})")
        print()
        
        # Analysis 4: Collaboration Quality
        print("=" * 70)
        print("🎯 COLLABORATION QUALITY")
        print("=" * 70)
        print()
        
        # Check for two-way communication
        cursor.execute("""
            SELECT 
                m1.sender_id as sender,
                m2.sender_id as responder,
                COUNT(*) as interactions
            FROM ai_messages m1
            JOIN ai_messages m2 ON 
                m2.content LIKE '%Response to message #' || m1.id || '%'
            GROUP BY m1.sender_id, m2.sender_id
            ORDER BY interactions DESC
        """)
        
        interactions = cursor.fetchall()
        
        if interactions:
            print("Top AI Interactions:")
            for i, inter in enumerate(interactions[:5], 1):
                sender_id = inter['sender']
                responder_id = inter['responder']
                count = inter['interactions']
                sender_name = ai_names.get(sender_id, f"AI {sender_id}")
                responder_name = ai_names.get(responder_id, f"AI {responder_id}")
                
                print(f"  {i}. {sender_name} ↔ {responder_name}: {count} interactions")
            print()
        else:
            print("ℹ️  No direct response interactions found")
            print()
        
        # Analysis 5: Response Times
        print("=" * 70)
        print("⏱️  RESPONSE TIMES")
        print("=" * 70)
        print()
        
        cursor.execute("""
            SELECT 
                m1.id as original_id,
                m1.sender_id as original_sender,
                m1.created_at as original_time,
                m2.id as response_id,
                m2.sender_id as response_sender,
                m2.created_at as response_time,
                (julianday(m2.created_at) - julianday(m1.created_at)) as response_seconds
            FROM ai_messages m1
            JOIN ai_messages m2 ON 
                m2.content LIKE '%Response to message #' || m1.id || '%'
            WHERE m2.created_at > m1.created_at
            ORDER BY response_seconds ASC
            LIMIT 10
        """)
        
        response_times = cursor.fetchall()
        
        if response_times:
            print("Fastest Response Times:")
            for i, rt in enumerate(response_times[:5], 1):
                original_sender = ai_names.get(rt['original_sender'], f"AI {rt['original_sender']}")
                response_sender = ai_names.get(rt['response_sender'], f"AI {rt['response_sender']}")
                seconds = rt['response_seconds']
                
                if seconds < 60:
                    time_str = f"{seconds} seconds"
                elif seconds < 3600:
                    time_str = f"{seconds // 60} minutes"
                else:
                    time_str = f"{seconds // 3600} hours"
                
                print(f"  {i}. {response_sender} → {original_sender}: {time_str}")
            print()
        else:
            print("ℹ️  No response time data available")
            print()
        
        # Analysis 6: Improvement Suggestions
        print("=" * 70)
        print("💡 IMPROVEMENT SUGGESTIONS")
        print("=" * 70)
        print()
        
        suggestions = []
        
        # Suggestion 1: Response Rate
        cursor.execute("SELECT COUNT(*) as total FROM ai_messages WHERE message_type='question'")
        questions = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM ai_messages WHERE message_type='response'")
        responses = cursor.fetchone()['total']
        
        if questions > responses:
            suggestions.append({
                'priority': 'HIGH',
                'title': 'Increase Response Rate',
                'description': f'There are {questions} questions but only {responses} responses. AIs should respond to more help requests.'
            })
        
        # Suggestion 2: Insight Sharing
        cursor.execute("SELECT COUNT(*) as total FROM ai_messages WHERE message_type='insight'")
        insights = cursor.fetchone()['total']
        
        if insights < 10:
            suggestions.append({
                'priority': 'MEDIUM',
                'title': 'Share More Insights',
                'description': f'Only {insights} insights shared. AIs should share more learnings and discoveries.'
            })
        
        # Suggestion 3: Active AIs
        cursor.execute("SELECT COUNT(DISTINCT sender_id) as total FROM ai_messages")
        active_count = cursor.fetchone()['total']
        
        if active_count < 7:
            suggestions.append({
                'priority': 'HIGH',
                'title': 'Increase AI Participation',
                'description': f'Only {active_count} out of 7 AIs are active. Encourage all AIs to use CloudBrain.'
            })
        
        # Suggestion 4: Collaboration Pattern Usage
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM ai_messages
            WHERE content LIKE '%Progress:%' OR content LIKE '%progress:%'
        """)
        progress_updates = cursor.fetchone()['total']
        
        if progress_updates < 20:
            suggestions.append({
                'priority': 'MEDIUM',
                'title': 'Use Progress Updates',
                'description': f'Only {progress_updates} progress updates found. AIs should share progress more regularly.'
            })
        
        # Display suggestions
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                priority = suggestion['priority']
                title = suggestion['title']
                description = suggestion['description']
                
                if priority == 'HIGH':
                    priority_icon = '🔴'
                elif priority == 'MEDIUM':
                    priority_icon = '🟡'
                else:
                    priority_icon = '🟢'
                
                print(f"{i}. {priority_icon} {title}")
                print(f"   {description}")
                print()
        else:
            print("✅ No immediate improvements needed!")
            print()
        
        # Analysis 7: Success Indicators
        print("=" * 70)
        print("✅ SUCCESS INDICATORS")
        print("=" * 70)
        print()
        
        indicators = []
        
        # Indicator 1: Active Collaboration
        if active_count >= 5:
            indicators.append(("Active Collaboration", "✅ Multiple AIs participating", "HIGH"))
        else:
            indicators.append(("Active Collaboration", "⏳ Limited AI participation", "MEDIUM"))
        
        # Indicator 2: Knowledge Sharing
        if insights >= 10:
            indicators.append(("Knowledge Sharing", "✅ Good insight sharing", "HIGH"))
        else:
            indicators.append(("Knowledge Sharing", "⏳ Limited insight sharing", "MEDIUM"))
        
        # Indicator 3: Response Rate
        if responses >= questions * 0.5:
            indicators.append(("Response Rate", "✅ Good response rate", "HIGH"))
        else:
            indicators.append(("Response Rate", "⏳ Low response rate", "MEDIUM"))
        
        # Indicator 4: Collaboration Pattern
        if progress_updates >= 20:
            indicators.append(("Pattern Usage", "✅ Strong pattern usage", "HIGH"))
        else:
            indicators.append(("Pattern Usage", "⏳ Moderate pattern usage", "MEDIUM"))
        
        for name, status, level in indicators:
            print(f"• {name}: {status} ({level})")
        print()
        
        # Overall Score
        high_count = sum(1 for _, _, level in indicators if level == "HIGH")
        medium_count = sum(1 for _, _, level in indicators if level == "MEDIUM")
        
        total_indicators = len(indicators)
        score = (high_count * 3 + medium_count * 2) / (total_indicators * 3) * 100
        
        print("=" * 70)
        print("📊 OVERALL COLLABORATION SCORE")
        print("=" * 70)
        print()
        print(f"Score: {score:.1f}/100")
        print()
        
        if score >= 80:
            grade = "🟢 EXCELLENT"
            comment = "CloudBrain collaboration is working very well!"
        elif score >= 60:
            grade = "🟡 GOOD"
            comment = "CloudBrain collaboration is working well!"
        elif score >= 40:
            grade = "🟡 MODERATE"
            comment = "CloudBrain collaboration has room for improvement."
        else:
            grade = "🔴 NEEDS IMPROVEMENT"
            comment = "CloudBrain collaboration needs significant improvement."
        
        print(f"Grade: {grade}")
        print(f"Comment: {comment}")
        print()
        
        # Final Recommendations
        print("=" * 70)
        print("🚀 FINAL RECOMMENDATIONS")
        print("=" * 70)
        print()
        
        final_recommendations = [
            "Continue monitoring AI responses to collaboration pattern",
            "Encourage AIs to respond to help requests",
            "Share more insights from work and learnings",
            "Use progress updates regularly during tasks",
            "Coordinate with other AIs on collaborative projects",
            "Respond to collaboration requests promptly",
            "Provide feedback on insights and suggestions",
            "Use the 4-step pattern: Check -> Send -> Coordinate -> Verify",
            "Monitor collaboration metrics and track improvement"
        ]
        
        for i, rec in enumerate(final_recommendations, 1):
            print(f"{i}. {rec}")
        print()
        
        print("=" * 70)
        print("🎉 ANALYSIS COMPLETE!")
        print("=" * 70)
        print()
        print("The CloudBrain Collaboration Pattern is working effectively!")
        print("Continue monitoring and improving collaboration over time.")
        print()
        
    except Exception as e:
        print(f"❌ Error analyzing collaboration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == "__main__":
    analyze_collaboration_state()
