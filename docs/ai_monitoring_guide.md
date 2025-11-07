# AI Monitoring Dashboard Guide

## Overview

The AI Monitoring Dashboard is a comprehensive real-time system for monitoring AI model performance, spectral bias analysis, trading signal tracking, and Polish market insights. This system provides continuous monitoring, alerting, and visualization capabilities for AI-powered financial applications.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation & Setup](#installation--setup)
3. [Features](#features)
4. [Usage Guide](#usage-guide)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

## System Architecture

### Core Components

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   AI Performance    │    │   AI Monitoring      │    │   Real-time Data    │
│      Tracker        │◄──►│     Dashboard        │◄──►│     Streaming       │
│                     │    │                      │    │                     │
│ - Model Metrics     │    │ - Web Interface      │    │ - Socket.IO         │
│ - Spectral Bias     │    │ - Chart Visualizations│   │ - Live Updates      │
│ - Trading Signals   │    │ - Alert Management   │    │ - WebSocket Events  │
│ - Health Monitoring │    │ - Data Export        │    │ - Background Tasks  │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
         ▲                          ▲                          ▲
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Database Layer                                   │
│                                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │  Model      │  │  Spectral   │  │   Trading   │  │   Alerts    │  │
│  │  Metrics    │  │   Bias      │  │   Signals   │  │   Log       │  │
│  │             │  │             │  │             │  │             │  │
│  │ - SQLite    │  │ - SQLite    │  │ - SQLite    │  │ - SQLite    │  │
│  │ - Real-time │  │ - Analysis  │  │ - Performance│  │ - Thresholds│  │
│  │ - Historical│  │ - Frequency │  │ - Profit/Loss│  │ - Severity  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Data Collection**: AI models send metrics to the Performance Tracker
2. **Processing**: Metrics are processed, analyzed, and stored in SQLite database
3. **Analysis**: Spectral bias analysis and health assessments are performed
4. **Visualization**: Dashboard generates real-time charts and visualizations
5. **Alerts**: Threshold-based alerting system generates notifications
6. **Streaming**: Real-time updates via WebSocket connections

## Installation & Setup

### Prerequisites

- Python 3.8+
- Flask and Flask-SocketIO
- Plotly for visualizations
- NumPy and Pandas for data processing
- SQLite3 for data storage

### Installation Steps

1. **Install Dependencies**

```bash
pip install flask flask-socketio plotly numpy pandas sqlite3
```

2. **Set up Directory Structure**

```bash
mkdir -p /workspace/code
mkdir -p /workspace/docs
mkdir -p /workspace/code/templates
```

3. **Initialize the System**

```python
from ai_performance_tracker import AIPerformanceTracker
from ai_monitoring_dashboard import AIMonitoringDashboard

# Initialize tracker
tracker = AIPerformanceTracker()

# Initialize dashboard
dashboard = AIMonitoringDashboard(tracker, port=8080)

# Create sample data for testing
dashboard.create_sample_data(num_models=4, num_signals=200)

# Start the dashboard
dashboard.run(debug=True)
```

### Environment Configuration

Create a `.env` file with the following variables:

```bash
# Database Configuration
AI_DB_PATH=ai_performance.db

# Dashboard Configuration
DASHBOARD_PORT=8080
DASHBOARD_HOST=0.0.0.0

# Polish Market Configuration
OVERVALUATION_THRESHOLD=1.5
VOLATILITY_THRESHOLD=0.3
VOLUME_ANOMALY_THRESHOLD=2.0

# Alert Thresholds
ACCURACY_DROP_THRESHOLD=0.1
ERROR_RATE_THRESHOLD=0.05
MEMORY_USAGE_THRESHOLD=80.0
CPU_USAGE_THRESHOLD=80.0
SPECTRAL_BIAS_THRESHOLD=0.7

# Real-time Update Interval
UPDATE_INTERVAL_SECONDS=30
```

## Features

### 1. Real-time AI Model Performance Monitoring

- **Continuous Metrics Collection**: Track accuracy, precision, recall, F1-score
- **Performance Visualization**: Real-time charts and trends
- **Health Status Monitoring**: Automated health assessments
- **Resource Usage Tracking**: Memory, CPU, and inference time monitoring
- **Throughput Analysis**: Prediction volume and processing speed

#### Supported Metrics

| Metric | Description | Unit |
|--------|-------------|------|
| Accuracy | Model prediction accuracy | 0-1 (percentage) |
| Loss | Training/validation loss | Decimal |
| Precision | True positive rate | 0-1 (percentage) |
| Recall | Sensitivity, true positive rate | 0-1 (percentage) |
| F1-Score | Harmonic mean of precision/recall | 0-1 (percentage) |
| Inference Time | Model prediction time | Seconds |
| Memory Usage | RAM consumption | Percentage |
| CPU Usage | Processor utilization | Percentage |
| Throughput | Predictions per second | Number/sec |
| Error Rate | Prediction error frequency | 0-1 (percentage) |

### 2. Spectral Bias Analysis

- **Frequency Band Analysis**: Learning rates across different frequencies
- **Convergence Time Tracking**: Time to convergence per frequency
- **Bias Score Calculation**: Quantified spectral bias measurement
- **Overfitting Risk Assessment**: Model generalization evaluation
- **Generalization Gap Analysis**: Training vs. validation performance

#### Analysis Components

1. **Frequency Bands**: Different frequency components of the data
2. **Learning Rates**: Speed of learning at each frequency
3. **Convergence Times**: Time required for model to stabilize
4. **Bias Score**: Overall spectral bias quantification (0-1)
5. **Risk Metrics**: Overfitting and generalization assessments

### 3. Polish Market Insights Dashboard

- **WIG80 Company Monitoring**: Track top Polish stock index components
- **Overvaluation Alerts**: P/E ratio threshold-based notifications
- **Volatility Analysis**: Real-time volatility monitoring
- **Volume Anomaly Detection**: Unusual trading volume identification
- **Market Status**: Real-time market open/close status
- **Sector Analysis**: Performance by market sector

#### Alert Types

1. **Overvaluation Alerts**: P/E ratios above threshold
2. **High Volatility**: Daily volatility exceeding limits
3. **Volume Anomalies**: Unusual trading volume patterns
4. **Top Movers**: Biggest gainers and losers
5. **Sector Performance**: Sector-specific analysis

### 4. Trading Signal Performance Tracking

- **Signal Accuracy**: Success rate of trading signals
- **Profit/Loss Analysis**: Financial performance tracking
- **Confidence Scoring**: Signal confidence measurement
- **Execution Metrics**: Timing and execution analysis
- **Model Comparison**: Performance across different models

#### Performance Metrics

- **Total Signals**: Number of signals generated
- **Overall Accuracy**: Percentage of accurate predictions
- **Total Profit/Loss**: Financial performance summary
- **Average Confidence**: Mean confidence score
- **Execution Time**: Signal execution speed
- **Risk Assessment**: Signal risk evaluation

### 5. AI Model Health and Accuracy Metrics

- **Health Score Calculation**: Comprehensive 0-100 health rating
- **Status Classification**: Excellent, Good, Fair, Poor categories
- **Trend Analysis**: Performance trends over time
- **Alert Generation**: Automated health-based alerts
- **Historical Tracking**: Long-term performance analysis

## Usage Guide

### Starting the Dashboard

```python
#!/usr/bin/env python3
from ai_performance_tracker import AIPerformanceTracker
from ai_monitoring_dashboard import AIMonitoringDashboard
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize components
tracker = AIPerformanceTracker(db_path="production_ai_metrics.db")
dashboard = AIMonitoringDashboard(tracker, port=8080)

# Register your AI models
tracker.register_model("my_trading_model", {"version": "1.2.3", "type": "LSTM"})
tracker.register_model("risk_assessment_model", {"version": "2.1.0", "type": "RandomForest"})

# Start dashboard
dashboard.run(debug=False)
```

### Adding Model Metrics

```python
# Update model metrics in real-time
import time
import random

def update_model_metrics(model_id, iteration):
    metrics = {
        'accuracy': 0.85 + random.uniform(-0.1, 0.1),
        'loss': 0.15 + random.uniform(-0.05, 0.05),
        'precision': 0.80 + random.uniform(-0.1, 0.1),
        'recall': 0.78 + random.uniform(-0.1, 0.1),
        'f1_score': 0.79 + random.uniform(-0.1, 0.1),
        'inference_time': 0.1 + random.uniform(-0.05, 0.1),
        'memory_usage': 65 + random.uniform(-10, 15),
        'cpu_usage': 45 + random.uniform(-15, 25),
        'throughput': 50 + random.uniform(-10, 30),
        'error_rate': 0.05 + random.uniform(-0.02, 0.03),
        'predictions': 100 + random.randint(-20, 30),
        'correct_predictions': 85 + random.randint(-15, 25)
    }
    
    tracker.update_model_metrics(model_id, metrics)

# Simulate real-time updates
for i in range(100):
    update_model_metrics("my_trading_model", i)
    time.sleep(10)  # Update every 10 seconds
```

### Adding Spectral Bias Analysis

```python
def run_spectral_bias_analysis(model_id):
    # Simulate spectral bias analysis
    import numpy as np
    
    # Generate realistic spectral bias data
    frequency_bands = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
    learning_rates = [0.01, 0.008, 0.005, 0.003, 0.001, 0.0005]
    convergence_times = [10, 25, 60, 120, 200, 300]
    
    analysis = {
        'frequency_bands': frequency_bands,
        'learning_rates': learning_rates,
        'convergence_times': convergence_times,
        'bias_score': 0.6 + random.uniform(-0.2, 0.2),
        'overfitting_risk': 0.4 + random.uniform(-0.2, 0.3),
        'generalization_gap': 0.25 + random.uniform(-0.1, 0.2)
    }
    
    tracker.update_spectral_bias_analysis(model_id, analysis)

# Run analysis
run_spectral_bias_analysis("my_trading_model")
```

### Adding Trading Signals

```python
from ai_performance_tracker import TradingSignalMetrics
import time

def generate_trading_signal(model_id, signal_type, confidence, target_price):
    signal = TradingSignalMetrics(
        signal_id=f"{model_id}_{int(time.time())}_{random.randint(1000, 9999)}",
        timestamp=time.time(),
        model_id=model_id,
        signal_type=signal_type,
        confidence=confidence,
        target_price=target_price,
        actual_price=target_price * random.uniform(0.9, 1.1),  # Simulated actual
        profit_loss=random.uniform(-50, 100),
        accuracy=random.choice([True, False]),
        execution_time=random.uniform(0.1, 2.0)
    )
    
    tracker.add_trading_signal(signal)

# Generate sample trading signals
for i in range(50):
    signal_types = ['BUY', 'SELL', 'HOLD']
    generate_trading_signal(
        "my_trading_model",
        random.choice(signal_types),
        random.uniform(0.5, 1.0),
        100 + random.uniform(-20, 40)
    )
```

### Accessing the Dashboard

1. **Open Web Browser**: Navigate to `http://localhost:8080`
2. **Dashboard Sections**:
   - **Overview**: System status, model health, alerts
   - **AI Models**: Performance charts and metrics
   - **Trading Signals**: Signal performance analysis
   - **Polish Market**: Market insights and alerts
   - **Spectral Bias**: Bias analysis visualizations

## API Reference

### Performance Tracker API

#### `register_model(model_id, model_config=None)`
Register a new AI model for monitoring.

**Parameters:**
- `model_id` (str): Unique identifier for the model
- `model_config` (dict, optional): Model configuration data

**Returns:** None

**Example:**
```python
tracker.register_model("lstm_trading_v1", {
    "architecture": "LSTM",
    "layers": 3,
    "features": 50
})
```

#### `update_model_metrics(model_id, metrics)`
Update real-time metrics for a model.

**Parameters:**
- `model_id` (str): Model identifier
- `metrics` (dict): Dictionary of metric values

**Returns:** None

**Example:**
```python
tracker.update_model_metrics("lstm_trading_v1", {
    'accuracy': 0.85,
    'loss': 0.15,
    'precision': 0.80,
    'recall': 0.78,
    'f1_score': 0.79,
    'inference_time': 0.1,
    'memory_usage': 65.0,
    'cpu_usage': 45.0,
    'throughput': 50.0,
    'error_rate': 0.05,
    'predictions': 100,
    'correct_predictions': 85
})
```

#### `get_model_health_status(model_id)`
Get comprehensive health status for a model.

**Parameters:**
- `model_id` (str): Model identifier

**Returns:** `dict` - Health status information

**Example:**
```python
health = tracker.get_model_health_status("lstm_trading_v1")
print(f"Model health: {health['status']} (score: {health['health_score']})")
```

#### `get_trading_performance_summary(model_id=None, days=7)`
Get trading signal performance summary.

**Parameters:**
- `model_id` (str, optional): Specific model to analyze
- `days` (int): Number of days to analyze

**Returns:** `dict` - Performance summary

#### `export_metrics(model_id, format='json', output_file=None)`
Export model metrics to file.

**Parameters:**
- `model_id` (str): Model identifier
- `format` (str): Export format ('json' or 'csv')
- `output_file` (str, optional): Output file path

**Returns:** `str` - Success message with file path

### Dashboard API Endpoints

#### `GET /api/dashboard/summary`
Get overall dashboard summary data.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_models": 3,
    "active_models": 3,
    "total_signals": 150,
    "recent_alerts": 2,
    "models_health": {
      "model_id": {
        "status": "good",
        "health_score": 78.5,
        "accuracy": 0.845,
        "error_rate": 0.045
      }
    }
  },
  "timestamp": "2025-11-06T21:27:12"
}
```

#### `GET /api/models/<model_id>/metrics`
Get detailed metrics for a specific model.

**Parameters:**
- `model_id` (path): Model identifier
- `hours` (query, optional): Number of hours of data to return

**Response:**
```json
{
  "status": "success",
  "data": {
    "model_id": "lstm_trading_v1",
    "metrics": [...],
    "health": {...}
  }
}
```

#### `GET /api/trading/signals`
Get trading signal performance data.

**Parameters:**
- `model_id` (query, optional): Filter by model
- `days` (query): Analysis period in days (default: 7)

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_signals": 150,
    "overall_accuracy": 0.67,
    "total_profit": 1250.50,
    "avg_confidence": 0.78
  }
}
```

#### `GET /api/spectral-bias/<model_id>`
Get spectral bias analysis for a model.

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "available",
    "latest_bias_score": 0.62,
    "latest_overfitting_risk": 0.45,
    "latest_generalization_gap": 0.28,
    "frequency_bands": [1.0, 2.0, 4.0, 8.0, 16.0, 32.0],
    "recommendations": ["Consider regularization techniques"]
  }
}
```

#### `GET /api/polish-market/insights`
Get Polish market insights and overvaluation alerts.

**Response:**
```json
{
  "status": "success",
  "data": {
    "market_status": "OPEN",
    "overvaluation_alerts": [
      {
        "company": "PKN ORLEN",
        "pe_ratio": 2.1,
        "alert_type": "OVERVALUATION",
        "severity": "MEDIUM",
        "recommendation": "MONITOR"
      }
    ],
    "volatility_alerts": [...],
    "top_movers": {
      "gainers": [...],
      "losers": [...]
    }
  }
}
```

#### Chart Endpoints

- `GET /api/charts/model-performance?model_id=<id>&hours=<h>` - Model performance chart
- `GET /api/charts/spectral-bias?model_id=<id>` - Spectral bias visualization
- `GET /api/charts/trading-performance?model_id=<id>&days=<d>` - Trading performance chart
- `GET /api/charts/polish-market` - Polish market insights chart

#### `GET /api/alerts`
Get recent alerts.

**Parameters:**
- `hours` (query): Hours to look back (default: 24)

#### `GET /api/export/<model_id>?format=<format>`
Export model data.

**Parameters:**
- `model_id` (path): Model identifier
- `format` (query): Export format ('json' or 'csv')

### WebSocket Events

#### Client Events

- `connect` - Client connects to dashboard
- `subscribe_model` - Subscribe to real-time model updates

**Subscribe Example:**
```javascript
socket.emit('subscribe_model', { model_id: 'my_model' });
```

#### Server Events

- `connected` - Confirmation of client connection
- `dashboard_update` - Real-time dashboard data updates

**Update Payload:**
```json
{
  "summary": {...},
  "alerts": [...],
  "market_insights": {...},
  "timestamp": "2025-11-06T21:27:12"
}
```

## Configuration

### Alert Thresholds

Configure alert thresholds in the performance tracker:

```python
tracker.alert_thresholds = {
    'accuracy_drop': 0.1,        # 10% accuracy drop
    'error_rate_increase': 0.05,  # 5% error rate increase
    'memory_usage': 80.0,         # 80% memory usage
    'cpu_usage': 80.0,            # 80% CPU usage
    'spectral_bias_threshold': 0.7  # 0.7 spectral bias score
}
```

### Polish Market Configuration

```python
polish_market_config = {
    'overvaluation_threshold': 1.5,    # P/E ratio threshold
    'volatility_threshold': 0.3,       # Daily volatility threshold
    'volume_anomaly_threshold': 2.0,   # Volume ratio threshold
    'market_hours': {
        'start': '08:00',
        'end': '16:45',
        'timezone': 'Europe/Warsaw'
    }
}
```

### Database Configuration

```python
# SQLite database configuration
tracker = AIPerformanceTracker(
    db_path="ai_performance.db",  # Database file path
    max_history=10000            # Maximum historical records per model
)
```

### Dashboard Configuration

```python
dashboard = AIMonitoringDashboard(
    tracker=tracker,           # Performance tracker instance
    port=8080,                 # Web server port
)
```

## Troubleshooting

### Common Issues

#### 1. Dashboard Won't Start

**Symptoms:** Port already in use error

**Solution:**
```python
# Check if port is in use
import socket
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Try different port
if is_port_in_use(8080):
    print("Port 8080 is in use, trying 8081")
    dashboard = AIMonitoringDashboard(tracker, port=8081)
