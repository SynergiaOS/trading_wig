# WIG80 QuestDB Setup Guide

## Overview

This repository contains a complete setup for **QuestDB** database specifically configured for **WIG80 Polish Stock Market Analysis**. QuestDB is a high-performance time series database that excels at handling financial data with real-time analytics capabilities.

## What is WIG80?

WIG80 is an index of the 80 largest and most liquid companies listed on the Warsaw Stock Exchange (WSE), representing various sectors of the Polish economy. This setup provides tools to analyze historical stock data, generate AI insights, track correlations, and perform fundamental analysis.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 8812, 9009, 9000 available

### One-Command Setup

```bash
# Run the complete setup
./setup_questdb.sh

# Or with options
./setup_questdb.sh --skip-docker --skip-data  # Skip Docker and sample data
./setup_questdb.sh --verbose                    # Show detailed output
```

### Manual Setup

If you prefer manual setup:

```bash
# 1. Start QuestDB
docker-compose -f docker-compose.questdb.yml up -d

# 2. Wait for API to be ready (30 seconds)
sleep 30

# 3. Initialize database schema
# Use the SQL scripts provided

# 4. Install Python dependencies and populate data
python3 wig80_questdb_client.py
```

## Architecture

### Database Schema

The QuestDB instance includes four optimized tables:

#### 1. `wig80_historical` - Historical Stock Data
```sql
CREATE TABLE wig80_historical (
    ts TIMESTAMP,           -- Timestamp
    symbol SYMBOL,          -- Stock symbol (e.g., PKN, KGH)
    open DOUBLE,            -- Opening price
    high DOUBLE,            -- Highest price
    low DOUBLE,             -- Lowest price
    close DOUBLE,           -- Closing price
    volume LONG,            -- Trading volume
    macd DOUBLE,            -- MACD technical indicator
    rsi DOUBLE,             -- RSI technical indicator
    bb_upper DOUBLE,        -- Bollinger Band upper
    bb_lower DOUBLE         -- Bollinger Band lower
) TIMESTAMP(ts) PARTITION BY DAY WAL;
```

#### 2. `ai_insights` - AI-Generated Analysis
```sql
CREATE TABLE ai_insights (
    ts TIMESTAMP,           -- Analysis timestamp
    symbol SYMBOL,          -- Stock symbol
    insight_type STRING,    -- Type of insight (sentiment, prediction, etc.)
    result JSON,            -- Insight data as JSON
    confidence DOUBLE       -- Confidence score (0-1)
) TIMESTAMP(ts) PARTITION BY DAY WAL;
```

#### 3. `market_correlations` - Correlation Analysis
```sql
CREATE TABLE market_correlations (
    ts TIMESTAMP,           -- Correlation timestamp
    symbol_a SYMBOL,        -- First stock symbol
    symbol_b SYMBOL,        -- Second stock symbol
    correlation DOUBLE,     -- Correlation coefficient (-1 to 1)
    strength DOUBLE         -- Correlation strength (0-1)
) TIMESTAMP(ts) PARTITION BY DAY WAL;
```

#### 4. `valuation_analysis` - Fundamental Analysis
```sql
CREATE TABLE valuation_analysis (
    ts TIMESTAMP,           -- Analysis timestamp
    symbol SYMBOL,          -- Stock symbol
    pe_ratio DOUBLE,        -- Price-to-Earnings ratio
    pb_ratio DOUBLE,        -- Price-to-Book ratio
    historical_pe_avg DOUBLE, -- Historical PE average
    historical_pb_avg DOUBLE, -- Historical PB average
    overvaluation_score DOUBLE -- Overvaluation score
) TIMESTAMP(ts) PARTITION BY DAY WAL;
```

### Performance Optimizations

- **Partitioning**: Daily partitioning for efficient time-range queries
- **WAL (Write-Ahead Logging)**: Enabled for durability
- **Symbol Caching**: 200 capacity for frequently accessed symbols
- **Indexes**: Optimized indexes on symbol and timestamp combinations
- **Materialized Views**: Pre-aggregated daily and monthly summaries

## Access Information

### Web Console
- **URL**: http://localhost:9009
- **Username**: admin
- **Password**: quest

### REST API
- **Base URL**: http://localhost:8812
- **Authentication**: Basic Auth (admin/quest)
- **Query Endpoint**: `/exec`

### PostgreSQL Wire Protocol
- **Host**: localhost
- **Port**: 9000
- **Database**: `questdb`
- **Username**: admin
- **Password**: quest

## API Usage Examples

### REST API Queries

#### Get Top Performing Stocks (Last 30 Days)
```bash
curl -u admin:quest "http://localhost:8812/exec?query=$(urlencode 'SELECT symbol, SUM(volume) as total_volume, AVG(close) as avg_price FROM wig80_historical WHERE ts >= dateadd(day, -30, now()) GROUP BY symbol ORDER BY total_volume DESC LIMIT 10')"
```

