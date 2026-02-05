-- Create API requests table for rate limiting
CREATE TABLE IF NOT EXISTS api_requests (
    id SERIAL PRIMARY KEY,
    ai_id VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for rate limiting queries
CREATE INDEX IF NOT EXISTS idx_api_requests_ai_id ON api_requests(ai_id);
CREATE INDEX IF NOT EXISTS idx_api_requests_created_at ON api_requests(created_at);