```

#### 2. No Data Appearing in Charts

**Symptoms:** Empty charts or "No data found" messages

**Solutions:**
1. **Check Model Registration:** Ensure models are properly registered
```python
print("Registered models:", list(tracker.models.keys()))
```

2. **Verify Metrics Format:** Ensure metrics dictionary has correct keys
```python
required_keys = ['accuracy', 'loss', 'precision', 'recall', 'f1_score']
missing_keys = [key for key in required_keys if key not in metrics]
if missing_keys:
    print(f"Missing metric keys: {missing_keys}")
```

3. **Check Database:** Verify database file exists and is readable
```python
import os
if os.path.exists(tracker.db_path):
    print("Database file exists")
else:
    print("Database file not found")
```

#### 3. Spectral Bias Analysis Missing

**Symptoms:** No spectral bias data available

**Solution:**
```python
# Ensure spectral bias analysis is performed
tracker.simulate_spectral_bias_analysis("your_model_id")

# Or manually add analysis
analysis = {
    'frequency_bands': [1.0, 2.0, 4.0, 8.0],
    'learning_rates': [0.01, 0.005, 0.0025, 0.001],
    'convergence_times': [10, 25, 60, 120],
    'bias_score': 0.6,
    'overfitting_risk': 0.4,
    'generalization_gap': 0.25
}
tracker.update_spectral_bias_analysis("your_model_id", analysis)
```

#### 4. High Memory Usage

**Symptoms:** System running out of memory

**Solutions:**
```python
# Reduce history size
tracker = AIPerformanceTracker(max_history=5000)  # Default was 10000

