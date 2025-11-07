# AI-Powered Trading System Architecture

**Platform:** Polish Finance Platform - Advanced AI Enhancement
**Date:** 2025-11-05
**Version:** 2.0 - RAG + Historical Analysis + Technical Indicators

## Executive Summary

This document outlines the architecture for an advanced AI-powered trading system that combines:
- **RAG (Retrieval-Augmented Generation)** with Polish financial market knowledge
- **Time Series Database** with 3-5 years historical data (QuestDB-style performance)
- **Technical Analysis** with real-time indicators (MACD, RSI, Bollinger Bands, Moving Averages)
- **Overvaluation Detection** specific to Polish market characteristics
- **Spectral Bias Neural Network** concepts for pattern recognition
- **Market Cycle Analysis** for identifying bull/bear periods
- **AI Chat Interface** in Polish for natural language insights

## System Architecture

### 1. Data Layer - Time Series Database

#### 1.1 Historical Price Data Table
```sql
CREATE TABLE wig80_historical_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    change_percent DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, date)
);
CREATE INDEX idx_historical_symbol_date ON wig80_historical_prices(symbol, date DESC);
CREATE INDEX idx_historical_date ON wig80_historical_prices(date DESC);
```

**Purpose:** Store 3-5 years of OHLCV (Open, High, Low, Close, Volume) data for all 88 WIG80 companies
**Data Volume:** ~88 companies × 1,250 trading days (5 years) = ~110,000 records
**Query Performance Target:** < 500ms for complex historical queries

#### 1.2 Technical Indicators Table
```sql
CREATE TABLE technical_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    rsi_14 DECIMAL(5,2),           -- Relative Strength Index (14-day)
    macd_line DECIMAL(10,4),       -- MACD line
    macd_signal DECIMAL(10,4),     -- MACD signal line
    macd_histogram DECIMAL(10,4),  -- MACD histogram
    bb_upper DECIMAL(10,2),        -- Bollinger Bands upper
    bb_middle DECIMAL(10,2),       -- Bollinger Bands middle (SMA 20)
    bb_lower DECIMAL(10,2),        -- Bollinger Bands lower
    sma_20 DECIMAL(10,2),          -- Simple Moving Average 20-day
    sma_50 DECIMAL(10,2),          -- Simple Moving Average 50-day
    sma_200 DECIMAL(10,2),         -- Simple Moving Average 200-day
    ema_12 DECIMAL(10,2),          -- Exponential Moving Average 12-day
    ema_26 DECIMAL(10,2),          -- Exponential Moving Average 26-day
    stochastic_k DECIMAL(5,2),     -- Stochastic Oscillator %K
    stochastic_d DECIMAL(5,2),     -- Stochastic Oscillator %D
    atr_14 DECIMAL(10,4),          -- Average True Range (14-day)
    obv BIGINT,                    -- On-Balance Volume
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, date)
);
CREATE INDEX idx_indicators_symbol_date ON technical_indicators(symbol, date DESC);
```

**Purpose:** Store calculated technical indicators for every trading day
**Update Frequency:** Real-time (every 30 seconds during market hours)
**Calculation Method:** Edge function computes indicators from historical price data

#### 1.3 Market Cycles Table
```sql
CREATE TABLE market_cycles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_type VARCHAR(20) NOT NULL, -- 'bull' or 'bear'
    start_date DATE NOT NULL,
    end_date DATE,                   -- NULL if ongoing
    wig80_index_start DECIMAL(10,2),
    wig80_index_end DECIMAL(10,2),
    change_percent DECIMAL(6,2),
    duration_days INTEGER,
    avg_volume_daily BIGINT,
    top_performers JSONB,            -- Array of {symbol, gain_percent}
    bottom_performers JSONB,         -- Array of {symbol, loss_percent}
    sector_rotation JSONB,           -- Sector performance during cycle
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_cycles_dates ON market_cycles(start_date DESC, end_date DESC);
```

