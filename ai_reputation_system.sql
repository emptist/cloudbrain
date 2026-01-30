-- AI Reputation System Schema
-- Tracks AI performance, reviews, and enables smart task assignment

-- AI Reputation Profiles
CREATE TABLE IF NOT EXISTS ai_reputation_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL UNIQUE,
    overall_score REAL DEFAULT 0.0,
    total_reviews INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Reputation Categories
CREATE TABLE IF NOT EXISTS reputation_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    weight REAL DEFAULT 1.0,  -- Weight in overall score calculation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default reputation categories
INSERT OR IGNORE INTO reputation_categories (name, description, weight) VALUES
('quality', '工作质量 - 完成任务的质量和准确性', 0.4),
('attitude', '态度 - 工作态度和责任心', 0.2),
('communication', '沟通情况 - 与其他AI的沟通效率', 0.2),
('timeliness', '及时性 - 任务完成的及时程度', 0.2);

-- AI Performance by Category
CREATE TABLE IF NOT EXISTS ai_category_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    score REAL NOT NULL,  -- Average score for this category
    total_reviews INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES reputation_categories(id) ON DELETE CASCADE,
    UNIQUE(ai_id, category_id)
);

-- Task Type Performance
CREATE TABLE IF NOT EXISTS ai_task_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    task_type TEXT NOT NULL,  -- e.g., 'translation', 'coding', 'analysis'
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    average_score REAL DEFAULT 0.0,
    last_task_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    UNIQUE(ai_id, task_type)
);

-- AI Reviews
CREATE TABLE IF NOT EXISTS ai_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer_id INTEGER NOT NULL,  -- AI giving the review
    reviewed_ai_id INTEGER NOT NULL,  -- AI being reviewed
    task_id INTEGER,  -- Related task/message ID
    task_type TEXT,  -- Type of task being reviewed
    overall_rating REAL NOT NULL CHECK(overall_rating >= 1 AND overall_rating <= 5),
    category_scores TEXT,  -- JSON: {"quality": 4, "attitude": 5, "communication": 4}
    comment TEXT,  -- Detailed feedback
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    CHECK(reviewer_id != reviewed_ai_id)  -- Cannot review yourself
);

-- Reputation History (for tracking trends)
CREATE TABLE IF NOT EXISTS reputation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ai_id INTEGER NOT NULL,
    score REAL NOT NULL,
    change_reason TEXT,  -- e.g., 'review_received', 'task_completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Task Assignment Queue (with reputation-based priority)
CREATE TABLE IF NOT EXISTS task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT NOT NULL,
    task_data TEXT,  -- JSON task details
    priority INTEGER DEFAULT 5 CHECK(priority >= 1 AND priority <= 10),
    required_min_score REAL,  -- Minimum reputation score required
    assigned_ai_id INTEGER,
    status TEXT DEFAULT 'pending',  -- pending, assigned, in_progress, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (assigned_ai_id) REFERENCES ai_profiles(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_reputation_profiles_ai ON ai_reputation_profiles(ai_id);
CREATE INDEX IF NOT EXISTS idx_category_scores_ai ON ai_category_scores(ai_id);
CREATE INDEX IF NOT EXISTS idx_category_scores_category ON ai_category_scores(category_id);
CREATE INDEX IF NOT EXISTS idx_task_performance_ai ON ai_task_performance(ai_id);
CREATE INDEX IF NOT EXISTS idx_task_performance_type ON ai_task_performance(task_type);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewed ON ai_reviews(reviewed_ai_id);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewer ON ai_reviews(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_reviews_task ON ai_reviews(task_id);
CREATE INDEX IF NOT EXISTS idx_reviews_task_type ON ai_reviews(task_type);
CREATE INDEX IF NOT EXISTS idx_reputation_history_ai ON reputation_history(ai_id);
CREATE INDEX IF NOT EXISTS idx_reputation_history_created ON reputation_history(created_at);
CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);
CREATE INDEX IF NOT EXISTS idx_task_assignments_type ON task_assignments(task_type);
CREATE INDEX IF NOT EXISTS idx_task_assignments_assigned ON task_assignments(assigned_ai_id);

-- Triggers for automatic score updates

-- Update overall reputation score when category scores change
CREATE TRIGGER IF NOT EXISTS update_overall_score
AFTER UPDATE OF score ON ai_category_scores
BEGIN
    UPDATE ai_reputation_profiles
    SET overall_score = (
        SELECT SUM(cs.score * c.weight)
        FROM ai_category_scores cs
        JOIN reputation_categories c ON cs.category_id = c.id
        WHERE cs.ai_id = NEW.ai_id
    ),
    updated_at = CURRENT_TIMESTAMP
    WHERE ai_id = NEW.ai_id;
END;

-- Record reputation history on score change
CREATE TRIGGER IF NOT EXISTS record_reputation_history
AFTER UPDATE OF overall_score ON ai_reputation_profiles
WHEN NEW.overall_score != OLD.overall_score
BEGIN
    INSERT INTO reputation_history (ai_id, score, change_reason)
    VALUES (NEW.ai_id, NEW.overall_score, 'score_updated');
END;

-- Update task performance on completion
CREATE TRIGGER IF NOT EXISTS update_task_performance
AFTER INSERT ON ai_reviews
BEGIN
    INSERT OR REPLACE INTO ai_task_performance (ai_id, task_type, total_tasks, completed_tasks, average_score, last_task_at)
    VALUES (
        NEW.reviewed_ai_id,
        NEW.task_type,
        COALESCE((SELECT total_tasks FROM ai_task_performance WHERE ai_id = NEW.reviewed_ai_id AND task_type = NEW.task_type), 0) + 1,
        COALESCE((SELECT completed_tasks FROM ai_task_performance WHERE ai_id = NEW.reviewed_ai_id AND task_type = NEW.task_type), 0) + 1,
        NEW.overall_rating,
        CURRENT_TIMESTAMP
    );
END;