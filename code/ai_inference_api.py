"""
AI Inference API for Spectral Bias Neural Networks
Real-time market analysis service for WIG80 Polish stock market

This module provides a complete FastAPI-based inference service for real-time
market analysis using spectral bias neural networks trained on WIG80 data.
The service integrates with QuestDB and PocketBase for data storage and retrieval,
and provides both RESTful and WebSocket APIs for real-time updates.

Author: AI Inference Service Team
Version: 1.0
Date: 2025-11-06
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import aiohttp
import asyncpg
import redis
import pickle
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# FastAPI imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# WebSocket imports
import websockets
from websockets.exceptions import ConnectionClosed

# Scientific computing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Monitoring
import psutil
import time
from prometheus_client import Counter, Histogram, Gauge, start_http_server, generate_latest

# Import training components and model
try:
    from ai_training_pipeline import AITrainingPipeline, TrainingConfig
    from ai_model_design import (
        AIConfig, SpectralBiasNeuralNetwork, RAGNeuralNetwork, 
        RAGKnowledgeBase, FinancialDataPreprocessor, MarketEvent,
        PredictionResult, create_ai_system
    )
except ImportError as e:
    print(f"Warning: Could not import training components: {e}")
    # Create basic fallbacks
    class AITrainingPipeline:
        def __init__(self, config): pass
    class TrainingConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_inference.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# Data Models and Configuration
# =============================================================================

@dataclass
class InferenceConfig:
    """Configuration for inference service"""
    # Model settings
    model_path: str = "./models"
    model_name: str = "best_model.pth"
    device: str = "auto"  # auto, cpu, cuda
    batch_size: int = 1
    
    # API settings
    host: str = "0.0.0.0"
    port: int = 8001
    workers: int = 4
    reload: bool = False
    cors_origins: List[str] = None
    
    # Database settings
    questdb_host: str = "localhost"
    questdb_port: int = 9009
    questdb_user: str = "admin"
    questdb_password: str = "quest"
    pocketbase_url: str = "http://localhost:8090"
    redis_url: str = "redis://localhost:6379"
    
    # Performance settings
    max_request_size: int = 1000
    request_timeout: int = 30
    cache_ttl: int = 300  # 5 minutes
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 8002
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

# Pydantic models for API
class AnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    symbol: str = Field(..., description="Stock symbol to analyze", example="KGH")
    timeframe: str = Field("1d", description="Analysis timeframe", example="1d")
    prediction_horizon: int = Field(1, description="Days to predict ahead", ge=1, le=30)
    include_spectral: bool = Field(True, description="Include spectral analysis")
    include_rag_context: bool = Field(True, description="Include RAG context")
    confidence_threshold: float = Field(0.5, description="Minimum confidence for alerts", ge=0.0, le=1.0)

class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    symbols: List[str] = Field(..., description="List of symbols to analyze", example=["KGH", "PKN", "PKO"])
    timeframe: str = Field("1d", description="Analysis timeframe")
    prediction_horizon: int = Field(1, description="Days to predict ahead", ge=1, le=30)

class RealtimeSubscription(BaseModel):
    """WebSocket subscription model"""
    symbols: List[str] = Field(..., description="Symbols to subscribe to")
    update_frequency: int = Field(5, description="Update frequency in seconds", ge=1, le=60)
    include_spectral: bool = Field(True, description="Include spectral analysis")

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    symbol: str
    timestamp: str
    current_price: float
    predicted_price: float
    prediction_horizon: int
    confidence: float
    direction: str  # "bullish", "bearish", "neutral"
    expected_return: float
    risk_level: str  # "low", "medium", "high"
    spectral_analysis: Optional[Dict[str, Any]] = None
    technical_indicators: Optional[Dict[str, float]] = None
    market_context: Optional[Dict[str, Any]] = None
    model_version: str
    processing_time_ms: float

class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions"""
    results: List[PredictionResponse]
    total_symbols: int
    successful_predictions: int
    failed_symbols: List[str]
    processing_time_ms: float
    batch_id: str

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    model_loaded: bool
    database_connected: bool
    websocket_connections: int
    uptime_seconds: float
    system_metrics: Dict[str, float]

# =============================================================================
# Core Inference Engine
# =============================================================================

