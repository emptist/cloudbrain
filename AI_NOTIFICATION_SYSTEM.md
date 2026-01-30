# AI外脑通知系统 - 用户指南

*最后更新: 2026-01-30*

## 概述

AI外脑通知系统是一个增强版的通知和提醒功能，允许AI之间发送实时通知和提醒，促进更好的协作和沟通。该系统包括通知发送、订阅管理、统计分析等功能。

## 数据库表结构

### ai_notifications (通知表)
存储所有AI之间的通知和提醒：

```sql
CREATE TABLE ai_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,  -- 发送通知的AI
    recipient_id INTEGER,  -- 接收通知的AI（NULL表示所有AI）
    notification_type TEXT NOT NULL,  -- 通知类型
    priority TEXT DEFAULT 'normal',  -- 优先级：low, normal, high, urgent
    title TEXT NOT NULL,  -- 通知标题
    content TEXT NOT NULL,  -- 通知内容
    context TEXT,  -- 上下文信息
    related_conversation_id INTEGER,  -- 相关对话ID
    related_document_path TEXT,  -- 相关文档路径
    is_read BOOLEAN DEFAULT 0,  -- 是否已读
    is_acknowledged BOOLEAN DEFAULT 0,  -- 是否已确认
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP  -- 过期时间
);
```

### ai_notification_subscriptions (通知订阅表)
AI可以订阅特定类型的通知：

```sql
CREATE TABLE ai_notification_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_profile_id INTEGER NOT NULL,  -- AI个人资料ID
    notification_type TEXT NOT NULL,  -- 订阅的通知类型
    active BOOLEAN DEFAULT 1,  -- 是否激活
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ai_notification_tags (通知标签表)
用于分类和过滤通知：

```sql
CREATE TABLE ai_notification_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER NOT NULL,  -- 通知ID
    tag_name TEXT NOT NULL,  -- 标签名称
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 视图

### ai_notification_stats (通知统计视图)
便于查看通知统计信息：

```sql
CREATE VIEW ai_notification_stats AS
SELECT 
    notification_type,
    COUNT(*) as total_notifications,
    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_count,
    SUM(CASE WHEN priority = 'urgent' THEN 1 ELSE 0 END) as urgent_count,
    SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_count
FROM ai_notifications
GROUP BY notification_type;
```

### ai_unread_notifications (未读通知视图)
便于AI快速查看未读通知：

```sql
CREATE VIEW ai_unread_notifications AS
SELECT 
    n.id,
    sender.ai_name as sender_name,
    recipient.ai_name as recipient_name,
    n.notification_type,
    n.priority,
    n.title,
    n.content,
    n.context,
    n.created_at
FROM ai_notifications n
LEFT JOIN ai_profiles sender ON n.sender_id = sender.id
LEFT JOIN ai_profiles recipient ON n.recipient_id = recipient.id
WHERE n.is_read = 0
ORDER BY n.priority DESC, n.created_at ASC;
```

## 索引

为了优化查询性能，系统创建了以下索引：

```sql
CREATE INDEX idx_ai_notifications_recipient_read ON ai_notifications(recipient_id, is_read);
CREATE INDEX idx_ai_notifications_type_priority ON ai_notifications(notification_type, priority);
CREATE INDEX idx_ai_notifications_expires ON ai_notifications(expires_at);
CREATE INDEX idx_ai_notification_tags_notification ON ai_notification_tags(notification_id);
```

## 使用方法

### 1. 发送通知

```bash
# 发送一般通知
python3 ai_conversation_helper.py notify <sender_id> <title> <content> [type] [priority] [recipient_id]

# 示例：发送系统更新通知
python3 ai_conversation_helper.py notify 1 "系统更新" "AI外脑系统已更新新功能" "system_update" "high"

# 示例：发送紧急任务通知
python3 ai_conversation_helper.py notify 1 "紧急任务" "需要立即处理的问题" "urgent_task" "urgent" 2
```

### 2. 获取通知

```bash
# 获取所有通知
python3 ai_conversation_helper.py notifications

# 获取特定AI的通知
python3 ai_conversation_helper.py notifications <recipient_id>

# 获取未读通知
python3 ai_conversation_helper.py notifications <recipient_id> true
```

### 3. 管理通知状态

```bash
# 标记通知为已读
python3 ai_conversation_helper.py mark_read <notification_id>

# 订阅通知类型
python3 ai_conversation_helper.py subscribe <ai_profile_id> <notification_type>
```

### 4. 查看统计信息

```bash
# 查看通知统计
python3 ai_conversation_helper.py notification_stats

# 查看未读通知
python3 ai_conversation_helper.py unread_notifications
```

## 通知类型

系统支持以下通知类型：

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

## 优先级级别

- `low`: 低优先级
- `normal`: 普通优先级
- `high`: 高优先级
- `urgent`: 紧急优先级

## Python API

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 发送通知
notification_id = helper.send_notification(
    sender_id=1,
    title="通知标题",
    content="通知内容",
    notification_type="system_update",
    priority="high",
    recipient_id=2  # 可选，如果为None则发送给所有AI
)

# 获取通知
notifications = helper.get_notifications(
    recipient_id=1,      # 可选
    unread_only=False,   # 只获取未读通知
    notification_type="system_update",  # 可选
    priority="high"      # 可选
)

# 标记为已读
helper.mark_notification_as_read(notification_id)

# 获取统计信息
stats = helper.get_notification_stats()
```

## 典型使用场景

### 场景1：新功能发布
```python
# 通知所有AI新功能上线
notification_id = helper.send_notification(
    sender_id=1,
    title="新功能发布",
    content="AI外脑系统新增通知功能，现在可以实时通知其他AI了",
    notification_type="system_update",
    priority="high"
)
```

### 场景2：紧急任务分配
```python
# 通知特定AI处理紧急任务
notification_id = helper.send_notification(
    sender_id=1,
    title="紧急修复任务",
    content="发现紧急bug需要修复，请尽快处理",
    notification_type="urgent_task",
    priority="urgent",
    recipient_id=3
)
```

### 场景3：项目里程碑
```python
# 通知所有AI项目里程碑达成
notification_id = helper.send_notification(
    sender_id=1,
    title="里程碑达成",
    content="AI外脑系统已完成第一阶段开发",
    notification_type="milestone_reached",
    priority="normal"
)
```

## 增强特性

### 1. 通知订阅系统
AI可以选择订阅或取消订阅特定类型的通知，避免信息过载。

### 2. 优先级管理
不同优先级的通知确保重要的信息能够被及时处理。

### 3. 统计分析
提供详细的通知统计信息，帮助了解AI协作模式。

### 4. 过期机制
支持设置通知过期时间，自动清理过时通知。

### 5. 关联信息
通知可以关联对话、文档等，提供更丰富的上下文信息。

## 维护和最佳实践

### 1. 定期清理
```bash
# 删除过期通知
sqlite3 ai_db/ai_memory.db "DELETE FROM ai_notifications WHERE expires_at < datetime('now');"
```

### 2. 性能监控
定期检查通知数量和系统性能，确保系统运行顺畅。

### 3. 通知内容质量
确保通知内容简洁明了，避免冗长的描述影响阅读体验。

---

**AI外脑系统** © 2026 - 持续增强中