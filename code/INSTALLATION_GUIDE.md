# WIG80 QuestDB Complete Installation Guide

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Quick Installation](#quick-installation)
4. [Detailed Installation](#detailed-installation)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Production Deployment](#production-deployment)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Overview

This guide provides complete instructions for setting up QuestDB specifically for **WIG80 Polish Stock Market Analysis**. QuestDB is a high-performance time series database optimized for financial data processing.

### What You'll Get

- ✅ High-performance time series database
- ✅ Optimized schema for WIG80 stock data
- ✅ Technical indicators and AI insights storage
- ✅ Correlation analysis capabilities
- ✅ Fundamental analysis metrics
- ✅ Real-time data ingestion support
- ✅ Advanced time-series queries
- ✅ Web-based administration console

## System Requirements

### Minimum Requirements

- **OS**: Linux, macOS, or Windows with Docker support
- **CPU**: 2+ cores
- **RAM**: 4GB (8GB recommended)
- **Storage**: 10GB free space
- **Network**: Ports 8812, 9000, 9009 available

### Recommended Requirements

- **OS**: Ubuntu 20.04+, CentOS 8+, or macOS 12+
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB for production)
- **Storage**: 50GB+ SSD
- **Network**: Stable internet for data feeds

### Software Dependencies

- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **Python**: 3.8+ (for client scripts)
- **Browser**: Chrome/Firefox/Safari for web console

## Quick Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone or download the setup files
cd code/

# Run the complete setup script
chmod +x setup_questdb.sh
./setup_questdb.sh

# Wait for setup to complete (2-3 minutes)
# Follow the success messages and access information
```

### Option 2: Manual Setup

```bash
# 1. Start QuestDB
docker-compose -f docker-compose.questdb.yml up -d

# 2. Wait for services to be ready
sleep 30

# 3. Initialize database schema
curl -u admin:quest "http://localhost:8812/exec" --data-urlencode "query@-" << 'EOF'
-- Run the SQL from wig80_database_setup.sql file
EOF

# 4. Install Python dependencies
pip3 install -r requirements.txt

# 5. Populate sample data
python3 wig80_questdb_client.py

# 6. Test the setup
python3 test_questdb_setup.py
```

## Detailed Installation

### Step 1: Install Docker and Docker Compose

#### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (optional, for non-root usage)
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### CentOS/RHEL

```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS

```bash
# Install Docker Desktop (recommended)
# Download from: https://docs.docker.com/desktop/mac/install/

# Or install via Homebrew
brew install --cask docker
brew install docker-compose
```

#### Windows

```bash
# Install Docker Desktop for Windows
# Download from: https://docs.docker.com/desktop/windows/install/
```

### Step 2: Download Setup Files

Create a working directory and download all required files:

```bash
# Create working directory
mkdir wig80-questdb
cd wig80-questdb

# Create required directories
mkdir -p questdb_config data logs

# Download/copy these files to the directory:
# - docker-compose.questdb.yml
# - questdb_config/server.conf
# - wig80_database_setup.sql
# - wig80_questdb_client.py
# - setup_questdb.sh
# - sample_queries.sql
# - requirements.txt
# - questdb_management.py
# - test_questdb_setup.py
# - README_QuestDB.md
```

### Step 3: Configure QuestDB

#### Memory Configuration

Edit `questdb_config/server.conf` to set appropriate memory limits:

```bash
# For 8GB system
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-Xmx4g

# For 16GB+ system
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-Xmx8g
```

#### Network Configuration

Ensure required ports are available:

```bash
# Check port availability
netstat -tulpn | grep -E "8812|9000|9009"

# If ports are in use, modify docker-compose.questdb.yml
# to use different ports or stop conflicting services
```

### Step 4: Start QuestDB

```bash
# Start services
docker-compose -f docker-compose.questdb.yml up -d

# Check status
docker-compose -f docker-compose.questdb.yml ps

# View logs
docker-compose -f docker-compose.questdb.yml logs -f questdb
```

### Step 5: Initialize Database

```bash
# Initialize schema
curl -u admin:quest -G "http://localhost:8812/exec" --data-urlencode "query@-" < wig80_database_setup.sql

# Alternative: Execute SQL file directly
# Copy contents from wig80_database_setup.sql and paste into QuestDB console
```

### Step 6: Install Python Dependencies

```bash
# Install required packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import aiohttp, pandas, numpy; print('Dependencies installed successfully')"
```

### Step 7: Populate Sample Data

```bash
# Run data population script
python3 wig80_questdb_client.py

# Check if data was inserted
curl -u admin:quest "http://localhost:8812/exec?query=SELECT COUNT(*) FROM wig80_historical"
```

## Configuration

### Authentication Configuration

Default credentials (change in production):

```yaml
# docker-compose.questdb.yml
environment:
  - QDB_HTTP_USER=admin
  - QDB_HTTP_PASSWORD=quest
  - QDB_PG_USER=admin
  - QDB_PG_PASSWORD=quest
```

To change credentials:

1. Update `docker-compose.questdb.yml`
2. Update `questdb_config/server.conf`
3. Restart container

### Performance Tuning

#### Memory Settings

```bash
# Edit docker-compose.questdb.yml
command: >
  -d
  -f
  -j 0
  -Xmx8g              # Increase heap size
  -XX:+UseG1GC        # Use G1 garbage collector
  -i /etc/questdb/server.conf
```

#### Partition Settings

```conf
# questdb_config/server.conf
partitions.autocreate.day=true    # Auto-create daily partitions
partitions.retention=7d           # Keep 7 days of partitions
wal.max.file.size=2048MiB        # Larger WAL files for bulk inserts
```

### Data Retention

Configure automatic data cleanup:

```bash
# Run cleanup script
python3 questdb_management.py clean --days 90

# Or set up cron job for regular cleanup
echo "0 2 * * 0 /usr/bin/python3 /path/to/questdb_management.py clean --days 90" | crontab -
```

## Verification

### Automated Testing

```bash
# Run comprehensive test suite
python3 test_questdb_setup.py

# Expected output: "ALL TESTS PASSED! QuestDB is ready for WIG80 analysis"
```

### Manual Verification

#### 1. Check Service Status

```bash
# Check container status
docker-compose -f docker-compose.questdb.yml ps

# Check logs
docker-compose -f docker-compose.questdb.yml logs questdb
```

#### 2. Test Web Console

```bash
# Test console accessibility
curl -I http://localhost:9009

# Expected: HTTP/1.1 401 or 200 (depending on auth)
```

#### 3. Test REST API

```bash
# Test health endpoint
curl -u admin:quest http://localhost:8812/health

# Test data query
curl -u admin:quest "http://localhost:8812/exec?query=SELECT COUNT(*) FROM wig80_historical"
```

#### 4. Test PostgreSQL Wire Protocol

```bash
# Test with psql (if available)
psql -h localhost -p 9000 -U admin -d questdb -c "SELECT COUNT(*) FROM wig80_historical;"
```

### Web Console Access

1. Open browser to `http://localhost:9009`
2. Login with:
   - Username: `admin`
   - Password: `quest`
3. Navigate through tables and run queries

### Sample Queries to Test

```sql
-- Test 1: Basic data query
SELECT * FROM wig80_historical LIMIT 5;

-- Test 2: Symbol filtering
SELECT DISTINCT symbol FROM wig80_historical LIMIT 10;

-- Test 3: Time range query
SELECT * FROM wig80_historical WHERE ts >= dateadd('day', -1, now()) LIMIT 10;

-- Test 4: Aggregation
SELECT symbol, COUNT(*), AVG(close) FROM wig80_historical GROUP BY symbol LIMIT 10;
```

## Usage Examples

### Python Client Usage

```python
import asyncio
from wig80_questdb_client import QuestDBClient

async def example():
    async with QuestDBClient(auth=("admin", "quest")) as client:
        # Query recent data
        results = await client.execute_query("""
            SELECT symbol, AVG(close) as avg_price, SUM(volume) as total_volume
            FROM wig80_historical
            WHERE ts >= dateadd('day', -30, now())
            GROUP BY symbol
            ORDER BY total_volume DESC
            LIMIT 10
        """)
        
        for row in results:
            print(f"Symbol: {row[0]}, Avg Price: {row[1]:.2f}, Volume: {row[2]:,}")

asyncio.run(example())
```

### API Integration

```bash
# Get top performers
curl -u admin:quest "http://localhost:8812/exec?query=$(urlencode 'SELECT symbol, SUM(volume) FROM wig80_historical WHERE ts >= dateadd(day, -30, now()) GROUP BY symbol ORDER BY SUM(volume) DESC LIMIT 10')"

# Get technical indicators
curl -u admin:quest "http://localhost:8812/exec?query=$(urlencode 'SELECT symbol, AVG(rsi), AVG(macd) FROM wig80_historical WHERE ts >= dateadd(day, -7, now()) GROUP BY symbol ORDER BY AVG(rsi) DESC LIMIT 10')"
```

### Data Insertion

```python
# Insert new historical data
new_data = {
    'ts': '2025-11-05 14:30:00',
    'symbol': 'PKN',
    'open': 50.25,
    'high': 51.75,
    'low': 49.80,
    'close': 51.50,
    'volume': 125000,
    'macd': 0.75,
    'rsi': 65.2,
    'bb_upper': 55.0,
    'bb_lower': 45.0
}

async with QuestDBClient(auth=("admin", "quest")) as client:
    success = await client.insert_historical_data(new_data)
    print(f"Insert successful: {success}")
```

## Troubleshooting

### Common Issues

#### QuestDB Won't Start

**Symptoms**: Container exits immediately or fails to start

**Solutions**:
```bash
# Check logs
docker-compose -f docker-compose.questdb.yml logs questdb

# Check port conflicts
netstat -tulpn | grep -E "8812|9000|9009"

# Check disk space
df -h

# Check memory
free -h

# Restart with fresh container
docker-compose -f docker-compose.questdb.yml down -v
docker-compose -f docker-compose.questdb.yml up -d
```

#### Connection Refused

**Symptoms**: Cannot connect to localhost:8812

**Solutions**:
```bash
# Verify container is running
docker ps | grep questdb

# Check firewall
sudo ufw status
sudo iptables -L

# Test connectivity
curl -v http://localhost:8812/health

# Check authentication
curl -u admin:quest http://localhost:8812/exec?query=SELECT 1
```

#### No Data After Population

**Symptoms**: Tables exist but are empty

**Solutions**:
```bash
# Check table contents
curl -u admin:quest "http://localhost:8812/exec?query=SELECT COUNT(*) FROM wig80_historical"

# Check for errors in Python script
python3 wig80_questdb_client.py --verbose

# Re-run population with verbose output
python3 -u wig80_questdb_client.py
```

#### Slow Queries

**Symptoms**: Queries take too long to execute

**Solutions**:
```bash
# Monitor query performance
python3 questdb_management.py monitor --continuous

# Optimize tables
python3 questdb_management.py optimize

# Check system resources
htop
iostat -x 1

# Analyze query plans
EXPLAIN SELECT ... FROM wig80_historical WHERE ts >= dateadd('day', -30, now());
```

### Performance Issues

#### High Memory Usage

**Check**:
```bash
# Monitor memory usage
docker stats questdb

# Check system memory
free -h
top
```

**Solutions**:
- Reduce heap size in docker-compose.yml
- Enable automatic partition cleanup
- Increase system swap space
- Monitor query complexity

#### Slow Query Performance

**Check**:
```bash
# Identify slow queries
python3 questdb_management.py monitor

# Check table statistics
SELECT table, rows FROM information_schema.tables;
```

**Solutions**:
- Use appropriate time range filters
- Create additional indexes if needed
- Leverage materialized views
- Partition by appropriate time intervals

### Data Issues

#### Missing or Corrupted Data

**Check**:
```bash
# Verify data integrity
SELECT COUNT(*) FROM wig80_historical;
SELECT MIN(ts), MAX(ts) FROM wig80_historical;

# Check for null values
SELECT COUNT(*) FROM wig80_historical WHERE symbol IS NULL;
```

**Solutions**:
- Re-run data population script
- Check data source validity
- Verify insertion process logs
- Restore from backup if available

## Production Deployment

### Security Considerations

#### 1. Change Default Credentials

```yaml
# docker-compose.questdb.yml
environment:
  - QDB_HTTP_USER=${QUESTDB_HTTP_USER}
  - QDB_HTTP_PASSWORD=${QUESTDB_HTTP_PASSWORD}
  - QDB_PG_USER=${QUESTDB_PG_USER}
  - QDB_PG_PASSWORD=${QUESTDB_PG_PASSWORD}
```

Create `.env` file:
```env
QUESTDB_HTTP_USER=your_admin_user
QUESTDB_HTTP_PASSWORD=your_secure_password
QUESTDB_PG_USER=your_pg_user
QUESTDB_PG_PASSWORD=your_secure_pg_password
```

#### 2. Network Security

```yaml
# Limit exposure to localhost only
services:
  questdb:
    ports:
      - "127.0.0.1:8812:8812"  # Bind to localhost
      - "127.0.0.1:9009:9009"
      - "127.0.0.1:9000:9000"
```

#### 3. SSL/TLS Configuration

Configure HTTPS in production using reverse proxy (Nginx/Apache):

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:9009;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Backup Strategy

#### Automated Backups

```bash
# Create backup script
cat > backup_questdb.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/questdb_$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
python3 questdb_management.py backup --directory $BACKUP_DIR

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only last 30 days
find /backups -name "questdb_*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup_questdb.sh

# Add to crontab for daily backups
echo "0 2 * * * /path/to/backup_questdb.sh" | crontab -
```

### High Availability

#### QuestDB Clustering

For production environments, consider:

1. **Master-Slave Setup**
2. **QuestDB Enterprise** for clustering
3. **Load Balancing** with multiple instances
4. **Data Replication** strategies

#### Health Monitoring

```bash
# Create monitoring script
cat > monitor_questdb.sh << 'EOF'
#!/bin/bash
HEALTH_URL="http://localhost:8812/health"

if curl -f $HEALTH_URL > /dev/null 2>&1; then
    echo "$(date): QuestDB is healthy"
else
    echo "$(date): QuestDB is DOWN - restarting..."
    docker-compose -f /path/to/docker-compose.questdb.yml restart
fi
EOF

# Add to crontab for monitoring
echo "*/5 * * * * /path/to/monitor_questdb.sh" | crontab -
```

## Monitoring and Maintenance

### Performance Monitoring

```bash
# Real-time monitoring
python3 questdb_management.py monitor --continuous

# Get query statistics
python3 questdb_management.py query --file sample_queries.sql --output results.json

# Check table sizes
python3 questdb_management.py health
```

### Regular Maintenance Tasks

#### Daily Tasks

- Monitor query performance
- Check disk usage
- Verify data ingestion

#### Weekly Tasks

- Run table optimization
- Review slow queries
- Check backup integrity

#### Monthly Tasks

- Analyze capacity planning
- Update documentation
- Review security settings
- Performance tuning review

### Log Management

```bash
# View QuestDB logs
docker-compose -f docker-compose.questdb.yml logs -f questdb

# Search for errors
docker-compose -f docker-compose.questdb.yml logs questdb | grep -i error

# External log rotation
sudo journalctl -u docker | grep questdb > /var/log/questdb.log
```

---

## Getting Help

### Documentation

- [QuestDB Official Docs](https://questdb.io/docs/)
- [SQL Reference](https://questdb.io/docs/reference/sql/)
- [Performance Guide](https://questdb.io/docs/performance/)

### Community Support

- [QuestDB GitHub](https://github.com/questdb/questdb)
- [Community Forum](https://questdb.io/community/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/questdb)

### Professional Support

For enterprise support and custom development, consider:

- QuestDB Enterprise Support
- Professional Services
- Custom Training

---

**🎉 Congratulations! Your WIG80 QuestDB setup is complete and ready for Polish stock market analysis!**

For any issues or questions, refer to the troubleshooting section or check the documentation links above.
