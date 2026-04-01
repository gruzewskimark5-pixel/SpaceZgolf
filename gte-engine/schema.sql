-- GTE v2 Database Schema

CREATE TABLE IF NOT EXISTS baseline_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS adaptive_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    pace_curve JSONB DEFAULT '{}',
    strength_curve JSONB DEFAULT '{}',
    hr_signature JSONB DEFAULT '{}',
    behavior_profile JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS integrity_ledger (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    activity_id VARCHAR(255) NOT NULL,
    anomaly_factors JSONB DEFAULT '{}',
    integrity_score FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS score_ledger (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    activity_id VARCHAR(255) NOT NULL,
    performance_score FLOAT NOT NULL,
    components JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_baseline_user ON baseline_history(user_id);
CREATE INDEX idx_integrity_user ON integrity_ledger(user_id);
CREATE INDEX idx_score_user ON score_ledger(user_id);