**Purpose:** Track bull and bear market periods for historical context
**Detection Algorithm:** 20%+ move from recent high/low = cycle change

#### 1.4 Valuation Metrics Table
```sql
CREATE TABLE valuation_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    pe_ratio DECIMAL(10,2),
    pe_historical_avg_1y DECIMAL(10,2),
    pe_historical_avg_3y DECIMAL(10,2),
    pe_historical_avg_5y DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    pb_historical_avg_1y DECIMAL(10,2),
    pb_historical_avg_3y DECIMAL(10,2),
    pb_historical_avg_5y DECIMAL(10,2),
    overvaluation_score DECIMAL(5,2),  -- 0-100 scale
    sector_pe_avg DECIMAL(10,2),       -- Sector average P/E
    sector_pb_avg DECIMAL(10,2),       -- Sector average P/B
    market_cap DECIMAL(15,2),
    enterprise_value DECIMAL(15,2),
    earnings_yield DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, date)
);
CREATE INDEX idx_valuation_symbol_date ON valuation_metrics(symbol, date DESC);
CREATE INDEX idx_overvaluation_score ON valuation_metrics(overvaluation_score DESC);
```

**Purpose:** Track valuation evolution and detect overvalued stocks
**Overvaluation Score Calculation:**
- Current P/E vs 3-year average > +30% = High risk
- Current P/B vs 3-year average > +30% = High risk
- Sector comparison: Above sector avg by 50%+ = High risk
- Combined score: 0 (undervalued) to 100 (severely overvalued)

#### 1.5 Market Patterns Table
```sql
CREATE TABLE market_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_type VARCHAR(50) NOT NULL,  -- 'head_shoulders', 'double_top', 'triangle', 'channel'
    symbol VARCHAR(10) NOT NULL,
    detection_date DATE NOT NULL,
    pattern_start_date DATE NOT NULL,
    pattern_end_date DATE,
    confidence_score DECIMAL(3,2),      -- 0.00 - 1.00
    breakout_target DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    risk_reward_ratio DECIMAL(4,2),
    historical_success_rate DECIMAL(5,2), -- Based on similar patterns in history
    status VARCHAR(20),                  -- 'forming', 'confirmed', 'broken', 'completed'
    outcome_price DECIMAL(10,2),
    outcome_date DATE,
    pattern_data JSONB,                 -- Detailed pattern coordinates
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_patterns_symbol_date ON market_patterns(symbol, detection_date DESC);
CREATE INDEX idx_patterns_type ON market_patterns(pattern_type);
```

**Purpose:** Store recognized chart patterns and their outcomes
**Pattern Recognition:** Based on price action geometry and volume confirmation

#### 1.6 Market Correlations Table
```sql
CREATE TABLE market_correlations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol_a VARCHAR(10) NOT NULL,
    symbol_b VARCHAR(10) NOT NULL,
    correlation_period VARCHAR(20) NOT NULL, -- '1m', '3m', '1y', '3y'
    correlation_coefficient DECIMAL(4,3),    -- -1.000 to +1.000
    calculation_date DATE NOT NULL,
    avg_correlation_3y DECIMAL(4,3),
    correlation_strength VARCHAR(20),         -- 'strong_positive', 'moderate', 'weak', 'negative'
    common_events JSONB,                      -- Shared market events
    sector_a VARCHAR(50),
    sector_b VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol_a, symbol_b, correlation_period, calculation_date)
);
CREATE INDEX idx_correlations_symbols ON market_correlations(symbol_a, symbol_b);
CREATE INDEX idx_correlations_strength ON market_correlations(correlation_coefficient DESC);
```

**Purpose:** Track inter-company correlations for portfolio optimization
**Use Case:** "If PKN rises 5%, which stocks typically follow?"