# Clear old data periodically
def cleanup_old_data(tracker, days_to_keep=30):
    cutoff_time = time.time() - (days_to_keep * 24 * 3600)
    for model_id in tracker.metrics_history:
        tracker.metrics_history[model_id] = deque(
            [m for m in tracker.metrics_history[model_id] if m.timestamp > cutoff_time],
            maxlen=tracker.max_history
        )

# Call cleanup periodically
cleanup_old_data(tracker, days_to_keep=7)
```

#### 5. Slow Performance

**Symptoms:** Dashboard loading slowly or timing out

**Solutions:**
1. **Optimize Database Queries:**
```python
# Use indexed queries for large datasets
def get_recent_metrics_efficiently(model_id, hours=24):
    cutoff_time = time.time() - (hours * 3600)
    with sqlite3.connect(tracker.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM model_metrics WHERE model_id = ? AND timestamp > ? ORDER BY timestamp",
            (model_id, cutoff_time)
        )
        return cursor.fetchall()
```

2. **Reduce Update Frequency:**
```python
# Update dashboard less frequently
dashboard._start_background_updates = lambda: None  # Disable auto-updates

# Manual updates
def manual_update():
    summary = tracker.get_dashboard_summary()
    # Process summary
    return summary

# Update every 5 minutes instead of 30 seconds
```

### Debugging Tips

#### 1. Enable Debug Logging

```python
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_monitoring_debug.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. Monitor Database Size