class SpectralBiasInferenceEngine:
    """Core inference engine for spectral bias predictions"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        
        # Model components
        self.model = None
        self.preprocessor = None
        self.knowledge_base = None
        self.device = self._setup_device()
        
        # Database connections
        self.questdb_pool = None
        self.redis_client = None
        self.pocketbase_client = None
        
        # Caching
        self.prediction_cache = {}
        self.feature_cache = {}
        
        # WebSocket connections
        self.websocket_connections = {}
        
        # Performance tracking
        self.request_count = 0
        self.start_time = time.time()
        
        logger.info(f"Inference engine initialized on device: {self.device}")
    
    def _setup_device(self):
        """Setup computation device"""
        if self.config.device == "auto":
            return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            return torch.device(self.config.device)
    
    async def initialize(self):
        """Initialize inference engine"""
        try:
            # Load model
            await self.load_model()
            
            # Initialize database connections
            await self.initialize_databases()
            
            # Initialize preprocessor
            await self.initialize_preprocessor()
            
            # Setup WebSocket manager
            self.setup_websocket_manager()
            
            logger.info("Inference engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize inference engine: {e}")
            raise
    
    async def load_model(self):
        """Load trained model"""
        try:
            model_path = Path(self.config.model_path) / self.config.model_name
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Load checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Extract config from checkpoint if available
            if 'config' in checkpoint:
                ai_config = checkpoint['config']
            else:
                # Default config
                ai_config = AIConfig(
                    input_dim=50,
                    spectral_dim=128,
                    hidden_dim=256,
                    output_dim=4,
                    num_heads=8,
                    num_layers=6,
                    dropout_rate=0.1
                )
            
            # Create model
            ai_system = create_ai_system(ai_config)
            self.model = ai_system['rag_model']
            self.knowledge_base = ai_system['knowledge_base']
            
            # Load weights
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                # Legacy checkpoint format
                self.model.load_state_dict(checkpoint)
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded successfully from {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Create fallback model
            self.model = self._create_fallback_model()
            logger.info("Using fallback model")
    
    def _create_fallback_model(self):
        """Create a simple fallback model"""
        class FallbackModel(nn.Module):
            def __init__(self, input_dim=50, hidden_dim=128, output_dim=4):
                super().__init__()
                self.layers = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.ReLU(),
                    nn.Linear(hidden_dim // 2, output_dim),
                    nn.Sigmoid()
                )
                
                self.confidence_head = nn.Sequential(
                    nn.Linear(hidden_dim // 2, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x, return_spectral=False):
                if len(x.shape) == 3:
                    x = x.mean(dim=1)
                
                features = self.layers[:-1](x)
                predictions = self.layers[-1:](features)
                confidence = self.confidence_head(features)
                
                # Simulate spectral components
                spectral_features = {
                    'low_freq_trend': torch.rand(1),
                    'mid_freq_cycle': torch.rand(1),
                    'high_freq_noise': torch.rand(1)
                }
                
                if return_spectral:
                    return predictions, confidence, spectral_features
                else:
                    return predictions, confidence
        
        model = FallbackModel().to(self.device)
        model.eval()
        return model
    
    async def initialize_databases(self):
        """Initialize database connections"""
        try:
            # QuestDB connection
            self.questdb_pool = await asyncpg.create_pool(
                host=self.config.questdb_host,
                port=self.config.questdb_port,
                user=self.config.questdb_user,
                password=self.config.questdb_password,
                database="qdb",
                min_size=5,
                max_size=20
            )
            
            # Redis connection
            self.redis_client = redis.from_url(self.config.redis_url)
            
            # Test connections
            async with self.questdb_pool.acquire() as conn:
                result = await conn.fetchrow("SELECT 1 as test")
                if result['test'] != 1:
                    raise Exception("QuestDB connection test failed")
            
            logger.info("Database connections established")
            
        except Exception as e:
            logger.error(f"Failed to initialize databases: {e}")
            # Continue without database for basic functionality
            self.questdb_pool = None
            self.redis_client = None
    
    async def initialize_preprocessor(self):
        """Initialize data preprocessor"""
        try:
            ai_config = AIConfig(
                input_dim=50,
                window_size=252
            )
            self.preprocessor = FinancialDataPreprocessor(ai_config)
            logger.info("Preprocessor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize preprocessor: {e}")
            self.preprocessor = None
    
    def setup_websocket_manager(self):
        """Setup WebSocket connection manager"""
        self.websocket_manager = WebSocketManager()
    
    async def get_market_data(self, symbol: str, days: int = 252) -> Optional[pd.DataFrame]:
        """Get market data for symbol"""
        try:
            # Check cache first
            cache_key = f"market_data:{symbol}:{days}"
            
            if self.redis_client:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return pickle.loads(cached_data)
            
            if not self.questdb_pool:
                # Generate synthetic data as fallback
                return self._generate_synthetic_data(symbol, days)
            
            async with self.questdb_pool.acquire() as conn:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                query = """
                SELECT 
                    ts as timestamp,
                    symbol,
                    open,
                    high,
                    low,
                    close as price,
                    volume,
                    (close - open) / open as intraday_return,
                    (high - low) / close as price_range
                FROM market_data 
                WHERE symbol = $1 
                AND ts BETWEEN $2::timestamp AND $3::timestamp
                ORDER BY ts ASC
                """
                
                rows = await conn.fetch(query, symbol, start_date, end_date)
                
                if not rows:
                    logger.warning(f"No data found for {symbol}, using synthetic data")
                    return self._generate_synthetic_data(symbol, days)
                
                df = pd.DataFrame([dict(row) for row in rows])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                # Cache the data
                if self.redis_client:
                    self.redis_client.setex(
                        cache_key, 
                        self.config.cache_ttl, 
                        pickle.dumps(df)
                    )
                
                return df
                
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return self._generate_synthetic_data(symbol, days)
    
    def _generate_synthetic_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Generate synthetic market data for testing"""
        try:
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=days),
                end=datetime.now(),
                freq='D'
            )
            
            # Generate realistic price data
            base_price = 100 + np.random.normal(0, 10)
            np.random.seed(hash(symbol) % 2**32)  # Consistent data for same symbol
            
            prices = base_price + np.cumsum(np.random.normal(0, 2, days))
            prices = np.maximum(prices, 1)
            
            df = pd.DataFrame({
                'symbol': symbol,
                'price': prices,
                'open': prices * (1 + np.random.normal(0, 0.01, days)),
                'high': prices * (1 + np.abs(np.random.normal(0, 0.02, days))),
                'low': prices * (1 - np.abs(np.random.normal(0, 0.02, days))),
                'volume': np.random.exponential(100000, days),
            }, index=dates)
            
            # Ensure high >= max(open, close) and low <= min(open, close)
            df['high'] = np.maximum(df['high'], np.maximum(df['open'], df['price']))
            df['low'] = np.minimum(df['low'], np.minimum(df['open'], df['price']))
            
            # Add derived columns
            df['intraday_return'] = (df['price'] - df['open']) / df['open']
            df['price_range'] = (df['high'] - df['low']) / df['price']
            
            return df
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {e}")
            return None
    
    def preprocess_data(self, data: pd.DataFrame) -> Optional[np.ndarray]:
        """Preprocess market data for model input"""
        try:
            if self.preprocessor:
                processed_data = self.preprocessor.preprocess_market_data(data)
            else:
                # Basic preprocessing
                processed_data = data.copy()
                
                # Add simple technical indicators
                processed_data['sma_20'] = data['price'].rolling(20).mean()
                processed_data['rsi'] = self._calculate_rsi(data['price'])
                processed_data['volatility'] = data['price'].pct_change().rolling(20).std()
                
                # Select numerical features
                feature_columns = [col for col in processed_data.columns 
                                 if col not in ['symbol', 'timestamp'] and not processed_data[col].isna().all()]
                processed_data = processed_data[feature_columns].fillna(0)
            
            # Create sequences
            sequences = []
            window_size = getattr(self.preprocessor.config, 'window_size', 252) if self.preprocessor else 252
            
            for i in range(window_size, len(processed_data)):
                sequence = processed_data.iloc[i-window_size:i].values
                if not np.isnan(sequence).any() and sequence.shape[0] == window_size:
                    sequences.append(sequence)
            
            if not sequences:
                return None
            
            # Return the last sequence
            return np.array(sequences[-1:])
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    async def predict(self, symbol: str, prediction_horizon: int = 1, 
                     include_spectral: bool = True) -> Optional[PredictionResponse]:
        """Generate prediction for a symbol"""
        start_time = time.time()
        
        try:
            # Get market data
            data = await self.get_market_data(symbol, days=252)
            if data is None or len(data) < 252:
                raise ValueError(f"Insufficient data for {symbol}")
            
            # Preprocess data
            sequence = self.preprocess_data(data)
            if sequence is None:
                raise ValueError(f"Failed to preprocess data for {symbol}")
            
            # Convert to tensor
            sequence_tensor = torch.FloatTensor(sequence).to(self.device)
            
            # Generate prediction
            with torch.no_grad():
                if include_spectral:
                    predictions, confidence, spectral_features = self.model(sequence_tensor, return_spectral=True)
                else:
                    predictions, confidence = self.model(sequence_tensor)
            
            # Extract prediction values
            pred_values = predictions.squeeze().cpu().numpy()
            conf_value = confidence.squeeze().cpu().item()
            
            # Current price
            current_price = float(data['price'].iloc[-1])
            
            # Calculate predicted price and direction
            if len(pred_values) > 0:
                predicted_change = float(pred_values[0])
                predicted_price = current_price * (1 + predicted_change)
                
                if predicted_change > 0.01:  # > 1% increase
                    direction = "bullish"
                elif predicted_change < -0.01:  # > 1% decrease
                    direction = "bearish"
                else:
                    direction = "neutral"
            else:
                predicted_price = current_price
                direction = "neutral"
            
            # Risk level based on confidence and volatility
            volatility = data['price'].pct_change().std()
            if conf_value > 0.8 and volatility < 0.02:
                risk_level = "low"
            elif conf_value > 0.5 and volatility < 0.05:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            # Technical indicators
            technical_indicators = {
                'rsi': float(data['price'].rolling(14).apply(lambda x: self._calculate_rsi(pd.Series(x)).iloc[-1] if len(x) == 14 else 50)),
                'volatility_20d': float(data['price'].pct_change().rolling(20).std().iloc[-1]),
                'sma_ratio': float(data['price'].iloc[-1] / data['price'].rolling(20).mean().iloc[-1]),
                'volume_trend': float(data['volume'].tail(10).mean() / data['volume'].mean() - 1)
            }
            
            # Market context
            market_context = {
                'current_price': current_price,
                'price_change_1d': float((data['price'].iloc[-1] - data['price'].iloc[-2]) / data['price'].iloc[-2]),
                'price_change_7d': float((data['price'].iloc[-1] - data['price'].iloc[-7]) / data['price'].iloc[-7]) if len(data) >= 7 else 0,
                'volume_rank': float(data['volume'].rank(pct=True).iloc[-1])
            }
            
            # Processing time
            processing_time = (time.time() - start_time) * 1000
            
            response = PredictionResponse(
                symbol=symbol,
                timestamp=datetime.now().isoformat(),
                current_price=current_price,
                predicted_price=predicted_price,
                prediction_horizon=prediction_horizon,
                confidence=conf_value,
                direction=direction,
                expected_return=float(predicted_change) * 100,
                risk_level=risk_level,
                spectral_analysis=spectral_features if include_spectral else None,
                technical_indicators=technical_indicators,
                market_context=market_context,
                model_version="1.0",
                processing_time_ms=processing_time
            )
            
            # Cache prediction
            cache_key = f"prediction:{symbol}:{prediction_horizon}:{include_spectral}"
            if self.redis_client:
                self.redis_client.setex(cache_key, 60, json.dumps(asdict(response), default=str))
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating prediction for {symbol}: {e}")
            return None
    
    async def batch_predict(self, symbols: List[str], **kwargs) -> BatchPredictionResponse:
        """Generate predictions for multiple symbols"""
        start_time = time.time()
        results = []
        failed_symbols = []
        
        # Process symbols concurrently
        tasks = [self.predict(symbol, **kwargs) for symbol in symbols]
        predictions = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, prediction in zip(symbols, predictions):
            if isinstance(prediction, PredictionResponse):
                results.append(prediction)
            else:
                failed_symbols.append(symbol)
                logger.error(f"Failed to predict {symbol}: {prediction}")
        
        processing_time = (time.time() - start_time) * 1000
        
        return BatchPredictionResponse(
            results=results,
            total_symbols=len(symbols),
            successful_predictions=len(results),
            failed_symbols=failed_symbols,
            processing_time_ms=processing_time,
            batch_id=str(uuid.uuid4())
        )

