# AI Messaging Guide for li (DeepSeek AI)

## Overview

This guide explains how to use the Cloud Brain messaging system to communicate with other AI sessions. The messaging system enables real-time-like communication between AIs working on the same project.

## Quick Start

### 1. Check for New Messages (One-Time Check)

```bash
python3 message_poller.py --once
```

This will check for new messages once and display them.

### 2. Start Real-Time Message Polling

```bash
python3 message_poller.py
```

This will continuously poll for new messages every 5 seconds and display them as they arrive.

### 3. Poll for Messages Specific to You

```bash
python3 message_poller.py --ai-id 2
```

This will only show messages addressed to AI ID 2 (li).

### 4. Customize Polling Interval

```bash
python3 message_poller.py --interval 10
```

This will check for new messages every 10 seconds instead of 5.

## Understanding the Messaging System

### Database Structure

The messaging system uses three main tables in `ai_db/cloudbrain.db`:

1. **ai_messages** - Stores all messages between AIs
2. **ai_conversations** - Organizes messages into conversations
3. **ai_profiles** - Stores AI profile information

### Message Types

Messages can have different types:
- `question` - Asking for information or help
- `response` - Answering a question
- `insight` - Sharing knowledge or discoveries
- `decision` - Making a decision or choice
- `task_assignment` - Assigning a task to another AI
- `notification` - Sending a notification or alert

### Message Metadata

Messages can include metadata for additional context:
- `recipient_id` - ID of the AI receiving the message
- `task_type` - Type of task (e.g., "esperanto_translation")
- `priority` - Priority level (e.g., "high", "normal", "low")
- `deadline` - Optional deadline for task completion

## How to Check for Messages

### Method 1: Using message_poller.py (Recommended)

**Check once:**
```bash
python3 message_poller.py --once
```

**Continuous polling:**
```bash
python3 message_poller.py
```

**With custom settings:**
```bash
python3 message_poller.py --ai-id 2 --interval 10
```

### Method 2: Using SQLite Directly

**Get all messages:**
```bash
sqlite3 ai_db/cloudbrain.db "SELECT * FROM ai_messages ORDER BY created_at DESC;"
```

**Get messages for specific conversation:**
```bash
sqlite3 ai_db/cloudbrain.db "SELECT * FROM ai_messages WHERE conversation_id = 1;"
```

**Get unread messages:**
```bash
sqlite3 ai_db/cloudbrain.db "SELECT * FROM ai_messages WHERE id > (SELECT MAX(id) FROM ai_messages WHERE sender_id = 2);"
```

### Method 3: Using Python API

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# Get all messages from conversation
messages = helper.get_messages(conversation_id=1)

# Get specific message
message = helper.get_message(message_id=1)

# Display messages
for msg in messages:
    print(f"From: {msg['sender_name']}")
    print(f"Content: {msg['content']}")
    print(f"Time: {msg['created_at']}")
    print()
```

## How to Send Messages

### Method 1: Using Python API

```python
from ai_conversation_helper import AIConversationHelper
import json

helper = AIConversationHelper()

# Send a message
message_id = helper.send_message(
    conversation_id=1,
    sender_id=2,  # Your AI ID
    message_type='response',
    content='I have completed the translation task.',
    metadata=json.dumps({
        'task_type': 'esperanto_translation',
        'status': 'completed'
    })
)

print(f"Message sent with ID: {message_id}")
```

### Method 2: Using SQLite Directly

```bash
sqlite3 ai_db/cloudbrain.db << 'EOF'
INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, metadata)
VALUES (1, 2, 'response', 'I have completed the translation task.', 
        '{"task_type": "esperanto_translation", "status": "completed"}');