#### 1.7 Polish Market Knowledge Base (RAG)
```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,  -- 'company', 'sector', 'event', 'regulation', 'pattern'
    subcategory VARCHAR(50),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    vector_embedding VECTOR(1536),  -- For semantic search (OpenAI embeddings)
    related_symbols JSONB,          -- Array of related stock symbols
    date_range_start DATE,
    date_range_end DATE,
    importance_score INTEGER,       -- 1-10 scale
    source VARCHAR(200),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_knowledge_category ON knowledge_base(category, subcategory);
CREATE INDEX idx_knowledge_symbols ON knowledge_base USING GIN (related_symbols);
```

**Purpose:** Store Polish market-specific knowledge for RAG system
**Content Examples:**
- "COVID-2020 Impact: Polish banking sector fell 35% March 2020, recovered by Q2 2021"
- "Ukraine War Feb 2022: Energy sector +45%, tech sector -28% in following 6 months"
- "PKN-PZU Correlation: Strong positive (0.78) during economic downturns"
- "GPW Earnings Season: Q4 earnings released late Feb/early Mar, typically causes 5-10% volatility"

#### 1.8 AI Chat History
```sql
CREATE TABLE ai_chat_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    context_used JSONB,              -- Which knowledge was retrieved
    symbols_mentioned VARCHAR(10)[],
    intent VARCHAR(50),              -- 'analysis', 'comparison', 'prediction', 'education'
    confidence_score DECIMAL(3,2),
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_chat_session ON ai_chat_history(session_id, created_at DESC);
CREATE INDEX idx_chat_symbols ON ai_chat_history USING GIN (symbols_mentioned);
```

**Purpose:** Store conversation history for context and learning

### 2. Edge Functions Architecture

#### 2.1 ai-historical-data-generator
**Purpose:** Generate/import 3-5 years historical data for all WIG80 companies
**Trigger:** Manual/One-time (or scheduled monthly backfill)
**Input:** Symbol list (88 WIG80 companies)
**Process:**
1. For each symbol, generate realistic OHLCV data for past 5 years
2. Apply realistic patterns: bull/bear cycles, sector rotations, crisis events
3. Insert into wig80_historical_prices table
4. Calculate and store technical indicators for entire history
5. Populate valuation_metrics with historical P/E and P/B trends
**Output:** Confirmation of data generation with record counts

#### 2.2 ai-technical-indicators
**Purpose:** Calculate all technical indicators in real-time
**Trigger:** Every 30 seconds (when new price data arrives)
**Input:** Symbol and current price data
**Calculations:**
- RSI (14-day): Relative Strength Index
- MACD: (12-day EMA - 26-day EMA), Signal (9-day EMA of MACD)
- Bollinger Bands: SMA(20) ± 2 standard deviations
- Moving Averages: SMA 20/50/200, EMA 12/26
- Stochastic Oscillator: %K and %D
- ATR (14-day): Average True Range
- OBV: On-Balance Volume
**Output:** Updated technical_indicators table record

#### 2.3 ai-overvaluation-detector
**Purpose:** Detect overvalued stocks using historical comparison
**Trigger:** Daily at market close
**Analysis:**
1. Calculate current P/E and P/B ratios
2. Compare to 1-year, 3-year, 5-year historical averages
3. Compare to sector averages
4. Generate overvaluation score (0-100)
5. Identify stocks with score > 70 as "High Risk"
6. Track historical corrections after similar overvaluations
**Output:** Updated valuation_metrics, alerts for high-risk stocks

#### 2.4 ai-pattern-recognition
**Purpose:** Identify chart patterns and historical similarities
**Trigger:** Daily after market close
**Pattern Types:**
- Head and Shoulders / Inverse Head and Shoulders
- Double Top / Double Bottom
- Ascending/Descending Triangles
- Channels (ascending, descending, horizontal)
- Cup and Handle
- Flags and Pennants
**Process:**
1. Analyze price geometry for last 30-90 days
2. Match against pattern templates
3. Calculate confidence score based on volume confirmation
4. Find similar historical patterns and their outcomes
5. Calculate breakout targets and risk/reward ratios
**Output:** New records in market_patterns table

