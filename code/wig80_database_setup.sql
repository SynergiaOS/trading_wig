-- WIG80 QuestDB Database Setup Script
-- Polish Stock Market Time Series Analysis
-- =======================================

-- Create the main historical data table
CREATE TABLE IF NOT EXISTS wig80_historical (
    ts TIMESTAMP,
    symbol SYMBOL CAPACITY 200 CACHE,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    volume LONG,
    macd DOUBLE,
    rsi DOUBLE,
    bb_upper DOUBLE,
    bb_lower DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create AI insights table
CREATE TABLE IF NOT EXISTS ai_insights (
    ts TIMESTAMP,
    symbol SYMBOL CAPACITY 200 CACHE,
    insight_type STRING,
    result JSON,
    confidence DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create market correlations table
CREATE TABLE IF NOT EXISTS market_correlations (
    ts TIMESTAMP,
    symbol_a SYMBOL CAPACITY 200 CACHE,
    symbol_b SYMBOL CAPACITY 200 CACHE,
    correlation DOUBLE,
    strength DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create valuation analysis table
CREATE TABLE IF NOT EXISTS valuation_analysis (
    ts TIMESTAMP,
    symbol SYMBOL CAPACITY 200 CACHE,
    pe_ratio DOUBLE,
    pb_ratio DOUBLE,
    historical_pe_avg DOUBLE,
    historical_pb_avg DOUBLE,
    overvaluation_score DOUBLE
) TIMESTAMP(ts) PARTITION BY DAY WAL;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS wig80_historical_symbol_idx ON wig80_historical(symbol);
CREATE INDEX IF NOT EXISTS wig80_historical_symbol_ts_idx ON wig80_historical(symbol, ts DESC);

CREATE INDEX IF NOT EXISTS ai_insights_symbol_idx ON ai_insights(symbol);
CREATE INDEX IF NOT EXISTS ai_insights_symbol_ts_idx ON ai_insights(symbol, ts DESC);
CREATE INDEX IF NOT EXISTS ai_insights_type_idx ON ai_insights(insight_type);

CREATE INDEX IF NOT EXISTS market_correlations_symbol_a_idx ON market_correlations(symbol_a);
CREATE INDEX IF NOT EXISTS market_correlations_symbol_b_idx ON market_correlations(symbol_b);
CREATE INDEX IF NOT EXISTS market_correlations_symbols_ts_idx ON market_correlations(symbol_a, symbol_b, ts DESC);

CREATE INDEX IF NOT EXISTS valuation_analysis_symbol_idx ON valuation_analysis(symbol);
CREATE INDEX IF NOT EXISTS valuation_analysis_symbol_ts_idx ON valuation_analysis(symbol, ts DESC);

-- Create materialized views for common queries
-- Daily aggregation view for wig80_historical
CREATE MATERIALIZED VIEW IF NOT EXISTS wig80_daily_summary AS
SELECT
    symbol,
    to_timestamp(to_int(ts / 86400000) * 86400000, 'yyyyMMdd') AS date,
    first_value(open) as open,
    max(high) as high,
    min(low) as low,
    last_value(close) as close,
    sum(volume) as volume,
    last_value(macd) as macd,
    last_value(rsi) as rsi,
    last_value(bb_upper) as bb_upper,
    last_value(bb_lower) as bb_lower
FROM wig80_historical
SAMPLE BY 1d ALIGN TO CALENDAR;

-- Monthly aggregation view
CREATE MATERIALIZED VIEW IF NOT EXISTS wig80_monthly_summary AS
SELECT
    symbol,
    to_timestamp(to_int(ts / 86400000) * 86400000, 'yyyyMM') AS month,
    first_value(open) as open,
    max(high) as high,
    min(low) as low,
    last_value(close) as close,
    sum(volume) as volume,
    last_value(macd) as macd,
    last_value(rsi) as rsi,
    last_value(bb_upper) as bb_upper,
    last_value(bb_lower) as bb_lower
FROM wig80_historical
SAMPLE BY 1M ALIGN TO CALENDAR;

-- Create sample data for WIG80 companies (Polish stock symbols)
-- These are some common WIG80 companies
INSERT INTO wig80_historical (ts, symbol, open, high, low, close, volume, macd, rsi, bb_upper, bb_lower)
SELECT
    dateadd('day', -random_int(0, 365), now()) as ts,
    symbol,
    (100 + random_double() * 50) as open,
    (120 + random_double() * 80) as high,
    (90 + random_double() * 40) as low,
    (105 + random_double() * 70) as close,
    (10000 + random_int(0, 1000000)) as volume,
    (random_double() * 2 - 1) as macd,
    (30 + random_double() * 40) as rsi,
    (150 + random_double() * 50) as bb_upper,
    (80 + random_double() * 30) as bb_lower
FROM (
    SELECT 'PKN' as symbol UNION ALL
    SELECT 'KGH' UNION ALL
    SELECT 'PGE' UNION ALL
    SELECT 'PZU' UNION ALL
    SELECT 'TPS' UNION ALL
    SELECT 'ALE' UNION ALL
    SELECT 'PCC' UNION ALL
    SELECT 'KRU' UNION ALL
    SELECT 'PGN' UNION ALL
    SELECT 'CCC' UNION ALL
    SELECT 'ING' UNION ALL
    SELECT 'LPP' UNION ALL
    SELECT 'MIL' UNION ALL
    SELECT 'CDR' UNION ALL
    SELECT 'CIG' UNION ALL
    SELECT 'LPP' UNION ALL
    SELECT 'DNP' UNION ALL
    SELECT 'ORB' UNION ALL
    SELECT 'BIOT' UNION ALL
    SELECT 'JOP' UNION ALL
    SELECT 'KGN' UNION ALL
    SELECT '11B' UNION ALL
    SELECT 'ACM' UNION ALL
    SELECT 'ACP' UNION ALL
    SELECT 'ACT' UNION ALL
    SELECT 'ADR' UNION ALL
    SELECT 'ADV' UNION ALL
    SELECT 'AGO' UNION ALL
    SELECT 'AMB' UNION ALL
    SELECT 'APN' UNION ALL
    SELECT 'ARH' UNION ALL
    SELECT 'ASB' UNION ALL
    SELECT 'ATR' UNION ALL
    SELECT 'BFT' UNION ALL
    SELECT 'BMC' UNION ALL
    SELECT 'BRA' UNION ALL
    SELECT 'BRU' UNION ALL
    SELECT 'BST' UNION ALL
    SELECT 'CDA' UNION ALL
    SELECT 'CIE' UNION ALL
    SELECT 'COM' UNION ALL
    SELECT 'COR' UNION ALL
    SELECT 'CYF' UNION ALL
    SELECT 'DEK' UNION ALL
    SELECT 'DOM' UNION ALL
    SELECT 'DVL' UNION ALL
    SELECT 'DWN' UNION ALL
    SELECT 'EAT' UNION ALL
    SELECT 'ENI' UNION ALL
    SELECT 'ERB' UNION ALL
    SELECT 'ETH' UNION ALL
    SELECT 'FOR' UNION ALL
    SELECT 'FSK' UNION ALL
    SELECT 'GHE' UNION ALL
    SELECT 'GLC' UNION ALL
    SELECT 'GPL' UNION ALL
    SELECT 'GRO' UNION ALL
    SELECT 'GTN' UNION ALL
    SELECT 'HUD' UNION ALL
    SELECT 'HRS' UNION ALL
    SELECT 'IFR' UNION ALL
    SELECT 'IGN' UNION ALL
    SELECT 'IKC' UNION ALL
    SELECT 'IPN' UNION ALL
    SELECT 'IRC' UNION ALL
    SELECT 'IRL' UNION ALL
    SELECT 'ITM' UNION ALL
    SELECT 'KER' UNION ALL
    SELECT 'KTY' UNION ALL
    SELECT 'LCC' UNION ALL
    SELECT 'LST' UNION ALL
    SELECT 'MAB' UNION ALL
    SELECT 'MAL' UNION ALL
    SELECT 'MCL' UNION ALL
    SELECT 'MLG' UNION ALL
    SELECT 'MRC' UNION ALL
    SELECT 'MSP' UNION ALL
    SELECT 'MSW' UNION ALL
    SELECT 'OPN' UNION ALL
    SELECT 'ORB' UNION ALL
    SELECT 'PCE' UNION ALL
    SELECT 'PCF' UNION ALL
    SELECT 'PCR' UNION ALL
    SELECT 'PCT' UNION ALL
    SELECT 'PEN' UNION ALL
    SELECT 'PEP' UNION ALL
    SELECT 'PGM' UNION ALL
    SELECT 'PKO' UNION ALL
    SELECT 'PLY' UNION ALL
    SELECT 'PMA' UNION ALL
    SELECT 'PNT' UNION ALL
    SELECT 'POM' UNION ALL
    SELECT 'PRI' UNION ALL
    SELECT 'PST' UNION ALL
    SELECT 'REG' UNION ALL
    SELECT 'RIV' UNION ALL
    SELECT 'SAL' UNION ALL
    SELECT 'SEL' UNION ALL
    SELECT 'SFG' UNION ALL
    SELECT 'SKR' UNION ALL
    SELECT 'SLM' UNION ALL
    SELECT 'SNK' UNION ALL
    SELECT 'SON' UNION ALL
    SELECT 'SPL' UNION ALL
    SELECT 'STS' UNION ALL
    SELECT 'STX' UNION ALL
    SELECT 'SVD' UNION ALL
    SELECT 'TER' UNION ALL
    SELECT 'TXM' UNION ALL
    SELECT 'ULG' UNION ALL
    SELECT 'UNI' UNION ALL
    SELECT 'VOT' UNION ALL
    SELECT 'VTI' UNION ALL
    SELECT 'WIG' UNION ALL
    SELECT 'WSE' UNION ALL
    SELECT 'XTB'
) symbols
SAMPLE 10000;