# AI Training Guide - Spectral Bias Neural Networks for WIG80

## Overview

This guide provides comprehensive instructions for training, deploying, and using spectral bias neural networks for WIG80 Polish stock market analysis. The system implements Multi-Grade Deep Learning (MGDL) architecture with real-time inference capabilities.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Installation and Setup](#installation-and-setup)
3. [Data Preprocessing](#data-preprocessing)
4. [Model Training](#model-training)
5. [Model Deployment](#model-deployment)
6. [Inference API](#inference-api)
7. [WebSocket Real-time Streaming](#websocket-real-time-streaming)
8. [Monitoring and Maintenance](#monitoring-and-maintenance)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

## System Architecture

### High-Level Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Mobile App     │    │  Third Party    │
│   (React/Vue)   │    │   (React Native) │    │     APIs        │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────┬─────────────────────┬───────┘
                         │                     │
          ┌──────────────▼──────────┐  ┌──────▼───────┐
          │    FastAPI Server       │  │ Load Balancer │
          │   (Inference API)       │  │    (NGINX)    │
          └──────────────┬──────────┘  └──────┬───────┘
                         │                    │
          ┌──────────────▼──────────┐  ┌──────▼───────┐
          │  Training Pipeline      │  │  QuestDB     │
          │ (Spectral Bias Model)   │  │ (Time Series │
          │                         │  │   Database)  │
          └──────────────┬──────────┘  └──────┬───────┘
                         │                    │
          ┌──────────────▼──────────┐  ┌──────▼───────┐
          │    PocketBase           │  │   Redis      │
          │   (Metadata Storage)    │  │ (Caching)    │
          └─────────────────────────┘  └──────────────┘
```

### Key Technologies

- **Deep Learning**: PyTorch with spectral bias neural networks
- **Database**: QuestDB (time-series) + PocketBase (metadata)
- **API**: FastAPI with WebSocket support
- **Caching**: Redis for performance optimization
- **Monitoring**: Prometheus + custom metrics
- **Deployment**: Docker + Kubernetes ready

## Installation and Setup

### Prerequisites

```bash
# System requirements
- Python 3.8+
- 8GB+ RAM recommended
- GPU support (optional, for faster training)
- Docker (optional, for containerized deployment)

# Database systems
- QuestDB 7.0+
- PocketBase 0.31+
- Redis 6.0+
```

### Dependencies Installation

```bash
# Clone the repository
cd /workspace

# Install Python dependencies
pip install -r requirements.txt

# Additional ML libraries
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install scikit-learn pandas numpy matplotlib seaborn
pip install fastapi uvicorn websockets
pip install asyncpg redis faiss-cpu
pip install prometheus-client psutil

# Optional: GPU support
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Database Setup

```bash
# 1. Start QuestDB
cd /workspace/questdb-9.1.1-rt-linux-x86-64
./questdb.sh start

# 2. Start PocketBase
cd /workspace/pocketbase
./pocketbase serve --http=0.0.0.0:8090

# 3. Start Redis
redis-server --port 6379
```

### Environment Configuration

Create `.env` file:

```bash
# Database Configuration
QUESTDB_HOST=localhost
QUESTDB_PORT=9009
QUESTDB_USER=admin
QUESTDB_PASSWORD=quest

POCKETBASE_URL=http://localhost:8090
REDIS_URL=redis://localhost:6379

# Model Configuration
MODEL_PATH=./models
MAX_BATCH_SIZE=32
CACHE_TTL=300

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=*

# Training Configuration
LEARNING_RATE=0.001
BATCH_SIZE=32
EPOCHS=100
EARLY_STOPPING_PATIENCE=10
```

## Data Preprocessing

### WIG80 Data Collection

The system automatically collects and preprocesses WIG80 data:

```python
from ai_training_pipeline import WIG80DataCollector, TrainingConfig

# Initialize data collector
config = TrainingConfig()
collector = WIG80DataCollector(config)

# Load WIG80 symbols
await collector.initialize()
symbols = await collector.load_wig80_symbols()

print(f"Loaded {len(symbols)} WIG80 symbols: {symbols[:10]}")
```

### Data Sources

1. **Real Market Data**: QuestDB integration
2. **Synthetic Data**: Fallback for missing data
3. **Historical Data**: Up to 800 days of price history
4. **Real-time Data**: WebSocket streaming support

### Feature Engineering

The system automatically creates features:

```python
# Technical Indicators
- Moving Averages (5, 10, 20, 50 days)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume indicators
- Volatility measures

# Spectral Features
- FFT-based frequency decomposition
- Power spectral density
- Spectral centroid
- Spectral rolloff
- Spectral flatness
- Spectral entropy

# Market Microstructure
- Bid-ask spreads
- Intraday returns
- Price ranges
- Turnover rates
```

## Model Training

### Basic Training

```python
import asyncio
from ai_training_pipeline import AITrainingPipeline, TrainingConfig

async def train_model():
    # Create training configuration
    config = TrainingConfig(
        experiment_name="wig80_spectral_mgdl_v1",
        num_epochs=50,
        batch_size=16,
        learning_rate=0.001,
        early_stopping_patience=10
    )
    
    # Initialize and run training pipeline
    pipeline = AITrainingPipeline(config)
    results = await pipeline.run_complete_training()
    
    print("Training completed!")
    print(f"Final validation loss: {results['final_metrics']['val_loss']}")
    print(f"Model saved to: {results['deployment_info']['model_path']}")
    
    return results

# Run training
results = asyncio.run(train_model())
```

### Advanced Training Configuration

```python
# Custom training configuration
config = TrainingConfig(
    # Model architecture
    input_dim=50,
    spectral_dim=128,
    hidden_dim=256,
    output_dim=4,
    num_heads=8,
    num_layers=6,
    dropout_rate=0.1,
    
    # Spectral bias parameters
    spectral_lambda_low=0.1,
    spectral_lambda_mid=0.2,
    spectral_lambda_high=0.3,
    
    # Training parameters
    learning_rate=0.001,
    batch_size=32,
    num_epochs=100,
    validation_split=0.2,
    early_stopping_patience=10,
    
    # Data parameters
    window_size=252,  # 1 year of trading days
    step_size=1,
    min_data_points=500,
    
    # Performance tracking
    track_metrics=[
        'train_loss', 'val_loss', 'mae', 'rmse', 'r2_score',
        'directional_accuracy', 'spectral_loss', 'confidence_score'
    ],
    save_frequency=10,
    
    # Database configuration
    questdb_host="localhost",
    questdb_port=9009,
    pocketbase_url="http://localhost:8090",
    redis_url="redis://localhost:6379",
    
    # Model storage
    model_save_path="./models",
    experiment_name="custom_wig80_experiment"
)
```

### Training Process

1. **Data Collection** (Step 1)
   - Load WIG80 symbols from data files
   - Fetch market data from QuestDB
   - Generate synthetic data as fallback
   - Validate data quality

2. **Data Preprocessing** (Step 2)
   - Handle missing values
   - Detect and handle outliers
   - Compute technical indicators
   - Extract spectral features
   - Normalize features

3. **Sequence Creation** (Step 3)
   - Create sliding windows
   - Generate input/output pairs
   - Split into train/validation sets
   - Create DataLoaders

4. **Model Training** (Step 4)
   - Initialize spectral bias model
   - Train with multiple loss functions
   - Apply spectral regularization
   - Monitor training progress
   - Save checkpoints

5. **Model Evaluation** (Step 5)
   - Calculate performance metrics
   - Generate training curves
   - Create comprehensive report
   - Save model metadata

6. **Model Deployment** (Step 6)
   - Save final model
   - Update model registry
   - Generate deployment package

### Training Monitoring

```python
# Training metrics are automatically tracked
training_history = results['training_history']

# Plot training curves
pipeline.trainer.plot_training_curves()

# Print final summary
print(f"Training completed in {len(training_history)} epochs")
print(f"Best validation loss: {min(t.loss for t in training_history):.6f}")
print(f"Final directional accuracy: {training_history[-1].directional_accuracy:.4f}")
```

## Model Deployment

### Automatic Deployment

The training pipeline automatically handles deployment:

```python
# Training includes automatic deployment
results = await pipeline.run_complete_training()

deployment_info = results['deployment_info']
print(f"Model deployed to: {deployment_info['model_path']}")
print(f"Model version: {deployment_info['metadata']['model_version']}")
```

### Manual Deployment

```python
# Load trained model
import torch
from pathlib import Path

model_path = Path("./models/wig80_spectral_mgdl_v1/best_model.pth")
checkpoint = torch.load(model_path, map_location='cpu')

# Deploy to inference service
# (Model is automatically loaded by inference API)
```

### Model Versioning

Models are automatically versioned:

```
models/
├── wig80_spectral_mgdl_v1_20251106_123456/
│   ├── best_model.pth          # Best model checkpoint
│   ├── checkpoint_epoch_10.pth # Periodic checkpoint
│   ├── checkpoint_epoch_20.pth
│   ├── final_model.pth         # Final model
│   ├── training_history.json   # Training metrics
│   ├── training_curves.png     # Visualization
│   ├── model_metadata.json     # Model info
│   └── training_report.md      # Comprehensive report
```

## Inference API

### Starting the API Server

```bash
# Start inference API
cd /workspace/code
python ai_inference_api.py

# Or with custom configuration
uvicorn ai_inference_api:app --host 0.0.0.0 --port 8001 --workers 4
```

### API Endpoints

#### 1. Health Check

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T12:00:00",
  "version": "1.0.0",
  "model_loaded": true,
  "database_connected": true,
  "websocket_connections": 5,
  "uptime_seconds": 3600,
  "system_metrics": {
    "cpu_percent": 45.2,
    "memory_percent": 68.5,
    "disk_percent": 23.1
  }
}
```

#### 2. Single Stock Analysis

```bash
curl -X POST "http://localhost:8001/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "KGH",
    "timeframe": "1d",
    "prediction_horizon": 1,
    "include_spectral": true,
    "confidence_threshold": 0.5
  }'
```

Response:
```json
{
  "symbol": "KGH",
  "timestamp": "2025-11-06T12:00:00",
  "current_price": 157.80,
  "predicted_price": 162.34,
  "prediction_horizon": 1,
  "confidence": 0.78,
  "direction": "bullish",
  "expected_return": 2.87,
  "risk_level": "medium",
  "spectral_analysis": {
    "low_freq_trend": 0.65,
    "mid_freq_cycle": 0.42,
    "high_freq_noise": 0.18
  },
  "technical_indicators": {
    "rsi": 58.3,
    "volatility_20d": 0.024,
    "sma_ratio": 1.02,
    "volume_trend": 0.15
  },
  "market_context": {
    "current_price": 157.80,
    "price_change_1d": 1.23,
    "price_change_7d": 3.45,
    "volume_rank": 0.78
  },
  "model_version": "1.0",
  "processing_time_ms": 23.7
}
```

#### 3. Batch Analysis

```bash
curl -X POST "http://localhost:8001/batch_analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["KGH", "PKN", "PKO"],
    "timeframe": "1d",
    "prediction_horizon": 1
  }'
```

#### 4. Frequency Spectrum Analysis

```bash
curl "http://localhost:8001/spectrum/KGH?days=252"
```

Response:
```json
{
  "symbol": "KGH",
  "frequency_bands": {
    "low_frequency": {
      "range": "0 - 0.1 Hz",
      "power": 1247.5,
      "interpretation": "Long-term trends"
    },
    "medium_frequency": {
      "range": "0.1 - 0.5 Hz",
      "power": 834.2,
      "interpretation": "Business cycles and seasonality"
    },
    "high_frequency": {
      "range": "0.5+ Hz",
      "power": 156.8,
      "interpretation": "Market noise and microstructure"
    }
  },
  "spectral_centroid": 0.187,
  "total_power": 2238.5,
  "analysis_date": "2025-11-06T12:00:00"
}
```

#### 5. Available Symbols

```bash
curl "http://localhost:8001/symbols"
```

#### 6. Prometheus Metrics

```bash
curl "http://localhost:8001/metrics"
```

## WebSocket Real-time Streaming

### Connection Setup

```javascript
// JavaScript WebSocket client
const ws = new WebSocket('ws://localhost:8001/ws/realtime');

// Subscribe to symbols
const subscription = {
    symbols: ['KGH', 'PKN', 'PKO'],
    update_frequency: 5,  // seconds
    include_spectral: true
};

ws.onopen = function() {
    ws.send(JSON.stringify(subscription));
};
```

### Real-time Messages

```javascript
// Receive prediction updates
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'prediction') {
        console.log('Prediction for', data.symbol);
        console.log('Current price:', data.data.current_price);
        console.log('Predicted price:', data.data.predicted_price);
        console.log('Direction:', data.data.direction);
        console.log('Confidence:', data.data.confidence);
        
        // Update UI
        updatePriceDisplay(data.symbol, data.data);
    }
};
```

### Python WebSocket Client

```python
import asyncio
import websockets
import json

async def subscribe_to_updates():
    uri = "ws://localhost:8001/ws/realtime"
    
    subscription = {
        "symbols": ["KGH", "PKN", "PKO"],
        "update_frequency": 5,
        "include_spectral": True
    }
    
    async with websockets.connect(uri) as websocket:
        # Send subscription
        await websocket.send(json.dumps(subscription))
        
        # Listen for updates
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'prediction':
                symbol = data['symbol']
                prediction = data['data']
                
                print(f"Update for {symbol}:")
                print(f"  Current: {prediction['current_price']}")
                print(f"  Predicted: {prediction['predicted_price']}")
                print(f"  Direction: {prediction['direction']}")
                print(f"  Confidence: {prediction['confidence']:.2f}")

# Run the client
asyncio.run(subscribe_to_updates())
```

## Monitoring and Maintenance

### Performance Monitoring

```python
# Prometheus metrics are automatically collected
# Access metrics at http://localhost:8002/metrics

# Key metrics:
# - predictions_total: Total predictions made
# - prediction_duration_seconds: Prediction latency
# - websocket_connections: Active WebSocket connections
# - model_accuracy: Model accuracy estimate
```

### System Health Monitoring

```python
# Monitor system resources
import psutil
import time

def monitor_system():
    while True:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"CPU: {cpu_percent}%")
        print(f"Memory: {memory.percent}%")
        print(f"Disk: {disk.percent}%")
        
        # Alert if thresholds exceeded
        if cpu_percent > 80:
            print("WARNING: High CPU usage")
        if memory.percent > 85:
            print("WARNING: High memory usage")
        
        time.sleep(30)

monitor_system()
```

### Model Retraining

```python
# Schedule regular model retraining
import schedule
import time

def retrain_model():
    print("Starting model retraining...")
    
    config = TrainingConfig(
        experiment_name=f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    pipeline = AITrainingPipeline(config)
    results = asyncio.run(pipeline.run_complete_training())
    
    if results['training_completed']:
        print("Retraining completed successfully")
        # Deploy new model
        deploy_new_model(results)
    else:
        print("Retraining failed")

# Schedule retraining weekly
schedule.every().sunday.at("02:00").do(lambda: asyncio.run(retrain_model()))

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### Log Management

```python
# Logs are automatically saved to:
# - ai_training.log: Training pipeline logs
# - ai_inference.log: Inference service logs

# View logs
tail -f ai_training.log
tail -f ai_inference.log

# Log rotation (add to crontab)
0 0 * * * logrotate /etc/logrotate.conf
```

## Troubleshooting

### Common Issues

1. **Model Loading Failures**
   ```bash
   # Check if model file exists
   ls -la ./models/
   
   # Verify model format
   python -c "import torch; print(torch.load('./models/best_model.pth').keys())"
   ```

2. **Database Connection Issues**
   ```bash
   # Test QuestDB connection
   psql -h localhost -p 9009 -U admin -d qdb -c "SELECT 1;"
   
   # Test Redis connection
   redis-cli ping
   ```

3. **High Memory Usage**
   ```python
   # Reduce batch size
   config.batch_size = 16  # Instead of 32
   
   # Use CPU-only inference
   config.device = "cpu"
   ```

4. **Slow Predictions**
   ```python
   # Enable caching
   config.cache_ttl = 300  # 5 minutes
   
   # Reduce model complexity
   config.hidden_dim = 128  # Instead of 256
   ```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run training with verbose output
config = TrainingConfig(
    debug=True,
    save_frequency=1  # Save every epoch
)
```

### Performance Profiling

```python
# Profile inference performance
import cProfile
import pstats

def profile_inference():
    # Run multiple predictions
    for i in range(100):
        result = asyncio.run(inference_engine.predict("KGH"))

cProfile.run('profile_inference()', 'profile_output.prof')

# Analyze results
stats = pstats.Stats('profile_output.prof')
stats.sort_stats('cumulative').print_stats(20)
```

## API Reference

### Request/Response Models

#### AnalysisRequest
```python
{
    "symbol": "KGH",                    # Stock symbol (required)
    "timeframe": "1d",                  # Analysis timeframe (default: "1d")
    "prediction_horizon": 1,            # Days to predict (default: 1, range: 1-30)
    "include_spectral": true,           # Include spectral analysis (default: true)
    "include_rag_context": true,        # Include RAG context (default: true)
    "confidence_threshold": 0.5         # Minimum confidence (default: 0.5, range: 0.0-1.0)
}
```

#### PredictionResponse
```python
{
    "symbol": "KGH",                    # Stock symbol
    "timestamp": "2025-11-06T12:00:00", # Analysis timestamp
    "current_price": 157.80,            # Current market price
    "predicted_price": 162.34,          # AI predicted price
    "prediction_horizon": 1,            # Prediction timeframe in days
    "confidence": 0.78,                 # Prediction confidence (0.0-1.0)
    "direction": "bullish",             # Market direction: "bullish", "bearish", "neutral"
    "expected_return": 2.87,            # Expected return percentage
    "risk_level": "medium",             # Risk level: "low", "medium", "high"
    "spectral_analysis": {              # Spectral bias analysis
        "low_freq_trend": 0.65,         # Low frequency component
        "mid_freq_cycle": 0.42,         # Medium frequency component
        "high_freq_noise": 0.18         # High frequency component
    },
    "technical_indicators": {           # Technical analysis
        "rsi": 58.3,                    # RSI value
        "volatility_20d": 0.024,        # 20-day volatility
        "sma_ratio": 1.02,              # Price to SMA ratio
        "volume_trend": 0.15            # Volume trend indicator
    },
    "market_context": {                 # Market context
        "current_price": 157.80,        # Current price
        "price_change_1d": 1.23,        # 1-day price change %
        "price_change_7d": 3.45,        # 7-day price change %
        "volume_rank": 0.78             # Volume percentile rank
    },
    "model_version": "1.0",             # Model version identifier
    "processing_time_ms": 23.7          # Processing time in milliseconds
}
```

### Error Codes

- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Symbol not found or no data available
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Inference engine not initialized

### Rate Limiting

- Default: 100 requests per minute per client
- Burst limit: 20 requests per second
- WebSocket: 5 updates per second per connection

## Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001 8002

CMD ["uvicorn", "ai_inference_api:app", "--host", "0.0.0.0", "--port", "8001"]
```

```bash
# Build and run
docker build -t wig80-ai-inference .
docker run -p 8001:8001 -p 8002:8002 wig80-ai-inference
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wig80-ai-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wig80-ai-inference
  template:
    metadata:
      labels:
        app: wig80-ai-inference
    spec:
      containers:
      - name: inference
        image: wig80-ai-inference:latest
        ports:
        - containerPort: 8001
        - containerPort: 8002
        env:
        - name: QUESTDB_HOST
          value: "questdb-service"
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
```

### Production Configuration

```python
# production_config.py
config = InferenceConfig(
    host="0.0.0.0",
    port=8001,
    workers=4,
    reload=False,
    cors_origins=["https://yourdomain.com"],
    questdb_host="prod-questdb",
    redis_url="redis://prod-redis:6379",
    model_path="/app/models",
    enable_metrics=True,
    metrics_port=8002
)
```

## Conclusion

This AI training guide provides a complete framework for training, deploying, and using spectral bias neural networks for WIG80 market analysis. The system is designed for production use with:

- **Scalable Architecture**: Microservices with load balancing
- **Real-time Processing**: WebSocket streaming for live updates
- **Robust Monitoring**: Prometheus metrics and health checks
- **Production Ready**: Docker and Kubernetes deployment support
- **Comprehensive Logging**: Detailed logging and debugging tools

For additional support or questions, refer to the troubleshooting section or examine the code documentation in the individual modules.

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-06  
**Next Review**: 2025-12-06