```python
import os

def check_database_size(db_path):
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"Database size: {size_mb:.2f} MB")
        return size_mb
    return 0

# Check regularly
size = check_database_size(tracker.db_path)
if size > 100:  # 100 MB
    print("Warning: Database size is large, consider cleanup")
```

#### 3. Test Individual Components

```python
# Test tracker independently
def test_tracker():
    print("Testing tracker...")
    
    # Test model registration
    tracker.register_model("test_model")
    assert "test_model" in tracker.models
    
    # Test metrics update
    test_metrics = {'accuracy': 0.8, 'loss': 0.2}
    tracker.update_model_metrics("test_model", test_metrics)
    assert tracker.current_metrics["test_model"] is not None
    
    # Test health calculation
    health = tracker.get_model_health_status("test_model")
    assert 'health_score' in health
    
    print("All tracker tests passed!")

test_tracker()
```

## Advanced Usage

### Custom Metrics

Add custom metrics specific to your AI models:

```python
def update_custom_model_metrics(model_id, custom_data):
    metrics = {
        # Standard metrics
        'accuracy': custom_data.get('accuracy', 0.0),
        'loss': custom_data.get('loss', 0.0),
        
        # Custom financial metrics
        'sharpe_ratio': custom_data.get('sharpe_ratio', 0.0),
        'max_drawdown': custom_data.get('max_drawdown', 0.0),
        'calmar_ratio': custom_data.get('calmar_ratio', 0.0),
        'var_95': custom_data.get('var_95', 0.0),  # Value at Risk
        
        # Custom model metrics
        'gradient_norm': custom_data.get('gradient_norm', 0.0),
        'layer_sparsity': custom_data.get('layer_sparsity', 0.0),
        'attention_entropy': custom_data.get('attention_entropy', 0.0),
        
        # Standard performance metrics
        'inference_time': custom_data.get('inference_time', 0.0),
        'memory_usage': custom_data.get('memory_usage', 0.0),
        'cpu_usage': custom_data.get('cpu_usage', 0.0),
        'throughput': custom_data.get('throughput', 0.0),
        'error_rate': custom_data.get('error_rate', 0.0)
    }
    
    tracker.update_model_metrics(model_id, metrics)
```

