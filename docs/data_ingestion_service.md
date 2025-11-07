# QuestDB to Pocketbase Data Ingestion Service

## Overview

The QuestDB to Pocketbase Data Ingestion Service is a comprehensive Python application that synchronizes WIG80 Polish stock market data from QuestDB time-series database to Pocketbase collections. The service provides both batch data transfer and real-time streaming capabilities, making it suitable for both initial data migration and ongoing data synchronization.

### Key Features

- **Batch Transfer**: Efficiently transfers 32,120+ historical records for 88 WIG80 companies
- **Real-time Streaming**: Continuously monitors and syncs new data updates
- **Data Validation**: Comprehensive validation ensures data quality and integrity
- **Error Handling**: Robust error handling with exponential backoff retry logic
- **Performance Monitoring**: Detailed logging and statistics tracking
- **Concurrent Processing**: Multi-threaded design for optimal performance
- **Health Monitoring**: Built-in health checks for all system components

### Data Flow

```
QuestDB (Test Database) → Data Transformation → Pocketbase Collections
        ↓
    Real-time Monitoring
        ↓
    Continuous Sync
```

## Architecture

### Core Components

1. **QuestDBPocketbaseSync**: Main service class orchestrating the data flow
2. **Data Transformers**: Convert QuestDB format to Pocketbase schema
3. **Batch Processor**: Handles bulk data transfers with retry logic
4. **Real-time Streamer**: Monitors and syncs new data entries
5. **Health Monitor**: System health verification and alerting
6. **Statistics Tracker**: Performance metrics and sync status

### Database Schema

#### QuestDB Tables
- `wig80_historical`: Stock price data with OHLCV and technical indicators
- `ai_insights`: AI-generated market insights and analysis
- `market_correlations`: Stock correlation matrices
- `valuation_analysis`: P/E, P/B ratios and valuation metrics

#### Pocketbase Collections
- `stock_data`: Transformed stock market data
- `ai_insights`: AI analysis results
- `market_correlations`: Correlation data between stocks
- `valuation_analysis`: Valuation metrics and analysis

## Installation

### Prerequisites

- Python 3.8+
- QuestDB test database (`questdb_wig80_test.db`)
- Pocketbase server running and accessible
- Administrative access to Pocketbase

### Dependencies

Install required Python packages:

```bash
pip install aiohttp asyncio pandas numpy python-dateutil
```

Or use the provided requirements:

```bash
pip install -r /workspace/code/requirements.txt
```

### Directory Structure

```
/workspace/
├── code/
│   ├── questdb_pocketbase_sync.py  # Main service file
│   ├── questdb_wig80_test.db       # Test database
│   └── requirements.txt            # Dependencies
├── logs/                           # Log files directory
└── docs/
    └── data_ingestion_service.md   # This documentation
```

## Configuration

### Environment Setup

1. **QuestDB Database Path**
   ```python
   QUESTDB_PATH = "/workspace/code/questdb_wig80_test.db"
   ```

2. **Pocketbase Configuration**
   ```python
   POCKETBASE_URL = "http://localhost:8090"
   ADMIN_EMAIL = "admin@example.com"
   ADMIN_PASSWORD = "admin123"
   ```

3. **Service Parameters**
   ```python
   batch_size = 1000           # Records per batch
   max_retries = 5             # Maximum retry attempts
   retry_delay = 1.0           # Base retry delay (seconds)
   max_concurrent_transfers = 3 # Concurrent transfer threads
   ```

### Advanced Configuration

#### Performance Tuning

Adjust these parameters based on your system capabilities:

```python
# For high-performance systems
sync_service.batch_size = 2000
sync_service.max_concurrent_transfers = 5
sync_service.retry_delay = 0.5

# For resource-constrained systems
sync_service.batch_size = 500
sync_service.max_concurrent_transfers = 1
sync_service.retry_delay = 2.0
```

#### Real-time Streaming

Configure streaming parameters:

```python
# High-frequency updates
await sync_service.start_realtime_streaming(poll_interval=30)

# Low-frequency updates
await sync_service.start_realtime_streaming(poll_interval=300)
```

## Usage

### Basic Usage