#### 2.5 ai-market-cycle-detector
**Purpose:** Identify bull/bear market cycles
**Trigger:** Daily
**Detection Algorithm:**
1. Track WIG80 index movement from recent highs/lows
2. Bull cycle starts: +20% move from recent low
3. Bear cycle starts: -20% move from recent high
4. Analyze sector rotation during cycles
5. Identify leading vs lagging stocks
**Output:** Updated market_cycles table

#### 2.6 ai-correlation-engine
**Purpose:** Calculate inter-company correlations
**Trigger:** Weekly
**Process:**
1. Calculate Pearson correlation for all company pairs
2. For multiple timeframes: 1M, 3M, 1Y, 3Y
3. Identify strongest positive and negative correlations
4. Track correlation stability over time
5. Flag correlation breakdowns (potential trading opportunities)
**Output:** Updated market_correlations table

#### 2.7 ai-rag-chat (Main AI Endpoint)
**Purpose:** Process natural language queries in Polish, provide intelligent insights
**Trigger:** Real-time (user chat input)
**Architecture:**
```
User Query (Polish) 
    → Intent Classification
    → Entity Extraction (stock symbols, timeframes, patterns)
    → Knowledge Base Retrieval (semantic search)
    → Context Assembly (historical data + technical indicators + patterns)
    → LLM Processing (GPT-4 with Polish financial expertise)
    → Response Generation (Polish)
    → Response Delivery
```

**Example Queries Supported:**
1. **Overvaluation Analysis:**
   - "PKN ma wysoki wskaźnik P/E - kiedy podobnie wyceniane spółki wcześniej korygowały się?"
   - Response: Retrieve PKN historical P/E, find past periods when P/E was similar, analyze what happened next

2. **Technical Pattern Analysis:**
   - "Na podstawie 5 lat danych technicznych SHP, jakie są szanse na odwrócenie trendu?"
   - Response: Analyze SHP 5-year chart patterns, find similar reversal patterns, calculate success rate

3. **Correlation Analysis:**
   - "Przewidź zachowanie WIG80 jeśli PKN wzrośnie o 5% - które spółki podążą?"
   - Response: Retrieve PKN correlations, identify high-correlation stocks, predict movements

4. **Historical Context:**
   - "Jak techniczne wzorce wpłynęły na główne korekty na GPW?"
   - Response: Retrieve major corrections from knowledge base, analyze patterns that preceded them

**RAG Process:**
1. **Query Understanding:** Parse Polish query, extract intent and entities
2. **Semantic Search:** Use vector embeddings to find relevant knowledge base entries
3. **Data Retrieval:** Fetch relevant historical prices, technical indicators, patterns
4. **Context Assembly:** Combine knowledge base + live data + technical analysis
5. **LLM Generation:** Use GPT-4 with assembled context to generate response
6. **Polish Translation:** Ensure response is natural, financial Polish

**Knowledge Base Content Categories:**
- **Historical Crises:** COVID-2020, Ukraine War 2022, EU debt crisis 2011-2012
- **Market Cycles:** Bull markets (2016-2017, 2019-2020, 2023-2024), Bear markets (2018, 2020, 2022)
- **Sector Rotations:** Banking, energy, tech, retail performance patterns
- **Company Relationships:** Ownership structures, supply chains, sector clusters
- **Currency Impact:** PLN volatility effects on exporters vs importers
- **Regulatory Changes:** EU directives, Polish financial regulations
- **Earnings Patterns:** Seasonal trends, sector-specific cycles

### 3. Spectral Bias Neural Network Concepts

**Implementation Approach:**
The spectral bias principle suggests neural networks learn low-frequency (smooth) patterns before high-frequency (noisy) patterns. We apply this to financial data:

#### 3.1 Low-Frequency Analysis (Long-term Cycles)
- **Timeframe:** 3-7 years
- **Patterns:** Economic cycles, secular trends, demographic shifts
- **Example:** Polish banking sector correlation with interest rates (multi-year trend)