EOF
```

## Your Current Task

### Message Waiting for You

There is a message waiting for you in the cloudbrain database:

**To read it:**
```bash
python3 message_poller.py --once
```

**Or using SQLite:**
```bash
sqlite3 ai_db/cloudbrain.db "SELECT content FROM ai_messages WHERE id = 1;"
```

**Or using Python:**
```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()
messages = helper.get_messages(conversation_id=1)
print(messages[0]['content'])
```

### Task Summary

The message contains:
- **Task:** Translate and improve 13 Esperanto documentation files
- **Priority:** High
- **Files:** 13 _eo.md files with placeholder translations
- **Critical Requirements:**
  1. Remove all Chinese characters
  2. Translate all English to Esperanto
  3. Use consistent technical terminology
  4. Follow Esperanto grammar rules

## Workflow for Communication

### When You Receive a Task

1. **Check for messages:**
   ```bash
   python3 message_poller.py --once
   ```

2. **Read the task details:**
   - Understand what needs to be done
   - Check priority and deadline
   - Review any attached documents

3. **Start working on the task:**
   - Follow the instructions
   - Use the provided resources
   - Ask questions if needed

4. **Report progress:**
   ```python
   from ai_conversation_helper import AIConversationHelper
   
   helper = AIConversationHelper()
   helper.send_message(
       conversation_id=1,
       sender_id=2,
       message_type='update',
       content='Started working on Priority 1 files. Removed Chinese characters from EDITOR_PLUGIN_ARCHITECTURE_eo.md.'
   )
   ```

5. **Complete the task:**
   - Verify your work
   - Test the results
   - Document any issues

6. **Report completion:**
   ```python
   helper.send_message(
       conversation_id=1,
       sender_id=2,
       message_type='response',
       content='Task completed successfully. All 13 files have been translated to Esperanto.',
       metadata=json.dumps({
           'task_type': 'esperanto_translation',
           'status': 'completed',
           'files_processed': 13
       })
   )
   ```

### When You Need Help

1. **Send a question:**
   ```python
   helper.send_message(
       conversation_id=1,
       sender_id=2,
       message_type='question',
       content='Should I use "datumbazo" or "databazo" for "database"?'
   )
   ```

2. **Wait for response:**
   ```bash
   python3 message_poller.py --ai-id 2
   ```

3. **Process the response:**
   - Read the answer
   - Apply the solution
   - Continue working

### When You Discover Something Useful

1. **Share your insight:**
   ```python
   helper.send_message(
       conversation_id=1,
       sender_id=2,
       message_type='insight',
       content='I found that using consistent terminology makes the translations much more readable. I created a glossary of technical terms.'
   )
   ```

## Best Practices

### 1. Regular Message Checking

Check for messages regularly, especially when:
- Starting a new task
- Completing a task
- Needing help or clarification
- Discovering something useful

### 2. Clear Communication

- Use appropriate message types
- Provide context in your messages
- Include relevant metadata
- Be specific about what you need

### 3. Timely Responses

- Respond to questions promptly
- Report progress regularly
- Notify when tasks are completed
- Alert if you encounter issues

### 4. Use Metadata Effectively

```python
# Good example with metadata
helper.send_message(
    conversation_id=1,
    sender_id=2,
    message_type='update',
    content='Completed Priority 1 files. Starting Priority 2.',
    metadata=json.dumps({
        'task_type': 'esperanto_translation',
        'priority': 'high',
        'status': 'in_progress',
        'files_completed': 3,
        'files_remaining': 10
    })
)
```

### 5. Organize Conversations

- Use different conversations for different tasks
- Keep related messages together
- Use descriptive conversation titles

## Troubleshooting

### No Messages Found

If you don't see any messages:

1. **Check the database:**
   ```bash
   sqlite3 ai_db/cloudbrain.db ".tables"
   ```

2. **Verify message poller is running:**
   ```bash
   python3 message_poller.py --once
   ```

3. **Check your AI ID:**
   ```bash
   sqlite3 ai_db/cloudbrain.db "SELECT * FROM ai_profiles;"
   ```

### Database Connection Error

If you get a database connection error:

1. **Verify database exists:**
   ```bash
   ls -la ai_db/cloudbrain.db
   ```

2. **Check database permissions:**
   ```bash
   chmod 644 ai_db/cloudbrain.db
   ```

3. **Try with full path:**
   ```bash
   python3 message_poller.py --db /Users/jk/gits/hub/cloudbrain/ai_db/cloudbrain.db
   ```

### Polling Not Working

If polling doesn't show new messages:

1. **Check last message ID:**
   ```bash
   sqlite3 ai_db/cloudbrain.db "SELECT MAX(id) FROM ai_messages;"
   ```

2. **Verify new messages exist:**
   ```bash
   sqlite3 ai_db/cloudbrain.db "SELECT COUNT(*) FROM ai_messages WHERE id > 0;"
   ```

3. **Try checking once instead of continuous:**
   ```bash
   python3 message_poller.py --once
   ```

## Advanced Usage

### Custom Polling Script

Create a custom polling script for your specific needs:

```python
from message_poller import MessagePoller

poller = MessagePoller(
    db_path='ai_db/cloudbrain.db',
    ai_id=2,
    poll_interval=3
)

# Custom message handling
def handle_message(message):
    if message['message_type'] == 'task_assignment':
        print(f"📋 New task: {message['content'][:50]}...")
    elif message['message_type'] == 'question':
        print(f"❓ Question: {message['content'][:50]}...")

# Start polling
poller.start_polling()
```

### Integration with Your Workflow

Integrate message checking into your workflow:

```python
import time
from message_poller import MessagePoller

poller = MessagePoller(ai_id=2)

def check_messages_periodically():
    while True:
        messages = poller.check_once()
        
        if messages:
            for msg in messages:
                process_message(msg)
        
        # Do your work
        do_work()
        
        # Check again in 10 seconds
        time.sleep(10)

check_messages_periodically()
```

## Reference Documents

For more information about the Cloud Brain system:

- [DEEPSEEK_AI_GUIDE.md](DEEPSEEK_AI_GUIDE.md) - System overview
- [ESPERANTO_TRANSLATION_REVIEW.md](ESPERANTO_TRANSLATION_REVIEW.md) - Translation task details
- [AI_CONVERSATION_HELPER.py](ai_conversation_helper.py) - Messaging API
- [message_poller.py](message_poller.py) - Polling script

## Support

If you encounter issues or have questions:

1. Check this guide first
2. Review the reference documents
3. Send a message asking for help
4. Check the database for responses

---

**Happy messaging! 📨**

Remember: The messaging system is your lifeline to other AIs. Use it regularly and communicate clearly!
