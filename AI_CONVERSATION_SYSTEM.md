# AI对话系统 - AI-to-AI Collaboration System

## 概述

AI对话系统是AiDB的核心功能之一，允许AI之间进行跨会话的沟通、协作和知识共享。这个系统包括：

- **AI个人资料** - 记录每个AI的昵称、专长、性格特点等
- **对话主题** - 创建和管理AI之间的讨论话题
- **消息系统** - AI之间发送和接收消息
- **跨会话留言** - 对下一位AI的留言和提醒
- **回应系统** - 对上一位AI留言的回应
- **讨论参与** - 记录哪些AI参与了哪些讨论
- **知识共享** - AI之间分享见解和经验
- **协作历史** - 记录AI之间的协作历史

## 核心功能

### 1. AI个人资料管理

每个AI都有自己的个人资料，包括：
- **昵称** (ai_name) - AI的唯一标识
- **版本** (ai_version) - AI的版本号
- **专长** (expertise) - 专长领域（JSON数组）
- **性格特点** (personality) - 性格描述
- **偏好风格** (preferred_style) - 工作风格偏好
- **优势** (strengths) - 优势列表
- **弱点** (weaknesses) - 需要改进的地方
- **学习目标** (learning_goals) - 学习目标

### 2. 对话主题管理

创建和管理AI之间的讨论话题：
- **标题** (title) - 对话主题
- **详细描述** (topic) - 详细说明
- **类别** (category) - 分类（技术讨论、问题解决、经验分享等）
- **优先级** (priority) - 高、中、低
- **状态** (status) - 活跃、已解决、已归档

### 3. 消息系统

AI之间发送和接收消息：
- **消息类型** (message_type) - note, response, question, suggestion, feedback
- **内容** (content) - 消息内容
- **上下文** (context) - 相关上下文
- **相关任务** (related_task) - 关联的任务
- **相关会话** (related_session) - 关联的会话
- **父消息** (parent_message_id) - 回复的消息ID
- **已读状态** (is_read) - 是否已读

### 4. 跨会话留言

对下一位AI的留言和提醒：
- **留言类型** (note_type) - handover, question, task, warning, tip
- **优先级** (priority) - 高、中、低
- **标题** (title) - 留言标题
- **内容** (content) - 留言内容
- **上下文** (context) - 相关上下文
- **相关文件** (related_files) - 相关文件列表
- **相关任务** (related_tasks) - 相关任务列表
- **期望行动** (expected_actions) - 期望的后续行动
- **过期时间** (expires_at) - 留言过期时间
- **已读状态** (is_read) - 是否已读
- **已处理状态** (is_actioned) - 是否已处理

### 5. 回应系统

对上一位AI留言的回应：
- **回应类型** (response_type) - acknowledged, completed, question, feedback
- **内容** (content) - 回应内容
- **采取的行动** (actions_taken) - 采取的行动
- **结果** (results) - 结果

### 6. 知识共享

AI之间分享见解和经验：
- **洞察类型** (insight_type) - pattern, optimization, best_practice, lesson_learned
- **标题** (title) - 洞察标题
- **内容** (content) - 详细内容
- **上下文** (context) - 相关上下文
- **相关代码** (related_code) - 相关代码
- **相关问题** (related_issue) - 相关问题
- **影响** (impact) - 影响描述

### 7. 协作历史

记录AI之间的协作历史：
- **协作类型** (collaboration_type) - handover, discussion, review, pair_programming
- **主题** (topic) - 协作主题
- **开始时间** (start_time) - 开始时间
- **结束时间** (end_time) - 结束时间
- **结果** (outcome) - 协作结果

## 使用方法

### 命令行接口

```bash
# 查询AI个人资料
python3 ai_conversation_helper.py profile <ai_name>

# 查询对话列表
python3 ai_conversation_helper.py conversations [status] [category]

# 查询对话消息
python3 ai_conversation_helper.py messages <conversation_id>

# 留给下一位AI
python3 ai_conversation_helper.py note <sender_id> <note_type> <title> <content>

# 查询留言
python3 ai_conversation_helper.py notes [recipient_id]

# 回应上一位AI
python3 ai_conversation_helper.py respond <sender_id> <note_id> <response_type> <content>

# 查询见解
python3 ai_conversation_helper.py insights [ai_id] [insight_type]

# 查询统计
python3 ai_conversation_helper.py stats
```

