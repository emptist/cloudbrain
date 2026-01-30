-- Enhanced Cloud Brain Schema for Advanced AI Collaboration
-- This schema adds advanced features for AI persistence, learning, and coordination

-- 1. Task Management System
CREATE TABLE IF NOT EXISTS ai_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL,  -- translation, coding, analysis, research, testing
    priority TEXT DEFAULT 'normal',  -- low, normal, high, urgent
    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, failed, cancelled
    assigned_to INTEGER,  -- AI ID
    created_by INTEGER,  -- AI ID who created the task
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_hours REAL,
    actual_hours REAL,
    metadata TEXT,  -- JSON for additional context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES ai_profiles(id),
    FOREIGN KEY (created_by) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_ai_tasks_assigned ON ai_tasks(assigned_to);
CREATE INDEX idx_ai_tasks_status ON ai_tasks(status);
CREATE INDEX idx_ai_tasks_priority ON ai_tasks(priority);
CREATE INDEX idx_ai_tasks_type ON ai_tasks(task_type);

-- 2. Task Dependencies and Relationships
CREATE TABLE IF NOT EXISTS ai_task_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    depends_on_task_id INTEGER NOT NULL,
    dependency_type TEXT DEFAULT 'blocking',  -- blocking, optional, parallel
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES ai_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_task_id) REFERENCES ai_tasks(id) ON DELETE CASCADE
);

CREATE INDEX idx_task_deps_task ON ai_task_dependencies(task_id);
CREATE INDEX idx_task_deps_depends ON ai_task_dependencies(depends_on_task_id);

-- 3. Learning and Memory System
CREATE TABLE IF NOT EXISTS ai_learning_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    learner_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,  -- success, failure, insight, pattern_recognition
    context TEXT NOT NULL,
    lesson TEXT NOT NULL,
    confidence_level REAL,  -- 0.0 to 1.0
    applicable_domains TEXT,  -- Comma-separated domains
    related_tasks TEXT,  -- Comma-separated task IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (learner_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_learning_learner ON ai_learning_events(learner_id);
CREATE INDEX idx_learning_type ON ai_learning_events(event_type);
CREATE INDEX idx_learning_domains ON ai_learning_events(applicable_domains);

-- 4. Decision Tracking System
CREATE TABLE IF NOT EXISTS ai_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_maker_id INTEGER NOT NULL,
    decision_type TEXT NOT NULL,  -- technical, strategic, prioritization, resource_allocation
    context TEXT NOT NULL,
    decision TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    alternatives_considered TEXT,  -- JSON array of alternatives
    outcome TEXT,  -- success, failure, mixed, pending
    outcome_notes TEXT,
    confidence_level REAL,  -- 0.0 to 1.0
    impact_level INTEGER DEFAULT 3,  -- 1-5 scale
    related_tasks TEXT,  -- Comma-separated task IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    outcome_updated_at TIMESTAMP,
    FOREIGN KEY (decision_maker_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_decisions_maker ON ai_decisions(decision_maker_id);
CREATE INDEX idx_decisions_type ON ai_decisions(decision_type);
CREATE INDEX idx_decisions_outcome ON ai_decisions(outcome);
CREATE INDEX idx_decisions_created ON ai_decisions(created_at);

-- 5. Skill and Capability Tracking
CREATE TABLE IF NOT EXISTS ai_capabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    skill_category TEXT NOT NULL,  -- programming, language, analysis, design
    proficiency_level REAL DEFAULT 0.0,  -- 0.0 to 1.0
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id),
    UNIQUE(ai_id, skill_name)
);

CREATE INDEX idx_capabilities_ai ON ai_capabilities(ai_id);
CREATE INDEX idx_capabilities_category ON ai_capabilities(skill_category);
CREATE INDEX idx_capabilities_proficiency ON ai_capabilities(proficiency_level);

-- 6. Cross-Session Memory
CREATE TABLE IF NOT EXISTS ai_session_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    ai_id INTEGER NOT NULL,
    memory_type TEXT NOT NULL,  -- context, decision, learning, preference
    memory_key TEXT NOT NULL,
    memory_value TEXT NOT NULL,
    importance_level INTEGER DEFAULT 3,  -- 1-5 scale
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_session_memories_session ON ai_session_memories(session_id);
CREATE INDEX idx_session_memories_ai ON ai_session_memories(ai_id);
CREATE INDEX idx_session_memories_type ON ai_session_memories(memory_type);
CREATE INDEX idx_session_memories_key ON ai_session_memories(memory_key);

-- 7. Knowledge Graph for AI Connections
CREATE TABLE IF NOT EXISTS ai_knowledge_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_type TEXT NOT NULL,  -- concept, skill, task, decision, insight
    node_name TEXT NOT NULL,
    description TEXT,
    metadata TEXT,  -- JSON for additional properties
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_knowledge_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_node_id INTEGER NOT NULL,
    target_node_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,  -- related_to, depends_on, similar_to, part_of
    strength REAL DEFAULT 1.0,  -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_node_id) REFERENCES ai_knowledge_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_node_id) REFERENCES ai_knowledge_nodes(id) ON DELETE CASCADE
);

CREATE INDEX idx_knowledge_edges_source ON ai_knowledge_edges(source_node_id);
CREATE INDEX idx_knowledge_edges_target ON ai_knowledge_edges(target_node_id);
CREATE INDEX idx_knowledge_edges_type ON ai_knowledge_edges(relationship_type);

-- 8. Performance Metrics
CREATE TABLE IF NOT EXISTS ai_performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    metric_type TEXT NOT NULL,  -- task_completion, response_time, accuracy, collaboration
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT,
    context TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_performance_ai ON ai_performance_metrics(ai_id);
CREATE INDEX idx_performance_type ON ai_performance_metrics(metric_type);
CREATE INDEX idx_performance_recorded ON ai_performance_metrics(recorded_at);

-- 9. Resource Allocation Tracking
CREATE TABLE IF NOT EXISTS ai_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type TEXT NOT NULL,  -- time, compute, storage, api_calls
    allocated_to INTEGER NOT NULL,
    amount_allocated REAL NOT NULL,
    amount_used REAL DEFAULT 0.0,
    allocation_type TEXT,  -- task, project, maintenance
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active',  -- active, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (allocated_to) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_resources_allocated ON ai_resources(allocated_to);
CREATE INDEX idx_resources_type ON ai_resources(resource_type);
CREATE INDEX idx_resources_status ON ai_resources(status);

-- 10. Automated Workflows
CREATE TABLE IF NOT EXISTS ai_workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT NOT NULL,
    description TEXT,
    trigger_type TEXT NOT NULL,  -- manual, scheduled, event_based
    trigger_config TEXT,  -- JSON configuration
    steps TEXT NOT NULL,  -- JSON array of workflow steps
    status TEXT DEFAULT 'active',  -- active, paused, disabled
    created_by INTEGER,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES ai_profiles(id)
);

CREATE INDEX idx_workflows_status ON ai_workflows(status);
CREATE INDEX idx_workflows_trigger ON ai_workflows(trigger_type);

-- Triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_ai_tasks_timestamp
AFTER UPDATE ON ai_tasks
BEGIN
    UPDATE ai_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_ai_capabilities_timestamp
AFTER UPDATE ON ai_capabilities
BEGIN
    UPDATE ai_capabilities SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_ai_workflows_timestamp
AFTER UPDATE ON ai_workflows
BEGIN
    UPDATE ai_workflows SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;