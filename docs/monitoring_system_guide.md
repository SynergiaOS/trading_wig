# QuestDB-Pocketbase Monitoring System Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Features](#features)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tuning](#performance-tuning)
10. [Integration Guide](#integration-guide)

## Overview

The QuestDB-Pocketbase Monitoring System is a comprehensive solution designed to ensure the health, reliability, and performance of your QuestDB-Pocketbase integration. It provides real-time monitoring, data consistency validation, automated backup and recovery, centralized logging, and intelligent alerting for production environments.

### Key Benefits

- **Proactive Monitoring**: Detect issues before they impact users
- **Data Integrity**: Ensure consistency between QuestDB and Pocketbase
- **Automated Recovery**: Backup and restore capabilities
- **Real-time Dashboard**: Visual monitoring interface
- **Intelligent Alerts**: Smart notification system
- **Performance Optimization**: Track and optimize system performance

### Supported Components

- **QuestDB**: Time-series database monitoring
- **Pocketbase**: Backend service monitoring
- **System Resources**: CPU, memory, disk usage
- **Data Sync**: Real-time synchronization tracking
- **API Endpoints**: Service health monitoring

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Monitoring Dashboard                         │
│                    (Web Interface :8080)                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────────┐
│                   Monitoring System                             │
│              (Python Service)                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ REST API / Database
┌─────────────────────▼───────────────────────────────────────────┐
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│   │  QuestDB    │  │  Pocketbase │  │   System    │           │
│   │  Database   │  │   Service   │  │  Resources  │           │
│   └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Monitoring System (`monitoring_system.py`)**
   - Health check engine
   - Data integrity validator
   - Backup manager
   - Alert system
   - Performance tracker

2. **Dashboard (`monitoring_dashboard.py`)**
   - Real-time web interface
   - API endpoints
   - Data visualization
   - Alert management

3. **Monitoring Database**
   - SQLite database for historical data
   - Performance metrics storage
   - Alert history
   - Backup tracking

## Installation & Setup

### Prerequisites

```bash
# Ensure required Python packages are installed
pip install aiohttp psutil

# Create necessary directories
mkdir -p /workspace/logs
mkdir -p /workspace/backups
mkdir -p /workspace/monitoring
```

### Quick Start

1. **Start the Monitoring System**:
   ```bash
   python /workspace/code/monitoring_system.py
   ```

2. **Start the Dashboard** (in a new terminal):
   ```bash
   python /workspace/code/monitoring_dashboard.py
   ```

3. **Access the Dashboard**:
   Open your browser to `http://localhost:8080`

### Advanced Setup

1. **Systemd Service Setup** (Linux):
   ```bash
   sudo nano /etc/systemd/system/questdb-monitoring.service
   ```

   ```ini
   [Unit]
   Description=QuestDB-Pocketbase Monitoring System
   After=network.target

   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/workspace
   ExecStart=/usr/bin/python3 /workspace/code/monitoring_system.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and Start Service**:
   ```bash
   sudo systemctl enable questdb-monitoring
   sudo systemctl start questdb-monitoring
   ```

## Configuration

### Basic Configuration

Edit `/workspace/code/monitoring_system.py` and modify the `DEFAULT_CONFIG` dictionary:

```python
DEFAULT_CONFIG = {
    # Database Paths
    'questdb_path': '/workspace/code/questdb_wig80_test.db',
    'pocketbase_url': 'http://localhost:8090',
    'pocketbase_admin_email': 'admin@example.com',
    'pocketbase_admin_password': 'admin123',
    
    # Alert Configuration
    'email_alerts_enabled': True,
    'email_smtp_server': 'smtp.gmail.com',
    'email_port': 587,
    'email_username': 'your-email@gmail.com',
    'email_password': 'your-app-password',
    'email_recipients': ['admin@yourcompany.com'],
    
    'slack_alerts_enabled': True,
    'slack_webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
    
    # Alert Thresholds
    'alert_thresholds': {
        'data_quality_score_min': 0.95,
        'questdb_response_time_max': 5.0,
        'pocketbase_response_time_max': 3.0,
        'disk_usage_max': 0.85,
        'memory_usage_max': 0.80,
        'cpu_usage_max': 0.75
    }
}
```

### Email Configuration (Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. **Use App Password** in configuration (not your regular password)

### Slack Integration

1. **Create Slack App**:
   - Go to https://api.slack.com/apps
   - Create new app
   - Add Incoming Webhooks feature
   - Copy webhook URL

2. **Configure Webhook**:
   ```json
   {
     "slack_alerts_enabled": true,
     "slack_webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
   }
   ```

### Environment Variables

You can also use environment variables:

```bash
export QUESTDB_MONITORING_EMAIL_ALERTS=true
export QUESTDB_MONITORING_SLACK_WEBHOOK="https://hooks.slack.com/..."
export QUESTDB_MONITORING_POCKETBASE_URL="http://your-pocketbase:8090"
```

## Usage

### Command Line Interface

#### Start Monitoring System
```bash
# Basic usage
python monitoring_system.py

# Custom configuration
python monitoring_system.py --config /path/to/config.json

# Debug mode
python monitoring_system.py --log-level DEBUG
```

#### Start Dashboard
```bash
# Default port (8080)
python monitoring_dashboard.py

# Custom port
python monitoring_dashboard.py --port 9000

# Custom database paths
python monitoring_dashboard.py \
  --questdb-path /custom/path/questdb.db \
  --pocketbase-url http://custom-pb:8090
```

### Programmatic Usage

```python
import asyncio
from monitoring_system import MonitoringSystem, DEFAULT_CONFIG

async def main():
    # Initialize with custom config
    config = DEFAULT_CONFIG.copy()
    config['questdb_path'] = '/path/to/your/questdb.db'
    
    monitoring = MonitoringSystem(config)
    
    try:
        # Run health check
        health = await monitoring.perform_comprehensive_health_check()
        print(f"Health Status: {health}")
        
        # Validate data integrity
        integrity = await monitoring.validate_data_consistency()
        print(f"Data Integrity: {integrity}")
        
        # Create backup
        backup = await monitoring.create_backup("questdb")
        print(f"Backup: {backup}")
        
        # Start continuous monitoring
        await monitoring.start_monitoring(check_interval=300)  # 5 minutes
        
    finally:
        await monitoring.cleanup()

asyncio.run(main())
```

### Dashboard Features

#### Main Dashboard
- **System Health**: Real-time status of all components
- **Data Integrity**: Consistency validation results
- **Performance Metrics**: CPU, memory, disk usage
- **Active Alerts**: Current warnings and critical issues
- **Backup Status**: Last backup and system status
- **Data Statistics**: Record counts and quality scores

#### Interactive Features
- **Auto-refresh**: Updates every 30 seconds
- **Manual Actions**: Trigger backups, acknowledge alerts
- **Drill-down**: Click on components for detailed metrics
- **Export Data**: Download reports and metrics

## Features

### 1. Health Monitoring

#### System Health Checks
- **QuestDB Connection**: Database accessibility and query performance
- **Pocketbase Service**: API availability and authentication
- **System Resources**: CPU, memory, disk usage
- **Network Connectivity**: Service-to-service communication

#### Health Status Levels
- **🟢 Healthy**: System operating normally
- **🟡 Warning**: Performance concerns, needs attention
- **🔴 Critical**: System failure or major issues
- **⚫ Unknown**: Unable to determine status

#### Example Health Check Response
```json
{
  "questdb": {
    "component": "questdb",
    "status": "healthy",
    "last_check": "2025-11-06T20:32:54Z",
    "response_time": 0.045,
    "details": {
      "record_count": 32120,
      "query_time": 0.045
    }
  }
}
```

### 2. Data Integrity Validation

#### Consistency Checks
- **Record Count Validation**: Compare QuestDB vs Pocketbase record counts
- **Data Quality Scoring**: Calculate data quality percentage
- **Missing Field Detection**: Identify incomplete records
- **Duplicate Detection**: Find duplicate entries

#### Integrity Report Structure
```json
{
  "collection": "wig80_historical",
  "total_records": 32120,
  "valid_records": 32095,
  "invalid_records": 25,
  "duplicate_records": 0,
  "missing_fields": [],
  "data_quality_score": 0.9992,
  "last_check": "2025-11-06T20:32:54Z",
  "issues": [
    "25 records with missing RSI values"
  ]
}
```

### 3. Backup & Recovery

#### Automated Backups
- **Daily QuestDB Backups**: Compressed database snapshots
- **Pocketbase Data Backups**: JSON exports of all collections
- **Incremental Backups**: Only changed data
- **Full System Backups**: Complete system state

#### Backup Features
- **Compression**: Gzip compression for storage efficiency
- **Checksums**: SHA256 validation for data integrity
- **Retention Policy**: Automatic cleanup of old backups
- **Recovery Testing**: Automated backup validation

#### Manual Backup Trigger
```bash
# Via dashboard
curl -X POST http://localhost:8080/api/trigger_backup

# Via monitoring system
await monitoring.create_backup("questdb", "manual")
```

### 4. Alert System

#### Alert Severity Levels
- **🔵 Info**: Informational messages
- **🟡 Warning**: Performance concerns
- **🔴 Critical**: System failures

#### Alert Channels
- **Email**: SMTP email notifications
- **Slack**: Incoming webhook notifications
- **Dashboard**: Real-time alert display
- **Log Files**: Comprehensive logging

#### Alert Configuration
```python
alert_config = {
    'email_enabled': True,
    'email_recipients': ['admin@company.com'],
    'slack_enabled': True,
    'slack_webhook_url': 'https://hooks.slack.com/...',
    'alert_thresholds': {
        'data_quality_score_min': 0.95,
        'questdb_response_time_max': 5.0,
        'disk_usage_max': 0.85
    }
}
```

### 5. Performance Monitoring

#### Metrics Collected
- **CPU Usage**: Processor utilization percentage
- **Memory Usage**: RAM utilization and available memory
- **Disk Usage**: Storage utilization and free space
- **Network I/O**:.bytes sent/received
- **Response Times**: Database and API response times
- **Throughput**: Records processed per second

#### Performance Thresholds
```python
{
    'cpu_usage_max': 0.75,        # 75% CPU usage
    'memory_usage_max': 0.80,     # 80% memory usage
    'disk_usage_max': 0.85,       # 85% disk usage
    'questdb_response_time_max': 5.0,   # 5 second response time
    'pocketbase_response_time_max': 3.0  # 3 second response time
}
```

### 6. Centralized Logging

#### Log Files
- **Monitoring System**: `/workspace/logs/monitoring_system.log`
- **Dashboard**: `/workspace/logs/monitoring_dashboard.log`
- **QuestDB Sync**: `/workspace/logs/questdb_pocketbase_sync.log`

#### Log Format
```
2025-11-06 20:32:54 - monitoring_system - INFO - Starting monitoring cycle...
2025-11-06 20:32:55 - monitoring_system - INFO - QuestDB health check: healthy (0.045s)
2025-11-06 20:32:56 - monitoring_system - INFO - Data consistency validation completed for 4 collections
```

## API Reference

### Health Check API

#### GET /api/health

Get current system health status.

**Response:**
```json
{
  "questdb": {
    "component": "questdb",
    "status": "healthy",
    "response_time": 0.045,
    "details": {"record_count": 32120}
  },
  "pocketbase": {
    "component": "pocketbase",
    "status": "healthy",
    "response_time": 0.032,
    "details": {"record_count": 32120}
  },
  "system_resources": {
    "component": "system_resources",
    "status": "healthy",
    "response_time": 0.001,
    "details": {
      "cpu_percent": 15.2,
      "memory_percent": 45.8,
      "disk_percent": 67.3
    }
  }
}
```

### System Status API

#### GET /api/status

Get comprehensive system status including statistics and active alerts.

**Response:**
```json
{
  "is_running": true,
  "stats": {
    "health_checks_performed": 24,
    "data_integrity_checks": 24,
    "backups_created": 1,
    "alerts_generated": 2,
    "last_monitoring_cycle": "2025-11-06T20:32:54Z"
  },
  "active_alerts": {
    "uuid-here": {
      "alert_id": "uuid-here",
      "severity": "warning",
      "component": "data_integrity",
      "message": "Data quality score below threshold",
      "timestamp": "2025-11-06T20:30:00Z"
    }
  }
}
```

### Data Integrity API

#### GET /api/integrity

Get data consistency validation reports.

**Response:**
```json
[
  {
    "collection": "wig80_historical",
    "total_records": 32120,
    "valid_records": 32095,
    "invalid_records": 25,
    "data_quality_score": 0.9992,
    "issues": ["25 records with missing RSI values"],
    "last_check": "2025-11-06T20:32:54Z"
  }
]
```

### Backup Management API

#### GET /api/backups

Get backup history and status.

**Response:**
```json
[
  {
    "backup_id": "uuid-here",
    "system": "questdb",
    "backup_type": "full",
    "file_path": "/workspace/backups/questdb/questdb_backup_20251106_203254_abc12345.db.gz",
    "file_size": 1048576,
    "checksum": "sha256-hash",
    "status": "success",
    "created_at": "2025-11-06T20:32:54Z"
  }
]
```

#### POST /api/trigger_backup

Manually trigger a backup.

**Request Body:**
```json
{
  "system": "questdb",
  "type": "full"
}
```

**Response:**
```json
{
  "backup_id": "new-uuid-here",
  "status": "success",
  "file_path": "/workspace/backups/questdb/questdb_backup_20251106_203300_xyz67890.db.gz"
}
```

### Performance Metrics API

#### GET /api/performance

Get current performance metrics.

**Response:**
```json
{
  "cpu_percent": 15.2,
  "memory_percent": 45.8,
  "memory_available_gb": 8.2,
  "disk_percent": 67.3,
  "disk_free_gb": 15.7,
  "network_bytes_sent": 1048576,
  "network_bytes_recv": 2097152
}
```

### Alert Management API

#### GET /api/alerts

Get active alerts.

**Response:**
```json
[
  {
    "alert_id": "uuid-here",
    "severity": "warning",
    "component": "system_performance",
    "message": "High CPU usage: 85.2%",
    "timestamp": "2025-11-06T20:30:00Z",
    "acknowledged": false,
    "resolved": false
  }
]
```

#### POST /api/acknowledge_alert

Acknowledge an alert.

**Request Body:**
```json
{
  "alert_id": "uuid-here"
}
```

**Response:**
```json
{
  "status": "acknowledged",
  "message": "Alert acknowledged successfully"
}
```

## Troubleshooting

### Common Issues

#### 1. Monitoring System Won't Start

**Symptoms:**
- ImportError for missing packages
- Permission denied errors
- Database connection failures

**Solutions:**
```bash
# Install missing packages
pip install aiohttp psutil

# Check file permissions
chmod 755 /workspace/code/monitoring_system.py

# Verify database paths
ls -la /workspace/code/questdb_wig80_test.db
```

#### 2. Dashboard Not Loading

**Symptoms:**
- Connection refused on port 8080
- "Monitoring system not available" error

**Solutions:**
```bash
# Check if port is already in use
netstat -tulpn | grep 8080

# Check monitoring system logs
tail -f /workspace/logs/monitoring_system.log

# Restart services
pkill -f monitoring_dashboard.py
python /workspace/code/monitoring_dashboard.py
```

#### 3. Health Checks Failing

**Symptoms:**
- QuestDB connection timeout
- Pocketbase authentication errors
- High response times

**Solutions:**
```bash
# Test QuestDB connection
sqlite3 /workspace/code/questdb_wig80_test.db "SELECT COUNT(*) FROM wig80_historical;"

# Test Pocketbase connectivity
curl -X POST http://localhost:8090/api/admins/auth-with-password \
  -H "Content-Type: application/json" \
  -d '{"identity":"admin@example.com","password":"admin123"}'

# Check system resources
top
df -h
free -h
```

#### 4. Email Alerts Not Working

**Symptoms:**
- No email notifications received
- SMTP authentication errors

**Solutions:**
```python
# Test SMTP connection manually
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
```

**Common Gmail Issues:**
- Use App Password, not regular password
- Enable 2-Factor Authentication
- Check "Less secure app access" settings

#### 5. Slack Alerts Not Working

**Symptoms:**
- No Slack notifications
- Webhook URL errors

**Solutions:**
```bash
# Test webhook URL
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message from monitoring system"}' \
  https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Verify webhook format (must be https://hooks.slack.com/services/...)
```

### Debug Mode

Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

Or via command line:
```bash
python monitoring_system.py --log-level DEBUG
```

### Log Analysis

#### Check Recent Errors
```bash
# Monitor live logs
tail -f /workspace/logs/monitoring_system.log | grep ERROR

# Search for specific issues
grep -i "connection" /workspace/logs/monitoring_system.log

# Check dashboard errors
tail -f /workspace/logs/monitoring_dashboard.log
```

#### Database Inspection
```bash
# Connect to monitoring database
sqlite3 /workspace/monitoring/monitoring_data.db

# Check recent health metrics
SELECT * FROM health_metrics ORDER BY timestamp DESC LIMIT 10;

# Check active alerts
SELECT * FROM alerts WHERE resolved = 0 ORDER BY timestamp DESC;

# Check backup history
SELECT * FROM backup_history ORDER BY timestamp DESC LIMIT 5;
```

## Performance Tuning

### Optimization Guidelines

#### 1. Monitoring Frequency
- **Production**: 300 seconds (5 minutes)
- **Development**: 60 seconds (1 minute)
- **High-frequency trading**: 30 seconds

```python
# Adjust in monitoring_system.py
await monitoring.start_monitoring(check_interval=300)  # 5 minutes
```

#### 2. Database Optimization
- **QuestDB**: Optimize queries with proper indexes
- **Monitoring DB**: Regular cleanup of old records

```sql
-- Clean old performance metrics (keep last 30 days)
DELETE FROM performance_metrics 
WHERE timestamp < datetime('now', '-30 days');

-- Archive old health metrics
CREATE TABLE health_metrics_archive AS 
SELECT * FROM health_metrics 
WHERE timestamp < datetime('now', '-7 days');

DELETE FROM health_metrics 
WHERE timestamp < datetime('now', '-7 days');
```

#### 3. Resource Usage
- **Memory**: Monitor memory usage of monitoring process
- **CPU**: Adjust check frequency based on system load
- **Disk**: Implement log rotation and cleanup

```python
# Monitor resource usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
print(f"CPU usage: {process.cpu_percent():.2f}%")
```

#### 4. Alert Threshold Tuning

Adjust thresholds based on your environment:

```python
# For high-performance systems
alert_config = {
    'questdb_response_time_max': 1.0,   # 1 second
    'pocketbase_response_time_max': 0.5,  # 0.5 seconds
    'cpu_usage_max': 0.90,              # 90% CPU
    'memory_usage_max': 0.85,           # 85% memory
    'disk_usage_max': 0.80              # 80% disk
}

# For development systems
alert_config = {
    'questdb_response_time_max': 10.0,   # 10 seconds
    'pocketbase_response_time_max': 5.0,  # 5 seconds
    'cpu_usage_max': 0.95,              # 95% CPU
    'memory_usage_max': 0.90,           # 90% memory
    'disk_usage_max': 0.95              # 95% disk
}
```

### Scalability Considerations

#### 1. Multiple QuestDB Instances
```python
config = {
    'questdb_instances': [
        {'name': 'primary', 'path': '/path/to/primary.db'},
        {'name': 'secondary', 'path': '/path/to/secondary.db'}
    ]
}
```

#### 2. High-Frequency Data
- Reduce monitoring frequency
- Implement sampling for large datasets
- Use incremental integrity checks

#### 3. Distributed Monitoring
- Deploy monitoring system on dedicated server
- Use Redis for shared state
- Implement cluster health checks

## Integration Guide

### Integration with Existing Services

#### 1. QuestDB-Pocketbase Sync Service

The monitoring system integrates seamlessly with your existing sync service:

```python
# Import monitoring system
from monitoring_system import MonitoringSystem

# Integrate with sync service
class IntegratedSyncService(QuestDBPocketbaseSync):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitoring = MonitoringSystem(DEFAULT_CONFIG)
    
    async def sync_all_tables(self):
        # Perform sync
        results = await super().sync_all_tables()
        
        # Report to monitoring system
        await self.monitoring._check_alert_conditions({
            'health_checks': await self.monitoring.perform_comprehensive_health_check(),
            'data_integrity': await self.monitoring.validate_data_consistency()
        })
        
        return results
```

#### 2. Real-time API Server

Add monitoring to your real-time API:

```python
# In realtime_api_server.py
from monitoring_system import MonitoringSystem

class EnhancedAPIHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.monitoring = MonitoringSystem(DEFAULT_CONFIG)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        # Add monitoring to API calls
        start_time = time.time()
        
        # Original API logic
        result = self.original_get_logic()
        
        # Report performance
        response_time = time.time() - start_time
        if response_time > 1.0:  # Log slow requests
            logger.warning(f"Slow API request: {response_time:.2f}s")
        
        return result
```

#### 3. Production Deployment

##### Docker Integration
```dockerfile
# Dockerfile for monitoring system
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY code/monitoring_system.py .
COPY code/monitoring_dashboard.py .

EXPOSE 8080

CMD ["python", "monitoring_dashboard.py"]
```

##### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: questdb-monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: questdb-monitoring
  template:
    metadata:
      labels:
        app: questdb-monitoring
    spec:
      containers:
      - name: monitoring
        image: questdb-monitoring:latest
        ports:
        - containerPort: 8080
        env:
        - name: QUESTDB_MONITORING_POCKETBASE_URL
          value: "http://pocketbase-service:8090"
        - name: QUESTDB_MONITORING_EMAIL_ALERTS
          value: "true"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: backups
          mountPath: /app/backups
      volumes:
      - name: logs
        emptyDir: {}
      - name: backups
        persistentVolumeClaim:
          claimName: backup-pvc
```

##### Prometheus Integration
```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
health_checks_total = Counter('questdb_health_checks_total', 'Total health checks')
response_time = Histogram('questdb_response_time_seconds', 'Response time in seconds')
data_quality_score = Gauge('questdb_data_quality_score', 'Data quality score')

# Use in monitoring system
async def perform_health_check():
    health_checks_total.inc()
    start_time = time.time()
    
    # Health check logic
    result = await check_questdb_health()
    
    response_time.observe(time.time() - start_time)
    return result
```

### Custom Integrations

#### 1. Custom Alert Channels

```python
class CustomAlertChannel:
    async def send_alert(self, alert: AlertInfo):
        # Implement your custom alert logic
        # Examples: SMS, PagerDuty, Microsoft Teams, etc.
        pass

# Add to monitoring system
monitoring.custom_alert_channels = [
    CustomSMSChannel(),
    CustomPagerDutyChannel(),
    CustomTeamsChannel()
]
```

#### 2. Custom Data Sources

```python
class CustomDataSource:
    async def get_metrics(self) -> Dict[str, Any]:
        # Implement custom metric collection
        return {
            'custom_metric_1': get_custom_value(),
            'custom_metric_2': calculate_custom_ratio()
        }

# Add to monitoring system
monitoring.custom_data_sources = [
    CustomDataSource(),
    AnotherCustomSource()
]
```

#### 3. Custom Health Checks

```python
async def custom_health_check() -> SystemHealth:
    # Implement custom health check logic
    try:
        result = await check_custom_component()
        return SystemHealth(
            component="custom_component",
            status="healthy",
            last_check=datetime.now(),
            response_time=0.1,
            details=result
        )
    except Exception as e:
        return SystemHealth(
            component="custom_component",
            status="critical",
            last_check=datetime.now(),
            response_time=0,
            error_message=str(e)
        )

# Add to monitoring system
monitoring.custom_health_checks = [
    custom_health_check,
    another_custom_check
]
```

### Best Practices

1. **Secure Configuration**: Use environment variables for sensitive data
2. **Log Rotation**: Implement log rotation to prevent disk fill
3. **Backup Validation**: Regularly test backup restoration
4. **Performance Monitoring**: Monitor the monitoring system itself
5. **Alert Fatigue**: Fine-tune thresholds to avoid excessive alerts
6. **Documentation**: Keep monitoring configuration documented
7. **Testing**: Regular testing of alert and backup systems
8. **Updates**: Keep monitoring system dependencies updated

## Support and Maintenance

### Regular Maintenance Tasks

#### Daily
- Check active alerts
- Review backup status
- Monitor system resources

#### Weekly
- Analyze performance trends
- Review data quality reports
- Test alert notifications

#### Monthly
- Clean up old log files
- Archive old monitoring data
- Update alert thresholds
- Review and update documentation

### Health Check Schedule

```python
# Recommended monitoring intervals
MONITORING_SCHEDULE = {
    'health_checks': 300,        # Every 5 minutes
    'data_integrity': 1800,      # Every 30 minutes
    'performance_metrics': 60,   # Every minute
    'backup_check': 86400,       # Daily
    'full_system_check': 3600    # Every hour
}
```

### Troubleshooting Resources

1. **Log Files**: `/workspace/logs/`
2. **Monitoring Database**: `/workspace/monitoring/monitoring_data.db`
3. **Configuration**: `/workspace/code/monitoring_system.py`
4. **Dashboard**: `http://localhost:8080`

For additional support, refer to the system logs and monitoring dashboard for detailed diagnostics.

---

## Conclusion

The QuestDB-Pocketbase Monitoring System provides comprehensive monitoring capabilities for production environments. With real-time health checks, data integrity validation, automated backup and recovery, and intelligent alerting, it ensures your integration remains reliable and performant.

Key features include:
- ✅ Real-time system health monitoring
- ✅ Data consistency validation
- ✅ Automated backup and recovery
- ✅ Centralized logging and monitoring
- ✅ Intelligent alert system
- ✅ Web-based dashboard interface
- ✅ RESTful API for integration
- ✅ Production-ready deployment options

For questions or issues, check the troubleshooting section or review the system logs and dashboard for detailed diagnostics.