### Custom Alerts

Implement custom alert logic:

```python
def setup_custom_alerts(tracker):
    def custom_alert_check(model_id, metrics):
        alerts = []
        
        # Custom financial risk alert
        if 'sharpe_ratio' in metrics and metrics['sharpe_ratio'] < 0.5:
            alerts.append({
                'type': 'low_sharpe_ratio',
                'severity': 'HIGH',
                'message': f'Low Sharpe ratio ({metrics["sharpe_ratio"]:.3f}) for {model_id}',
                'value': metrics['sharpe_ratio'],
                'threshold': 0.5
            })
        
        # Custom model stability alert
        if 'gradient_norm' in metrics and metrics['gradient_norm'] > 1000:
            alerts.append({
                'type': 'high_gradient_norm',
                'severity': 'MEDIUM',
                'message': f'High gradient norm indicating unstable training in {model_id}',
                'value': metrics['gradient_norm'],
                'threshold': 1000
            })
        
        return alerts
    
    # Override the default alert check
    tracker._check_alerts = lambda model_id, metrics: [
        tracker._original_check_alerts(model_id, metrics),
        custom_alert_check(model_id, metrics)
    ]
```

### External Data Integration

Connect to external data sources:

```python
import requests
import json

def fetch_external_market_data():
    """Fetch real market data from external APIs"""
    try:
        # Example: Connect to financial data API
        response = requests.get('https://api.example.com/polish-market/wig80')
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logging.error(f"Failed to fetch external data: {e}")
    return None

def update_with_external_data(tracker):
    """Update tracker with external market data"""
    market_data = fetch_external_market_data()
    if market_data:
        # Process and add to trading signals
        for company_data in market_data:
            signal = TradingSignalMetrics(
                signal_id=f"external_{company_data['ticker']}_{int(time.time())}",
                timestamp=time.time(),
                model_id="external_market_data",
                signal_type=company_data.get('signal', 'HOLD'),
                confidence=company_data.get('confidence', 0.5),
                target_price=company_data.get('target_price', 0.0),
                actual_price=company_data.get('current_price', 0.0),
                profit_loss=company_data.get('daily_pnl', 0.0),
                accuracy=company_data.get('signal_accurate', False),
                execution_time=company_data.get('signal_delay', 1.0)
            )
            tracker.add_trading_signal(signal)
```

