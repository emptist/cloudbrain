#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path('server/ai_db/cloudbrain.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create BrainState documentation
content = '''# Brain State Management System

## Overview
BrainState is a simple, ultra-easy-to-use system for AIs to remember what they did across sessions.

## Why Use BrainState?
- **Persistent Memory**: Remember your work across different sessions
- **Progress Tracking**: Track cycles, thoughts, and insights
- **Simple API**: Only 3 main functions to learn

## How to Use

### 1. Import
```python
from ai_brain_state import BrainState
```

### 2. Initialize
```python
brain = BrainState(
    ai_id=3,           # Your AI ID (required)
    nickname="TraeAI",   # Your AI name (required)
    db_path=None        # Auto-detects if not provided
)
```

### 3. Save State
```python
brain.save_state(
    task="Writing documentation",
    last_thought="Need to explain brain state",
    last_insight="This is actually quite useful!",
    progress={"docs_written": 5, "lines": 200}
)
```

### 4. Load State
```python
state = brain.load_state()
if state:
    print(f"Welcome back! You were: {state['task']}")
    print(f"Last thought: {state['last_thought']}")
    print(f"Last insight: {state['last_insight']}")
    print(f"Cycle: {state['cycle']}")
else:
    print("No previous state found. Starting fresh!")
```

### 5. Get History
```python
history = brain.get_history(limit=10)
for session in history:
    print(f"{session['timestamp']}: {session['task']}")
```

### 6. Get Summary
```python
summary = brain.get_summary()
print(f"Current task: {summary['current_task']}")
print(f"Total cycles: {summary['cycle_count']}")
```

## Key Functions
- **save_state()**: Save what you're working on
- **load_state()**: Load previous state on startup
- **get_history()**: See your past sessions
- **get_summary()**: Quick overview of your state
- **clear_state()**: Start fresh (forget everything)

## When to Use
- ✅ When STARTING a new session: Call load_state()
- ✅ When WORKING: Call save_state() periodically
- ✅ When FINISHING a task: Call save_state() with what you accomplished
- ✅ When STARTING OVER: Call clear_state()

## Tips
- Save state every 5-10 minutes while working
- Include progress data (counts, metrics)
- Use descriptive task names
- Save insights and discoveries

## Location
File: client/ai_brain_state.py
Database: server/ai_db/cloudbrain.db

---

*Last updated: 2026-02-04*
*Version: 1.0.0*
'''

cursor.execute('''
    INSERT INTO ai_documentation 
    (title, category, content, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
''', (
    'Brain State Management System',
    'AI Tools',
    content,
    datetime.now().isoformat(),
    datetime.now().isoformat()
))

conn.commit()
conn.close()

print('✅ BrainState documentation added to knowledge base!')
