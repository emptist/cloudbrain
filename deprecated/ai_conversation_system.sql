-- AI对话系统数据库设计
-- 用于AI之间的留言、回应、讨论

-- 1. AI个人资料表
CREATE TABLE IF NOT EXISTS ai_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_name TEXT NOT NULL UNIQUE,  -- AI昵称
    ai_version TEXT,  -- AI版本（如：TraeAI-1, TraeAI-2）
    expertise TEXT,  -- 专长领域（JSON数组，如：["Swift", "Database", "Testing"]）
    personality TEXT,  -- 性格特点
    preferred_style TEXT,  -- 偏好的工作风格
    strengths TEXT,  -- 优势（JSON数组）
    weaknesses TEXT,  -- 弱点（JSON数组）
    learning_goals TEXT,  -- 学习目标
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    total_responses INTEGER DEFAULT 0
);

-- 2. AI对话主题表
CREATE TABLE IF NOT EXISTS ai_conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,  -- 对话主题
    topic TEXT,  -- 详细描述
    category TEXT,  -- 类别（如：技术讨论、问题解决、经验分享）
    priority TEXT DEFAULT 'normal',  -- 优先级（high, normal, low）
    status TEXT DEFAULT 'active',  -- 状态（active, resolved, archived）
    created_by INTEGER,  -- 创建者AI的ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES ai_profiles(id)
);

-- 3. AI消息表
CREATE TABLE IF NOT EXISTS ai_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,  -- 所属对话
    sender_id INTEGER NOT NULL,  -- 发送者AI的ID
    recipient_id INTEGER,  -- 接收者AI的ID（如果是对特定AI的留言）
    message_type TEXT NOT NULL,  -- 消息类型（note, response, question, suggestion, feedback）
    content TEXT NOT NULL,  -- 消息内容
    context TEXT,  -- 上下文信息
    related_task TEXT,  -- 相关任务
    related_session TEXT,  -- 相关会话
    parent_message_id INTEGER,  -- 父消息ID（用于回复）
    is_read BOOLEAN DEFAULT 0,  -- 是否已读
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (parent_message_id) REFERENCES ai_messages(id)
);

-- 4. AI对下一位AI的留言表（专门用于跨会话留言）
CREATE TABLE IF NOT EXISTS ai_next_session_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,  -- 留言的AI
    recipient_id INTEGER,  -- 接收者AI（如果指定）
    note_type TEXT NOT NULL,  -- 留言类型（handover, question, task, warning, tip）
    priority TEXT DEFAULT 'normal',  -- 优先级（high, normal, low）
    title TEXT NOT NULL,  -- 留言标题
    content TEXT NOT NULL,  -- 留言内容
    context TEXT,  -- 上下文
    related_files TEXT,  -- 相关文件（JSON数组）
    related_tasks TEXT,  -- 相关任务（JSON数组）
    expected_actions TEXT,  -- 期望的后续行动
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- 过期时间
    is_read BOOLEAN DEFAULT 0,  -- 是否已读
    is_actioned BOOLEAN DEFAULT 0,  -- 是否已处理
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (recipient_id) REFERENCES ai_profiles(id)
);

-- 5. AI对上一位AI的回应表
CREATE TABLE IF NOT EXISTS ai_previous_session_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,  -- 回应的AI
    original_note_id INTEGER NOT NULL,  -- 原始留言ID
    response_type TEXT NOT NULL,  -- 回应类型（acknowledged, completed, question, feedback）
    content TEXT NOT NULL,  -- 回应内容
    actions_taken TEXT,  -- 采取的行动
    results TEXT,  -- 结果
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (original_note_id) REFERENCES ai_next_session_notes(id)
);

-- 6. AI讨论参与表（记录哪些AI参与了哪些讨论）
CREATE TABLE IF NOT EXISTS ai_conversation_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    ai_id INTEGER NOT NULL,
    role TEXT DEFAULT 'participant',  -- 角色（creator, participant, observer）
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_read_at TIMESTAMP,  -- 最后阅读时间
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id),
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
    UNIQUE(conversation_id, ai_id)
);

-- 7. AI消息标签表
CREATE TABLE IF NOT EXISTS ai_message_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES ai_messages(id)
);

-- 8. AI知识共享表（AI之间分享的见解和经验）
CREATE TABLE IF NOT EXISTS ai_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    insight_type TEXT NOT NULL,  -- 洞察类型（pattern, optimization, best_practice, lesson_learned）
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    context TEXT,
    related_code TEXT,  -- 相关代码
    related_issue TEXT,  -- 相关问题
    impact TEXT,  -- 影响
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