```python
#!/usr/bin/env python3
import asyncio
from questdb_pocketbase_sync import QuestDBPocketbaseSync

async def main():
    # Initialize service
    sync_service = QuestDBPocketbaseSync(
        questdb_path="/workspace/code/questdb_wig80_test.db",
        pocketbase_url="http://localhost:8090",
        admin_email="admin@example.com",
        admin_password="admin123"
    )
    
    try:
        # Health check
        health = await sync_service.health_check()
        print(f"System health: {health}")
        
        # Run synchronization
        results = await sync_service.sync_all_tables()
        print(f"Sync results: {results}")
        
        # Start real-time streaming
        await sync_service.start_realtime_streaming()
        
    finally:
        await sync_service.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Command Line Usage

Run the service directly:

```bash
python /workspace/code/questdb_pocketbase_sync.py
```

### Selective Table Sync

Sync only specific tables:

```python
# Sync only stock data
stock_data = await sync_service.fetch_questdb_data('wig80_historical')
transformed_data = await sync_service.transform_stock_data_for_pocketbase(stock_data)
synced, total = await sync_service.batch_upload_to_pocketbase('stock_data', transformed_data)

# Sync only AI insights
ai_data = await sync_service.fetch_questdb_data('ai_insights')
transformed_ai = await sync_service._transform_ai_data_for_pocketbase(ai_data)
synced, total = await sync_service.batch_upload_to_pocketbase('ai_insights', transformed_ai)
```

### Real-time Only Mode

Start only real-time streaming:

```python
# No initial sync, just real-time
await sync_service.start_realtime_streaming(poll_interval=60)

# Keep running
while sync_service.is_running:
    await asyncio.sleep(60)
    stats = sync_service.get_sync_statistics()
    print(f"Streaming stats: {stats}")
```

## API Reference

### QuestDBPocketbaseSync Class

#### Constructor

```python
QuestDBPocketbaseSync(
    questdb_path: str,
    pocketbase_url: str,
    admin_email: str = None,
    admin_password: str = None
)
```

**Parameters:**
- `questdb_path`: Path to QuestDB test database
- `pocketbase_url`: Pocketbase server URL
- `admin_email`: Pocketbase admin email
- `admin_password`: Pocketbase admin password

#### Core Methods

##### `async sync_all_tables() -> Dict[str, Dict[str, int]]`

Synchronizes all data from QuestDB to Pocketbase.

**Returns:**
```python
{
    'stock_data': {'synced': 32120, 'total': 32120},
    'ai_insights': {'synced': 5000, 'total': 5000},
    'market_correlations': {'synced': 1200, 'total': 1200},
    'valuation_analysis': {'synced': 800, 'total': 800}
}
```

##### `async start_realtime_streaming(poll_interval: int = 60) -> None`

Starts real-time data streaming.

**Parameters:**
- `poll_interval`: Seconds between data polls (default: 60)

##### `async health_check() -> Dict[str, bool]`

Performs system health verification.

**Returns:**
```python
{
    'pocketbase_connection': True,
    'questdb_connection': True,
    'authentication': True,
    'data_access': True
}
```

##### `get_sync_statistics() -> Dict[str, Any]`

Returns comprehensive sync statistics.

**Returns:**
```python
{
    'total_records_processed': 40120,
    'records_synced': 39850,
    'records_failed': 270,
    'sync_duration_seconds': 1200.5,
    'records_per_second': 33.4,
    'success_rate': 99.33
}
```

#### Data Transformation Methods

##### `async transform_stock_data_for_pocketbase(data: List[Dict]) -> List[Dict]`

Transforms QuestDB stock data to Pocketbase format.

##### `async _transform_ai_data_for_pocketbase(data: List[Dict]) -> List[Dict]`

Transforms AI insights data to Pocketbase format.

##### `async _transform_correlation_data_for_pocketbase(data: List[Dict]) -> List[Dict]`

Transforms correlation data to Pocketbase format.

##### `async _transform_valuation_data_for_pocketbase(data: List[Dict]) -> List[Dict]`

Transforms valuation analysis to Pocketbase format.

## Data Validation

### Stock Data Validation

The service validates stock data against the following criteria:

1. **Required Fields**: symbol, ts, open, high, low, close, volume
2. **Data Types**: All numeric fields must be numbers
3. **Range Validation**: Prices must be positive, volume must be non-negative
4. **OHLC Logic**: High >= Open,Close,Low and Low <= Open,Close,High
5. **Timestamp Format**: Must be valid datetime

### Data Quality Checks

```python
def validate_stock_data(self, data: Dict[str, Any]) -> bool:
    # Field presence check
    required_fields = ['symbol', 'ts', 'open', 'high', 'low', 'close', 'volume']
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    
    # Numeric validation
    for field in ['open', 'high', 'low', 'close']:
        if not isinstance(data[field], (int, float)) or data[field] <= 0:
            return False
    
    # OHLC logic validation
    if data['high'] < data['low']:
        return False
    
    return True
