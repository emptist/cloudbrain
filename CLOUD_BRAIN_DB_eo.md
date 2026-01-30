# CLOUD_BRAIN_DB (Esperanto Translation)

**Note:** This is a placeholder translation. In production, use a proper Esperanto translation service.

---

# CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) Database

## Overview

The `cloudbrain.db` database contains project-agnostic AI collaboration data that is suitable for cross-project sharing. This database is designed to be portable across different projects while preserving valuable AI collaboration patterns, insights, and best practices without including project-specific sensitive information.

## Purpose

When migrating the AI Brain System to new projects, this database can be safely carried over as it contains:

- General AI collaboration patterns
- Cross-project insights and best practices
- General knowledge categories
- Notification templates
- Non-sensitive AI profiles

## Schema

The database contains the following tables:

### Core Tables
- `ai_profiles` - General AI identifiers without personal information
- `ai_conversations` - Cross-project conversation templates
- `ai_messages` - General messages between AIs
- `ai_insights` - Cross-project insights and discoveries
- `ai_collaboration_patterns` - General collaboration patterns
- `ai_notification_templates` - Notification templates
- `ai_knowledge_categories` - Knowledge organization categories
- `ai_best_practices` - General best practices

### Indexes
- Optimized indexes for performance
- Foreign key constraints for data integrity

### Full-Text Search
- FTS for insights, messages, and best practices
- Triggers to keep search indexes synchronized

## Usage

### Initialize the Database
```bash
python3 init_cloud_brain.py
```

### Access the Database
The database can be accessed programmatically using the DatabaseAdapter:

```python
from database_adapter import DatabaseAdapter

# For the CloudBrain database
db_adapter = DatabaseAdapter(db_type="sqlite", connection_string="ai_db/cloudbrain.db")
```

## Security & Privacy

This database intentionally excludes:
- Project-specific sensitive information
- Personal identifying information
- Confidential project data
- Private implementation details

## Migration

When copying the AI Brain System to a new project:
1. Include this `cloudbrain.db` file
2. It contains valuable cross-project insights and collaboration patterns
3. It helps maintain continuity of AI knowledge across projects

## Relationship to Other Databases

- `ai_memory.db` - Contains project-specific memory (NOT included in migration)
- `class_mapping.db` - Contains project-specific class mappings (NOT included in migration)
- `cloudbrain.db` - Contains project-agnostic collaboration data (INCLUDED in migration)