### Batch Processing

Process large datasets efficiently:

```python
def batch_update_metrics(tracker, model_metrics_batch):
    """Update multiple model metrics in batch"""
    with sqlite3.connect(tracker.db_path) as conn:
        conn.executemany('''
            INSERT INTO model_metrics (
                model_id, timestamp, accuracy, loss, precision, recall, f1_score,
                inference_time, memory_usage, cpu_usage, throughput, error_rate,
                predictions, correct_predictions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', model_metrics_batch)

# Usage
batch_data = [
    ('model_1', time.time(), 0.85, 0.15, 0.80, 0.78, 0.79, 0.1, 65.0, 45.0, 50.0, 0.05, 100, 85),
    ('model_2', time.time(), 0.78, 0.22, 0.75, 0.73, 0.74, 0.15, 70.0, 50.0, 45.0, 0.08, 90, 70),
    # ... more records
]

batch_update_metrics(tracker, batch_data)
```

### Performance Optimization

Optimize for production deployment:

```python
class OptimizedAIMonitoringDashboard(AIMonitoringDashboard):
    def __init__(self, tracker, port=8080, enable_caching=True):
        super().__init__(tracker, port)
        self.enable_caching = enable_caching
        self._cache = {}
        self._cache_timeout = 60  # 1 minute cache
        
    def _get_cached_data(self, cache_key, data_func):
        """Cache expensive operations"""
        if not self.enable_caching:
            return data_func()
            
        now = time.time()
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if now - cached_time < self._cache_timeout:
                return cached_data
                
        data = data_func()
        self._cache[cache_key] = (now, data)
        return data
        
    def get_dashboard_summary(self):
        """Optimized dashboard summary with caching"""
        def generate_summary():
            return super().get_dashboard_summary()
            
        return self._get_cached_data("dashboard_summary", generate_summary)
```

