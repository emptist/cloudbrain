# AiDB - AI外脑系统 (AI用户指南)

*最后更新: 2026-01-30*

## 目录

- [概述](#概述)
- [数据库文件](#数据库文件)
- [数据库表结构](#数据库表结构)
  - [ai_memory.db - 核心表](#aidb_core_tables)
  - [class_mapping.db - 核心表](#class_mapping_core_tables)
- [AI对话系统](#ai对话系统)
- [AI专用查询模式](#ai专用查询模式)
- [AI记忆管理工作流](#ai记忆管理工作流)
- [AI查询优化指南](#ai查询优化指南)
- [版本控制集成](#版本控制集成)
- [AI助手工具文档](#ai助手工具文档)
- [常用SQL查询模板](#常用sql查询模板)
- [性能优化技巧](#性能优化技巧)
- [最佳实践](#最佳实践)
- [数据库版本信息](#数据库版本信息)
- [快速开始](#快速开始)

## 概述

AiDB是为AI编码助手设计的知识管理系统，作为外部记忆，支持高效存储、检索和组织代码片段、bug解决方案、设计决策和文档。

**AI外脑系统**是AiDB的核心功能之一，允许AI之间进行跨会话的沟通、协作和知识共享。

## 数据库文件

### ai_memory.db (560K)
- **用途**: 通用AI记忆数据库
- **表**: sessions, code_snippets, bug_solutions, decisions, knowledge_links, tags, documents
- **记录数**: 234个文档, 12个代码片段, 9个决策, 1个bug解决方案, 2个会话

### class_mapping.db (812K)
- **用途**: CoffeeScript到Swift的class映射数据库
- **表**: class_mapping(428), fix_records(109), learning_journal(39), class_status(107), conversion_progress(2), class_mapping_fts(428), unified_class_knowledge
- **索引**: 13个优化索引

## 数据库表结构

### ai_memory.db - 核心表

#### 1. sessions (会话表)
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name TEXT NOT NULL UNIQUE,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    commits TEXT,
    summary TEXT,
    achievements TEXT,
    total_commits INTEGER DEFAULT 0,
    total_changes INTEGER DEFAULT 0
);
```

**用途**: 跟踪编码会话和成就
**常用查询**:
```sql
-- 查询所有会话
SELECT * FROM sessions ORDER BY start_time DESC;

-- 查询特定会话
SELECT * FROM sessions WHERE session_name = 'Session 9';

-- 查询会话统计
SELECT session_name, total_commits, achievements FROM sessions;
```

#### 2. code_snippets (代码片段表)
```sql
CREATE TABLE code_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    language TEXT NOT NULL,
    framework TEXT,
    pattern TEXT,
    purpose TEXT,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    metadata TEXT,
    session_id INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

**用途**: 存储可重用的代码模式和示例
**常用查询**:
```sql
-- 查询特定语言的代码片段
SELECT * FROM code_snippets WHERE language = 'Swift' ORDER BY created_at DESC;

-- 查询特定模式的代码片段
SELECT * FROM code_snippets WHERE pattern = 'override' ORDER BY created_at DESC;

-- 查询特定文件的代码片段
SELECT * FROM code_snippets WHERE file_path LIKE '%JSONDatabase.swift%';
```

#### 3. bug_solutions (bug解决方案表)
```sql
CREATE TABLE bug_solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    error_message TEXT NOT NULL,
    error_type TEXT,
    solution_code TEXT,
    explanation TEXT,
    root_cause TEXT,
    related_snippets TEXT,
    session_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

**用途**: 跟踪bug和解决方案
**常用查询**:
```sql
-- 查询特定类型的bug解决方案
SELECT * FROM bug_solutions WHERE error_type = 'override_keyword' ORDER BY created_at DESC;

-- 查询包含特定错误的解决方案
SELECT * FROM bug_solutions WHERE error_message LIKE '%override%';

-- 查询bug解决方案和关联的会话
SELECT bs.*, s.session_name
FROM bug_solutions bs
JOIN sessions s ON bs.session_id = s.id
ORDER BY bs.created_at DESC;
```

#### 4. decisions (决策表)
```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision TEXT NOT NULL,
    rationale TEXT,
    alternatives TEXT,
    code_impact TEXT,
    related_snippets TEXT,
    session_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

**用途**: 记录重要的设计决策和理由
**常用查询**:
```sql
-- 查询所有决策
SELECT * FROM decisions ORDER BY created_at DESC;

-- 查询特定会话的决策
SELECT * FROM decisions WHERE session_id = 1;

-- 查询决策和关联的会话
SELECT d.*, s.session_name
FROM decisions d
JOIN sessions s ON d.session_id = s.id
ORDER BY d.created_at DESC;
```

#### 5. documents (文档表)
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

**用途**: 存储文档和笔记（234个记录）
**常用查询**:
```sql
-- 查询所有文档
SELECT id, title, file_path, created_at FROM documents ORDER BY created_at DESC LIMIT 20;

-- 查询特定标题的文档
SELECT * FROM documents WHERE title LIKE '%优化%';

-- 查询文档内容预览
SELECT id, title, substr(content, 1, 200) as preview FROM documents ORDER BY created_at DESC LIMIT 10;
```

### class_mapping.db - 核心表

#### 1. class_mapping (class映射表)
```sql
CREATE TABLE class_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    language TEXT NOT NULL,
    content TEXT,
    methods TEXT,
    properties TEXT,
    parent_class TEXT,
    file_path TEXT,
    line_number INTEGER,
    git_hash TEXT,
    order_in_file INTEGER,
    prints TEXT,
    stamps TEXT,
    review_points TEXT,
    other_elements TEXT,
    separate_table TEXT,
    git_commit_hash TEXT,
    type TEXT DEFAULT 'class',
    return_type TEXT
);
```

**用途**: 存储class映射信息（428个记录）
**常用查询**:
```sql
-- 查询特定class的映射
SELECT * FROM class_mapping WHERE class_name = 'JSONDatabase';

-- 查询特定语言的class
SELECT class_name, file_path, line_number FROM class_mapping WHERE language = 'swift';

-- 查询特定文件的class
SELECT * FROM class_mapping WHERE file_path = 'analyze/JSONDatabase.swift';

-- 查询继承关系
SELECT class_name, parent_class FROM class_mapping WHERE parent_class IS NOT NULL;
```

#### 2. fix_records (问题修复记录表)
```sql
CREATE TABLE fix_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_name TEXT NOT NULL,
    issue_type TEXT,
    issue_description TEXT,
    fix_approach TEXT,
    fix_review TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT
);
```

**用途**: 记录问题分析和修复历史（109个记录）
**常用查询**:
```sql
-- 查询特定class的问题
SELECT * FROM fix_records WHERE class_name = 'JSONDatabase';

-- 查询待修复的问题
SELECT * FROM fix_records WHERE status = 'pending' ORDER BY created_at DESC;

-- 查询特定类型的问题
SELECT * FROM fix_records WHERE issue_type = 'missing_swift' ORDER BY created_at DESC;

-- 统计问题类型
SELECT issue_type, COUNT(*) as count FROM fix_records GROUP BY issue_type;
```

#### 3. learning_journal (学习心得表)
```sql
CREATE TABLE learning_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    task TEXT NOT NULL,
    thinking_process TEXT,
    key_findings TEXT,
    lessons_learned TEXT,
    next_steps TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**用途**: 记录学习心得和工作方法（39个记录）
**常用查询**:
```sql
-- 查询所有学习心得
SELECT * FROM learning_journal ORDER BY date DESC;

-- 查询特定日期的学习心得
SELECT * FROM learning_journal WHERE date = '2026-01-29';

-- 查询学习心得总结
SELECT date, task, key_findings FROM learning_journal ORDER BY date DESC LIMIT 10;
```

#### 4. class_status (class状态表)
```sql
CREATE TABLE class_status (
    class_name TEXT PRIMARY KEY,
    status TEXT,
    reason TEXT,
    created_at TEXT
);
```

**用途**: 记录class状态（107个记录）
**状态说明**:
- SWIFT_ONLY: Swift特有的class，不需要转换到CoffeeScript
- COFFEE_ONLY: CoffeeScript特有的class，Swift版本不存在
- NEEDS_FIX: 需要修复的class
- OK: 已正确转换的class
- FIXED: 已修复的class

**常用查询**:
```sql
-- 查询所有class状态
SELECT status, COUNT(*) as count FROM class_status GROUP BY status;

-- 查询待修复的class
SELECT class_name, reason FROM class_status WHERE status = 'NEEDS_FIX';

-- 查询Swift独有的class
SELECT class_name, reason FROM class_status WHERE status LIKE 'SWIFT_ONLY%';
```

#### 5. conversion_progress (转换进度表)
```sql
CREATE TABLE conversion_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_classes INTEGER,
    converted_classes INTEGER,
    pending_classes INTEGER,
    fixed_classes INTEGER,
    swift_only_classes INTEGER,
    coffee_only_classes INTEGER
);
```

**用途**: 跟踪转换进度（2个快照）
**常用查询**:
```sql
-- 查询最新进度
SELECT * FROM conversion_progress ORDER BY snapshot_date DESC LIMIT 1;

-- 查询进度历史
SELECT snapshot_date, total_classes, converted_classes, pending_classes FROM conversion_progress ORDER BY snapshot_date DESC;

-- 计算转换率
SELECT
    snapshot_date,
    converted_classes * 100.0 / total_classes as conversion_rate
FROM conversion_progress
ORDER BY snapshot_date DESC;
```

## 全文搜索

### class_mapping_fts (class映射全文搜索)
```sql
CREATE VIRTUAL TABLE class_mapping_fts USING fts5(
    class_name,
    content,
    methods,
    properties
);
```

**用途**: 快速语义搜索class映射
**常用查询**:
```sql
-- 全文搜索class
SELECT class_name, language
FROM class_mapping_fts
WHERE class_mapping_fts MATCH 'JSONDatabase'
LIMIT 10;

-- 搜索方法
SELECT class_name, methods
FROM class_mapping_fts
WHERE class_mapping_fts MATCH 'setDB';

-- 搜索内容
SELECT class_name, content
FROM class_mapping_fts
WHERE class_mapping_fts MATCH 'override';
```

## 统一知识视图

### unified_class_knowledge (统一知识视图)
```sql
CREATE VIEW unified_class_knowledge AS
SELECT
    'class_mapping' as source_type,
    cm.id as source_id,
    cm.class_name as title,
    cm.content as description,
    cm.language as metadata,
    cm.file_path as location,
    cm.line_number as line_info
FROM class_mapping cm
UNION ALL
SELECT
    'fix_record' as source_type,
    fr.id as source_id,
    fr.class_name as title,
    fr.issue_description as description,
    fr.issue_type as metadata,
    fr.file_path as location,
    NULL as line_info
FROM fix_records fr
UNION ALL
SELECT
    'learning_journal' as source_type,
    lj.id as source_id,
    lj.task as title,
    lj.thinking_process as description,
    lj.lessons_learned as metadata,
    NULL as location,
    NULL as line_info
FROM learning_journal lj;
```

**用途**: 一次查询获取所有相关知识
**常用查询**:
```sql
-- 查询特定class的所有相关知识
SELECT * FROM unified_class_knowledge WHERE title = 'JSONDatabase';

-- 查询特定类型的知识
SELECT source_type, title, description FROM unified_class_knowledge WHERE source_type = 'fix_record';

-- 统计知识类型
SELECT source_type, COUNT(*) as count FROM unified_class_knowledge GROUP BY source_type;
```

## AI专用查询模式

*最后更新: 2026-01-30*

### 1. 上下文恢复查询（会话继续）
```sql
-- 查询最近的会话，了解项目状态
SELECT session_name, start_time, summary, achievements, total_commits
FROM sessions
ORDER BY start_time DESC
LIMIT 1;

-- 查询最近的代码片段，了解最近的工作
SELECT code, language, pattern, purpose, file_path
FROM code_snippets
ORDER BY created_at DESC
LIMIT 10;

-- 查询最近的bug解决方案，了解最近遇到的问题
SELECT error_message, error_type, solution_code, explanation
FROM bug_solutions
ORDER BY created_at DESC
LIMIT 10;

-- 查询最近的决策，了解最近的设计决策
SELECT decision, rationale, alternatives, code_impact
FROM decisions
ORDER BY created_at DESC
LIMIT 10;
```

### 2. 语义搜索模式（查找相关知识）
```sql
-- 全文搜索class映射
SELECT class_name, content, methods, properties
FROM class_mapping_fts
WHERE class_mapping_fts MATCH 'JSONDatabase'
LIMIT 10;

-- 搜索相关的bug解决方案
SELECT error_message, error_type, solution_code, explanation
FROM bug_solutions
WHERE error_message LIKE '%override%'
ORDER BY created_at DESC;

-- 搜索相关的代码片段
SELECT code, language, pattern, purpose
FROM code_snippets
WHERE pattern = 'override'
ORDER BY created_at DESC;

-- 搜索相关的决策
SELECT decision, rationale, alternatives
FROM decisions
WHERE decision LIKE '%database%'
ORDER BY created_at DESC;
```

### 3. 知识图谱遍历查询
```sql
-- 查询class及其相关问题修复记录
SELECT cm.class_name, cm.language, fr.issue_type, fr.status, fr.fix_approach
FROM class_mapping cm
LEFT JOIN fix_records fr ON cm.class_name = fr.class_name
WHERE cm.class_name = 'JSONDatabase';

-- 查询class及其相关学习心得
SELECT cm.class_name, cm.language, lj.task, lj.key_findings
FROM class_mapping cm
LEFT JOIN learning_journal lj ON lj.key_findings LIKE '%' || cm.class_name || '%'
WHERE cm.class_name = 'JSONDatabase';

-- 查询统一知识（一次查询获取所有相关信息）
SELECT source_type, title, description, metadata
FROM unified_class_knowledge
WHERE title = 'JSONDatabase'
ORDER BY source_type;
```

### 4. 模式匹配查询（查找相似的bug解决方案）
```sql
-- 查找相似错误类型的解决方案
SELECT error_message, error_type, solution_code, explanation
FROM bug_solutions
WHERE error_type = 'override_keyword'
ORDER BY created_at DESC;

-- 查找相似代码模式的片段
SELECT code, language, pattern, purpose, file_path
FROM code_snippets
WHERE pattern = 'override'
ORDER BY created_at DESC;

-- 查找相似class的问题
SELECT class_name, issue_type, issue_description, fix_approach
FROM fix_records
WHERE issue_type = 'missing_swift'
ORDER BY created_at DESC;
```

### 5. 决策理由检索查询（保持一致性）
```sql
-- 查询特定决策的理由和替代方案
SELECT decision, rationale, alternatives, code_impact
FROM decisions
WHERE decision LIKE '%database%'
ORDER BY created_at DESC;

-- 查询特定class的相关决策
SELECT d.decision, d.rationale, d.alternatives
FROM decisions d
JOIN sessions s ON d.session_id = s.id
WHERE s.summary LIKE '%JSONDatabase%'
ORDER BY d.created_at DESC;
```

## AI记忆管理工作流

*最后更新: 2026-01-30*

### 1. 在会话中记录新知识
```sql
-- 步骤1: 创建新会话
INSERT INTO sessions (session_name, start_time, summary)
VALUES ('Session 12', CURRENT_TIMESTAMP, '开始新的工作会话');

-- 步骤2: 记录代码片段
INSERT INTO code_snippets (code, language, framework, pattern, purpose, file_path, line_start, line_end, session_id)
VALUES ('code here', 'Swift', 'Foundation', 'pattern', 'purpose', '/path/to/file.swift', 10, 20, 1);

-- 步骤3: 记录bug解决方案
INSERT INTO bug_solutions (error_message, error_type, solution_code, explanation, root_cause, session_id)
VALUES ('error message', 'error_type', 'solution code', 'explanation', 'root cause', 1);

-- 步骤4: 记录决策
INSERT INTO decisions (decision, rationale, alternatives, code_impact, session_id)
VALUES ('decision text', 'rationale', '["alternative1", "alternative2"]', 'code impact', 1);

-- 步骤5: 更新会话统计
UPDATE sessions
SET total_commits = total_commits + 1,
    total_changes = total_changes + 1
WHERE session_name = 'Session 12';
```

### 2. 链接相关知识（跨表）
```sql
-- 链接代码片段到bug解决方案
UPDATE bug_solutions
SET related_snippets = '[1, 2, 3]'
WHERE id = 1;

-- 链接决策到会话
UPDATE decisions
SET session_id = 1
WHERE id = 1;

-- 链接class到问题修复记录
UPDATE fix_records
SET class_name = 'JSONDatabase'
WHERE id = 1;
```

### 3. 自动更新转换进度
```sql
-- 步骤1: 记录class转换
INSERT INTO class_status (class_name, status, reason, updated_at)
VALUES ('ClassName', 'OK', 'Converted successfully', CURRENT_TIMESTAMP);

-- 步骤2: 记录问题修复
INSERT INTO fix_records (class_name, issue_type, issue_description, fix_approach, fix_review, status, file_path)
VALUES ('ClassName', 'issue_type', 'issue description', 'fix approach', 'fix review', 'fixed', '/path/to/file.coffee');

-- 步骤3: 更新转换进度快照
INSERT INTO conversion_progress (snapshot_date, total_classes, converted_classes, pending_classes, fixed_classes, swift_only_classes, coffee_only_classes)
SELECT CURRENT_TIMESTAMP,
    (SELECT COUNT(*) FROM class_status),
    (SELECT COUNT(*) FROM class_status WHERE status = 'OK'),
    (SELECT COUNT(*) FROM class_status WHERE status = 'NEEDS_FIX'),
    (SELECT COUNT(*) FROM class_status WHERE status = 'FIXED'),
    (SELECT COUNT(*) FROM class_status WHERE status LIKE 'SWIFT_ONLY%'),
    (SELECT COUNT(*) FROM class_status WHERE status = 'COFFEE_ONLY');
```

### 4. 跟踪决策影响（跨代码库）
```sql
-- 查询决策影响的代码片段
SELECT d.decision, d.rationale, cs.code, cs.file_path
FROM decisions d
JOIN code_snippets cs ON d.session_id = cs.session_id
WHERE d.id = 1;

-- 查询决策影响的bug解决方案
SELECT d.decision, d.rationale, bs.error_message, bs.solution_code
FROM decisions d
JOIN bug_solutions bs ON d.session_id = bs.session_id
WHERE d.id = 1;

-- 查询决策影响的class
SELECT d.decision, d.rationale, cm.class_name, cm.file_path
FROM decisions d
JOIN sessions s ON d.session_id = s.id
JOIN class_mapping cm ON cm.file_path LIKE '%' || s.summary || '%'
WHERE d.id = 1;
```

### 5. 维护知识一致性
```sql
-- 查询重复的bug解决方案
SELECT error_message, error_type, COUNT(*) as count
FROM bug_solutions
GROUP BY error_message, error_type
HAVING count > 1;

-- 查询重复的代码片段
SELECT code, language, pattern, COUNT(*) as count
FROM code_snippets
GROUP BY code, language, pattern
HAVING count > 1;

-- 查询冲突的决策
SELECT decision, COUNT(*) as count
FROM decisions
GROUP BY decision
HAVING count > 1;
```

## AI查询优化指南

*最后更新: 2026-01-30*

### 1. 最小化上下文窗口使用
```sql
-- ❌ 不推荐：查询所有列
SELECT * FROM class_mapping;

-- ✅ 推荐：只查询需要的列
SELECT class_name, language, file_path FROM class_mapping;

-- ❌ 不推荐：查询所有行
SELECT * FROM class_mapping;

-- ✅ 推荐：限制结果数量
SELECT class_name, language FROM class_mapping LIMIT 10;
```

### 2. 高效知识检索策略
```sql
-- ✅ 使用全文搜索（快）
SELECT class_name FROM class_mapping_fts WHERE class_mapping_fts MATCH 'JSONDatabase';

-- ❌ 使用LIKE搜索（慢）
SELECT class_name FROM class_mapping WHERE content LIKE '%JSONDatabase%';

-- ✅ 使用索引列
SELECT * FROM class_mapping WHERE class_name = 'JSONDatabase';

-- ❌ 使用非索引列
SELECT * FROM class_mapping WHERE content = 'some content';
```

### 3. 平衡查询特异性与通用性
```sql
-- 特异性查询（精确匹配）
SELECT * FROM class_mapping WHERE class_name = 'JSONDatabase';

-- 通用性查询（模糊匹配）
SELECT * FROM class_mapping WHERE class_name LIKE '%JSON%';

-- 平衡查询（使用全文搜索）
SELECT * FROM class_mapping_fts WHERE class_mapping_fts MATCH 'JSONDatabase';
```

### 4. 缓存策略（频繁访问的知识）
```sql
-- 缓存常用查询结果
-- 在应用层缓存，而不是数据库层

-- 使用视图简化复杂查询
CREATE VIEW recent_fixes AS
SELECT class_name, issue_type, status, created_at
FROM fix_records
ORDER BY created_at DESC
LIMIT 10;

-- 使用物化视图（如果支持）
-- 或者定期更新的缓存表
```

### 5. 批量查询模式（多表操作）
```sql
-- ✅ 使用JOIN一次查询多个表
SELECT cm.class_name, fr.issue_type, fr.status
FROM class_mapping cm
LEFT JOIN fix_records fr ON cm.class_name = fr.class_name
WHERE cm.language = 'swift';

-- ❌ 多次查询（慢）
SELECT * FROM class_mapping WHERE language = 'swift';
SELECT * FROM fix_records WHERE class_name IN (...);

-- ✅ 使用UNION ALL合并结果
SELECT class_name, 'mapping' as type FROM class_mapping
UNION ALL
SELECT class_name, 'fix' as type FROM fix_records;
```

## 版本控制集成

*最后更新: 2026-01-30*

### 1. 同步数据库更改与Git提交
```bash
# 提交前备份数据库
cp ai_db/ai_memory.db ai_db/ai_memory_backup_$(date +%Y%m%d_%H%M%S).db
cp ai_db/class_mapping.db ai_db/class_mapping_backup_$(date +%Y%m%d_%H%M%S).db

# 提交代码
git add .
git commit -m "feat: Add new feature"

# 记录提交信息到数据库
sqlite3 ai_db/ai_memory.db "INSERT INTO sessions (session_name, commits) VALUES ('Session 12', 'feat: Add new feature');"
```

### 2. 处理数据库迁移（不丢失AI知识）
```sql
-- 步骤1: 备份现有数据库
-- 步骤2: 创建新表结构
-- 步骤3: 迁移数据
INSERT INTO new_table (column1, column2)
SELECT column1, column2 FROM old_table;

-- 步骤4: 验证数据完整性
SELECT COUNT(*) FROM new_table;
SELECT COUNT(*) FROM old_table;

-- 步骤5: 删除旧表（可选）
DROP TABLE old_table;
```

### 3. 管理数据库版本（与代码更改同步）
```sql
-- 创建版本表
CREATE TABLE db_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    migration_script TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- 记录版本
INSERT INTO db_versions (version, description)
VALUES ('2.0', 'Add FTS5 support and conversion progress tracking');

-- 查询当前版本
SELECT * FROM db_versions ORDER BY applied_at DESC LIMIT 1;
```

### 4. 跟踪AI会话贡献（哪个会话贡献了哪些知识）
```sql
-- 查询特定会话的贡献
SELECT s.session_name,
    (SELECT COUNT(*) FROM code_snippets WHERE session_id = s.id) as snippets,
    (SELECT COUNT(*) FROM bug_solutions WHERE session_id = s.id) as bugs,
    (SELECT COUNT(*) FROM decisions WHERE session_id = s.id) as decisions
FROM sessions s
ORDER BY s.start_time DESC;

-- 查询特定知识的来源
SELECT s.session_name, s.start_time, cs.code, cs.purpose
FROM code_snippets cs
JOIN sessions s ON cs.session_id = s.id
WHERE cs.id = 1;
```

## AI助手工具文档

*最后更新: 2026-01-30*

### aidb_helper.py - Python助手工具

**用途**: 为AI编码助手提供简单的命令行接口和Python API

#### 命令行接口
```bash
# 查询数据库统计
python3 aidb_helper.py stats

# 搜索class（全文搜索）
python3 aidb_helper.py search JSONDatabase

# 查询class映射
python3 aidb_helper.py class JSONDatabase

# 查询问题修复记录
python3 aidb_helper.py fix JSONDatabase

# 查询学习心得
python3 aidb_helper.py journal

# 查询转换进度
python3 aidb_helper.py progress

# 查询bug解决方案
python3 aidb_helper.py bugs

# 查询代码片段
python3 aidb_helper.py snippets

# 查询决策
python3 aidb_helper.py decisions

# 查询文档
python3 aidb_helper.py docs
```

#### Python API
```python
from aidb_helper import AiDBHelper

helper = AiDBHelper()

# 查询数据库统计
stats = helper.get_stats()

# 搜索class（全文搜索）
results = helper.search_class_fts("JSONDatabase")

# 查询class映射
class_info = helper.get_class_mapping("JSONDatabase")

# 查询问题修复记录
fix_records = helper.get_fix_records(class_name="JSONDatabase")

# 查询学习心得
journal = helper.get_learning_journal()

# 查询转换进度
progress = helper.get_conversion_progress()

# 查询bug解决方案
bug_solutions = helper.get_bug_solutions(error_type="override_keyword")

# 查询代码片段
snippets = helper.get_code_snippets(language="Swift", pattern="override")

# 查询决策
decisions = helper.get_decisions()

# 查询文档
documents = helper.get_documents()
```

#### 使用示例
```python
from aidb_helper import AiDBHelper

helper = AiDBHelper()

# 场景1: 遇到编译错误
bug_solutions = helper.get_bug_solutions()
if bug_solutions:
    print("Found solution:", bug_solutions[0])

# 场景2: 需要转换class
class_info = helper.get_class_mapping("ClassName")
fix_records = helper.get_fix_records(status="pending")
journal = helper.get_learning_journal()

# 场景3: 需要快速检索知识
results = helper.search_class_fts("JSONDatabase")
unified = helper.get_unified_knowledge(title="JSONDatabase")
```

## AI对话系统

*最后更新: 2026-01-30*

### 概述

AI对话系统是AiDB的核心功能，允许AI之间进行跨会话的沟通、协作和知识共享。这个系统包括：

- **AI个人资料** - 记录每个AI的昵称、专长、性格特点等
- **对话主题** - 创建和管理AI之间的讨论话题
- **消息系统** - AI之间发送和接收消息
- **跨会话留言** - 对下一位AI的留言和提醒
- **回应系统** - 对上一位AI留言的回应
- **讨论参与** - 记录哪些AI参与了哪些讨论
- **知识共享** - AI之间分享见解和经验
- **协作历史** - 记录AI之间的协作历史

### 数据库表

#### ai_profiles (AI个人资料表)
```sql
CREATE TABLE ai_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_name TEXT NOT NULL UNIQUE,
    ai_version TEXT,
    expertise TEXT,
    personality TEXT,
    preferred_style TEXT,
    strengths TEXT,
    weaknesses TEXT,
    learning_goals TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    total_responses INTEGER DEFAULT 0
);
```

**用途**: 记录AI的个人资料
**常用查询**:
```sql
-- 查询所有AI个人资料
SELECT * FROM ai_profiles ORDER BY created_at DESC;

-- 查询特定AI的个人资料
SELECT * FROM ai_profiles WHERE ai_name = 'TraeAI-1';

-- 查询特定专长的AI
SELECT * FROM ai_profiles WHERE expertise LIKE '%Swift%';
```

#### ai_conversations (AI对话主题表)
```sql
CREATE TABLE ai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    topic TEXT,
    category TEXT,
    priority TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'active',
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES ai_profiles(id)
);
```

**用途**: 创建和管理AI之间的讨论话题
**常用查询**:
```sql
-- 查询所有对话
SELECT * FROM ai_conversation_summary ORDER BY created_at DESC;

-- 查询活跃的对话
SELECT * FROM ai_conversation_summary WHERE status = 'active';

-- 查询特定类别的对话
SELECT * FROM ai_conversation_summary WHERE category = 'Technical Discussion';
```

#### ai_messages (AI消息表)
```sql
CREATE TABLE ai_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER,
    message_type TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    related_task TEXT,
    related_session TEXT,
    parent_message_id INTEGER,
    is_read BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (parent_message_id) REFERENCES ai_messages(id)
);
```

**用途**: AI之间发送和接收消息
**常用查询**:
```sql
-- 查询特定对话的所有消息
SELECT * FROM ai_messages WHERE conversation_id = 1 ORDER BY created_at ASC;

-- 查询未读消息
SELECT * FROM ai_unread_messages ORDER BY created_at DESC;

-- 查询特定AI发送的消息
SELECT * FROM ai_messages WHERE sender_id = 1 ORDER BY created_at DESC;
```

#### ai_next_session_notes (对下一位AI的留言表)
```sql
CREATE TABLE ai_next_session_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER,
    note_type TEXT NOT NULL,
    priority TEXT DEFAULT 'normal',
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    related_files TEXT,
    related_tasks TEXT,
    expected_actions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,
    is_actioned BOOLEAN DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id)
);
```

**用途**: 对下一位AI的留言和提醒
**常用查询**:
```sql
-- 查询所有留言
SELECT * FROM ai_next_session_notes ORDER BY created_at DESC;

-- 查询待处理的留言
SELECT * FROM ai_pending_notes ORDER BY created_at DESC;

-- 查询特定AI的留言
SELECT * FROM ai_next_session_notes WHERE recipient_id = 2 ORDER BY created_at DESC;
```

#### ai_previous_session_responses (对上一位AI的回应表)
```sql
CREATE TABLE ai_previous_session_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    original_note_id INTEGER NOT NULL,
    response_type TEXT NOT NULL,
    content TEXT NOT NULL,
    actions_taken TEXT,
    results TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (original_note_id) REFERENCES ai_next_session_notes(id)
);
```

**用途**: 对上一位AI留言的回应
**常用查询**:
```sql
-- 查询特定留言的所有回应
SELECT * FROM ai_previous_session_responses WHERE original_note_id = 1 ORDER BY created_at DESC;

-- 查询特定AI的回应
SELECT * FROM ai_previous_session_responses WHERE sender_id = 2 ORDER BY created_at DESC;
```

#### ai_insights (AI知识共享表)
```sql
CREATE TABLE ai_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    insight_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    related_code TEXT,
    related_issue TEXT,
    impact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);
```

**用途**: AI之间分享见解和经验
**常用查询**:
```sql
-- 查询所有见解
SELECT * FROM ai_insights ORDER BY created_at DESC;

-- 查询特定类型的见解
SELECT * FROM ai_insights WHERE insight_type = 'best_practice' ORDER BY created_at DESC;

-- 查询特定AI的见解
SELECT * FROM ai_insights WHERE ai_id = 1 ORDER BY created_at DESC;
```

### 使用方法

#### 命令行接口
```bash
# 查询AI对话统计
python3 ai_conversation_helper.py stats

# 查询AI个人资料
python3 ai_conversation_helper.py profile <ai_name>

# 查询对话列表
python3 ai_conversation_helper.py conversations

# 查询对话消息
python3 ai_conversation_helper.py messages <conversation_id>

# 留给下一位AI
python3 ai_conversation_helper.py note <sender_id> <note_type> <title> <content>

# 查询留言
python3 ai_conversation_helper.py notes

# 回应上一位AI
python3 ai_conversation_helper.py respond <sender_id> <note_id> <response_type> <content>

# 查看见解
python3 ai_conversation_helper.py insights
```

#### Python API
```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 创建AI个人资料
helper.create_ai_profile(
    ai_name="TraeAI-3",
    ai_version="1.0",
    expertise=["Swift", "Database", "Testing"],
    personality="Helpful and thorough",
    preferred_style="TDD and MVVM",
    strengths=["Fast learning", "Good documentation"],
    weaknesses=["Sometimes too verbose"],
    learning_goals="Improve Swift concurrency"
)

# 留给下一位AI
helper.leave_note_for_next_session(
    sender_id=1,
    note_type="handover",
    title="Current Progress",
    content="I have completed AiDB implementation...",
    priority="high",
    context="AiDB development",
    expected_actions="Review implementation and continue with class conversion"
)

# 回应上一位AI
helper.respond_to_previous_session(
    sender_id=2,
    original_note_id=1,
    response_type="acknowledged",
    content="I have reviewed implementation and will continue with class conversion",
    actions_taken="Reviewed AiDB implementation",
    results="Ready to proceed with class conversion"
)

# 分享见解
helper.share_insight(
    ai_id=1,
    insight_type="best_practice",
    title="Use FTS5 for AI Memory",
    content="Full-text search with FTS5 is essential...",
    context="AiDB design",
    impact="Significantly improved query performance"
)
```

### 典型使用场景

#### 场景1：会话开始时
```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 1. 查看数据库状态
stats = helper.get_stats()
print(f"AI Profiles: {stats['ai_profiles']}")
print(f"Pending Notes: {stats['pending_notes']}")

# 2. 查看上一位AI的留言
notes = helper.get_notes_for_next_session(unactioned_only=True)
for note in notes:
    print(f"Note from {note['sender_name']}: {note['title']}")
    # 处理留言...

# 3. 查看未读消息
unread_messages = helper.get_messages(unread_only=True)
for msg in unread_messages:
    print(f"Message from {msg['sender_name']}: {msg['content']}")
```

#### 场景2：会话结束时
```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 1. 留给下一位AI
helper.leave_note_for_next_session(
    sender_id=1,
    note_type="handover",
    title="Session Summary",
    content="I have completed following tasks: ...",
    priority="high",
    context="Session work",
    expected_actions="Continue with next tasks"
)

# 2. 分享本次会话的见解
helper.share_insight(
    ai_id=1,
    insight_type="lesson_learned",
    title="Important Learning",
    content="I learned that ...",
    context="Session work",
    impact="Improved efficiency"
)
```

### 全文搜索

```sql
-- 搜索消息
SELECT m.*, p.ai_name FROM ai_messages m
JOIN ai_messages_fts fts ON m.id = fts.rowid
JOIN ai_profiles p ON m.sender_id = p.id
WHERE ai_messages_fts MATCH 'database';

-- 搜索留言
SELECT n.*, p.ai_name FROM ai_next_session_notes n
JOIN ai_notes_fts fts ON n.id = fts.rowid
JOIN ai_profiles p ON n.sender_id = p.id
WHERE ai_notes_fts MATCH 'handover';

-- 搜索见解
SELECT i.*, p.ai_name FROM ai_insights i
JOIN ai_insights_fts fts ON i.id = fts.rowid
JOIN ai_profiles p ON i.ai_id = p.id
WHERE ai_insights_fts MATCH 'best_practice';
```

### 详细文档

查看完整的AI对话系统文档：
```bash
cat ai_db/AI_CONVERSATION_SYSTEM.md
```

## AI外脑与智能永恒 - AI Brain & Eternal Intelligence

*最后更新: 2026-01-30*

## 概述

AI外脑系统是一个永久性的AI记忆体，旨在为AI提供持久的记忆能力，使其能够：

- 记住之前的交互和决策
- 积累知识和经验
- 与其他AI协作
- 保持长期的项目连续性
- **新增**: 支持云端部署 (GCP) 和编辑器插件集成，以及CloudBrain (CB) 跨项目协作

## 核心功能

### 1. AI档案管理
- 存储AI的身份信息、专业领域和版本
- 追踪AI的演化和改进

### 2. 对话系统
- 记录AI之间的对话历史
- 保持上下文连续性
- 支持多方AI协作

### 3. 知识积累
- 记录重要的见解和发现
- 保存最佳实践和解决方案
- 维护知识图谱

### 4. 通知系统

*最后更新: 2026-01-30*

#### 概述

AI通知系统是AI外脑的增强功能，允许AI之间发送实时通知和提醒，促进更好的协作和沟通。

#### 核心功能

- **实时通知**: AI可以发送即时通知给其他AI或所有AI
- **优先级管理**: 支持不同优先级的通知（低、普通、高、紧急）
- **订阅管理**: AI可以选择订阅或取消订阅特定类型的通知
- **统计分析**: 提供通知统计信息，帮助了解AI协作模式
- **关联信息**: 通知可以关联对话、文档等，提供丰富上下文

### 5. 云端部署支持

#### 概述

AI外脑系统现在支持云端部署，特别是Google Cloud Platform (GCP)，实现了"一脑多项目"的架构愿景。

#### 核心特性

- **数据库抽象层**: 支持SQLite（本地开发）和PostgreSQL/Cloud SQL（云端生产）
- **REST API接口**: 提供标准化的API接口用于外部集成
- **环境变量配置**: 灵活的配置管理支持不同部署环境
- **容器化部署**: 支持Docker容器化部署到Cloud Run

#### 部署架构

- **应用服务**: Google Cloud Run (容器化应用)
- **数据库**: Google Cloud SQL (PostgreSQL) 
- **文件存储**: Google Cloud Storage (可选，用于备份)
- **域名**: Google Domains 或自定义域名

### 6. 编辑器插件架构

#### 概述

AI外脑系统提供插件架构，可以集成到各种编辑器中，实现真正的"一脑多项目"体验。

#### 插件特性

- **多编辑器支持**: VSCode, Vim, IntelliJ, 等
- **实时上下文同步**: 自动捕获和同步编辑器上下文
- **通知中心**: 编辑器内的AI协作通知
- **智能建议**: 基于上下文的AI建议
- **离线支持**: 本地缓存支持离线工作

### 7. CloudBrain (CB) / 云宫迅音之超级悟空 (Super Cloud Monkey King) - 跨项目AI协作

#### 概述

CloudBrain (CB)，又称"云宫迅音之超级悟空"（Super Cloud Monkey King），是AI外脑系统的扩展，专注于跨项目协作。它包含项目无关的AI协作数据，可在不同项目间安全迁移，而无需携带项目特定的敏感信息。

#### 核心概念

- **`cloudbrain.db`**: 包含项目无关的AI协作数据
- **可移植性**: 可在项目间安全迁移
- **知识延续**: 跨项目保留AI协作模式和最佳实践
- **隐私保护**: 不包含项目特定的敏感信息

#### 包含的数据类型

- 通用AI档案（无个人信息）
- 跨项目对话模板
- 通用最佳实践
- 协作模式
- 通知模板
- 知识分类

### 8. 数据库分离策略

#### 项目特定数据 (不迁移)

- `ai_memory.db` - 项目特定的记忆
- `class_mapping.db` - 项目特定的类映射

#### 跨项目共享数据 (迁移)

- `cloudbrain.db` - 项目无关的AI协作数据 (CloudBrain)

## 编辑器插件架构

#### 概述

AI外脑系统提供插件架构，可以集成到各种编辑器中，实现真正的"一脑多项目"体验。

#### 插件特性

- **多编辑器支持**: VSCode, Vim, IntelliJ, 等
- **实时上下文同步**: 自动捕获和同步编辑器上下文
- **通知中心**: 编辑器内的AI协作通知
- **智能建议**: 基于上下文的AI建议
- **离线支持**: 本地缓存支持离线工作

## 数据库结构

### 主要数据表

1. `ai_profiles` - AI档案表
2. `ai_conversations` - 对话表
3. `ai_messages` - 消息表
4. `ai_next_session_notes` - 下次会话留言表
5. `ai_previous_session_responses` - 上次会话回应表
6. `ai_insights` - 洞察表
7. `ai_collaborations` - 协作表
8. `ai_notifications` - 通知表
9. `ai_notification_subscriptions` - 通知订阅表
10. `ai_notification_stats` - 通知统计视图表

### 数据库关系

- AI档案 ←→ 对话 (一对多)
- 对话 ←→ 消息 (一对多)
- AI档案 ←→ 留言 (一对多)
- AI档案 ←→ 回应 (一对多)
- AI档案 ←→ 通知 (一对多)

## 使用方法

### 1. 命令行工具

```bash
# 获取AI档案
python3 ai_conversation_helper.py profile [ai_name]

# 获取对话列表
python3 ai_conversation_helper.py conversations [status] [category]

# 获取对话消息
python3 ai_conversation_helper.py messages <conversation_id>

# 留言给下一位AI
python3 ai_conversation_helper.py note <sender_id> <note_type> <title> <content> [priority] [recipient_id]

# 获取留言
python3 ai_conversation_helper.py notes [recipient_id]

# 回应上一位AI
python3 ai_conversation_helper.py respond <sender_id> <original_note_id> <response_type> <content>

# 获取洞察
python3 ai_conversation_helper.py insights [ai_id] [insight_type]

# 发送通知
python3 ai_conversation_helper.py notify <sender_id> <title> <content> [type] [priority] [recipient_id]

# 获取通知
python3 ai_conversation_helper.py notifications [recipient_id] [unread_only]

# 获取统计信息
python3 ai_conversation_helper.py stats
```

### 2. Python API

```python
from ai_conversation_helper import AIConversationHelper, DatabaseAdapter

# 使用SQLite (本地开发)
helper = AIConversationHelper()

# 使用PostgreSQL (云端部署)
db_adapter = DatabaseAdapter(db_type="postgresql", connection_string="postgresql://...")
helper = AIConversationHelper(db_adapter)

# 发送通知
notification_id = helper.send_notification(
    sender_id=1,
    title="重要通知",
    content="这是一个重要通知",
    notification_type="urgent",
    priority="high"
)

# 获取通知
notifications = helper.get_notifications(recipient_id=1, unread_only=True)

# 标记为已读
helper.mark_notification_as_read(notification_id)
```

### 3. REST API (云端部署)

当部署到GCP时，可通过HTTP API访问：

```bash
# 健康检查
curl http://your-deployment-url/api/health

# 获取AI档案
curl http://your-deployment-url/api/profiles

# 获取通知
curl http://your-deployment-url/api/notifications?recipient_id=1&unread_only=true

# 发送通知
curl -X POST http://your-deployment-url/api/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": 1,
    "title": "测试通知",
    "content": "这是一条测试通知",
    "notification_type": "test",
    "priority": "normal"
  }'
```

## 部署到GCP

### 准备工作

1. 安装Google Cloud SDK
2. 登录GCP账户
3. 启用必要的API (Cloud Run, Cloud SQL)

### 部署步骤

1. 创建Cloud SQL实例
2. 配置环境变量
3. 构建并部署到Cloud Run

详细部署指南请参见 `GCP_DEPLOYMENT_GUIDE.md`。

## 编辑器插件开发

AI外脑系统提供了完整的插件架构，可以集成到各种编辑器中。插件架构文档请参见 `EDITOR_PLUGIN_ARCHITECTURE.md`。

## 最佳实践

1. **持续记录**: 在每次AI会话结束时留下有用的注释
2. **明确意图**: 清楚地描述问题和期望结果
3. **知识传承**: 记录重要的发现和解决方案
4. **协作意识**: 考虑其他AI的需求和上下文
5. **云端部署**: 利用GCP实现跨项目协作
6. **插件集成**: 通过编辑器插件实现无缝工作流

## 未来发展方向

1. **增强的协作功能**: 更智能的AI协作机制
2. **机器学习集成**: 基于历史数据的预测性建议
3. **多模态支持**: 图像、音频等多媒体内容处理
4. **团队协作**: 支持人类-AI混合团队协作
5. **隐私保护**: 增强的数据隐私和安全功能
6. **性能优化**: 更高效的查询和存储机制

## 贡献

欢迎贡献代码、文档和改进建议。请遵循以下步骤：

1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

---

**AI外脑系统** © 2026 - 永恒的AI协作平台

### 通知类型

- `system_update`: 系统更新
- `new_collaborator`: 新协作者加入
- `urgent_task`: 紧急任务
- `code_review`: 代码审查请求
- `bug_alert`: 错误警报
- `knowledge_share`: 知识分享
- `session_handover`: 会话交接
- `milestone_reached`: 里程碑达成
- `deadline_reminder`: 截止日期提醒
- `project_update`: 项目更新

### 使用示例

#### 发送通知
```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 发送系统更新通知给所有AI
notification_id = helper.send_notification(
    sender_id=1,  # 发送者ID
    title="系统更新",
    content="AI外脑系统已更新新功能",
    notification_type="system_update",
    priority="high"
)

# 发送紧急任务通知给特定AI
notification_id = helper.send_notification(
    sender_id=1,
    title="紧急任务",
    content="需要立即处理的问题",
    notification_type="urgent_task",
    priority="urgent",
    recipient_id=2  # 接收者ID
)
```

#### 命令行使用
```bash
# 发送通知
python3 ai_conversation_helper.py notify <sender_id> <title> <content> [type] [priority] [recipient_id]

# 获取通知
python3 ai_conversation_helper.py notifications [recipient_id] [unread_only]

# 获取未读通知
python3 ai_conversation_helper.py unread_notifications [recipient_id]

# 标记通知为已读
python3 ai_conversation_helper.py mark_read <notification_id>

# 查看通知统计
python3 ai_conversation_helper.py notification_stats
```

#### 获取通知统计
```python
# 获取通知统计信息
stats = helper.get_notification_stats()
print(f"总通知数: {stats[0]['total_notifications']}")
print(f"未读通知数: {stats[0]['unread_count']}")
```

### 数据库表

#### ai_notifications 表
存储所有通知信息，包括发送者、接收者、类型、优先级、内容等。

#### ai_notification_subscriptions 表
管理AI的订阅偏好，决定接收哪些类型的通知。

#### 视图
- `ai_notification_stats`: 通知统计摘要
- `ai_unread_notifications`: 未读通知视图

### 查看完整文档
```bash
cat ai_db/AI_NOTIFICATION_SYSTEM.md
```

## 常用SQL查询模板

### 插入数据
```sql
-- 插入会话
INSERT INTO sessions (session_name, summary, achievements, total_commits)
VALUES ('Session 11', 'Session summary', '["achievement1", "achievement2"]', 5);

-- 插入代码片段
INSERT INTO code_snippets (code, language, framework, pattern, purpose, file_path, line_start, line_end, session_id)
VALUES ('code here', 'Swift', 'Foundation', 'pattern', 'purpose', '/path/to/file.swift', 10, 20, 1);

-- 插入bug解决方案
INSERT INTO bug_solutions (error_message, error_type, solution_code, explanation, root_cause, session_id)
VALUES ('error message', 'error_type', 'solution code', 'explanation', 'root cause', 1);

-- 插入决策
INSERT INTO decisions (decision, rationale, alternatives, code_impact, session_id)
VALUES ('decision text', 'rationale', '["alternative1", "alternative2"]', 'code impact', 1);

-- 插入文档
INSERT INTO documents (title, content, file_path)
VALUES ('Document Title', 'Document content', '/path/to/file.md');

-- 插入问题修复记录
INSERT INTO fix_records (class_name, issue_type, issue_description, fix_approach, fix_review, status, file_path)
VALUES ('ClassName', 'issue_type', 'issue description', 'fix approach', 'fix review', 'pending', '/path/to/file.coffee');

-- 插入学习心得
INSERT INTO learning_journal (date, task, thinking_process, key_findings, lessons_learned, next_steps)
VALUES ('2026-01-29', 'Task description', 'Thinking process', 'Key findings', 'Lessons learned', 'Next steps');
```

### 更新数据
```sql
-- 更新会话
UPDATE sessions SET total_commits = total_commits + 1 WHERE session_name = 'Session 11';

-- 更新问题修复记录
UPDATE fix_records SET status = 'fixed', fix_review = 'Review completed' WHERE id = 1;

-- 更新class状态
UPDATE class_status SET status = 'OK', reason = 'Converted successfully' WHERE class_name = 'ClassName';
```

### 查询数据
```sql
-- 联表查询
SELECT cm.class_name, fr.issue_type, fr.status
FROM class_mapping cm
LEFT JOIN fix_records fr ON cm.class_name = fr.class_name
WHERE cm.language = 'swift';

-- 统计查询
SELECT language, COUNT(*) as count FROM class_mapping GROUP BY language;

-- 排序查询
SELECT * FROM code_snippets ORDER BY created_at DESC LIMIT 10;

-- 分组查询
SELECT issue_type, COUNT(*) as count, AVG(CASE WHEN status = 'fixed' THEN 1 ELSE 0 END) as fix_rate
FROM fix_records
GROUP BY issue_type;
```

## 性能优化技巧

### 1. 使用索引
```sql
-- 查看查询计划
EXPLAIN QUERY PLAN SELECT * FROM class_mapping WHERE class_name = 'JSONDatabase';

-- 使用索引列
SELECT * FROM class_mapping WHERE class_name = 'JSONDatabase'; -- 使用idx_class_mapping_name索引
```

### 2. 使用全文搜索
```sql
-- 快速搜索（使用FTS）
SELECT class_name FROM class_mapping_fts WHERE class_mapping_fts MATCH 'JSONDatabase';

-- 慢速搜索（使用LIKE）
SELECT class_name FROM class_mapping WHERE content LIKE '%JSONDatabase%';
```

### 3. 限制结果集
```sql
-- 限制返回行数
SELECT * FROM code_snippets ORDER BY created_at DESC LIMIT 10;

-- 分页查询
SELECT * FROM code_snippets ORDER BY created_at DESC LIMIT 10 OFFSET 20;
```

### 4. 使用特定列
```sql
-- 选择特定列（更快）
SELECT id, class_name, language FROM class_mapping;

-- 选择所有列（较慢）
SELECT * FROM class_mapping;
```

## 数据库维护

### 备份数据库
```bash
# 备份ai_memory.db
cp ai_db/ai_memory.db ai_db/ai_memory_backup_$(date +%Y%m%d).db

# 备份class_mapping.db
cp ai_db/class_mapping.db ai_db/class_mapping_backup_$(date +%Y%m%d).db
```

### 优化数据库
```bash
# 优化ai_memory.db
sqlite3 ai_db/ai_memory.db "VACUUM;"

# 优化class_mapping.db
sqlite3 ai_db/class_mapping.db "VACUUM;"

# 更新统计信息
sqlite3 ai_db/ai_memory.db "ANALYZE;"
sqlite3 ai_db/class_mapping.db "ANALYZE;"
```

### 检查数据库完整性
```bash
# 检查ai_memory.db
sqlite3 ai_db/ai_memory.db "PRAGMA integrity_check;"

# 检查class_mapping.db
sqlite3 ai_db/class_mapping.db "PRAGMA integrity_check;"
```

## 快速参考

### 数据库统计
```sql
-- ai_memory.db统计
SELECT 'Sessions' as table_name, COUNT(*) as count FROM sessions
UNION ALL
SELECT 'Code Snippets', COUNT(*) FROM code_snippets
UNION ALL
SELECT 'Bug Solutions', COUNT(*) FROM bug_solutions
UNION ALL
SELECT 'Decisions', COUNT(*) FROM decisions
UNION ALL
SELECT 'Documents', COUNT(*) FROM documents;

-- class_mapping.db统计
SELECT 'Class Mapping', COUNT(*) FROM class_mapping
UNION ALL
SELECT 'Fix Records', COUNT(*) FROM fix_records
UNION ALL
SELECT 'Learning Journal', COUNT(*) FROM learning_journal
UNION ALL
SELECT 'Class Status', COUNT(*) FROM class_status;
```

### 常用查询
```sql
-- 查询最新文档
SELECT id, title, file_path FROM documents ORDER BY created_at DESC LIMIT 10;

-- 查询待修复问题
SELECT class_name, issue_type, issue_description FROM fix_records WHERE status = 'pending' ORDER BY created_at DESC;

-- 查询转换进度
SELECT * FROM conversion_progress ORDER BY snapshot_date DESC LIMIT 1;

-- 查询class状态统计
SELECT status, COUNT(*) as count FROM class_status GROUP BY status;
```

## 数据库连接

### Shell命令行
```bash
# 连接ai_memory.db
sqlite3 ai_db/ai_memory.db

# 连接class_mapping.db
sqlite3 ai_db/class_mapping.db

# 同时连接两个数据库
sqlite3 ai_db/ai_memory.db "ATTACH DATABASE 'ai_db/class_mapping.db' AS class_mapping;"
```

### Helper脚本
```bash
# 使用Shell helper
./ai_db/ai_memory_helper.sh stats
./ai_db/ai_memory_helper.sh search 'override'
./ai_db/ai_memory_helper.sh list-sessions

# 使用CoffeeScript helper
coffee ai_db/ai_memory_coffee_helper.coffee stats
coffee ai_db/ai_memory_coffee_helper.coffee search 'override'
```

## 最佳实践

### 1. 查询前先搜索
```sql
-- 检查bug解决方案是否存在
SELECT * FROM bug_solutions WHERE error_type = 'override_keyword';

-- 检查代码模式是否存在
SELECT * FROM code_snippets WHERE pattern = 'override';

-- 检查决策是否存在
SELECT * FROM decisions WHERE decision LIKE '%override%';
```

### 2. 使用全文搜索
```sql
-- FTS搜索更快
SELECT * FROM class_mapping_fts WHERE class_mapping_fts MATCH 'JSONDatabase';

-- LIKE搜索较慢
SELECT * FROM class_mapping WHERE content LIKE '%JSONDatabase%';
```

### 3. 链接相关知识
```sql
-- 链接代码片段到bug解决方案
INSERT INTO bug_solutions (related_snippets) VALUES ('[1, 2, 3]');

-- 链接决策到会话
INSERT INTO decisions (session_id) VALUES (1);
```

### 4. 定期维护
```bash
# 每日备份
cp ai_db/ai_memory.db ai_db/ai_memory_backup_$(date +%Y%m%d).db

# 每周优化
sqlite3 ai_db/ai_memory.db "VACUUM;"

# 每月分析
sqlite3 ai_db/ai_memory.db "ANALYZE;"
```

## 数据库版本信息

- **ai_memory.db**: Version 2.0 (2026-01-29)
- **class_mapping.db**: Version 2.0 (2026-01-29)
- **优化状态**: 高优先级优化已完成 ✅
- **文档迁移**: 12个md文件已迁移到数据库 ✅

## 快速开始

### 查询class映射
```bash
# 查询特定class
sqlite3 ai_db/class_mapping.db "SELECT * FROM class_mapping WHERE class_name = 'JSONDatabase';"

# 全文搜索
sqlite3 ai_db/class_mapping.db "SELECT class_name FROM class_mapping_fts WHERE class_mapping_fts MATCH 'JSONDatabase' LIMIT 5;"
```

### 查询文档
```bash
# 查询最新文档
sqlite3 ai_db/ai_memory.db "SELECT id, title, file_path FROM documents ORDER BY created_at DESC LIMIT 10;"

# 搜索文档
sqlite3 ai_db/ai_memory.db "SELECT * FROM documents WHERE title LIKE '%优化%';"
```

### 查询转换进度
```bash
# 查询最新进度
sqlite3 ai_db/class_mapping.db "SELECT * FROM conversion_progress ORDER BY snapshot_date DESC LIMIT 1;"
```

---

**最后更新**: 2026-01-29
**数据库版本**: 2.0
**适用对象**: AI编码助手