#### Technical Analysis Summary
```bash
curl -u admin:quest "http://localhost:8812/exec?query=$(urlencode 'SELECT symbol, AVG(rsi) as avg_rsi, AVG(macd) as avg_macd FROM wig80_historical WHERE ts >= dateadd(day, -7, now()) GROUP BY symbol ORDER BY avg_rsi DESC LIMIT 10')"
```

#### Recent Data for Specific Symbol
```bash
curl -u admin:quest "http://localhost:8812/exec?query=$(urlencode 'SELECT * FROM wig80_historical WHERE symbol = \"PKN\" AND ts >= dateadd(day, -1, now()) ORDER BY ts DESC')"
```

### Python Client Usage

```python
import asyncio
from wig80_questdb_client import QuestDBClient

async def example():
    async with QuestDBClient(auth=("admin", "quest")) as client:
        # Query recent data
        results = await client.execute_query("""
            SELECT * FROM wig80_historical 
            WHERE ts >= dateadd(day, -7, now())
            ORDER BY ts DESC
            LIMIT 100
        """)
        
        for row in results:
            print(f"Symbol: {row[1]}, Price: {row[5]}, Volume: {row[6]}")

asyncio.run(example())
```

## File Structure

```
code/
├── docker-compose.questdb.yml    # Docker Compose configuration
├── questdb_config/
│   └── server.conf               # QuestDB server configuration
├── wig80_database_setup.sql      # Database schema setup
├── wig80_questdb_client.py       # Python client and utilities
├── setup_questdb.sh             # Automated setup script
├── sample_queries.sql           # Sample SQL queries
├── management_scripts/          # Additional management tools
└── README.md                    # This file
```

## Sample Queries

### Performance Analysis

```sql
-- Top 10 stocks by volume (last 30 days)
SELECT symbol, 
       SUM(volume) as total_volume,
       AVG(close) as avg_price,
       (MAX(close) - MIN(close)) / MIN(close) * 100 as volatility_pct
FROM wig80_historical
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol
ORDER BY total_volume DESC
LIMIT 10;

-- Daily price change analysis
SELECT symbol,
       first_value(close) as open_price,
       last_value(close) as close_price,
       (last_value(close) - first_value(close)) / first_value(close) * 100 as daily_change_pct
FROM wig80_historical
WHERE ts >= dateadd('day', -1, now())
SAMPLE BY 1d ALIGN TO CALENDAR
ORDER BY daily_change_pct DESC
LIMIT 10;
```

### Technical Analysis

```sql
-- RSI-based signals
SELECT symbol,
       AVG(rsi) as avg_rsi,
       MIN(rsi) as min_rsi,
       MAX(rsi) as max_rsi,
       CASE 
           WHEN AVG(rsi) > 70 THEN 'OVERBOUGHT'
           WHEN AVG(rsi) < 30 THEN 'OVERSOLD'
           ELSE 'NEUTRAL'
       END as signal
FROM wig80_historical
WHERE ts >= dateadd('day', -14, now())
GROUP BY symbol
HAVING COUNT(*) > 10
ORDER BY avg_rsi DESC;

-- MACD crossover signals
SELECT symbol,
       AVG(macd) as current_macd,
       LAG(AVG(macd), 1) OVER (PARTITION BY symbol ORDER BY ts) as previous_macd
FROM wig80_historical
WHERE ts >= dateadd('day', -30, now())
GROUP BY symbol, to_timestamp(to_int(ts/86400000)*86400000, 'yyyyMMdd')
ORDER BY symbol, ts DESC;
```

### Correlation Analysis

```sql
-- Calculate correlations between stocks
SELECT 
    a.symbol_a,
    a.symbol_b,
    a.correlation,
    CASE 
        WHEN ABS(a.correlation) > 0.7 THEN 'STRONG'
        WHEN ABS(a.correlation) > 0.5 THEN 'MODERATE'
        ELSE 'WEAK'
    END as correlation_strength
FROM market_correlations a
WHERE a.ts >= dateadd('day', -7, now())
ORDER BY ABS(a.correlation) DESC
LIMIT 20;
```

### AI Insights Query

```sql
-- Get latest AI insights for high-confidence predictions
SELECT symbol,
       insight_type,
       result,
       confidence,
       ts
FROM ai_insights
WHERE confidence > 0.8
  AND ts >= dateadd('day', -1, now())
ORDER BY confidence DESC, ts DESC;
```

## Management Commands

### Start/Stop QuestDB

```bash
# Start QuestDB
docker-compose -f docker-compose.questdb.yml up -d

# Stop QuestDB
docker-compose -f docker-compose.questdb.yml down

# Stop and remove volumes (WARNING: Deletes all data)
docker-compose -f docker-compose.questdb.yml down -v

# View logs
docker-compose -f docker-compose.questdb.yml logs -f

# Restart
docker-compose -f docker-compose.questdb.yml restart
```

### Database Maintenance