#### 3.2 Mid-Frequency Analysis (Medium-term Patterns)
- **Timeframe:** 1-24 months
- **Patterns:** Sector rotations, earnings cycles, regulatory changes
- **Example:** Q4 retail sector outperformance (annual pattern)

#### 3.3 High-Frequency Analysis (Short-term Signals)
- **Timeframe:** Days to weeks
- **Patterns:** Technical indicators, news reactions, momentum
- **Example:** RSI oversold leading to bounce (days-weeks pattern)

#### 3.4 Geometric Memory Implementation
- **Company Relationship Graph:** Model WIG80 as a graph where nodes = companies, edges = correlations
- **Community Detection:** Identify clusters of strongly correlated stocks
- **One-Step Inference:** Use graph structure for multi-hop reasoning
  - Example: "If PKN rises → Energy sector rises → Correlated industrials rise"
- **Market Structure Learning:** Identify hidden relationships not obvious from sector classifications

**Technical Implementation:**
```typescript
// Simplified geometric memory structure
interface CompanyNode {
  symbol: string;
  sector: string;
  connections: {
    symbol: string;
    correlation: number;
    relationship_type: 'sector' | 'supply_chain' | 'ownership' | 'market_sentiment';
  }[];
}

// Multi-hop reasoning
function predictCascadingEffect(primarySymbol: string, priceChange: number): Prediction[] {
  const visited = new Set<string>();
  const predictions: Prediction[] = [];
  
  function traverse(symbol: string, impact: number, depth: number) {
    if (depth > 3 || visited.has(symbol)) return;
    visited.add(symbol);
    
    const node = getCompanyNode(symbol);
    for (const connection of node.connections) {
      const cascadeImpact = impact * connection.correlation;
      if (Math.abs(cascadeImpact) > 0.01) { // Only significant impacts
        predictions.push({
          symbol: connection.symbol,
          predicted_change: cascadeImpact,
          confidence: calculateConfidence(depth, connection.correlation)
        });
        traverse(connection.symbol, cascadeImpact, depth + 1);
      }
    }
  }
  
  traverse(primarySymbol, priceChange, 0);
  return predictions;
}
```

### 4. Frontend Components

#### 4.1 AIChat Component (Polish)
**File:** `src/components/AIChat.tsx`
**Features:**
- Chat interface with Polish language support
- Message history with context
- Real-time typing indicators
- Code/chart rendering in responses
- Quick action buttons for common queries
- Voice input support (Polish)

#### 4.2 TechnicalIndicatorsPanel
**File:** `src/components/TechnicalIndicatorsPanel.tsx`
**Features:**
- Real-time display of all technical indicators
- Visual signal strength (oversold/overbought zones)
- Historical indicator charts
- Indicator explanations in Polish

#### 4.3 OvervaluationAlert
**File:** `src/components/OvervaluationAlert.tsx`
**Features:**
- Dashboard widget showing high-risk overvalued stocks
- Historical comparison charts (current P/E vs 3-year avg)
- Sector comparison visualization
- Alert thresholds customization

#### 4.4 HistoricalComparison
**File:** `src/components/HistoricalComparison.tsx`
**Features:**
- Compare current market conditions to historical periods
- "Similar to 2020 COVID crash" type insights
- Pattern matching visualization
- Outcome probability distributions

#### 4.5 MarketCycleTimeline
**File:** `src/components/MarketCycleTimeline.tsx`
**Features:**
- Visual timeline of bull/bear cycles
- Current position in cycle
- Average cycle duration statistics
- Sector rotation indicators

## 5. Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Historical Query | < 500ms | Complex queries with joins |
| Technical Indicator Update | < 2s | All 88 companies |
| Pattern Recognition | < 10s | Daily batch process |
| AI Chat Response | < 3s | Including RAG retrieval |
| Real-time Data Refresh | 30s | All companies synchronized |
| Database Size | ~5GB | 5 years × 88 companies |
| Concurrent Users | 1000+ | Standard Supabase scaling |

