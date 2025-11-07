# Real-Time Data Streaming Guide

## Overview

The Real-Time Data Streaming Service provides a comprehensive WebSocket-based streaming solution that connects QuestDB and Pocketbase for live WIG80 stock data updates. This system enables real-time financial data distribution with automatic failover, connection monitoring, and event-driven architecture.

## Table of Contents

1. [Architecture](#architecture)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [WebSocket API](#websocket-api)
7. [Event System](#event-system)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Real-Time Stream Manager                   │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ QuestDB         │  │ Pocketbase      │  │ WebSocket    │ │
│  │ Connector       │  │ Connector       │  │ Server       │ │
│  │                 │  │                 │  │              │ │
│  │ • WebSocket     │  │ • REST API      │  │ • Subscriptions│ │
│  │ • SQL Queries   │  │ • Real-time     │  │ • Broadcasting│ │
│  │ • Auto Reconnect│  │ • Auth          │  │ • Connection  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│              Event-Driven Architecture                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Event Bus       │  │ Stock Data      │  │ Connection   │ │
│  │                 │  │ Providers       │  │ Monitor      │ │
│  │ • Decoupled     │  │                 │  │              │ │
│  │ • Async Events  │  │ • Stooq.pl      │  │ • Health     │ │
│  │ • Multiple Sub. │  │ • Alpha Vantage │  │ • Auto Recon │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Data Collection**: Stock data providers fetch real-time data from sources
2. **Data Processing**: Updates are processed and validated
3. **Database Storage**: Data is stored in QuestDB for time-series analysis
4. **Real-time Distribution**: Updates are distributed to Pocketbase collections
5. **WebSocket Broadcasting**: Live updates are broadcast to connected clients
6. **Event Publishing**: Events are published via the event bus system

## Features

### ✅ WebSocket Subscriptions for Live Stock Data Updates
- Real-time WebSocket server on `ws://localhost:8765`
- Subscription management for individual clients
- Live stock price updates every 30 seconds
- Market status indicators (Open/Closed/Pre-market/After-hours)

### ✅ Real-time Data Pipeline with 30-second Refresh Cycle
- Configurable update intervals (default: 30 seconds)
- Automatic data fetching from multiple sources
- Data validation and error handling
- Atomic data updates

### ✅ Connection Monitoring and Automatic Reconnection
- Continuous health monitoring of all connections
- Exponential backoff reconnection strategy
- Connection status tracking and reporting
- Automatic failover handling

### ✅ Real-time Data Distribution to Pocketbase Collections
- Automatic distribution to multiple Pocketbase collections
- Support for stock_data, market_updates, and alerts collections
- Real-time synchronization between QuestDB and Pocketbase
- Batch processing for efficiency

### ✅ Event-driven Architecture for Instant Updates
- Decoupled event system with async handlers
- Support for multiple event types (stock_update, connection_status, etc.)
- Real-time event broadcasting
- Extensible event subscription system

## Installation

### Prerequisites

1. **Python 3.8+** with pip
2. **QuestDB** running on `localhost:8812`
3. **Pocketbase** running on `http://localhost:8090`

### Install Dependencies

```bash
cd /workspace/code
pip install -r requirements.txt
```

### Verify QuestDB Installation

```bash
# Check if QuestDB is running
curl http://localhost:9000/health
```

### Verify Pocketbase Installation

```bash
# Check if Pocketbase is running
curl http://localhost:8090/api/health
```

## Configuration

### QuestDB Configuration

Edit the `QuestDBConfig` class in `realtime_data_stream.py`:

```python
@dataclass
class QuestDBConfig:
    host: str = "localhost"        # QuestDB host
    port: int = 8812               # QuestDB WebSocket port
    user: str = "admin"            # QuestDB user
    password: str = "quest"        # QuestDB password
    database: str = "qdb"          # Database name
    tls_enabled: bool = False      # Enable TLS encryption
```

### Pocketbase Configuration

Edit the `PocketbaseConfig` class:

```python
@dataclass
class PocketbaseConfig:
    url: str = "http://localhost:8090"              # Pocketbase URL
    admin_email: str = "admin@example.com"          # Admin email
    admin_password: str = "admin123"                # Admin password
    collections: List[str] = None                   # Target collections

    def __post_init__(self):
        if self.collections is None:
            self.collections = [
                "stock_data",      # Individual stock updates
                "market_updates",  # Market-wide updates
                "alerts"           # Alert notifications
            ]
```

### Data Provider Configuration

Add or modify data providers in the `RealTimeStreamManager`:

```python
# Add custom data provider
custom_provider = YourCustomProvider()
stream_manager.data_providers.append(custom_provider)

# Set update interval (in seconds)
stream_manager.update_interval = 30
```

## Usage

### Start the Service

```bash
cd /workspace/code
python realtime_data_stream.py
```

### Expected Output

```
======================================================================
🔄 Real-Time Data Streaming Service
======================================================================
QuestDB: localhost:8812
Pocketbase: http://localhost:8090
WebSocket: ws://localhost:8765
Update Interval: 30 seconds
======================================================================

✅ Service is running. Press Ctrl+C to stop.
```

### Stop the Service

Press `Ctrl+C` to gracefully shutdown the service.

### Run as Background Service

```bash
# Start in background
nohup python realtime_data_stream.py > stream.log 2>&1 &

# Check running process
ps aux | grep realtime_data_stream

# Stop the service
pkill -f realtime_data_stream
```

### Systemd Service (Linux)

Create `/etc/systemd/system/realtime-stream.service`:

```ini
[Unit]
Description=Real-Time Data Streaming Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/workspace/code
ExecStart=/usr/bin/python3 realtime_data_stream.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable realtime-stream.service
sudo systemctl start realtime-stream.service
sudo systemctl status realtime-stream.service
```

## WebSocket API

### Connection

Connect to the WebSocket server:

```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### Message Types

#### 1. Connection Confirmation
Sent immediately after connection:

```json
{
  "type": "connection",
  "status": "connected",
  "timestamp": "2025-11-06T20:23:56.000Z",
  "message": "Connected to real-time stream"
}
```

#### 2. Stock Updates
Broadcasted every 30 seconds with fresh data:

```json
{
  "type": "stock_updates",
  "timestamp": "2025-11-06T20:23:56.000Z",
  "count": 16,
  "data": [
    {
      "timestamp": "2025-11-06T20:23:56.000Z",
      "symbol": "PKN",
      "price": 65.50,
      "change": 1.25,
      "change_percent": 1.94,
      "volume": 1250000,
      "high": 66.80,
      "low": 64.20,
      "open": 64.80,
      "market_status": "open",
      "data_source": "stooq.pl"
    }
  ]
}
```

#### 3. Status Update
Response to status requests:

```json
{
  "type": "status",
  "questdb_status": "connected",
  "pocketbase_status": "connected",
  "data_providers": ["Stooq.pl"],
  "subscribers": 3,
  "timestamp": "2025-11-06T20:23:56.000Z"
}
```

#### 4. Subscription Confirmation
Response to subscription requests:

```json
{
  "type": "subscription_confirmed",
  "timestamp": "2025-11-06T20:23:56.000Z"
}
```

#### 5. Pong Response
Response to ping messages:

```json
{
  "type": "pong",
  "timestamp": "2025-11-06T20:23:56.000Z"
}
```

#### 6. Error Messages

```json
{
  "type": "error",
  "message": "Invalid JSON message"
}
```

### Client Messages

#### Subscribe to Updates
```json
{
  "type": "subscribe"
}
```

#### Ping the Server
```json
{
  "type": "ping"
}
```

#### Request System Status
```json
{
  "type": "status"
}
```

### JavaScript Client Example

```javascript
class RealtimeStreamClient {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.ws = null;
        this.subscribers = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('✅ Connected to real-time stream');
            this.reconnectAttempts = 0;
            
            // Subscribe to updates
            this.send({ type: 'subscribe' });
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            console.log('🔌 Disconnected from stream');
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };
    }

    handleMessage(data) {
        switch (data.type) {
            case 'stock_updates':
                this.notifySubscribers('stock_updates', data);
                break;
            case 'connection':
                this.notifySubscribers('connection', data);
                break;
            case 'status':
                this.notifySubscribers('status', data);
                break;
            case 'error':
                console.error('Server error:', data.message);
                break;
        }
    }

    subscribe(eventType, callback) {
        if (!this.subscribers[eventType]) {
            this.subscribers[eventType] = [];
        }
        this.subscribers[eventType].push(callback);
    }

    notifySubscribers(eventType, data) {
        if (this.subscribers[eventType]) {
            this.subscribers[eventType].forEach(callback => callback(data));
        }
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    requestStatus() {
        this.send({ type: 'status' });
    }

    ping() {
        this.send({ type: 'ping' });
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage example
const client = new RealtimeStreamClient();
client.connect();

// Subscribe to stock updates
client.subscribe('stock_updates', (data) => {
    console.log('📊 Received stock updates:', data.count, 'stocks');
    data.data.forEach(stock => {
        console.log(`${stock.symbol}: ${stock.price} (${stock.change_percent:+.2f}%)`);
    });
});

// Subscribe to connection status
client.subscribe('connection', (data) => {
    console.log('🔗 Connection status:', data.status);
});
```

## Event System

### Event Types

The system supports multiple event types:

1. **stock_update**: Fired when a stock price is updated
2. **connection_status**: Fired when connection status changes
3. **market_status**: Fired when market status changes
4. **data_provider_status**: Fired when data provider status changes

### Event Handler Registration

```python
# Register event handlers
await event_bus.subscribe("stock_update", handle_stock_update_event)
await event_bus.subscribe("connection_status", handle_connection_event)
```

### Publishing Events

```python
# Publish stock update event
await event_bus.publish("stock_update", {
    "symbol": "PKN",
    "price": 65.50,
    "change": 1.25
})

# Publish connection status event
await event_bus.publish("connection_status", {
    "service": "QuestDB",
    "status": "connected",
    "timestamp": datetime.now().isoformat()
})
```

## Monitoring

### Log Files

- **Main log**: `/workspace/questdb_wig80_logs/realtime_stream.log`
- **Console output**: Real-time status updates

### Key Metrics to Monitor

1. **Connection Status**
   - QuestDB connection: `connected` / `disconnected` / `reconnecting`
   - Pocketbase connection: `connected` / `disconnected` / `reconnecting`
   - WebSocket subscribers: Number of connected clients

2. **Data Flow**
   - Update cycle frequency: Should be every 30 seconds
   - Stock updates per cycle: 16 companies (WIG80 subset)
   - Data provider status: `Stooq.pl` / `Alpha Vantage`

3. **Performance**
   - WebSocket message rate: Updates broadcast frequency
   - Database insert success: QuestDB and Pocketbase
   - Error rate: Failed operations per hour

### Monitoring Script

```bash
#!/bin/bash
# monitor_stream.sh

LOG_FILE="/workspace/questdb_wig80_logs/realtime_stream.log"

echo "=== Real-Time Stream Monitor ==="
echo "Time: $(date)"
echo

# Check if service is running
if pgrep -f realtime_data_stream.py > /dev/null; then
    echo "✅ Service is running (PID: $(pgrep -f realtime_data_stream.py))"
else
    echo "❌ Service is not running"
    exit 1
fi

echo
echo "=== Recent Log Entries ==="
tail -20 "$LOG_FILE"

echo
echo "=== Connection Status (last 5 minutes) ==="
grep -E "(✅|❌|🔄|📊)" "$LOG_FILE" | tail -10

echo
echo "=== Memory Usage ==="
ps -o pid,vsz,rss,comm -p $(pgrep -f realtime_data_stream.py)

echo
echo "=== Network Connections ==="
netstat -tulpn 2>/dev/null | grep -E "(8765|8812|8090)" || echo "No relevant connections found"
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Problem**: `ModuleNotFoundError` or import errors

**Solution**:
```bash
# Check Python version
python3 --version

# Install missing dependencies
pip install aiohttp websockets

# Verify requirements.txt
pip install -r requirements.txt
```

#### 2. QuestDB Connection Failed

**Problem**: Cannot connect to QuestDB WebSocket

**Solution**:
```bash
# Check if QuestDB is running
curl http://localhost:9000/health

# Check QuestDB WebSocket port
netstat -tulpn | grep 8812

# Verify QuestDB configuration
cat /workspace/questdb-9.1.1-rt-linux-x86-64/conf/server.conf
```

#### 3. Pocketbase Connection Failed

**Problem**: Cannot authenticate with Pocketbase

**Solution**:
```bash
# Check if Pocketbase is running
curl http://localhost:8090/api/health

# Verify Pocketbase admin credentials
curl -X POST http://localhost:8090/api/admins/auth-with-password \
  -H "Content-Type: application/json" \
  -d '{"identity":"admin@example.com","password":"admin123"}'
```

#### 4. WebSocket Clients Disconnecting

**Problem**: Frequent client disconnections

**Solution**:
```bash
# Check WebSocket server port
netstat -tulpn | grep 8765

# Review connection logs
tail -f /workspace/questdb_wig80_logs/realtime_stream.log | grep -E "(disconnected|connected)"
```

#### 5. No Data Updates

**Problem**: Stock updates not being generated

**Solution**:
```bash
# Check data provider status
tail -f /workspace/questdb_wig80_logs/realtime_stream.log | grep "Fetched"

# Verify update cycle
grep "Starting data update cycle" /workspace/questdb_wig80_logs/realtime_stream.log

# Check for errors in log
grep -E "❌|Error|Exception" /workspace/questdb_wig80_logs/realtime_stream.log
```

### Performance Issues

#### High CPU Usage

**Problem**: Service consuming excessive CPU

**Solution**:
```bash
# Monitor CPU usage
top -p $(pgrep -f realtime_data_stream.py)

# Check update frequency
grep "Update cycle completed" /workspace/questdb_wig80_logs/realtime_stream.log

# Reduce update interval if needed
# Edit realtime_data_stream.py and change:
# stream_manager.update_interval = 30  # Increase to 60 for less frequent updates
```

#### Memory Leaks

**Problem**: Service memory usage growing over time

**Solution**:
```bash
# Monitor memory usage
watch -n 10 'ps -o pid,vsz,rss,comm -p $(pgrep -f realtime_data_stream.py)'

# Check for unreleased resources
# Ensure all connections are properly closed in error handling
```

### Debug Mode

Enable debug logging by modifying the logging configuration:

```python
# In realtime_data_stream.py, change:
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    ...
)
```

### Health Check Script

```python
#!/usr/bin/env python3
"""Health check script for real-time streaming service"""

import asyncio
import websockets
import aiohttp
import json
from datetime import datetime

async def check_health():
    """Perform comprehensive health check"""
    print("🏥 Real-Time Stream Health Check")
    print("=" * 50)
    
    # Check WebSocket server
    try:
        async with websockets.connect('ws://localhost:8765') as ws:
            await ws.send(json.dumps({"type": "status"}))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(response)
            print(f"✅ WebSocket: {data.get('questdb_status', 'unknown')} / {data.get('pocketbase_status', 'unknown')}")
    except Exception as e:
        print(f"❌ WebSocket: {e}")
    
    # Check QuestDB
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:9000/health') as response:
                if response.status == 200:
                    print("✅ QuestDB: Online")
                else:
                    print(f"❌ QuestDB: HTTP {response.status}")
    except Exception as e:
        print(f"❌ QuestDB: {e}")
    
    # Check Pocketbase
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8090/api/health') as response:
                if response.status == 200:
                    print("✅ Pocketbase: Online")
                else:
                    print(f"❌ Pocketbase: HTTP {response.status}")
    except Exception as e:
        print(f"❌ Pocketbase: {e}")
    
    print(f"\n⏰ Check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(check_health())
```

## API Reference

### Classes

#### `RealTimeStreamManager`

Main class for managing the streaming service.

**Methods**:
- `start()`: Start the streaming service
- `stop()`: Stop the streaming service

#### `QuestDBConnector`

Handles QuestDB WebSocket connections and SQL operations.

**Methods**:
- `connect()`: Connect to QuestDB
- `execute_query(query: str)`: Execute SQL query
- `insert_stock_data(data: StockUpdate)`: Insert stock data
- `close()`: Close connection

#### `PocketbaseConnector`

Handles Pocketbase API operations.

**Methods**:
- `connect()`: Connect to Pocketbase
- `create_record(collection: str, data: dict)`: Create record
- `update_record(collection: str, record_id: str, data: dict)`: Update record
- `distribute_stock_update(data: StockUpdate)`: Distribute update

#### `StockDataProvider`

Base class for data providers.

**Methods**:
- `fetch_data()`: Fetch stock data (implement in subclass)
- `connect()`: Initialize provider
- `close()`: Close provider

#### `EventBus`

Simple event bus for decoupled communication.

**Methods**:
- `subscribe(event_type: str, handler: Callable)`: Subscribe to event
- `publish(event_type: str, data: Any)`: Publish event

### Data Structures

#### `StockUpdate`

Stock data update structure:

```python
@dataclass
class StockUpdate:
    timestamp: str         # ISO format timestamp
    symbol: str            # Stock symbol (e.g., "PKN")
    price: float           # Current price
    change: float          # Price change amount
    change_percent: float  # Price change percentage
    volume: int            # Trading volume
    high: float            # High price
    low: float             # Low price
    open: float            # Opening price
    market_status: str     # Market status
    data_source: str       # Data source identifier
```

#### `ConnectionStatus`

Connection status enumeration:

```python
class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    FAILED = "failed"
```

#### `MarketStatus`

Market status enumeration:

```python
class MarketStatus(Enum):
    PRE_MARKET = "pre_market"    # 8:00-9:00
    OPEN = "open"                # 9:00-17:00
    AFTER_HOURS = "after_hours"  # 17:00-18:00
    CLOSED = "closed"            # After 18:00
    WEEKEND = "weekend"          # Saturday/Sunday
    HOLIDAY = "holiday"          # Market holidays
```

## Production Deployment

### Security Considerations

1. **TLS/SSL**: Enable TLS for WebSocket connections
2. **Authentication**: Add authentication for WebSocket clients
3. **Rate Limiting**: Implement rate limiting for client connections
4. **Input Validation**: Validate all incoming messages
5. **Access Control**: Restrict access by IP address

### High Availability

1. **Load Balancing**: Run multiple instances behind load balancer
2. **Database Clustering**: Use QuestDB clustering for redundancy
3. **Health Checks**: Implement health check endpoints
4. **Monitoring**: Set up comprehensive monitoring and alerting

### Scaling

1. **Horizontal Scaling**: Deploy multiple stream managers
2. **Message Queues**: Use Redis/RabbitMQ for message distribution
3. **Database Partitioning**: Partition data by date/symbol
4. **Caching**: Implement Redis for high-frequency data

## Support

For issues and questions:

1. Check the log files for error messages
2. Run the health check script
3. Review the troubleshooting section
4. Check QuestDB and Pocketbase documentation
5. Contact the development team

---

**Last Updated**: 2025-11-06  
**Version**: 1.0.0  
**Service**: Real-Time Data Streaming  
**Author**: Polish Finance Platform Team
