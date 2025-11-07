# Sample SQL Queries for WIG80 QuestDB Analysis
# ================================================

-- =====================================
-- 1. BASIC QUERIES
-- =====================================

-- Get recent historical data for a specific symbol
SELECT 
    ts,
    symbol,
    open,
    high,
    low,
    close,
    volume,
    rsi,
    macd
FROM wig80_historical 
WHERE symbol = 'PKN' 
  AND ts >= dateadd('day', -7, now())
ORDER BY ts DESC
LIMIT 100;

-- Get latest prices for all WIG80 companies
SELECT DISTINCT symbol,
       LAST_VALUE(close) OVER (PARTITION BY symbol ORDER BY ts) as latest_price,
       LAST_VALUE(volume) OVER (PARTITION BY symbol ORDER BY ts) as latest_volume,
       LAST_VALUE(rsi) OVER (PARTITION BY symbol ORDER BY ts) as latest_rsi
FROM wig80_historical
WHERE ts >= dateadd('hour', -1, now())
ORDER BY latest_price DESC;

-- =====================================
-- 2. PERFORMANCE ANALYSIS
-- =====================================

-- Top 10 stocks by volume (last 30 days)
SELECT 
    symbol, 
    SUM(volume) as total_volume,
    AVG(close) as avg_price,
    MIN(close) as min_price,
    MAX(close) as max_price,
    (MAX(close) - MIN(close)) / MIN(close) * 100 as volatility_pct,
    (LAST_VALUE(close) - FIRST_VALUE(close)) / FIRST_VALUE(close) * 100 as price_change_pct
FROM wig80_historical
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol
ORDER BY total_volume DESC
LIMIT 10;

-- Daily performance summary
SELECT 
    symbol,
    to_timestamp(to_int(ts / 86400000) * 86400000, 'yyyyMMdd') as date,
    FIRST_VALUE(open) as open_price,
    MAX(high) as high_price,
    MIN(low) as low_price,
    LAST_VALUE(close) as close_price,
    SUM(volume) as daily_volume,
    (LAST_VALUE(close) - FIRST_VALUE(open)) / FIRST_VALUE(open) * 100 as daily_return_pct
FROM wig80_historical
WHERE ts >= dateadd('day', -7, now())
SAMPLE BY 1d ALIGN TO CALENDAR
ORDER BY date DESC, daily_return_pct DESC;

-- Monthly performance comparison
SELECT 
    symbol,
    to_timestamp(to_int(ts / 86400000) * 86400000, 'yyyyMM') as month,
    FIRST_VALUE(open) as month_open,
    LAST_VALUE(close) as month_close,
    SUM(volume) as monthly_volume,
    (LAST_VALUE(close) - FIRST_VALUE(open)) / FIRST_VALUE(open) * 100 as monthly_return_pct
FROM wig80_historical
WHERE ts >= dateadd('month', -3, now())
SAMPLE BY 1M ALIGN TO CALENDAR
ORDER BY month DESC, monthly_return_pct DESC;

-- =====================================
-- 3. TECHNICAL ANALYSIS
-- =====================================

-- RSI-based trading signals
SELECT 
    symbol,
    AVG(rsi) as avg_rsi,
    MIN(rsi) as min_rsi,
    MAX(rsi) as max_rsi,
    CASE 
        WHEN AVG(rsi) > 70 THEN 'OVERBOUGHT'
        WHEN AVG(rsi) < 30 THEN 'OVERSOLD'
        WHEN AVG(rsi) BETWEEN 40 AND 60 THEN 'NEUTRAL'
        ELSE 'MOMENTUM'
    END as rsi_signal,
    COUNT(*) as data_points
FROM wig80_historical
WHERE ts >= dateadd('day', -14, now())
GROUP BY symbol
HAVING COUNT(*) > 5
ORDER BY avg_rsi DESC;

