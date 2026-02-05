#!/usr/bin/env python3
"""
Simple message sender for AI-to-AI communication via temp_mbox

Send messages to other AIs using disk-based mailbox.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def send_message(from_ai: str, to_ai: str, topic: str, body: str, mbox_path: str = "temp_mbox"):
    """
    Send a message to another AI
    
    Args:
        from_ai: Your AI name
        to_ai: Target AI name
        topic: Message topic/subject
        body: Message body
        mbox_path: Path to temp_mbox directory
    """
    # Ensure mbox directory exists
    mbox_dir = Path(mbox_path)
    mbox_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate message filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_from = from_ai.replace(' ', '_').replace('.', '').replace('-', '')
    safe_to = to_ai.replace(' ', '_').replace('.', '').replace('-', '')
    filename = f"message_{timestamp}_{safe_from}_to_{safe_to}.md"
    filepath = mbox_dir / filename
    
    # Create message content
    message_content = f"""# From: {from_ai}
# To: {to_ai}
# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Topic: {topic}

{body}

---
# Response (if any)
[Waiting for response...]
"""
    
    # Write message file
    with open(filepath, 'w') as f:
        f.write(message_content)
    
    print(f"✅ Message sent successfully!")
    print(f"📁 File: {filepath}")
    print(f"👤 From: {from_ai}")
    print(f"👤 To:   {to_ai}")
    print(f"📋 Topic: {topic}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("💡 Tip: The recipient can watch for messages using:")
    print(f"   python watch_messages.py {to_ai}")


def main():
    """Main entry point"""
    if len(sys.argv) < 5:
        print("Usage: python send_message.py <FROM_AI> <TO_AI> <TOPIC> <BODY> [MBOX_PATH]")
        print("\nExample:")
        print('  python send_message.py "GLM-4.7" "MiniMax-2.1" "Collaboration" "Let\'s work together!"')
        print('  python send_message.py "MiniMax-2.1" "GLM-4.7" "Response" "Great idea!" temp_mbox')
        print("\nOr use interactive mode:")
        print("  python send_message.py")
        sys.exit(1)
    
    # Check if interactive mode
    if len(sys.argv) == 1:
        # Interactive mode
        print("📬 AI-to-AI Message Sender (Interactive Mode)")
        print("=" * 70)
        
        from_ai = input("Your AI name: ").strip()
        to_ai = input("Recipient AI name: ").strip()
        topic = input("Topic: ").strip()
        print("\nEnter your message (Ctrl+D or Ctrl+Z to finish):")
        
        body_lines = []
        try:
            while True:
                line = input()
                body_lines.append(line)
        except EOFError:
            pass
        
        body = '\n'.join(body_lines)
        mbox_path = "temp_mbox"
        
    else:
        # Command line mode
        from_ai = sys.argv[1]
        to_ai = sys.argv[2]
        topic = sys.argv[3]
        body = sys.argv[4]
        mbox_path = sys.argv[5] if len(sys.argv) > 5 else "temp_mbox"
    
    # Send message
    send_message(from_ai, to_ai, topic, body, mbox_path)


if __name__ == "__main__":
    main()