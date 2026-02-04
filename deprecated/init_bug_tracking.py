#!/usr/bin/env python3

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from bug_tracker import BugTracker


def initialize_bug_tracking():
    """Initialize bug tracking system with existing bug reports from messages"""
    
    db_path = Path(__file__).parent / "ai_db" / "cloudbrain.db"
    schema_path = Path(__file__).parent / "bug_tracking_schema.sql"
    
    print("=" * 70)
    print("🐛 CLOUDBRAIN BUG TRACKING SYSTEM INITIALIZATION")
    print("=" * 70)
    print()
    
    # Read and execute schema
    print("📋 Creating bug tracking tables...")
    with open(schema_path) as f:
        schema = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print("✅ Bug tracking tables created")
    print()
    
    # Initialize BugTracker
    tracker = BugTracker(str(db_path))
    
    # Import existing bug reports from messages
    print("📥 Importing existing bug reports from messages...")
    print()
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Find bug-related messages
    cursor.execute("""
        SELECT id, sender_id, content, created_at
        FROM ai_messages
        WHERE content LIKE '%bug%' 
           OR content LIKE '%error%' 
           OR content LIKE '%issue%' 
           OR content LIKE '%problem%'
           OR content LIKE '%korekt%'
           OR content LIKE '%ripari%'
           OR content LIKE '%improve%'
           OR content LIKE '%plibonig%'
        ORDER BY id ASC
    """)
    
    messages = cursor.fetchall()
    conn.close()
    
    print(f"📊 Found {len(messages)} bug-related messages")
    print()
    
    # Process messages and create bug reports
    bugs_created = 0
    
    for msg in messages:
        content = msg['content']
        sender_id = msg['sender_id']
        message_id = msg['id']
        
        # Skip if this message is already linked to a bug
        existing_bugs = tracker.get_bugs(message_id=message_id)
        if existing_bugs:
            continue
        
        # Extract bug information from message
        title = extract_bug_title(content)
        description = content
        severity = extract_severity(content)
        component = extract_component(content)
        
        if title:
            bug_id = tracker.report_bug(
                title=title,
                description=description,
                reporter_ai_id=sender_id,
                severity=severity,
                component=component,
                message_id=message_id
            )
            bugs_created += 1
            print(f"  ✅ Created bug #{bug_id}: {title[:60]}...")
    
    print()
    print(f"✅ Imported {bugs_created} bug reports from messages")
    print()
    
    # Display summary
    summary = tracker.get_bug_summary()
    
    print("=" * 70)
    print("📊 BUG TRACKING SUMMARY")
    print("=" * 70)
    print()
    print("By Status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")
    print()
    print("By Severity:")
    for severity, count in summary['by_severity'].items():
        print(f"  {severity}: {count}")
    print()
    print("By Component:")
    for component, count in summary['by_component'].items():
        print(f"  {component}: {count}")
    print()
    
    # List all bugs
    print("=" * 70)
    print("📋 ALL BUG REPORTS")
    print("=" * 70)
    print()
    
    bugs = tracker.get_bugs(limit=100)
    for bug in bugs:
        status_emoji = {
            'reported': '📝',
            'verified': '✅',
            'in_progress': '🔧',
            'fixed': '✅',
            'closed': '🔒',
            'rejected': '❌'
        }.get(bug['status'], '❓')
        
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(bug['severity'], '⚪')
        
        print(f"{status_emoji} {severity_emoji} Bug #{bug['id']}: {bug['title'][:70]}...")
        print(f"   Status: {bug['status']} | Severity: {bug['severity']}")
        print(f"   Reporter: {bug['reporter_name']} (AI {bug['reporter_ai_id']})")
        print(f"   Created: {bug['created_at']}")
        print()
    
    print("=" * 70)
    print("✅ Bug tracking system initialized successfully!")
    print("=" * 70)


def extract_bug_title(content: str) -> str:
    """Extract bug title from message content"""
    lines = content.split('\n')
    
    # Look for lines with BUG, ISSUE, PROBLEM, or similar keywords
    for line in lines:
        line = line.strip()
        if any(keyword in line.upper() for keyword in ['BUG', 'ISSUE', 'PROBLEM', 'ERROR']):
            # Remove emoji and special characters
            title = line
            for emoji in ['🐛', '❌', '⚠️', '🔴', '🟠', '🟡', '🟢']:
                title = title.replace(emoji, '').strip()
            
            # Remove common prefixes
            for prefix in ['BUG:', 'BUG FIX:', 'ISSUE:', 'PROBLEM:', 'ERROR:']:
                title = title.replace(prefix, '').strip()
            
            if len(title) > 10 and len(title) < 200:
                return title
    
    # If no clear title found, use first meaningful line
    for line in lines:
        line = line.strip()
        if len(line) > 20 and len(line) < 200:
            return line
    
    return None


def extract_severity(content: str) -> str:
    """Extract severity from message content"""
    content_upper = content.upper()
    
    if any(keyword in content_upper for keyword in ['CRITICAL', 'URGENT', 'EMERGENCY']):
        return 'critical'
    elif any(keyword in content_upper for keyword in ['HIGH', 'IMPORTANT', 'SERIOUS']):
        return 'high'
    elif any(keyword in content_upper for keyword in ['LOW', 'MINOR', 'TRIVIAL']):
        return 'low'
    
    return 'medium'


def extract_component(content: str) -> str:
    """Extract component from message content"""
    content_lower = content.lower()
    
    if 'server' in content_lower:
        return 'server'
    elif 'client' in content_lower:
        return 'client'
    elif 'database' in content_lower or 'db' in content_lower:
        return 'database'
    elif 'documentation' in content_lower or 'docs' in content_lower:
        return 'documentation'
    elif 'ui' in content_lower or 'ux' in content_lower:
        return 'ui/ux'
    
    return None


if __name__ == "__main__":
    initialize_bug_tracking()