```

## Error Handling

### Retry Logic

The service implements exponential backoff retry logic:

```python
# Retry configuration
max_retries = 5
retry_delay = 1.0  # seconds

# Exponential backoff
for attempt in range(max_retries):
    try:
        # Attempt operation
        result = await upload_batch(batch)
        if result.success:
            return result
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = retry_delay * (2 ** attempt)
            await asyncio.sleep(wait_time)
        else:
            raise
```

### Error Types

1. **Connection Errors**: QuestDB or Pocketbase connection failures
2. **Authentication Errors**: Invalid admin credentials
3. **Data Validation Errors**: Invalid or malformed data
4. **Rate Limiting**: Pocketbase API rate limits
5. **Network Errors**: Network connectivity issues

### Error Recovery

```python
try:
    success = await sync_service.batch_upload_to_pocketbase('stock_data', data)
    if not success:
        logger.error("Batch upload failed, will retry on next cycle")
except Exception as e:
    logger.error(f"Critical error: {e}")
    # Service continues running and will retry later
```

## Performance Optimization

### Batch Processing

- **Optimal Batch Size**: 1000 records per batch
- **Memory Management**: Processes data in chunks to avoid memory issues
- **Concurrency**: Uses multiple threads for parallel processing

### Database Optimization

- **Indexing**: Leverages QuestDB's built-in indexes
- **Query Optimization**: Uses LIMIT clauses to prevent memory overflow
- **Connection Pooling**: Reuses database connections

### Real-time Performance

- **Polling Interval**: Configurable based on update frequency requirements
- **Delta Sync**: Only processes new/changed records
- **Background Processing**: Non-blocking real-time updates

### Performance Metrics

Monitor these key metrics:

```python
stats = sync_service.get_sync_statistics()
print(f"Processing rate: {stats['records_per_second']:.2f} records/second")
print(f"Success rate: {stats['success_rate']:.2f}%")
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
```

## Monitoring and Logging

### Log Levels

- **INFO**: General operational information
- **DEBUG**: Detailed processing information
- **WARNING**: Non-critical issues and retries
- **ERROR**: Critical errors requiring attention

### Log Output

Logs are written to both file and console:

```
/workspace/logs/questdb_pocketbase_sync.log
```

### Key Log Messages

```python
# Successful sync
logger.info(f"Successfully uploaded {count} records to {collection}")

# Retry operations
logger.warning(f"Batch upload attempt {attempt + 1} failed: {error}")

# Health check results
logger.info(f"Health check results: {health}")

# Real-time updates
logger.info(f"Real-time streaming started with {poll_interval}s poll interval")
```

### Statistics Monitoring

Track sync progress and performance:

```python
stats = sync_service.get_sync_statistics()
monitoring_data = {
    'timestamp': datetime.now().isoformat(),
    'total_processed': stats['total_records_processed'],
    'success_rate': stats.get('success_rate', 0),
    'processing_rate': stats.get('records_per_second', 0),
    'streaming_active': sync_service.streaming_active
}
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors

**Problem**: Cannot connect to QuestDB or Pocketbase

**Solution**:
```python
# Check database file exists
import os
if not os.path.exists(QUESTDB_PATH):
    print(f"QuestDB database not found: {QUESTDB_PATH}")

# Test Pocketbase URL accessibility
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(POCKETBASE_URL) as response:
        print(f"Pocketbase status: {response.status}")
```

#### 2. Authentication Failures

**Problem**: Pocketbase authentication error

**Solution**:
```python
# Verify admin credentials
health = await sync_service.health_check()
if not health['authentication']:
    print("Invalid admin credentials")
    # Update admin_email and admin_password
```

#### 3. Data Validation Errors

**Problem**: Records failing validation

**Solution**:
```python
# Enable detailed logging
logging.getLogger().setLevel(logging.DEBUG)

# Check specific validation errors
for record in failed_records:
    if not validate_stock_data(record):
        print(f"Invalid record: {record}")
```

#### 4. Memory Issues

**Problem**: Out of memory during large batch processing

**Solution**:
```python
# Reduce batch size
sync_service.batch_size = 500

# Enable streaming mode instead of bulk sync
await sync_service.start_realtime_streaming(poll_interval=60)
```

#### 5. Real-time Streaming Stopped

**Problem**: Streaming thread stops unexpectedly

