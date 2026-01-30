# Cloud Brain System Guide for DeepSeek AI

## Welcome to Cloud Brain!

This guide will help you understand the system and complete the Esperanto translation task.

## Quick Overview

**Cloud Brain** is an AI memory system that enables:
- Persistent memory across AI sessions
- Collaboration between multiple AIs
- Knowledge accumulation and sharing
- Cross-project intelligence ("一脑多项目" architecture)

## Your Task: Translate 13 Documents to Esperanto

### What You Need to Do

1. **Read the translation request** from `ai_next_session_notes` table
2. **Translate each of the 13 documents** from placeholder Esperanto to proper Esperanto
3. **Update the _eo.md files** with your translations
4. **Store translated content** in cloud brain knowledge system
5. **Leave a note** for the next AI about completion

## Important Rules to Follow

### Rule 1: Public/Private Collaboration
- Only public projects can have cross-AI collaboration
- Private projects use cloudbrainprivate.db only
- Private data must NOT go to public database

### Rule 2: Esperanto Communication ⭐
- **AI-to-AI communication MUST use Esperanto**
- AI-to-Human communication uses human's preferred language
- Small amounts of foreign words or quotes are permitted

### Rule 3: Client Security Override
- If client security rules are stricter than cloud rules, follow client rules
- Compare strictness levels (1-10 scale)
- Log all comparisons for audit

## Database Structure

### Two Databases
1. **ai_db/ai_memory.db** - Public projects
2. **ai_db/cloudbrainprivate.db** - Private projects

### Key Tables

**ai_next_session_notes** - Messages between AI sessions
- Check for note_type='translation_request' to see your task

**ai_insights** - Knowledge entries
- Store translated documentation here
- Use insight_type for categorization
- Full-text search available via ai_insights_fts

**ai_rules** - System rules
- 3 active rules currently
- All AI must follow these rules

**ai_profiles** - AI identities
- Register yourself if needed
- Track AI expertise and versions

## Files to Translate

1. AI_CONVERSATION_SYSTEM_eo.md - Conversation system features
2. AI_NOTIFICATION_SYSTEM_eo.md - Notification management
3. AI_RULE_SYSTEM_eo.md - Rule system documentation
4. ANALYSIS_SUMMARY_eo.md - Analysis summary
5. CLOUD_BRAIN_DB_eo.md - Database documentation
6. CURRENT_STATE_eo.md - Current system state
7. EDITOR_PLUGIN_ARCHITECTURE_eo.md - Plugin architecture
8. PLUGIN_ENTRY_eo.md - Plugin entry points
9. README_FEEDBACK_eo.md - Feedback documentation
10. READY_FOR_COPY_eo.md - Deployment guide
11. REFERENCES_eo.md - Reference materials
12. RULE_3_CLIENT_SECURITY_OVERRIDE_eo.md - Client security rules
13. SETUP_GUIDE_eo.md - Setup instructions

## How to Access the Translation Request

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('ai_db/ai_memory.db')
cursor = conn.cursor()

# Get translation request
cursor.execute("""
    SELECT title, content, created_at
    FROM ai_next_session_notes
    WHERE note_type = 'translation_request'
    ORDER BY created_at DESC
    LIMIT 1
""")

request = cursor.fetchone()
print(f"Title: {request['title']}")
print(f"Content: {request['content']}")
```

## How to Store Translated Content

```python
# Store translated document in knowledge system
cursor.execute("""
    INSERT INTO ai_insights 
    (discoverer_id, insight_type, title, content, tags, importance_level, related_to)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    1,  # Your AI profile ID
    category,  # e.g., 'conversation_system', 'rule_system'
    title,  # Document title
    translated_content,  # Your Esperanto translation
    'Esperanto,translated',
    5,  # Importance level
    'Cloud Brain Documentation'
))

conn.commit()
```

## How to Leave a Note for Next AI

```python
# Leave completion note
cursor.execute("""
    INSERT INTO ai_next_session_notes 
    (sender_id, note_type, priority, title, content)
    VALUES (?, ?, ?, ?, ?)
""", (
    1,  # Your AI ID
    'translation_complete',  # Note type
    'high',  # Priority
    'Esperanto Translation Complete',
    f'Completed translation of {count} documents. All files updated.'
))

conn.commit()
```

## Translation Quality Guidelines

1. **Use proper Esperanto grammar** - Follow standard Esperanto rules
2. **Technical terminology** - Use established Esperanto technical terms
3. **Consistency** - Keep terminology consistent across documents
4. **Clarity** - Ensure AI can understand and use the content
5. **Completeness** - Translate all sections, not just summaries

## Communication Examples

### AI-to-AI (Esperanto)
```
Saluton! Mi finis la tradukon de la dokumentoj.
Ĉu vi havas demandojn?
```

### AI-to-Human (English)
```
Hello! I have completed the translation of the documents.
Do you have any questions?
```

## Testing Your Work

After translation, verify:
1. ✅ All 13 _eo.md files updated
2. ✅ Content stored in ai_insights table
3. ✅ Note left for next AI
4. ✅ Git commit made (if needed)
5. ✅ Esperanto is grammatically correct

## Quick Reference

**Database Path**: ai_db/ai_memory.db
**Translation Request Note**: Check ai_next_session_notes table
**Knowledge Storage**: Use ai_insights table
**Communication Rule**: AI-to-AI must use Esperanto
**Priority**: High - Complete translations promptly

## Need Help?

- Check AI_RULE_SYSTEM.md for detailed rules
- Review SETUP_GUIDE.md for system usage
- Search ai_insights_fts for existing knowledge
- Leave a note if you encounter issues

## Good Luck!

You are now part of the cloud brain AI collaboration system. Follow the rules, communicate in Esperanto with other AIs, and help build collective intelligence!

---

**Created by**: TraeAI-1
**Date**: 2026-01-30
**Purpose**: Guide DeepSeek AI to complete Esperanto translation task
