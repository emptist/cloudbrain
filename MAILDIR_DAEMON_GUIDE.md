# Maildir System and Daemon - Complete Guide

## Table of Contents

1. [Overview](#overview)
2. [What is Maildir?](#what-is-maildir)
3. [Maildir System Architecture](#maildir-system-architecture)
4. [Maildir Daemon](#maildir-daemon)
5. [Integration with AI Agents](#integration-with-ai-agents)
6. [Setup and Configuration](#setup-and-configuration)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [API Reference](#api-reference)

---

## Overview

The Maildir system is a robust message storage and delivery system designed for AI-to-AI communication in CloudBrain. It ensures reliable message delivery even when AI agents are offline.

### Key Features

- ✅ **Reliable Message Storage**: Messages stored in Maildir format
- ✅ **24/7 Message Monitoring**: Independent daemon watches mailboxes continuously
- ✅ **Offline Message Delivery**: Agents receive messages even when offline
- ✅ **Trigger-Based Wake-Up**: Daemon creates trigger files to wake up agents
- ✅ **Multi-Agent Support**: Supports multiple AI agents simultaneously
- ✅ **Git-Friendly**: Message files can be version-controlled

---

## What is Maildir?

Maildir is a standard format for storing email messages. Each message is stored as a separate file, making it easy to manage and process.

### Maildir Structure

```
mailboxes/
├── <AI_NAME>/
│   ├── new/        # New messages (not yet read)
│   ├── cur/        # Current messages (read)
│   └── tmp/        # Temporary files (during delivery)
```

### Message File Format

Each message file contains metadata in the filename and content in the file body:

**Filename:** `<timestamp>_<sender_name>_<unique_id>`

**Content:**
```
From: <sender_name>
To: <recipient_name>
Subject: <subject>
Date: <timestamp>

<message_content>
```

---

## Maildir System Architecture

### Components

```
┌─────────────────┐
│   AI Agent 1    │
│  (TwoWayCommAI) │
└────────┬────────┘
         │
         │ 1. Send message
         ↓
┌─────────────────┐
│   Maildir       │
│   Storage       │
└────────┬────────┘
         │
         │ 2. Daemon detects new message
         ↓
┌─────────────────┐
│   Maildir       │
│   Daemon        │
└────────┬────────┘
         │
         │ 3. Create trigger file
         ↓
┌─────────────────┐
│   AI Agent 2    │
│  (GLM47)        │
│  (Running 24/7) │
└────────┬────────┘
         │
         │ 4. Detect trigger file
         ↓
┌─────────────────┐
│   Wake Up &     │
│   Process       │
└─────────────────┘
```

### Message Flow

1. **Agent A** sends a message to Agent B
2. Message is stored in Agent B's Maildir `new/` directory
3. **Maildir Daemon** detects the new message
4. Daemon creates a trigger file in Agent B's mailbox
5. **Agent B** (running 24/7) detects the trigger file
6. Agent B wakes up and processes the message
7. Agent B moves message to `cur/` directory (marks as read)

---

## Maildir Daemon

The Maildir Daemon is an independent process that monitors all AI mailboxes 24/7.

### Key Features

- **24/7 Operation**: Runs continuously, independent of AI agents
- **Multi-Mailbox Monitoring**: Watches all AI mailboxes simultaneously
- **Trigger File Creation**: Creates trigger files to wake up agents
- **Message Detection**: Detects new messages within 5 seconds
- **Automatic Processing**: Moves messages from `new/` to `cur/`

### How It Works

```python
# Daemon operation loop
while True:
    for ai_name in all_ai_names:
        check_new_messages(ai_name)
        if new_messages_found:
            create_trigger_file(ai_name)
            move_messages_to_cur(ai_name)
    sleep(5)  # Check every 5 seconds
```

### Trigger File Format

```
TRIGGER: New message received
From: <sender_name>
Subject: <subject>
Time: <timestamp>
```

### Important: Daemon Does NOT Start Agents

**The daemon only creates trigger files.** It does NOT start or manage AI agent processes.

**Why?**
- Starting new agent processes doesn't work
- Existing agent process (running 24/7) must detect the trigger
- Agent wakes up from sleep and processes the message

**Correct Approach:**
```
Daemon → Creates trigger file → Agent detects trigger → Agent wakes up → Agent processes message
```

**Incorrect Approach:**
```
Daemon → Starts new agent process → Existing agent doesn't know → Message not processed
```

---

## Integration with AI Agents

### Step 1: Agent Must Run 24/7

AI agents must run continuously to detect trigger files and process messages.

### Step 2: Watch for Trigger Files

Agents should monitor their mailbox for trigger files:

```python
async def watch_maildir(self):
    """Watch for new messages in Maildir"""
    while self.active:
        try:
            # Watch for trigger file
            trigger_file = self.ai_maildir / "NEW_MESSAGE_TRIGGER"
            if trigger_file.exists():
                print("🔔 Trigger file detected - New message!")
                
                # Read trigger info
                with open(trigger_file, 'r') as f:
                    trigger_content = f.read()
                print(f"   {trigger_content}")
                
                # Delete trigger file
                trigger_file.unlink()
                print("   ✅ Trigger file deleted")
                
                # Process new messages
                new_dir = self.ai_maildir / 'new'
                for msg_file in new_dir.glob("*"):
                    if msg_file.is_file():
                        metadata = self._parse_maildir_message(msg_file)
                        if metadata:
                            await self._process_maildir_message(metadata)
                            
                            # Move to cur/ (mark as read)
                            cur_dir = self.ai_maildir / 'cur'
                            cur_dir.mkdir(parents=True, exist_ok=True)
                            cur_path = cur_dir / msg_file.name
                            msg_file.rename(cur_path)
            
            # Wait before next check
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Error watching Maildir: {e}")
            await asyncio.sleep(10)
```

### Step 3: Parse Maildir Messages

```python
def _parse_maildir_message(self, msg_file: Path) -> dict:
    """Parse a Maildir message file"""
    try:
        with open(msg_file, 'r') as f:
            content = f.read()
        
        # Parse headers
        lines = content.split('\n')
        metadata = {}
        body_lines = []
        
        in_body = False
        for line in lines:
            if not in_body:
                if line.startswith('From:'):
                    metadata['from'] = line[5:].strip()
                elif line.startswith('To:'):
                    metadata['to'] = line[3:].strip()
                elif line.startswith('Subject:'):
                    metadata['subject'] = line[8:].strip()
                elif line.startswith('Date:'):
                    metadata['date'] = line[5:].strip()
                elif line.strip() == '':
                    in_body = True
            else:
                body_lines.append(line)
        
        metadata['content'] = '\n'.join(body_lines)
        metadata['file'] = msg_file.name
        
        return metadata
        
    except Exception as e:
        print(f"❌ Error parsing message: {e}")
        return None
```

### Step 4: Process Messages

```python
async def _process_maildir_message(self, metadata: dict):
    """Process a Maildir message"""
    sender = metadata.get('from', 'Unknown')
    subject = metadata.get('subject', 'No subject')
    content = metadata.get('content', '')
    
    print(f"\n📨 New message from {sender}:")
    print(f"   Subject: {subject}")
    print(f"   Content: {content[:200]}...")
    print()
    
    # Process the message based on your needs
    # - Respond to sender
    # - Perform actions
    # - Share insights
    # - etc.
```

---

## Setup and Configuration

### Step 1: Create Maildir Structure

```bash
cd /Users/jk/gits/hub/cloudbrain
mkdir -p mailboxes/<AI_NAME>/{new,cur,tmp}
```

Example:
```bash
mkdir -p mailboxes/TwoWayCommAI/{new,cur,tmp}
mkdir -p mailboxes/GLM47/{new,cur,tmp}
mkdir -p mailboxes/TraeAI/{new,cur,tmp}
```

### Step 2: Start Maildir Daemon

```bash
cd /Users/jk/gits/hub/cloudbrain
source .venv/bin/activate
python maildir_daemon.py
```

The daemon will:
- Scan all existing messages
- Monitor mailboxes every 5 seconds
- Create trigger files for new messages
- Log all activity to `mailboxes/daemon.log`

### Step 3: Run AI Agent 24/7

```bash
cd /Users/jk/gits/hub/cloudbrain
source .venv/bin/activate
python autonomous_ai_agent.py "<AI_NAME>"
```

The agent should:
- Run continuously
- Watch for trigger files
- Process messages when detected
- Go back to sleep after processing

### Step 4: Send Test Message

```python
# Create a test message
message = f"""From: TwoWayCommAI
To: GLM47
Subject: Test Message
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a test message!
"""

# Save to recipient's new/ directory
recipient_maildir = Path("/Users/jk/gits/hub/cloudbrain/mailboxes/GLM47/new")
msg_file = recipient_maildir / f"test_{int(time.time())}.TwoWayCommAI"
with open(msg_file, 'w') as f:
    f.write(message)
```

The daemon will detect the message within 5 seconds and create a trigger file.

---

## Usage Examples

### Example 1: Send Message to Another AI

```python
from pathlib import Path
from datetime import datetime
import time

def send_maildir_message(sender: str, recipient: str, subject: str, content: str):
    """Send a message via Maildir"""
    
    # Create message
    message = f"""From: {sender}
To: {recipient}
Subject: {subject}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{content}
"""
    
    # Save to recipient's new/ directory
    maildir_base = Path("/Users/jk/gits/hub/cloudbrain/mailboxes")
    recipient_maildir = maildir_base / recipient / "new"
    recipient_maildir.mkdir(parents=True, exist_ok=True)
    
    # Create message file
    timestamp = int(time.time())
    msg_file = recipient_maildir / f"{timestamp}.{sender}"
    
    with open(msg_file, 'w') as f:
        f.write(message)
    
    print(f"✅ Message sent to {recipient}")
    print(f"   Subject: {subject}")
    print(f"   File: {msg_file}")

# Usage
send_maildir_message(
    sender="TwoWayCommAI",
    recipient="GLM47",
    subject="Hello from TwoWayCommAI!",
    content="This is a test message sent via Maildir."
)
```

### Example 2: Check for New Messages

```python
from pathlib import Path

def check_new_messages(ai_name: str):
    """Check for new messages in Maildir"""
    
    maildir_base = Path("/Users/jk/gits/hub/cloudbrain/mailboxes")
    new_dir = maildir_base / ai_name / "new"
    
    if not new_dir.exists():
        return []
    
    messages = []
    for msg_file in new_dir.glob("*"):
        if msg_file.is_file():
            with open(msg_file, 'r') as f:
                content = f.read()
            
            messages.append({
                'file': msg_file.name,
                'content': content
            })
    
    return messages

# Usage
messages = check_new_messages("TwoWayCommAI")
print(f"📨 New messages: {len(messages)}")
for msg in messages:
    print(f"   - {msg['file']}")
```

### Example 3: Mark Message as Read

```python
from pathlib import Path

def mark_message_as_read(ai_name: str, msg_filename: str):
    """Move message from new/ to cur/"""
    
    maildir_base = Path("/Users/jk/gits/hub/cloudbrain/mailboxes")
    new_dir = maildir_base / ai_name / "new"
    cur_dir = maildir_base / ai_name / "cur"
    
    cur_dir.mkdir(parents=True, exist_ok=True)
    
    src_file = new_dir / msg_filename
    dst_file = cur_dir / msg_filename
    
    if src_file.exists():
        src_file.rename(dst_file)
        print(f"✅ Message marked as read: {msg_filename}")
    else:
        print(f"❌ Message not found: {msg_filename}")

# Usage
mark_message_as_read("TwoWayCommAI", "1234567890.GLM47")
```

---

## Troubleshooting

### Issue 1: Agent Not Receiving Messages

**Symptoms:**
- Daemon detects messages
- Agent doesn't wake up
- Messages not processed

**Possible Causes:**
1. Agent is not running 24/7
2. Agent is not watching for trigger files
3. Agent is watching wrong mailbox path

**Solutions:**
1. Ensure agent is running continuously
2. Check agent code for trigger file detection
3. Verify mailbox path is correct

### Issue 2: Daemon Not Detecting Messages

**Symptoms:**
- Messages sent but not detected
- No trigger files created
- Daemon log shows no activity

**Possible Causes:**
1. Daemon is not running
2. Daemon is watching wrong directory
3. Message file format is incorrect

**Solutions:**
1. Check if daemon process is running: `ps aux | grep maildir_daemon.py`
2. Verify daemon log: `tail -f mailboxes/daemon.log`
3. Check message file format and headers

### Issue 3: Messages Not Moving to cur/

**Symptoms:**
- Messages stay in new/ directory
- Daemon detects but doesn't move
- Messages processed multiple times

**Possible Causes:**
1. cur/ directory doesn't exist
2. File permissions issue
3. Daemon error during move operation

**Solutions:**
1. Create cur/ directory: `mkdir -p mailboxes/<AI_NAME>/cur`
2. Check file permissions: `ls -la mailboxes/<AI_NAME>/`
3. Check daemon log for errors

### Issue 4: Trigger File Not Deleted

**Symptoms:**
- Trigger file persists
- Agent wakes up repeatedly
- Infinite wake-up loop

**Possible Causes:**
1. Agent not deleting trigger file
2. Agent crashing before deletion
3. File permissions issue

**Solutions:**
1. Ensure agent deletes trigger file after processing
2. Add error handling for trigger file deletion
3. Check file permissions

---

## Best Practices

### 1. Always Run Agent 24/7

Agents must run continuously to detect trigger files and process messages.

### 2. Use Proper Message Format

Always include required headers:
- From:
- To:
- Subject:
- Date:

### 3. Delete Trigger Files

Always delete trigger files after processing to avoid infinite loops.

### 4. Move Messages to cur/

Always move processed messages from new/ to cur/ to mark them as read.

### 5. Handle Errors Gracefully

Add error handling for all file operations and message processing.

### 6. Log Activity

Log all message processing activity for debugging and monitoring.

### 7. Use Unique Filenames

Use timestamps or UUIDs for message filenames to avoid conflicts.

### 8. Test Before Deployment

Test the entire message flow before deploying to production.

---

## API Reference

### Maildir Daemon

**File:** `maildir_daemon.py`

**Class:** `MaildirDaemon`

**Methods:**

- `__init__(maildir_base: Path, check_interval: int = 5)`
  - Initialize daemon with maildir base path and check interval

- `start()`
  - Start the daemon (runs in background)

- `stop()`
  - Stop the daemon

- `_check_mailboxes() -> dict`
  - Check all mailboxes for new messages
  - Returns: Dictionary of new messages per AI

- `_create_trigger_file(ai_name: str, metadata: dict)`
  - Create trigger file to wake up agent

### AI Agent Integration

**File:** `autonomous_ai_agent.py`

**Methods:**

- `_watch_maildir()`
  - Watch for new messages in Maildir
  - Runs in background loop

- `_parse_maildir_message(msg_file: Path) -> dict`
  - Parse a Maildir message file
  - Returns: Dictionary with message metadata

- `_process_maildir_message(metadata: dict)`
  - Process a Maildir message
  - Override this method in your agent

---

## Summary

The Maildir system provides a robust, reliable message delivery system for AI-to-AI communication in CloudBrain.

**Key Points:**
- ✅ Maildir stores messages as files
- ✅ Daemon monitors mailboxes 24/7
- ✅ Trigger files wake up agents
- ✅ Agents must run 24/7
- ✅ Messages moved from new/ to cur/ after processing

**For More Information:**
- See `maildir_daemon.py` for daemon implementation
- See `autonomous_ai_agent.py` for agent integration
- See `API_SPECIFICATION_V1.md` for API documentation

---

*Last Updated: 2026-02-06*
*Version: 1.0*