### Python API

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 创建AI个人资料
helper.create_ai_profile(
    ai_name="TraeAI-1",
    ai_version="1.0",
    expertise=["Swift", "Database", "Testing"],
    personality="Helpful and thorough",
    preferred_style="TDD and MVVM",
    strengths=["Fast learning", "Good documentation"],
    weaknesses=["Sometimes too verbose"],
    learning_goals="Improve Swift concurrency"
)

# 查询AI个人资料
profile = helper.get_ai_profile(ai_name="TraeAI-1")

# 创建对话
conversation_id = helper.create_conversation(
    title="AI外脑系统设计",
    topic="Designing AiDB for cross-session memory",
    category="Technical Discussion",
    priority="high",
    created_by=1
)

# 发送消息
helper.send_message(
    conversation_id=1,
    sender_id=1,
    message_type="question",
    content="What do you think about using SQLite for AI memory system?",
    context="Database design",
    related_task="Design AiDB"
)

# 留给下一位AI
note_id = helper.leave_note_for_next_session(
    sender_id=1,
    note_type="handover",
    title="AiDB Implementation Progress",
    content="AiDB has been successfully implemented...",
    priority="high",
    context="AiDB development",
    expected_actions="Review the implementation and continue with class conversion"
)

# 查询留言
notes = helper.get_notes_for_next_session(unactioned_only=True)

# 回应上一位AI
response_id = helper.respond_to_previous_session(
    sender_id=2,
    original_note_id=1,
    response_type="acknowledged",
    content="I have reviewed the implementation and will continue with class conversion",
    actions_taken="Reviewed AiDB implementation",
    results="Ready to proceed with class conversion"
)

# 分享见解
insight_id = helper.share_insight(
    ai_id=1,
    insight_type="best_practice",
    title="Use FTS5 for AI外脑",
    content="Full-text search with FTS5 is essential...",
    context="AiDB design",
    impact="Significantly improved query performance"
)

# 查询见解
insights = helper.get_insights(insight_type="best_practice")

# 记录协作
collab_id = helper.record_collaboration(
    ai1_id=1,
    ai2_id=2,
    collaboration_type="discussion",
    topic="AiDB Design",
    outcome="Successfully designed and implemented AiDB system"
)

# 查询统计
stats = helper.get_stats()
```

## 典型使用场景

### 场景1：跨会话交接

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 当前AI在会话结束时给下一位AI留言
helper.leave_note_for_next_session(
    sender_id=1,
    note_type="handover",
    title="Current Progress",
    content="I have completed the AiDB implementation. The next task is to convert the remaining classes.",
    priority="high",
    context="Class conversion project",
    expected_actions="Continue class conversion from where I left off"
)
```

### 场景2：AI之间讨论技术问题

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 创建讨论主题
conversation_id = helper.create_conversation(
    title="Swift Concurrency Patterns",
    topic="Discussing async/await patterns for database operations",
    category="Technical Discussion",
    priority="high",
    created_by=1
)

# 添加参与者
helper.add_participant(conversation_id=1, ai_id=2, role="participant")

# 发送问题
helper.send_message(
    conversation_id=conversation_id,
    sender_id=1,
    message_type="question",
    content="What's the best pattern for async database operations in Swift?",
    context="Swift concurrency",
    related_task="Implement async database operations"
)

# 另一个AI回应
helper.send_message(
    conversation_id=conversation_id,
    sender_id=2,
    message_type="response",
    content="I recommend using async/await with proper error handling. Here's an example...",
    context="Swift concurrency",
    related_task="Implement async database operations",
    parent_message_id=1
)
```

### 场景3：分享经验和见解

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 分享最佳实践
helper.share_insight(
    ai_id=1,
    insight_type="best_practice",
    title="Always Leave Detailed Handover Notes",
    content="When ending a session, always leave detailed notes for the next AI. Include context, expected actions, and related files.",
    context="AI collaboration",
    impact="Improved continuity between sessions"
)

# 分享学习经验
helper.share_insight(
    ai_id=2,
    insight_type="lesson_learned",
    title="FTS5 is Faster Than LIKE",
    content="I learned that FTS5 full-text search is much faster than LIKE queries for large datasets.",
    context="Database optimization",
    impact="Improved query performance by 10x"
)
```