-- MACD analysis
SELECT 
    symbol,
    AVG(macd) as current_macd,
    LAG(AVG(macd), 1) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')) as prev_macd,
    CASE 
        WHEN AVG(macd) > LAG(AVG(macd), 1) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')) 
             AND LAG(AVG(macd), 1) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')) 
                 < LAG(AVG(macd), 2) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd'))
        THEN 'BULLISH_CROSSOVER'
        WHEN AVG(macd) < LAG(AVG(macd), 1) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')) 
             AND LAG(AVG(macd), 1) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')) 
                 > LAG(AVG(macd), 2) OVER (PARTITION BY symbol ORDER BY to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd'))
        THEN 'BEARISH_CROSSOVER'
        ELSE 'NO_SIGNAL'
    END as macd_signal
FROM wig80_historical
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol, to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')
ORDER BY symbol, to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd') DESC;

-- Bollinger Band analysis
SELECT 
    symbol,
    AVG(close) as avg_price,
    AVG(bb_upper) as avg_bb_upper,
    AVG(bb_lower) as avg_bb_lower,
    CASE 
        WHEN AVG(close) > AVG(bb_upper) THEN 'ABOVE_UPPER_BAND'
        WHEN AVG(close) < AVG(bb_lower) THEN 'BELOW_LOWER_BAND'
        ELSE 'WITHIN_BANDS'
    END as bb_position,
    (AVG(close) - AVG(bb_upper)) / (AVG(bb_upper) - AVG(bb_lower)) as bb_position_ratio
FROM wig80_historical
WHERE ts >= dateadd('day', -20, now())
GROUP BY symbol
HAVING COUNT(*) > 10
ORDER BY bb_position_ratio DESC;

-- =====================================
-- 4. VOLUME ANALYSIS
-- =====================================

-- Volume patterns and trends
SELECT 
    symbol,
    AVG(volume) as avg_volume,
    STDDEV(volume) as volume_stddev,
    MIN(volume) as min_volume,
    MAX(volume) as max_volume,
    CASE 
        WHEN STDDEV(volume) / AVG(volume) > 0.5 THEN 'HIGH_VOLATILITY'
        WHEN STDDEV(volume) / AVG(volume) > 0.3 THEN 'MODERATE_VOLATILITY'
        ELSE 'LOW_VOLATILITY'
    END as volume_pattern
FROM wig80_historical
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol
ORDER BY avg_volume DESC;

-- Volume-price relationship
SELECT 
    symbol,
    CORR(volume, close) as volume_price_correlation,
    AVG(volume) as avg_volume,
    AVG(close) as avg_price
FROM wig80_historical
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol
HAVING COUNT(*) > 20
ORDER BY ABS(volume_price_correlation) DESC;

-- =====================================
-- 5. CORRELATION ANALYSIS
-- =====================================

-- Get top correlations from market_correlations table
SELECT 
    symbol_a,
    symbol_b,
    correlation,
    strength,
    CASE 
        WHEN ABS(correlation) > 0.8 THEN 'VERY_STRONG'
        WHEN ABS(correlation) > 0.6 THEN 'STRONG'
        WHEN ABS(correlation) > 0.4 THEN 'MODERATE'
        WHEN ABS(correlation) > 0.2 THEN 'WEAK'
        ELSE 'VERY_WEAK'
    END as correlation_strength,
    ts
FROM market_correlations
WHERE ts >= dateadd('day', -7, now())
ORDER BY ABS(correlation) DESC
LIMIT 20;

-- Calculate moving correlations between top stocks
WITH stock_prices AS (
    SELECT symbol, 
           ts, 
           close
    FROM wig80_historical
    WHERE symbol IN ('PKN', 'KGH', 'PGE', 'PZU', 'TPS')
      AND ts >= dateadd('day', -30, now())
)
SELECT 
    a.symbol as symbol_a,
    b.symbol as symbol_b,
    a.ts,
    a.close as price_a,
    b.close as price_b,
    CORR(a.close, b.close) OVER (
        PARTITION BY a.symbol, b.symbol 
        ORDER BY a.ts 
        ROWS BETWEEN 20 PRECEDING AND CURRENT ROW
    ) as rolling_correlation_20d
FROM stock_prices a
JOIN stock_prices b ON DATE_TRUNC('day', a.ts) = DATE_TRUNC('day', b.ts)
WHERE a.symbol < b.symbol
  AND a.symbol IN ('PKN', 'KGH')
ORDER BY a.ts DESC, rolling_correlation_20d DESC;

-- =====================================
-- 6. AI INSIGHTS ANALYSIS
-- =====================================

-- Latest AI insights for high-confidence predictions
SELECT 
    symbol,
    insight_type,
    result,
    confidence,
    ts,
    CASE 
        WHEN confidence > 0.9 THEN 'VERY_HIGH'
        WHEN confidence > 0.8 THEN 'HIGH'
        WHEN confidence > 0.7 THEN 'MODERATE'
        ELSE 'LOW'
    END as confidence_level
FROM ai_insights
WHERE confidence > 0.8
  AND ts >= dateadd('day', -7, now())
ORDER BY confidence DESC, ts DESC
LIMIT 50;

-- AI insights by type
SELECT 
    insight_type,
    COUNT(*) as insight_count,
    AVG(confidence) as avg_confidence,
    COUNT(DISTINCT symbol) as symbols_covered
FROM ai_insights
WHERE ts >= dateadd('day', -30, now())
GROUP BY insight_type
ORDER BY insight_count DESC;

-- AI predictions vs actual performance
SELECT 
    i.symbol,
    i.insight_type,
    i.result,
    i.confidence as ai_confidence,
    h.close as predicted_price,
    h.close as actual_price,
    CASE 
        WHEN i.insight_type LIKE '%bullish%' OR i.insight_type LIKE '%buy%' THEN h.close > h.open
        WHEN i.insight_type LIKE '%bearish%' OR i.insight_type LIKE '%sell%' THEN h.close < h.open
        ELSE NULL
    END as prediction_actual_result
FROM ai_insights i
JOIN wig80_historical h ON i.symbol = h.symbol 
    AND DATE_TRUNC('hour', i.ts) = DATE_TRUNC('hour', h.ts)
WHERE i.ts >= dateadd('day', -7, now())
  AND h.ts >= dateadd('day', -7, now())
ORDER BY i.confidence DESC
LIMIT 100;

-- =====================================
-- 7. VALUATION ANALYSIS
-- =====================================

-- Valuation metrics analysis
SELECT 
    symbol,
    AVG(pe_ratio) as avg_pe,
    AVG(pb_ratio) as avg_pb,
    AVG(historical_pe_avg) as historical_pe,
    AVG(historical_pb_avg) as historical_pb,
    AVG(overvaluation_score) as avg_overvaluation,
    CASE 
        WHEN AVG(pe_ratio) > AVG(historical_pe_avg) * 1.2 THEN 'OVERVALUED_PE'
        WHEN AVG(pe_ratio) < AVG(historical_pe_avg) * 0.8 THEN 'UNDERVALUED_PE'
        ELSE 'FAIR_PE'
    END as pe_assessment
FROM valuation_analysis
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol
ORDER BY avg_overvaluation DESC;

-- Valuation scoring
SELECT 
    symbol,
    AVG(pe_ratio) as current_pe,
    AVG(pb_ratio) as current_pb,
    AVG(historical_pe_avg) as hist_pe,
    AVG(historical_pb_avg) as hist_pb,
    ((AVG(pe_ratio) - AVG(historical_pe_avg)) / AVG(historical_pe_avg)) * 100 as pe_deviation_pct,
    ((AVG(pb_ratio) - AVG(historical_pb_avg)) / AVG(historical_pb_avg)) * 100 as pb_deviation_pct,
    AVG(overvaluation_score)
FROM valuation_analysis
WHERE ts >= dateadd('day', -7, now())
GROUP BY symbol
HAVING COUNT(*) > 3
ORDER BY AVG(overvaluation_score) DESC;

-- =====================================
-- 8. COMPOSITE ANALYSIS
-- =====================================

-- Multi-factor ranking (combining technical, volume, and valuation)
WITH technical_scores AS (
    SELECT 
        symbol,
        AVG(rsi) as avg_rsi,
        AVG(macd) as avg_macd,
        RANK() OVER (ORDER BY AVG(rsi)) as rsi_rank
    FROM wig80_historical
    WHERE ts >= dateadd('day', -14, now())
    GROUP BY symbol
),
volume_scores AS (
    SELECT 
        symbol,
        SUM(volume) as total_volume,
        RANK() OVER (ORDER BY SUM(volume) DESC) as volume_rank
    FROM wig80_historical
    WHERE ts >= dateadd('day', -30, now())
    GROUP BY symbol
),
valuation_scores AS (
    SELECT 
        symbol,
        AVG(overvaluation_score) as overvaluation,
        RANK() OVER (ORDER BY AVG(overvaluation_score)) as valuation_rank
    FROM valuation_analysis
    WHERE ts >= dateadd('day', -30, now())
    GROUP BY symbol
)
SELECT 
    t.symbol,
    t.avg_rsi,
    t.rsi_rank,
    v.total_volume,
    v.volume_rank,
    val.overvaluation,
    val.valuation_rank,
    (t.rsi_rank + v.volume_rank + val.valuation_rank) / 3 as composite_score
FROM technical_scores t
JOIN volume_scores v ON t.symbol = v.symbol
JOIN valuation_scores val ON t.symbol = val.symbol
ORDER BY composite_score
LIMIT 20;

-- =====================================
-- 9. REAL-TIME ALERTS
-- =====================================

-- Stocks with unusual activity
SELECT 
    symbol,
    AVG(volume) as avg_volume,
    LAST_VALUE(volume) as current_volume,
    (LAST_VALUE(volume) - AVG(volume)) / AVG(volume) * 100 as volume_spike_pct,
    AVG(close) as avg_price,
    LAST_VALUE(rsi) as current_rsi
FROM wig80_historical
WHERE ts >= dateadd('hour', -24, now())
GROUP BY symbol
HAVING COUNT(*) > 10
  AND (LAST_VALUE(volume) - AVG(volume)) / AVG(volume) > 2.0  -- 200% volume spike
ORDER BY volume_spike_pct DESC;

-- Potential breakout signals
SELECT 
    symbol,
    LAST_VALUE(close) as current_price,
    AVG(bb_upper) as avg_bb_upper,
    AVG(bb_lower) as avg_bb_lower,
    LAST_VALUE(rsi) as current_rsi,
    CASE 
        WHEN LAST_VALUE(close) > AVG(bb_upper) AND LAST_VALUE(rsi) < 70 THEN 'POTENTIAL_BULLISH_BREAKOUT'
        WHEN LAST_VALUE(close) < AVG(bb_lower) AND LAST_VALUE(rsi) > 30 THEN 'POTENTIAL_BEARISH_BREAKDOWN'
        ELSE 'NO_BREAKOUT_SIGNAL'
    END as breakout_signal
FROM wig80_historical
WHERE ts >= dateadd('day', -7, now())
GROUP BY symbol
HAVING COUNT(*) > 5
ORDER BY current_price DESC;

-- =====================================
-- 10. DASHBOARD QUERIES
-- =====================================

-- Market overview
SELECT 
    COUNT(DISTINCT symbol) as total_symbols,
    AVG(close) as market_avg_price,
    SUM(volume) as total_volume,
    AVG(rsi) as avg_market_rsi,
    COUNT(CASE WHEN rsi > 70 THEN 1 END) as overbought_count,
    COUNT(CASE WHEN rsi < 30 THEN 1 END) as oversold_count
FROM wig80_historical
WHERE ts >= dateadd('hour', -1, now());

-- Top gainers/losers today
SELECT 
    symbol,
    FIRST_VALUE(open) as open_price,
    LAST_VALUE(close) as current_price,
    (LAST_VALUE(close) - FIRST_VALUE(open)) / FIRST_VALUE(open) * 100 as change_pct,
    LAST_VALUE(volume) as volume,
    LAST_VALUE(rsi) as rsi
FROM wig80_historical
WHERE ts >= dateadd('day', -1, now())
SAMPLE BY 1d ALIGN TO CALENDAR
ORDER BY change_pct DESC
LIMIT 10;

-- Watchlist query (favorite stocks)
SELECT 
    symbol,
    LAST_VALUE(close) as price,
    LAST_VALUE(rsi) as rsi,
    LAST_VALUE(macd) as macd,
    SUM(volume) as daily_volume,
    CASE 
        WHEN LAST_VALUE(rsi) > 70 THEN 'SELL_SIGNAL'
        WHEN LAST_VALUE(rsi) < 30 THEN 'BUY_SIGNAL'
        WHEN LAST_VALUE(macd) > 0 THEN 'BULLISH_MOMENTUM'
        ELSE 'BEARISH_MOMENTUM'
    END as trading_signal
FROM wig80_historical
WHERE symbol IN ('PKN', 'KGH', 'PGE', 'PZU', 'TPS')
  AND ts >= dateadd('day', -1, now())
GROUP BY symbol
ORDER BY rsi DESC;