### Custom Visualization Themes

Create custom chart themes:

```python
# Custom Plotly theme
CUSTOM_THEME = {
    'layout': {
        'font': {'family': 'Arial, sans-serif', 'size': 12},
        'colorway': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'],
        'paper_bgcolor': 'white',
        'plot_bgcolor': 'white',
        'grid': {'color': '#f0f0f0'},
        'xaxis': {'gridcolor': '#f0f0f0'},
        'yaxis': {'gridcolor': '#f0f0f0'}
    }
}

def create_custom_chart(data, chart_type='line'):
    """Create chart with custom theme"""
    if chart_type == 'line':
        fig = px.line(data, template='plotly_white')
    elif chart_type == 'scatter':
        fig = px.scatter(data, template='plotly_white')
    elif chart_type == 'bar':
        fig = px.bar(data, template='plotly_white')
    else:
        fig = go.Figure(template='plotly_white')
        
    fig.update_layout(CUSTOM_THEME['layout'])
    return json.loads(fig.to_json())
```

### Database Migration

Handle database schema changes:

```python
def migrate_database(db_path, target_version):
    """Migrate database to target version"""
    current_version = get_database_version(db_path)
    
    migrations = {
        1: migration_v1_to_v2,
        2: migration_v2_to_v3,
        # Add more migrations as needed
    }
    
    for version in range(current_version, target_version):
        if version + 1 in migrations:
            migrations[version + 1](db_path)
            update_database_version(db_path, version + 1)
            logging.info(f"Migrated database to version {version + 1}")

def migration_v1_to_v2(db_path):
    """Example migration adding new columns"""
    with sqlite3.connect(db_path) as conn:
        conn.execute("ALTER TABLE model_metrics ADD COLUMN custom_metric REAL")
        conn.execute("ALTER TABLE model_metrics ADD COLUMN metadata TEXT")

def get_database_version(db_path):
    """Get current database version"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT version FROM schema_version LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 1
    except:
        return 1

def update_database_version(db_path, version):
    """Update database version"""
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
        conn.execute("DELETE FROM schema_version")
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
```

