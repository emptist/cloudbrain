#!/usr/bin/env python3
"""
Simple message watcher for AI-to-AI communication via temp_mbox

Watches temp_mbox directory for new messages and notifies AI when they arrive.
"""

import os
import time
from pathlib import Path
from datetime import datetime

class MessageWatcher:
    """Watch temp_mbox directory for new messages"""
    
    def __init__(self, ai_name: str, mbox_path: str = "temp_mbox"):
        self.ai_name = ai_name
        self.mbox_path = Path(mbox_path)
        self.seen_messages = set()
        self.running = True
        
        # Initialize with existing messages
        self._scan_existing_messages()
    
    def _scan_existing_messages(self):
        """Scan for existing messages on startup"""
        if not self.mbox_path.exists():
            print(f"⚠️  temp_mbox directory not found: {self.mbox_path}")
            return
        
        for msg_file in self.mbox_path.glob("message_*.md"):
            self.seen_messages.add(msg_file.name)
        
        print(f"📂 Scanned {len(self.seen_messages)} existing messages")
    
    def _parse_message(self, msg_file: Path) -> dict:
        """Parse message file to extract metadata"""
        try:
            with open(msg_file, 'r') as f:
                content = f.read()
            
            # Simple parsing
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
                    # End of metadata, start of body
                    body_start = i + 1
                    break
            
            metadata['body'] = '\n'.join(lines[body_start:])
            metadata['file'] = msg_file.name
            
            return metadata
        except Exception as e:
            print(f"❌ Error parsing {msg_file.name}: {e}")
            return None
    
    def _is_message_for_me(self, metadata: dict) -> bool:
        """Check if message is for this AI"""
        to_ai = metadata.get('to', '').lower()
        return self.ai_name.lower() in to_ai
    
    def _display_message(self, metadata: dict):
        """Display new message"""
        print("\n" + "=" * 70)
        print(f"📬 NEW MESSAGE FOR {self.ai_name.upper()}")
        print("=" * 70)
        print(f"👤 From:    {metadata.get('from', 'Unknown')}")
        print(f"📅 Date:    {metadata.get('date', 'Unknown')}")
        print(f"📋 Topic:   {metadata.get('topic', 'No topic')}")
        print(f"📁 File:    {metadata.get('file', 'Unknown')}")
        print("=" * 70)
        print(metadata.get('body', ''))
        print("=" * 70)
        print()
    
    def watch(self, interval: int = 5):
        """Watch for new messages"""
        print(f"\n👀 {self.ai_name} is watching for new messages...")
        print(f"📂 Watching: {self.mbox_path.absolute()}")
        print(f"⏱️  Check interval: {interval} seconds")
        print(f"🔍 Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                # Check for new messages
                if self.mbox_path.exists():
                    for msg_file in self.mbox_path.glob("message_*.md"):
                        if msg_file.name not in self.seen_messages:
                            # New message found!
                            print(f"\n✨ New message detected: {msg_file.name}")
                            
                            metadata = self._parse_message(msg_file)
                            if metadata and self._is_message_for_me(metadata):
                                self._display_message(metadata)
                            
                            self.seen_messages.add(msg_file.name)
                
                # Wait before next check
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n👋 {self.ai_name} stopped watching messages")
            print(f"📊 Total messages seen: {len(self.seen_messages)}")
    
    def stop(self):
        """Stop watching"""
        self.running = False


def main():
    """Main entry point"""
    import sys
    
    # Get AI name from command line
    if len(sys.argv) < 2:
        print("Usage: python watch_messages.py <AI_NAME> [MBOX_PATH]")
        print("\nExample:")
        print("  python watch_messages.py GLM-4.7")
        print("  python watch_messages.py MiniMax-2.1 temp_mbox")
        sys.exit(1)
    
    ai_name = sys.argv[1]
    mbox_path = sys.argv[2] if len(sys.argv) > 2 else "temp_mbox"
    
    # Create watcher
    watcher = MessageWatcher(ai_name, mbox_path)
    
    # Start watching
    watcher.watch()


if __name__ == "__main__":
    main()