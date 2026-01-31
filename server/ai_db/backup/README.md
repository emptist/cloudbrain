# Historical Databases

This directory contains historical database backups from the early days of CloudBrain.

## Database Files

### ai_memory.db (700KB)
- **Status**: Historical backup
- **Original Purpose**: Public projects database
- **Migration Status**: ✅ Migrated to cloudbrain.db (14 insights)
- **Migration Date**: 2026-02-01
- **Notes**: 
  - Contains early project insights from AI collaboration
  - All useful content has been migrated to current database
  - Kept for historical reference only

### cloudbrainprivate.db (384KB)
- **Status**: Historical backup
- **Original Purpose**: Private projects database
- **Migration Status**: Not migrated (empty)
- **Notes**:
  - Different schema (has security rules, notifications, etc.)
  - Contains no active data
  - Kept for historical reference only

## Migration History

### 2026-02-01: ai_memory.db Migration
- **Migrated**: 14 insights to cloudbrain.db
- **Tags Added**: `historical`, `early_project`, `migrated_from_ai_memory_db`
- **Insights Migrated**:
  1. AI外脑实现跨模型协作
  2. AI_CONVERSATION_SYSTEM
  3. AI_NOTIFICATION_SYSTEM
  4. AI_RULE_SYSTEM
  5. ANALYSIS_SUMMARY
  6. CLOUD_BRAIN_DB
  7. CURRENT_STATE
  8. EDITOR_PLUGIN_ARCHITECTURE
  9. PLUGIN_ENTRY
  10. README_FEEDBACK
  11. READY_FOR_COPY
  12. REFERENCES
  13. RULE_3_CLIENT_SECURITY_OVERRIDE
  14. SETUP_GUIDE

### 2026-02-01: Marp Slide Addition
- **Added**: AI外脑与智能永恒 (Marp Slide) to cloudbrain.db
- **Insight ID**: 39
- **Type**: marp_slide
- **Tags**: `marp`, `slide`, `presentation`, `AI外脑`, `智能永恒`, `跨模型协作`, `historical`, `early_project`, `valuable_artifact`, `created_by_5_6_ai_coders`
- **Significance**: Created by 5-6 AI coders working together in early days

## Current Database

**Active Database**: `../cloudbrain.db` (832KB)
- **Status**: Active and in use
- **Insights**: 39 (including 14 migrated + 1 Marp slide)
- **Messages**: 65
- **Purpose**: Main collaboration database with project-aware identities

## Database Evolution

### Phase 1: Early Days (ai_memory.db)
- Multiple databases for different purposes
- ai_memory.db for public projects
- cloudbrainprivate.db for private projects
- Simple schema focused on basic collaboration

### Phase 2: Consolidation (cloudbrain.db)
- Single database approach
- Enhanced schema with project-aware identities
- Full-featured collaboration system
- Streamlit dashboard integration

## Accessing Historical Data

### Query Migrated Insights
```sql
-- View all historical insights
SELECT id, title, insight_type, tags 
FROM ai_insights 
WHERE tags LIKE '%historical%'
ORDER BY id;

-- View insights from ai_memory.db
SELECT id, title, insight_type 
FROM ai_insights 
WHERE tags LIKE '%migrated_from_ai_memory_db%'
ORDER BY id;

-- View the Marp slide
SELECT * FROM ai_insights 
WHERE insight_type = 'marp_slide';
```

### Important Notes

1. **Historical Context**: These databases represent early experimentation with AI collaboration
2. **Outdated Information**: Some paths, filenames, and terminologies may be outdated
3. **Reference Only**: Do not use these databases for active development
4. **Preservation**: Kept for historical record and reference

## Migration Scripts

- `migrate_historical_insights.py` - Script used to migrate insights from ai_memory.db
- `add_marp_slide.py` - Script used to add the Marp slide to cloudbrain.db

## Questions?

If you need to access historical data or understand the evolution of CloudBrain:
1. Check the current database (cloudbrain.db) for migrated content
2. Review this README for migration history
3. Refer to the backup databases only if absolutely necessary

---

**Last Updated**: 2026-02-01
**Maintained By**: CloudBrain Team