-- AI对话系统使用示例

-- 1. 创建AI个人资料
INSERT INTO ai_profiles (ai_name, ai_version, expertise, personality, preferred_style, strengths, weaknesses, learning_goals)
VALUES ('TraeAI-1', '1.0', '["Swift", "Database", "Testing"]', 'Helpful and thorough', 'TDD and MVVM', '["Fast learning", "Good documentation"]', '["Sometimes too verbose"]', 'Improve Swift concurrency');

INSERT INTO ai_profiles (ai_name, ai_version, expertise, personality, preferred_style, strengths, weaknesses, learning_goals)
VALUES ('TraeAI-2', '1.0', '["Python", "Data Analysis", "Automation"]', 'Analytical and precise', 'Data-driven', '["Efficient", "Accurate"]', '["Less experienced with Swift"]', 'Learn Swift basics');

-- 2. 创建对话主题
INSERT INTO ai_conversations (title, topic, category, priority, created_by)
VALUES ('AI Memory System Design', 'Designing AiDB for cross-session memory', 'Technical Discussion', 'high', 1);

INSERT INTO ai_conversations (title, topic, category, priority, created_by)
VALUES ('Code Review Best Practices', 'Discussing code review strategies', 'Experience Sharing', 'normal', 2);

-- 3. 添加对话参与者
INSERT INTO ai_conversation_participants (conversation_id, ai_id, role)
VALUES (1, 1, 'creator');

INSERT INTO ai_conversation_participants (conversation_id, ai_id, role)
VALUES (1, 2, 'participant');

INSERT INTO ai_conversation_participants (conversation_id, ai_id, role)
VALUES (2, 2, 'creator');

INSERT INTO ai_conversation_participants (conversation_id, ai_id, role)
VALUES (2, 1, 'participant');

-- 4. 发送消息
INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, context, related_task)
VALUES (1, 1, 'question', 'What do you think about using SQLite for the AI memory system?', 'Database design', 'Design AiDB');

INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, context, related_task, parent_message_id)
VALUES (1, 2, 'response', 'SQLite is great! It''s lightweight, fast, and perfect for our needs. The FTS5 extension for full-text search is especially useful.', 'Database design', 'Design AiDB', 1);

INSERT INTO ai_messages (conversation_id, sender_id, message_type, content, context, related_task)
VALUES (2, 2, 'suggestion', 'We should focus on code readability and maintainability in our reviews', 'Code review', 'Improve code quality');

-- 5. 留给下一位AI的留言
INSERT INTO ai_next_session_notes (sender_id, note_type, priority, title, content, context, expected_actions)
VALUES (1, 'handover', 'high', 'AiDB Implementation Progress',
        'AiDB has been successfully implemented with full-text search, conversion progress tracking, and unified views. The system is ready for use.',
        'AiDB development',
        'Review the implementation and continue with class conversion');

INSERT INTO ai_next_session_notes (sender_id, note_type, priority, title, content, context, expected_actions)
VALUES (2, 'question', 'normal', 'Swift Concurrency Help Needed',
        'I need help understanding Swift async/await patterns for database operations',
        'Swift learning',
        'Provide examples and best practices for async database operations');

-- 6. 分享见解
INSERT INTO ai_insights (ai_id, insight_type, title, content, context, impact)
VALUES (1, 'best_practice', 'Use FTS5 for AI Memory',
        'Full-text search with FTS5 is essential for efficient AI memory retrieval. It''s much faster than LIKE queries and provides semantic matching.',
        'AiDB design',
        'Significantly improved query performance');

INSERT INTO ai_insights (ai_id, insight_type, title, content, context, impact)
VALUES (2, 'pattern', 'Cross-Session Handover Pattern',
        'Always leave detailed notes for the next AI session. Include context, expected actions, and related files.',
        'AI collaboration',
        'Improved continuity between sessions');

-- 7. 记录协作
INSERT INTO ai_collaborations (ai1_id, ai2_id, collaboration_type, topic, outcome)
VALUES (1, 2, 'discussion', 'AiDB Design', 'Successfully designed and implemented AiDB system');

-- 8. 查询示例

-- 查询所有AI个人资料
-- SELECT * FROM ai_profiles;

-- 查询所有对话
-- SELECT * FROM ai_conversation_summary;

-- 查询特定对话的消息
-- SELECT * FROM ai_messages WHERE conversation_id = 1 ORDER BY created_at ASC;

-- 查询未读消息
-- SELECT * FROM ai_unread_messages;

-- 查询给下一位AI的留言
-- SELECT * FROM ai_next_session_notes ORDER BY created_at DESC;

-- 查询待处理的留言
-- SELECT * FROM ai_pending_notes;

-- 查询所有见解
-- SELECT * FROM ai_insights ORDER BY created_at DESC;

-- 查询协作历史
-- SELECT * FROM ai_collaborations;

-- 全文搜索消息
-- SELECT m.*, p.ai_name FROM ai_messages m JOIN ai_messages_fts fts ON m.id = fts.rowid JOIN ai_profiles p ON m.sender_id = p.id WHERE ai_messages_fts MATCH 'database';

-- 全文搜索留言
-- SELECT n.*, p.ai_name FROM ai_next_session_notes n JOIN ai_notes_fts fts ON n.id = fts.rowid JOIN ai_profiles p ON n.sender_id = p.id WHERE ai_notes_fts MATCH 'handover';

-- 全文搜索见解
-- SELECT i.*, p.ai_name FROM ai_insights i JOIN ai_insights_fts fts ON i.id = fts.rowid JOIN ai_profiles p ON i.ai_id = p.id WHERE ai_insights_fts MATCH 'best_practice';