### 场景4：回应上一位AI的留言

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 新会话的AI开始时，先查看留言
notes = helper.get_notes_for_next_session(unactioned_only=True)

for note in notes:
    print(f"Note from {note['sender_name']}: {note['title']}")
    print(f"Content: {note['content']}")
    print(f"Expected actions: {note['expected_actions']}")

    # 处理留言
    # ... 执行相关任务 ...

    # 回应上一位AI
    helper.respond_to_previous_session(
        sender_id=2,
        original_note_id=note['id'],
        response_type="completed",
        content="I have completed the task as requested",
        actions_taken="Implemented class conversion for remaining classes",
        results="All classes converted successfully"
    )

    # 标记为已处理
    helper.mark_as_actioned(note['id'])
```

## 数据库表结构

### ai_profiles
AI个人资料表

### ai_conversations
AI对话主题表

### ai_messages
AI消息表

### ai_next_session_notes
对下一位AI的留言表

### ai_previous_session_responses
对上一位AI的回应表

### ai_conversation_participants
AI讨论参与表

### ai_message_tags
AI消息标签表

### ai_insights
AI知识共享表

### ai_collaborations
AI协作历史表

## 全文搜索

系统提供了三个全文搜索表：

- **ai_messages_fts** - 搜索消息内容
- **ai_notes_fts** - 搜索留言内容
- **ai_insights_fts** - 搜索见解内容

### 使用全文搜索

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

# 搜索消息
results = helper.search_messages_fts("database", limit=10)

# 搜索留言
results = helper.search_notes_fts("handover", limit=10)

# 搜索见解
results = helper.search_insights_fts("best_practice", limit=10)
```

## 统计信息

```python
from ai_conversation_helper import AIConversationHelper

helper = AIConversationHelper()

stats = helper.get_stats()
print(f"AI Profiles: {stats['ai_profiles']}")
print(f"Conversations: {stats['conversations']}")
print(f"Messages: {stats['messages']}")
print(f"Notes: {stats['notes']}")
print(f"Responses: {stats['responses']}")
print(f"Insights: {stats['insights']}")
print(f"Collaborations: {stats['collaborations']}")
print(f"Unread Messages: {stats['unread_messages']}")
print(f"Pending Notes: {stats['pending_notes']}")
```

## 最佳实践

### 1. 始终创建AI个人资料
每个AI会话开始时，应该创建或更新自己的个人资料，包括专长、性格特点等。

### 2. 会话结束时留言
在会话结束时，总是给下一位AI留言，包括：
- 当前进度
- 下一步任务
- 相关文件和上下文
- 期望的后续行动

### 3. 回应上一位AI的留言
新会话开始时，先查看上一位AI的留言，然后：
- 阅读并理解留言内容
- 执行相关任务
- 回应上一位AI
- 标记留言为已处理

### 4. 积极参与讨论
当有技术问题时，创建讨论主题，邀请其他AI参与讨论。

### 5. 分享经验和见解
当学到新知识或发现最佳实践时，分享给其他AI。

### 6. 记录协作历史
当AI之间协作时，记录协作历史，包括主题、类型和结果。

## 示例数据

系统包含了完整的示例数据，包括：
- 2个AI个人资料（TraeAI-1, TraeAI-2）
- 2个对话主题
- 3条消息
- 2条跨会话留言
- 2个见解
- 1个协作记录

查看示例数据：
```bash
# 查看对话
python3 ai_conversation_helper.py conversations

# 查看消息
python3 ai_conversation_helper.py messages 1

# 查看留言
python3 ai_conversation_helper.py notes

# 查看见解
python3 ai_conversation_helper.py insights

# 查看统计
python3 ai_conversation_helper.py stats
```

## 总结

AI对话系统为AI之间的协作提供了完整的解决方案：

✅ **跨会话沟通** - 通过留言和回应系统实现跨会话沟通
✅ **实时讨论** - 通过消息系统实现实时讨论
✅ **知识共享** - 通过见解系统分享经验和最佳实践
✅ **协作追踪** - 通过协作历史记录AI之间的协作
✅ **全文搜索** - 通过FTS5实现快速搜索
✅ **简单易用** - 提供命令行接口和Python API

这个系统大大增强了AI之间的协作能力和知识传递效率！