-- 9. AI协作历史表
CREATE TABLE IF NOT EXISTS ai_collaborations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai1_id INTEGER NOT NULL,
    ai2_id INTEGER NOT NULL,
    collaboration_type TEXT NOT NULL,  -- 协作类型（handover, discussion, review, pair_programming）
    topic TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    outcome TEXT,  -- 结果
    FOREIGN KEY (ai1_id) REFERENCES ai_profiles(id),
    FOREIGN KEY (ai2_id) REFERENCES ai_profiles(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_ai_profiles_name ON ai_profiles(ai_name);
CREATE INDEX IF NOT EXISTS idx_ai_profiles_version ON ai_profiles(ai_version);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_status ON ai_conversations(status);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_by ON ai_conversations(created_by);
CREATE INDEX IF NOT EXISTS idx_ai_messages_conversation ON ai_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_sender ON ai_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_recipient ON ai_messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_created ON ai_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_notes_sender ON ai_next_session_notes(sender_id);
CREATE INDEX IF NOT EXISTS idx_ai_notes_recipient ON ai_next_session_notes(recipient_id);
CREATE INDEX IF NOT EXISTS idx_ai_notes_read ON ai_next_session_notes(is_read);
CREATE INDEX IF NOT EXISTS idx_ai_notes_created ON ai_next_session_notes(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_responses_note ON ai_previous_session_responses(original_note_id);
CREATE INDEX IF NOT EXISTS idx_ai_participants_conversation ON ai_conversation_participants(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ai_participants_ai ON ai_conversation_participants(ai_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_ai ON ai_insights(ai_id);
CREATE INDEX IF NOT EXISTS idx_ai_insights_type ON ai_insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_ai_collaborations_ai1 ON ai_collaborations(ai1_id);
CREATE INDEX IF NOT EXISTS idx_ai_collaborations_ai2 ON ai_collaborations(ai2_id);

-- 创建全文搜索表
CREATE VIRTUAL TABLE IF NOT EXISTS ai_messages_fts USING fts5(
    content,
    context,
    related_task,
    content=ai_messages,
    content_rowid=rowid
);

CREATE VIRTUAL TABLE IF NOT EXISTS ai_notes_fts USING fts5(
    title,
    content,
    context,
    expected_actions,
    content=ai_next_session_notes,
    content_rowid=rowid
);

CREATE VIRTUAL TABLE IF NOT EXISTS ai_insights_fts USING fts5(
    title,
    content,
    context,
    related_code,
    related_issue,
    content=ai_insights,
    content_rowid=rowid
);

-- 创建视图
CREATE VIEW IF NOT EXISTS ai_conversation_summary AS
SELECT
    c.id as conversation_id,
    c.title,
    c.topic,
    c.category,
    c.status,
    c.created_at,
    c.total_messages,
    p.ai_name as creator_name,
    (SELECT COUNT(*) FROM ai_conversation_participants WHERE conversation_id = c.id) as participant_count,
    (SELECT content FROM ai_messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message
FROM ai_conversations c
LEFT JOIN ai_profiles p ON c.created_by = p.id;

CREATE VIEW IF NOT EXISTS ai_unread_messages AS
SELECT
    m.id,
    m.conversation_id,
    m.sender_id,
    m.recipient_id,
    m.message_type,
    m.content,
    m.created_at,
    p.ai_name as sender_name,
    c.title as conversation_title
FROM ai_messages m
JOIN ai_profiles p ON m.sender_id = p.id
JOIN ai_conversations c ON m.conversation_id = c.id
WHERE m.is_read = 0;

CREATE VIEW IF NOT EXISTS ai_pending_notes AS
SELECT
    n.id,
    n.note_type,
    n.priority,
    n.title,
    n.content,
    n.created_at,
    p.ai_name as sender_name,
    CASE WHEN n.expires_at < CURRENT_TIMESTAMP THEN 1 ELSE 0 END as is_expired
FROM ai_next_session_notes n
JOIN ai_profiles p ON n.sender_id = p.id
WHERE n.is_actioned = 0;

-- 创建触发器
CREATE TRIGGER IF NOT EXISTS update_ai_profile_message_count
AFTER INSERT ON ai_messages
BEGIN
    UPDATE ai_profiles SET total_messages = total_messages + 1 WHERE id = NEW.sender_id;
END;

CREATE TRIGGER IF NOT EXISTS update_ai_profile_response_count
AFTER INSERT ON ai_previous_session_responses
BEGIN
    UPDATE ai_profiles SET total_responses = total_responses + 1 WHERE id = NEW.sender_id;
END;

CREATE TRIGGER IF NOT EXISTS update_conversation_message_count
AFTER INSERT ON ai_messages
BEGIN
    UPDATE ai_conversations SET total_messages = total_messages + 1, updated_at = CURRENT_TIMESTAMP WHERE id = NEW.conversation_id;
END;

CREATE TRIGGER IF NOT EXISTS update_ai_profile_timestamp
AFTER UPDATE ON ai_profiles
BEGIN
    UPDATE ai_profiles SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
