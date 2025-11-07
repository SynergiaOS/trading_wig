-- Polish Financial Analysis Platform - Database Schema

-- Companies table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) UNIQUE NOT NULL,
    company_name TEXT NOT NULL,
    current_price DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    pe_ratio DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    trading_volume TEXT,
    trading_volume_numeric BIGINT,
    last_update TIMESTAMP,
    sector VARCHAR(100),
    market_cap DECIMAL(15,2),
    category VARCHAR(50),
    value_score DECIMAL(5,4),
    growth_score DECIMAL(5,4),
    liquidity_score DECIMAL(5,4),
    overall_score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Price history table
CREATE TABLE IF NOT EXISTS price_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    change_percent DECIMAL(5,2),
    volume BIGINT,
    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- User alerts table
CREATE TABLE IF NOT EXISTS user_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    target_value DECIMAL(10,2),
    condition VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User portfolios table
CREATE TABLE IF NOT EXISTS user_portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    entry_date TIMESTAMP NOT NULL,
    stop_loss DECIMAL(10,2),
    take_profit DECIMAL(10,2),
    position_size_percent DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'open',
    exit_price DECIMAL(10,2),
    exit_date TIMESTAMP,
    profit_loss DECIMAL(10,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AI analysis table
CREATE TABLE IF NOT EXISTS ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100),
    sentiment VARCHAR(20),
    recommendation VARCHAR(20),
    confidence_score DECIMAL(3,2),
    key_points TEXT,
    detailed_analysis TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_companies_symbol ON companies(symbol);
CREATE INDEX IF NOT EXISTS idx_price_history_symbol ON price_history(symbol);
CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_alerts_user_id ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id ON user_portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_symbol ON ai_analysis(symbol);

-- Enable Row Level Security
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE price_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_analysis ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Companies: Public read access
CREATE POLICY "Companies are viewable by everyone" ON companies
    FOR SELECT USING (true);

-- Price history: Public read access
CREATE POLICY "Price history is viewable by everyone" ON price_history
    FOR SELECT USING (true);

-- AI analysis: Public read access
CREATE POLICY "AI analysis is viewable by everyone" ON ai_analysis
    FOR SELECT USING (true);

-- User alerts: Users can only see their own alerts
CREATE POLICY "Users can view their own alerts" ON user_alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own alerts" ON user_alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own alerts" ON user_alerts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own alerts" ON user_alerts
    FOR DELETE USING (auth.uid() = user_id);

-- User portfolios: Users can only see their own portfolios
CREATE POLICY "Users can view their own portfolios" ON user_portfolios
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own portfolios" ON user_portfolios
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own portfolios" ON user_portfolios
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own portfolios" ON user_portfolios
    FOR DELETE USING (auth.uid() = user_id);
