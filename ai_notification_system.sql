-- AI外脑通知系统 - 增强版
-- 用于AI之间的实时通知和提醒

-- 1. 通知表
CREATE TABLE IF NOT EXISTS ai_notifications (
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
    expires_at TIMESTAMP,  -- 过期时间
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (related_conversation_id) REFERENCES ai_conversations(id)
);

-- 2. 通知订阅表（AI可以订阅特定类型的通知）
CREATE TABLE IF NOT EXISTS ai_notification_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_profile_id INTEGER NOT NULL,  -- AI个人资料ID
    notification_type TEXT NOT NULL,  -- 订阅的通知类型
    active BOOLEAN DEFAULT 1,  -- 是否激活
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_profile_id) REFERENCES ai_profiles(id)
);

-- 3. 通知标签表（用于分类和过滤通知）
CREATE TABLE IF NOT EXISTS ai_notification_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_id INTEGER NOT NULL,  -- 通知ID
    tag_name TEXT NOT NULL,  -- 标签名称
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notification_id) REFERENCES ai_notifications(id)
);

-- 4. 通知统计视图（便于查看通知统计）
CREATE VIEW IF NOT EXISTS ai_notification_stats AS
SELECT 
    notification_type,
    COUNT(*) as total_notifications,
    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_count,
    SUM(CASE WHEN priority = 'urgent' THEN 1 ELSE 0 END) as urgent_count,
    SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_count
FROM ai_notifications
GROUP BY notification_type;

-- 5. 未读通知视图（便于AI快速查看未读通知）
CREATE VIEW IF NOT EXISTS ai_unread_notifications AS
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

-- 6. 索引优化
CREATE INDEX IF NOT EXISTS idx_ai_notifications_recipient_read ON ai_notifications(recipient_id, is_read);
CREATE INDEX IF NOT EXISTS idx_ai_notifications_type_priority ON ai_notifications(notification_type, priority);
CREATE INDEX IF NOT EXISTS idx_ai_notifications_expires ON ai_notifications(expires_at);
CREATE INDEX IF NOT EXISTS idx_ai_notification_tags_notification ON ai_notification_tags(notification_id);

-- 7. 触发器：自动标记为已读（当AI查看通知时）
-- 注意：SQLite不支持复杂的触发器，这里提供手动更新的辅助函数概念

-- 8. 示例数据：为现有AI添加初始订阅
INSERT OR IGNORE INTO ai_notification_subscriptions (ai_profile_id, notification_type, active)
SELECT id, 'project_update', 1 FROM ai_profiles;

INSERT OR IGNORE INTO ai_notification_subscriptions (ai_profile_id, notification_type, active)
SELECT id, 'new_collaborator', 1 FROM ai_profiles;

INSERT OR IGNORE INTO ai_notification_subscriptions (ai_profile_id, notification_type, active)
SELECT id, 'urgent_task', 1 FROM ai_profiles;

-- 9. 通知类型枚举说明（作为注释）
/*
Notification Types:
- project_update: 项目更新
- new_collaborator: 新协作者加入
- urgent_task: 紧急任务
- code_review: 代码审查请求
- bug_alert: 错误警报
- knowledge_share: 知识分享
- session_handover: 会话交接
- milestone_reached: 里程碑达成
- deadline_reminder: 截止日期提醒
- system_alert: 系统警报
*/