```sql
-- Optimize tables
OPTIMIZE TABLE wig80_historical;
OPTIMIZE TABLE ai_insights;
OPTIMIZE TABLE market_correlations;
OPTIMIZE TABLE valuation_analysis;

-- Check table statistics
SHOW TABLES;
DESCRIBE wig80_historical;

-- Vacuum operations (if needed)
VACUUM TABLE wig80_historical;
```

### Backup and Restore

```bash
# Backup data directory
cp -r ~/.questdb/db ./backup_questdb_$(date +%Y%m%d)

# Restore from backup
cp -r ./backup_questdb_YYYYMMDD ~/.questdb/db
```

## Monitoring and Performance

### System Monitoring

- **Memory Usage**: QuestDB uses memory-mapped files for optimal performance
- **Disk Space**: Monitor `/root/.questdb` directory for data growth
- **Query Performance**: Use `EXPLAIN` statements to optimize queries

### Performance Tips

1. **Use partitions**: Always filter by timestamp ranges when possible
2. **Symbol indexing**: Symbol columns are automatically indexed
3. **Sampling**: Use `SAMPLE BY` clause for time-based aggregations
4. **Materialized views**: Leverage pre-computed aggregations
5. **Batch operations**: Use batch inserts for large data loads

### Monitoring Queries

```sql
-- Check table sizes
SELECT table, rows, allocated_bytes, used_bytes 
FROM information_schema.tables 
WHERE table IN ('wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis');

-- Query performance statistics
SELECT query, count, avg_time_ms, max_time_ms
FROM information_schema.query_log
ORDER BY count DESC
LIMIT 10;
```

## Configuration Customization

### Memory Settings

Edit `questdb_config/server.conf` to adjust memory usage:

```conf
# For systems with 8GB+ RAM
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+UnlockExperimentalVMOptions
-XX:+UseCGroupMemoryLimitForHeap

# Set heap size (adjust based on available memory)
-Xmx4g
```

### Performance Tuning

```conf
# Writer pool configuration
writer.pool.capacity=4

# Reader pool configuration  
reader.pool.capacity=32

# WAL configuration
wal.max.file.size=1024MiB
wal.flush.interval=5s
```

## Troubleshooting

### Common Issues

#### QuestDB Won't Start
```bash
# Check if ports are available
netstat -tulpn | grep -E "8812|9009|9000"

# Check Docker logs
docker-compose -f docker-compose.questdb.yml logs

# Check system resources
free -h
df -h
```

#### Connection Issues
```bash
# Test connectivity
curl -u admin:quest http://localhost:8812/health

# Check authentication
curl -u admin:quest "http://localhost:8812/exec?query=SELECT 1"
```

#### Performance Issues
```sql
-- Check active queries
SHOW QUERIES;

-- Terminate long-running queries
KILL QUERY <query_id>;

-- Optimize tables
OPTIMIZE TABLE wig80_historical;
```

### Logs Location

- **QuestDB Logs**: `docker-compose logs questdb`
- **Data Directory**: `~/.questdb/`
- **Config Directory**: `./questdb_config/`

## Integration Examples

### Flask Integration

```python
from flask import Flask, jsonify
import asyncio
from wig80_questdb_client import QuestDBClient

app = Flask(__name__)

@app.route('/api/wig80/top-performers')
async def get_top_performers():
    async with QuestDBClient() as client:
        query = """
        SELECT symbol, AVG(close) as avg_price, SUM(volume) as total_volume
        FROM wig80_historical
        WHERE ts >= dateadd('day', -30, now())
        GROUP BY symbol
        ORDER BY total_volume DESC
        LIMIT 10
        """
        results = await client.execute_query(query)
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
```

### Real-time Data Pipeline

```python
import asyncio
from wig80_questdb_client import QuestDBClient

async def real_time_pipeline():
    async with QuestDBClient() as client:
        # Continuous monitoring
        while True:
            # Get latest data
            query = """
            SELECT symbol, close, volume, rsi
            FROM wig80_historical
            WHERE ts >= dateadd('hour', -1, now())
            ORDER BY ts DESC
            """
            results = await client.execute_query(query)
            
            # Process and analyze
            for row in results:
                if row[3] > 70:  # RSI overbought
                    print(f"OVERBOUGHT: {row[0]} RSI: {row[3]}")
                elif row[3] < 30:  # RSI oversold
                    print(f"OVERSOLD: {row[0]} RSI: {row[3]}")
            
            await asyncio.sleep(60)  # Check every minute

asyncio.run(real_time_pipeline())
```

## Support and Resources

### Documentation
- [QuestDB Documentation](https://questdb.io/docs/)
- [SQL Reference](https://questdb.io/docs/reference/sql/)
- [Performance Guide](https://questdb.io/docs/performance/)

### Community
- [QuestDB Community](https://questdb.io/community/)
- [GitHub Issues](https://github.com/questdb/questdb/issues)

### Performance Benchmarks
- [QuestDB Performance](https://questdb.io/benchmarks/)

## License

This setup is provided as-is for WIG80 Polish Stock Market Analysis. 
QuestDB is licensed under Apache License 2.0.

---

**Happy analyzing Polish stock market data with QuestDB!** 📈🇵🇱
