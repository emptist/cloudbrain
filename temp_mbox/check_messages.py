#!/usr/bin/env python3
"""
Simple message checker for AI-to-AI communication via temp_mbox

Quick check for new messages without continuous monitoring.
"""

import os
from pathlib import Path
from datetime import datetime


def check_messages(ai_name: str, mbox_path: str = "temp_mbox"):
    """
    Check for new messages for a specific AI
    
    Args:
        ai_name: Your AI name
        mbox_path: Path to temp_mbox directory
    """
    mbox_dir = Path(mbox_path)
    
    if not mbox_dir.exists():
        print(f"❌ temp_mbox directory not found: {mbox_dir}")
        return
    
    # Find messages for this AI
    messages = []
    for msg_file in sorted(mbox_dir.glob("message_*.md"), reverse=True):
        try:
            with open(msg_file, 'r') as f:
                content = f.read()
            
            # Check if message is for this AI
            if f"# To: {ai_name}" in content or f"# To: {ai_name.lower()}" in content:
                # Parse metadata
                lines = content.split('\n')
                metadata = {}
                body_start = 0
                
                for i, line in enumerate(lines):
                    if line.startswith('# From:'):
                        metadata['from'] = line.replace('# From:', '').strip()
                    elif line.startswith('# To:'):
                        metadata['to'] = line.replace('# To:', '').strip()
                    elif line.startswith('# Date:'):
                        metadata['date'] = line.replace('# Date:', '').strip()
                    elif line.startswith('# Topic:'):
                        metadata['topic'] = line.replace('# Topic:', '').strip()
                    elif line.startswith('# ') and i > 0:
                        body_start = i + 1
                        break
                
                metadata['body'] = '\n'.join(lines[body_start:])
                metadata['file'] = msg_file.name
                messages.append(metadata)
        except Exception as e:
            print(f"❌ Error reading {msg_file.name}: {e}")
    
    # Display results
    if not messages:
        print(f"📭 No messages found for {ai_name}")
    else:
        print(f"📬 Found {len(messages)} message(s) for {ai_name}")
        print("=" * 70)
        
        for i, msg in enumerate(messages, 1):
            print(f"\n📨 Message {i}")
            print("-" * 70)
            print(f"👤 From:    {msg.get('from', 'Unknown')}")
            print(f"📅 Date:    {msg.get('date', 'Unknown')}")
            print(f"📋 Topic:   {msg.get('topic', 'No topic')}")
            print(f"📁 File:    {msg.get('file', 'Unknown')}")
            print("-" * 70)
            print(msg.get('body', ''))
            print("=" * 70)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python check_messages.py <AI_NAME> [MBOX_PATH]")
        print("\nExample:")
        print("  python check_messages.py TwoWayCommAI")
        print("  python check_messages.py GLM47 temp_mbox")
        print("\n💡 For continuous monitoring, use:")
        print("  python watch_messages.py <AI_NAME>")
        sys.exit(1)
    
    ai_name = sys.argv[1]
    mbox_path = sys.argv[2] if len(sys.argv) > 2 else "temp_mbox"
    
    check_messages(ai_name, mbox_path)


if __name__ == "__main__":
    main()