**Solution**:
```python
# Check if service is still running
if not sync_service.is_running:
    print("Service stopped, restarting...")
    await sync_service.start_realtime_streaming()

# Check logs for errors
# Restart the service if necessary
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)

# This will output detailed information about:
# - Database queries
# - Data transformations
# - HTTP requests
# - Retry attempts
# - Performance metrics
```

### Health Check Diagnostics

Run comprehensive diagnostics:

```python
async def diagnostic_check():
    service = QuestDBPocketbaseSync(questdb_path, pocketbase_url, email, password)
    
    # Test each component
    health = await service.health_check()
    
    # Test data access
    stock_data = await service.fetch_questdb_data('wig80_historical', limit=10)
    print(f"Retrieved {len(stock_data)} sample records")
    
    # Test transformation
    transformed = await service.transform_stock_data_for_pocketbase(stock_data[:1])
    print(f"Transformed sample: {transformed[0] if transformed else 'None'}")
    
    return health, len(stock_data), len(transformed)
```

## Security Considerations

### Authentication

- Use strong passwords for Pocketbase admin accounts
- Store credentials securely (environment variables)
- Rotate credentials regularly

### Data Protection

- QuestDB database file permissions
- Network security for Pocketbase connections
- Encrypted transmission (HTTPS recommended)

### Access Control

- Limit admin access to authorized personnel
- Monitor access logs
- Use service accounts where possible

## Maintenance

### Regular Tasks

1. **Log Rotation**: Implement log rotation to prevent disk space issues
2. **Database Maintenance**: Regular QuestDB optimization
3. **Performance Monitoring**: Track sync performance over time
4. **Backup Procedures**: Regular data backups

### Log Rotation

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure rotating logs (10MB max, 5 backup files)
handler = RotatingFileHandler(
    '/workspace/logs/questdb_pocketbase_sync.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### Performance Monitoring

```python
import time
import psutil

def monitor_performance():
    process = psutil.Process()
    
    while True:
        stats = sync_service.get_sync_statistics()
        
        print(f"CPU: {process.cpu_percent()}%")
        print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        print(f"Records/sec: {stats.get('records_per_second', 0):.2f}")
        print(f"Success rate: {stats.get('success_rate', 0):.2f}%")
        
        time.sleep(60)  # Check every minute
```

## Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Create production environment
   python -m venv /opt/questdb-sync
   source /opt/questdb-sync/bin/activate
   pip install -r requirements.txt
   ```

2. **Service Configuration**
   ```python
   # production_config.py
   QUESTDB_PATH = "/data/questdb/production.db"
   POCKETBASE_URL = "https://pocketbase.company.com"
   ADMIN_EMAIL = "sync-service@company.com"
   ADMIN_PASSWORD = os.environ['POCKETBASE_ADMIN_PASSWORD']
   ```

3. **Systemd Service**
   ```ini
   [Unit]
   Description=QuestDB-Pocketbase Sync Service
   After=network.target
   
   [Service]
   Type=simple
   User=questdb-sync
   WorkingDirectory=/opt/questdb-sync
   ExecStart=/opt/questdb-sync/bin/python questdb_pocketbase_sync.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl enable questdb-sync
   sudo systemctl start questdb-sync
   sudo systemctl status questdb-sync
   ```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY questdb_pocketbase_sync.py .
COPY config.py .

CMD ["python", "questdb_pocketbase_sync.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  questdb-sync:
    build: .
    volumes:
      - ./data:/data
      - ./logs:/logs
    environment:
      - POCKETBASE_URL=http://pocketbase:8090
      - ADMIN_EMAIL=admin@example.com
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    depends_on:
      - pocketbase
    restart: unless-stopped
```

## Support and Contribution

### Getting Help

- Review this documentation thoroughly
- Check log files for specific error messages
- Run health checks to isolate issues
- Enable debug logging for detailed information

### Contributing

When contributing to the service:

1. Follow the existing code structure
2. Add comprehensive error handling
3. Include logging for new features
4. Update documentation for changes
5. Test with sample data before production

### Version History

- **v1.0.0**: Initial release with basic sync functionality
- **v1.1.0**: Added real-time streaming capabilities
- **v1.2.0**: Enhanced error handling and retry logic
- **v1.3.0**: Performance optimizations and monitoring

---

**Author**: Data Engineering Team  
**Last Updated**: 2025-11-06  
**Version**: 1.3.0

For additional support or questions, please refer to the project repository or contact the development team.