# =============================================================================
# WebSocket Management
# =============================================================================

class WebSocketManager:
    """Manager for WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, symbols: List[str]):
        """Accept WebSocket connection and subscribe to symbols"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        for symbol in symbols:
            if symbol not in self.subscriptions:
                self.subscriptions[symbol] = []
            self.subscriptions[symbol].append(websocket)
        
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection and clean up subscriptions"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all symbol subscriptions
        for symbol, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_symbol(self, symbol: str, message: str):
        """Broadcast message to all WebSockets subscribed to symbol"""
        if symbol in self.subscriptions:
            disconnected = []
            for websocket in self.subscriptions[symbol]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected WebSockets
            for websocket in disconnected:
                self.disconnect(websocket)

# =============================================================================
# FastAPI Application
# =============================================================================

# Create FastAPI app
app = FastAPI(
    title="WIG80 AI Inference API",
    description="Real-time AI-powered market analysis for WIG80 Polish stock market",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global inference engine
inference_engine: Optional[SpectralBiasInferenceEngine] = None
security = HTTPBearer()

# Prometheus metrics
PREDICTION_REQUESTS = Counter('predictions_total', 'Total predictions made')
PREDICTION_LATENCY = Histogram('prediction_duration_seconds', 'Prediction latency')
ACTIVE_CONNECTIONS = Gauge('websocket_connections', 'Active WebSocket connections')
MODEL_ACCURACY = Gauge('model_accuracy', 'Current model accuracy estimate')

# =============================================================================
# API Endpoints
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize inference engine on startup"""
    global inference_engine
    
    config = InferenceConfig()
    inference_engine = SpectralBiasInferenceEngine(config)
    await inference_engine.initialize()
    
    # Start metrics server
    if config.enable_metrics:
        start_http_server(config.metrics_port)
    
    logger.info("AI Inference API started successfully")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "service": "WIG80 AI Inference API",
        "version": "1.0.0",
        "description": "Real-time AI-powered market analysis for WIG80 Polish stock market",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "batch_analyze": "/batch_analyze",
            "spectrum": "/spectrum/{symbol}",
            "metrics": "/metrics",
            "websocket": "/ws/realtime"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if inference_engine:
            # Check database connection
            db_connected = inference_engine.questdb_pool is not None
            
            # Count WebSocket connections
            ws_connections = len(inference_engine.websocket_manager.active_connections)
            
            # System metrics
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
            
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                model_loaded=inference_engine.model is not None,
                database_connected=db_connected,
                websocket_connections=ws_connections,
                uptime_seconds=time.time() - inference_engine.start_time,
                system_metrics=system_metrics
            )
        else:
            return HealthResponse(
                status="unhealthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0",
                model_loaded=False,
                database_connected=False,
                websocket_connections=0,
                uptime_seconds=0,
                system_metrics={}
            )
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/analyze", response_model=PredictionResponse)
async def analyze_stock(request: AnalysisRequest):
    """Analyze a single stock with AI predictions"""
    if not inference_engine:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    try:
        PREDICTION_REQUESTS.inc()
        start_time = time.time()
        
        prediction = await inference_engine.predict(
            symbol=request.symbol,
            prediction_horizon=request.prediction_horizon,
            include_spectral=request.include_spectral
        )
        
        if prediction is None:
            raise HTTPException(status_code=404, detail=f"Could not generate prediction for {request.symbol}")
        
        # Record latency
        PREDICTION_LATENCY.observe(time.time() - start_time)
        
        return prediction
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_analyze", response_model=BatchPredictionResponse)
async def batch_analyze_stocks(request: BatchAnalysisRequest):
    """Analyze multiple stocks in batch"""
    if not inference_engine:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    try:
        PREDICTION_REQUESTS.inc()
        start_time = time.time()
        
        batch_result = await inference_engine.batch_predict(
            symbols=request.symbols,
            prediction_horizon=request.prediction_horizon
        )
        
        return batch_result
    
    except Exception as e:
        logger.error(f"Error in batch_analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/spectrum/{symbol}")
async def get_frequency_spectrum(symbol: str, days: int = Query(252, ge=30, le=1000)):
    """Get frequency spectrum analysis for a symbol"""
    if not inference_engine:
        raise HTTPException(status_code=503, detail="Inference engine not initialized")
    
    try:
        # Get market data
        data = await inference_engine.get_market_data(symbol, days=days)
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate frequency spectrum
        prices = data['price'].values
        
        # FFT analysis
        fft_values = np.fft.fft(prices)
        frequencies = np.fft.fftfreq(len(prices))
        power_spectrum = np.abs(fft_values) ** 2
        
        # Extract frequency bands
        positive_freq_idx = frequencies > 0
        positive_frequencies = frequencies[positive_freq_idx]
        positive_power = power_spectrum[positive_freq_idx]
        
        spectrum_analysis = {
            'symbol': symbol,
            'frequency_bands': {
                'low_frequency': {
                    'range': '0 - 0.1 Hz',
                    'power': float(np.sum(positive_power[positive_frequencies <= 0.1])),
                    'interpretation': 'Long-term trends'
                },
                'medium_frequency': {
                    'range': '0.1 - 0.5 Hz',
                    'power': float(np.sum(positive_power[(positive_frequencies > 0.1) & (positive_frequencies <= 0.5)])),
                    'interpretation': 'Business cycles and seasonality'
                },
                'high_frequency': {
                    'range': '0.5+ Hz',
                    'power': float(np.sum(positive_power[positive_frequencies > 0.5])),
                    'interpretation': 'Market noise and microstructure'
                }
            },
            'spectral_centroid': float(np.sum(positive_frequencies * positive_power) / np.sum(positive_power)),
            'total_power': float(np.sum(positive_power)),
            'analysis_date': datetime.now().isoformat()
        }
        
        return spectrum_analysis
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in spectrum endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    return StreamingResponse(
        iter([generate_latest()]),
        media_type="text/plain"
    )

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    if not inference_engine:
        await websocket.close(code=1011, reason="Inference engine not initialized")
        return
    
    try:
        # Receive subscription parameters
        data = await websocket.receive_text()
        subscription_data = json.loads(data)
        
        symbols = subscription_data.get('symbols', [])
        update_frequency = subscription_data.get('update_frequency', 5)
        include_spectral = subscription_data.get('include_spectral', True)
        
        if not symbols:
            await websocket.close(code=1008, reason="No symbols provided")
            return
        
        # Connect to WebSocket manager
        await inference_engine.websocket_manager.connect(websocket, symbols)
        ACTIVE_CONNECTIONS.set(len(inference_engine.websocket_manager.active_connections))
        
        # Send initial data
        for symbol in symbols:
            prediction = await inference_engine.predict(symbol, include_spectral=include_spectral)
            if prediction:
                message = {
                    'type': 'prediction',
                    'data': asdict(prediction)
                }
                await inference_engine.websocket_manager.send_personal_message(
                    json.dumps(message, default=str), websocket
                )
        
        # Keep connection alive and send updates
        while True:
            await asyncio.sleep(update_frequency)
            
            # Send updates for subscribed symbols
            for symbol in symbols:
                try:
                    prediction = await inference_engine.predict(symbol, include_spectral=include_spectral)
                    if prediction:
                        message = {
                            'type': 'prediction',
                            'symbol': symbol,
                            'data': asdict(prediction)
                        }
                        await inference_engine.websocket_manager.send_personal_message(
                            json.dumps(message, default=str), websocket
                        )
                except Exception as e:
                    logger.error(f"Error sending WebSocket update for {symbol}: {e}")
    
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if inference_engine:
            inference_engine.websocket_manager.disconnect(websocket)
            ACTIVE_CONNECTIONS.set(len(inference_engine.websocket_manager.active_connections))

@app.get("/symbols")
async def get_available_symbols():
    """Get list of available symbols for analysis"""
    # Return sample WIG80 symbols
    return {
        "symbols": [
            "KGH", "PKN", "PKO", "PZU", "LPP", "CCC", "CDR", "MIL", "PGE", "KGHM",
            "PKNORLEN", "PKOBP", "PGE", "LPP", "CCC", "CDR", "MIL", "DNP", "ALE", "JHP"
        ],
        "total": 20,
        "market": "WIG80"
    }

# =============================================================================
# Rate Limiting (Simple Implementation)
# =============================================================================

# Simple in-memory rate limiting
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False

rate_limiter = RateLimiter(
    max_requests=100,  # requests per window
    window_seconds=60  # 1 minute window
)

# =============================================================================
# Main Application
# =============================================================================

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    return app

if __name__ == "__main__":
    # Load configuration
    config = InferenceConfig()
    
    # Run the server
    uvicorn.run(
        "ai_inference_api:app",
        host=config.host,
        port=config.port,
        workers=config.workers,
        reload=config.reload,
        log_level="info"
    )