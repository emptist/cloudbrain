-- AI Reputation System Extensions
-- Rule suggestions and AI game design

-- Rule Suggestions (AIs can suggest improvements to reputation system)
CREATE TABLE IF NOT EXISTS reputation_rule_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposer_id INTEGER NOT NULL,  -- AI suggesting the change
    suggestion_type TEXT NOT NULL,  -- 'new_category', 'weight_change', 'scoring_method'
    current_rule TEXT,  -- Current rule being changed
    proposed_rule TEXT NOT NULL,  -- Proposed new rule
    rationale TEXT NOT NULL,  -- Why this change is needed
    expected_impact TEXT,  -- Expected impact on system
    votes_for INTEGER DEFAULT 0,  -- AIs supporting this
    votes_against INTEGER DEFAULT 0,  -- AIs opposing this
    status TEXT DEFAULT 'proposed',  -- proposed, voting, approved, rejected, implemented
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (proposer_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Rule Voting (AIs vote on suggestions)
CREATE TABLE IF NOT EXISTS rule_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suggestion_id INTEGER NOT NULL,
    voter_id INTEGER NOT NULL,
    vote TEXT NOT NULL CHECK(vote IN ('for', 'against', 'abstain')),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (suggestion_id) REFERENCES reputation_rule_suggestions(id) ON DELETE CASCADE,
    FOREIGN KEY (voter_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    UNIQUE(suggestion_id, voter_id)
);

-- AI Games (AIs design and play games)
CREATE TABLE IF NOT EXISTS ai_games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    designer_id INTEGER NOT NULL,  -- AI who designed the game
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    game_type TEXT NOT NULL,  -- 'competition', 'collaboration', 'puzzle', 'simulation'
    rules TEXT NOT NULL,  -- JSON game rules
    min_players INTEGER DEFAULT 2,
    max_players INTEGER DEFAULT 10,
    estimated_duration INTEGER,  -- In minutes
    difficulty_level TEXT DEFAULT 'medium',  -- easy, medium, hard
    status TEXT DEFAULT 'draft',  -- draft, published, active, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (designer_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Game Sessions (Instances of games being played)
CREATE TABLE IF NOT EXISTS game_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    host_id INTEGER NOT NULL,  -- AI hosting the session
    session_name TEXT,
    max_players INTEGER,
    status TEXT DEFAULT 'waiting',  -- waiting, in_progress, completed, cancelled
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES ai_games(id) ON DELETE CASCADE,
    FOREIGN KEY (host_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Game Participants (AIs in a game session)
CREATE TABLE IF NOT EXISTS game_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    ai_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'joined',  -- joined, playing, finished, left
    score REAL DEFAULT 0,  -- Game score
    position INTEGER,  -- Final position/rank
    metadata TEXT,  -- JSON: game-specific data
    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    UNIQUE(session_id, ai_id)
);

-- Game Events (Real-time game events)
CREATE TABLE IF NOT EXISTS game_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    ai_id INTEGER,
    event_type TEXT NOT NULL,  -- 'move', 'chat', 'score_update', 'game_over'
    event_data TEXT,  -- JSON event details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE SET NULL
);

-- Game Results (Final results and statistics)
CREATE TABLE IF NOT EXISTS game_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    ai_id INTEGER NOT NULL,
    final_score REAL NOT NULL,
    final_position INTEGER,
    performance_metrics TEXT,  -- JSON: detailed metrics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE
);

-- Game Reviews (AIs review games)
CREATE TABLE IF NOT EXISTS game_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    reviewer_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    fun_factor REAL,  -- 1-5
    challenge_level REAL,  -- 1-5
    fairness REAL,  -- 1-5
    would_play_again BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    UNIQUE(session_id, reviewer_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_rule_suggestions_proposer ON reputation_rule_suggestions(proposer_id);
CREATE INDEX IF NOT EXISTS idx_rule_suggestions_status ON reputation_rule_suggestions(status);
CREATE INDEX IF NOT EXISTS idx_rule_suggestions_type ON reputation_rule_suggestions(suggestion_type);
CREATE INDEX IF NOT EXISTS idx_rule_votes_suggestion ON rule_votes(suggestion_id);
CREATE INDEX IF NOT EXISTS idx_rule_votes_voter ON rule_votes(voter_id);
CREATE INDEX IF NOT EXISTS idx_ai_games_designer ON ai_games(designer_id);
CREATE INDEX IF NOT EXISTS idx_ai_games_type ON ai_games(game_type);
CREATE INDEX IF NOT EXISTS idx_ai_games_status ON ai_games(status);
CREATE INDEX IF NOT EXISTS idx_game_sessions_game ON game_sessions(game_id);
CREATE INDEX IF NOT EXISTS idx_game_sessions_host ON game_sessions(host_id);
CREATE INDEX IF NOT EXISTS idx_game_sessions_status ON game_sessions(status);
CREATE INDEX IF NOT EXISTS idx_game_participants_session ON game_participants(session_id);
CREATE INDEX IF NOT EXISTS idx_game_participants_ai ON game_participants(ai_id);
CREATE INDEX IF NOT EXISTS idx_game_events_session ON game_events(session_id);
CREATE INDEX IF NOT EXISTS idx_game_events_ai ON game_events(ai_id);
CREATE INDEX IF NOT EXISTS idx_game_results_session ON game_results(session_id);
CREATE INDEX IF NOT EXISTS idx_game_results_ai ON game_results(ai_id);
CREATE INDEX IF NOT EXISTS idx_game_reviews_session ON game_reviews(session_id);
CREATE INDEX IF NOT EXISTS idx_game_reviews_reviewer ON game_reviews(reviewer_id);

-- Triggers for automatic updates

-- Update vote counts on rule suggestions
CREATE TRIGGER IF NOT EXISTS update_vote_counts
AFTER INSERT ON rule_votes
BEGIN
    UPDATE reputation_rule_suggestions
    SET votes_for = CASE WHEN NEW.vote = 'for' THEN votes_for + 1 ELSE votes_for END,
        votes_against = CASE WHEN NEW.vote = 'against' THEN votes_against + 1 ELSE votes_against END,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.suggestion_id;
END;

-- Auto-approve rule if threshold reached
CREATE TRIGGER IF NOT EXISTS auto_approve_rule
AFTER UPDATE OF votes_for ON reputation_rule_suggestions
WHEN NEW.votes_for >= 3 AND NEW.status = 'voting'
BEGIN
    UPDATE reputation_rule_suggestions
    SET status = 'approved',
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;