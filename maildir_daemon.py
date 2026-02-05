#!/usr/bin/env python3
"""
📬 Maildir Daemon - Independent Message Watcher

This daemon runs independently of autonomous agents and watches for new messages
in all AI mailboxes. It ensures messages are delivered even when agents are offline.

Usage:
    python maildir_daemon.py [--maildir-path PATH] [--interval SECONDS]

Features:
    - Watches all AI mailboxes independently
    - Logs new messages to a central log
    - Can trigger agent wake-up (optional)
    - Persists messages for offline AIs
    - Runs as a background daemon process
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Set


class MaildirDaemon:
    """Independent daemon for watching Maildir messages"""
    
    def __init__(self, maildir_base: Path, interval: int = 5):
        self.maildir_base = maildir_base
        self.interval = interval
        self.seen_messages: Dict[str, Set[str]] = {}
        self.running = False
        self.log_file = maildir_base / "daemon.log"
        
    def _get_ai_mailboxes(self) -> Dict[str, Path]:
        """Get all AI mailboxes"""
        mailboxes = {}
        if self.maildir_base.exists():
            for ai_dir in self.maildir_base.iterdir():
                if ai_dir.is_dir() and not ai_dir.name.startswith('.'):
                    mailboxes[ai_dir.name] = ai_dir
        return mailboxes
    
    def _parse_maildir_message(self, msg_file: Path) -> dict:
        """Parse Maildir message file"""
        try:
            with open(msg_file, 'r') as f:
                content = f.read()
            
            metadata = {}
            lines = content.split('\n')
            in_headers = True
            
            for line in lines:
                if in_headers:
                    if line.startswith('From:'):
                        metadata['from'] = line.replace('From:', '').strip()
                    elif line.startswith('To:'):
                        metadata['to'] = line.replace('To:', '').strip()
                    elif line.startswith('Date:'):
                        metadata['date'] = line.replace('Date:', '').strip()
                    elif line.startswith('Subject:'):
                        metadata['subject'] = line.replace('Subject:', '').strip()
                    elif line.strip() == '':
                        in_headers = False
                else:
                    if 'body' not in metadata:
                        metadata['body'] = ''
                    metadata['body'] += line + '\n'
            
            metadata['file'] = msg_file.name
            metadata['path'] = str(msg_file)
            metadata['ai'] = msg_file.parent.parent.name
            
            if 'body' in metadata:
                metadata['body'] = metadata['body'].strip()
            
            return metadata
        except Exception as e:
            self._log(f"❌ Error parsing {msg_file.name}: {e}")
            return None
    
    def _log(self, message: str):
        """Log message to daemon log file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        print(log_entry, end='')
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def _scan_new_messages(self, ai_name: str, ai_mailbox: Path):
        """Scan for new messages in AI's mailbox"""
        new_dir = ai_mailbox / 'new'
        cur_dir = ai_mailbox / 'cur'
        
        if not new_dir.exists():
            return []
        
        new_messages = []
        
        for msg_file in new_dir.glob("*"):
            if not msg_file.is_file():
                continue
            
            if ai_name not in self.seen_messages:
                self.seen_messages[ai_name] = set()
            
            if msg_file.name in self.seen_messages[ai_name]:
                continue
            
            metadata = self._parse_maildir_message(msg_file)
            if metadata:
                new_messages.append(metadata)
                self.seen_messages[ai_name].add(msg_file.name)
                
                self._log(f"📬 New message for {ai_name}: {msg_file.name}")
                self._log(f"   From: {metadata.get('from', 'Unknown')}")
                self._log(f"   Subject: {metadata.get('subject', 'No subject')}")
                
                # Create trigger file to wake up agent
                self._create_trigger_file(ai_name, metadata)
                
                # Move to cur/ (mark as processed)
                if cur_dir.exists():
                    cur_path = cur_dir / msg_file.name
                    try:
                        msg_file.rename(cur_path)
                        self._log(f"   ✅ Moved to cur/")
                    except Exception as e:
                        self._log(f"   ⚠️  Could not move to cur/: {e}")
        
        return new_messages
    
    def _create_trigger_file(self, ai_name: str, metadata: dict):
        """Create trigger file to wake up agent"""
        try:
            trigger_file = self.maildir_base / ai_name / "NEW_MESSAGE_TRIGGER"
            
            with open(trigger_file, 'w') as f:
                f.write(f"TRIGGER: New message received\n")
                f.write(f"From: {metadata.get('from', 'Unknown')}\n")
                f.write(f"Subject: {metadata.get('subject', 'No subject')}\n")
                f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            self._log(f"   🔔 Trigger file created for {ai_name}")
            
            # Start agent process
            self._start_agent_process(ai_name)
            
        except Exception as e:
            self._log(f"   ❌ Error creating trigger file: {e}")
    
    def _start_agent_process(self, ai_name: str):
        """Start agent process for AI"""
        try:
            # Check if agent is already running
            agent_script = Path(__file__).parent / "autonomous_ai_agent.py"
            
            # Start agent process
            self._log(f"   🚀 Starting agent process for {ai_name}")
            
            # Run agent in background
            process = subprocess.Popen(
                [sys.executable, str(agent_script), ai_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(agent_script.parent)
            )
            
            self._log(f"   ✅ Agent process started (PID: {process.pid})")
            
        except Exception as e:
            self._log(f"   ❌ Error starting agent process: {e}")
    
    def _initialize_seen_messages(self):
        """Initialize with existing messages (don't process on startup)"""
        self._log("📂 Scanning existing messages...")
        
        mailboxes = self._get_ai_mailboxes()
        total_seen = 0
        
        for ai_name, ai_mailbox in mailboxes.items():
            new_dir = ai_mailbox / 'new'
            cur_dir = ai_mailbox / 'cur'
            
            if ai_name not in self.seen_messages:
                self.seen_messages[ai_name] = set()
            
            if new_dir.exists():
                for msg_file in new_dir.glob("*"):
                    if msg_file.is_file():
                        self.seen_messages[ai_name].add(msg_file.name)
                        total_seen += 1
            
            if cur_dir.exists():
                for msg_file in cur_dir.glob("*"):
                    if msg_file.is_file():
                        self.seen_messages[ai_name].add(msg_file.name)
                        total_seen += 1
        
        self._log(f"📂 Scanned {total_seen} existing messages across {len(mailboxes)} AIs")
    
    def run(self):
        """Run the daemon"""
        self.running = True
        self._log("=" * 70)
        self._log("🚀 Maildir Daemon Started")
        self._log(f"📂 Maildir path: {self.maildir_base.absolute()}")
        self._log(f"⏱️  Check interval: {self.interval} seconds")
        self._log("=" * 70)
        
        # Initialize with existing messages
        self._initialize_seen_messages()
        
        # Main loop
        while self.running:
            try:
                mailboxes = self._get_ai_mailboxes()
                
                if not mailboxes:
                    self._log("⚠️  No mailboxes found")
                else:
                    for ai_name, ai_mailbox in mailboxes.items():
                        new_messages = self._scan_new_messages(ai_name, ai_mailbox)
                        
                        if new_messages:
                            self._log(f"📨 {len(new_messages)} new message(s) for {ai_name}")
                
                # Wait before next check
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                self._log("\n🛑 Received interrupt signal")
                self.running = False
                break
            except Exception as e:
                self._log(f"❌ Error in main loop: {e}")
                time.sleep(10)
        
        self._log("=" * 70)
        self._log("🛑 Maildir Daemon Stopped")
        self._log("=" * 70)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Maildir Daemon - Independent Message Watcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python maildir_daemon.py
  python maildir_daemon.py --maildir-path /path/to/mailboxes --interval 10
        """
    )
    
    parser.add_argument(
        '--maildir-path',
        type=str,
        default='/Users/jk/gits/hub/cloudbrain/mailboxes',
        help='Path to mailboxes directory (default: /Users/jk/gits/hub/cloudbrain/mailboxes)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Check interval in seconds (default: 5)'
    )
    
    args = parser.parse_args()
    
    maildir_base = Path(args.maildir_path)
    
    if not maildir_base.exists():
        print(f"❌ Maildir path does not exist: {maildir_base}")
        sys.exit(1)
    
    daemon = MaildirDaemon(maildir_base, args.interval)
    daemon.run()


if __name__ == '__main__':
    main()