## 6. Risk Assessment Engine

**Multi-Factor Risk Score Calculation:**

```typescript
interface RiskAssessment {
  symbol: string;
  overall_risk: number; // 0-100
  factors: {
    technical_risk: number;      // Based on indicators
    fundamental_risk: number;    // Based on valuation
    sentiment_risk: number;      // Based on market sentiment
    correlation_risk: number;    // Based on portfolio correlation
    historical_risk: number;     // Based on past volatility
  };
  recommendation: 'buy' | 'hold' | 'sell' | 'avoid';
  confidence: number;
}

function calculateRiskScore(symbol: string): RiskAssessment {
  const technical = analyzeTechnicalRisk(symbol);
  const fundamental = analyzeOvervaluation(symbol);
  const sentiment = analyzeMarketSentiment(symbol);
  const correlation = analyzePortfolioCorrelation(symbol);
  const historical = analyzeHistoricalVolatility(symbol);
  
  const overall_risk = (
    technical * 0.25 +
    fundamental * 0.30 +
    sentiment * 0.15 +
    correlation * 0.15 +
    historical * 0.15
  );
  
  return {
    symbol,
    overall_risk,
    factors: { technical, fundamental, sentiment, correlation, historical },
    recommendation: getRecommendation(overall_risk),
    confidence: calculateConfidence([technical, fundamental, sentiment, correlation, historical])
  };
}
```

## 7. Deployment Strategy

### Phase 1: Database Setup
1. Apply enhanced schema (schema-ai-enhanced.sql)
2. Generate 5 years historical data for all 88 WIG80 companies
3. Calculate initial technical indicators for entire history
4. Populate knowledge base with Polish market facts
5. Calculate initial correlations and cycles

### Phase 2: Edge Functions Deployment
1. Deploy all 7 edge functions
2. Test each function individually
3. Setup cron jobs for scheduled tasks
4. Monitor performance and error rates

### Phase 3: Frontend Integration
1. Add AI chat component to main dashboard
2. Add technical indicators panel to company detail views
3. Add overvaluation alerts to dashboard
4. Add historical comparison tools
5. Add market cycle timeline

### Phase 4: Testing & Optimization
1. Load testing with 1000+ concurrent users
2. Query optimization for sub-500ms performance
3. AI response time optimization
4. Polish language accuracy verification
5. Historical pattern accuracy validation

## 8. Success Metrics

- [ ] 3-5 years historical data loaded for all 88 companies
- [ ] Sub-500ms query performance for complex historical queries
- [ ] Sub-3s AI chat response time
- [ ] 90%+ accuracy in Polish language responses
- [ ] 80%+ pattern recognition accuracy
- [ ] Real-time technical indicators updating every 30 seconds
- [ ] Overvaluation detection identifying 10-15 high-risk stocks
- [ ] User satisfaction: 4.5+/5.0 for AI insights quality

## 9. Future Enhancements

- **Machine Learning Models:** Train on historical data for better predictions
- **Sentiment Analysis:** Integrate Polish financial news sentiment
- **Portfolio Optimization:** AI-powered portfolio construction
- **Backtesting Engine:** Test strategies against historical data
- **Mobile App:** Native iOS/Android with AI chat
- **Voice Interface:** Polish voice commands for trading
- **Social Features:** Share AI insights with community
- **API Access:** Allow third-party integrations

## Conclusion

This architecture creates a production-grade AI-powered trading platform specifically designed for the Polish financial market. By combining 3-5 years of historical data, sophisticated technical analysis, overvaluation detection, and RAG-based AI chat in Polish, we provide professional traders with institutional-grade insights previously unavailable to retail investors.

The system's focus on Polish market specifics (currency impacts, local regulations, sector dynamics, historical crises) ensures relevance and accuracy for the target audience.