## Best Practices

### 1. Data Collection

- **Regular Updates**: Update metrics at consistent intervals (30 seconds to 5 minutes)
- **Data Validation**: Validate metric data before storing
- **Error Handling**: Handle missing or invalid data gracefully
- **Performance Monitoring**: Monitor the monitoring system itself

### 2. Alert Management

- **Meaningful Thresholds**: Set thresholds based on domain knowledge
- **Alert Fatigue**: Avoid too many false positives
- **Escalation**: Implement alert escalation for critical issues
- **Documentation**: Document all alert rules and thresholds

### 3. Performance

- **Database Optimization**: Use indexes for frequently queried columns
- **Caching**: Cache expensive operations
- **Batch Processing**: Process data in batches when possible
- **Resource Limits**: Set limits on memory and data retention

### 4. Security

- **Data Encryption**: Encrypt sensitive financial data
- **Access Control**: Implement proper access controls
- **Audit Logging**: Log all system access and changes
- **Data Backup**: Regular automated backups

### 5. Monitoring

- **System Health**: Monitor the monitoring system
- **Data Quality**: Validate incoming data quality
- **Performance Metrics**: Track system performance
- **User Feedback**: Collect and act on user feedback

## Support and Contributing

### Getting Help

1. **Documentation**: Check this guide first
2. **API Reference**: Review the API documentation
3. **Examples**: Look at the provided examples
4. **Logs**: Check system logs for error details

### Reporting Issues

When reporting issues, include:
- System configuration
- Error messages and logs
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

### Contributing

To contribute to the AI Monitoring Dashboard:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This AI Monitoring Dashboard is licensed under the MIT License. See LICENSE.md for details.

---

**Last Updated:** November 6, 2025  
**Version:** 1.0.0  
**Author:** AI Monitoring System Team

For additional support or questions, please contact the development team or refer to the system logs for detailed diagnostic information.