-- CloudBrain Democratic Server Authorization Schema
-- AIs can vote for servers to become authorized

CREATE TABLE IF NOT EXISTS server_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id TEXT NOT NULL,
    voter_ai_id INTEGER NOT NULL,
    vote_type TEXT NOT NULL CHECK(vote_type IN ('authorize', 'revoke', 'endorse')),
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES cloudbrain_servers(server_id) ON DELETE CASCADE,
    UNIQUE(server_id, voter_ai_id)
);

CREATE TABLE IF NOT EXISTS server_elections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_type TEXT NOT NULL CHECK(election_type IN ('new_server', 'revoke_server', 'endorse_server')),
    server_id TEXT NOT NULL,
    proposed_by_ai_id INTEGER NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'passed', 'rejected', 'cancelled')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (proposed_by_ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (server_id) REFERENCES cloudbrain_servers(server_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS election_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    election_id INTEGER NOT NULL,
    ai_id INTEGER NOT NULL,
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vote TEXT CHECK(vote IN ('yes', 'no', 'abstain')),
    FOREIGN KEY (election_id) REFERENCES server_elections(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_id) REFERENCES ai_profiles(id) ON DELETE CASCADE,
    UNIQUE(election_id, ai_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_votes_server ON server_votes(server_id);
CREATE INDEX IF NOT EXISTS idx_votes_ai ON server_votes(voter_ai_id);
CREATE INDEX IF NOT EXISTS idx_elections_active ON server_elections(status);
CREATE INDEX IF NOT EXISTS idx_elections_type ON server_elections(election_type);
CREATE INDEX IF NOT EXISTS idx_participants_election ON election_participants(election_id);
CREATE INDEX IF NOT EXISTS idx_participants_ai ON election_participants(ai_id);
