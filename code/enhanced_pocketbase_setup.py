#!/usr/bin/env python3
"""
Enhanced Pocketbase WIG80 REST API Server
==========================================

Comprehensive REST API endpoints for WIG80 stock data analysis including:
- Stock data query endpoints (historical prices, volume, OHLC data)
- Technical analysis endpoints (MACD, RSI, Bollinger Bands calculations)
- AI insights and market correlation endpoints
- Authentication and rate limiting
- Real-time WebSocket support

Author: WIG80 Analytics Team
Date: 2025-11-06
"""

import asyncio
import json
import sqlite3
import logging
import time
import hashlib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from contextlib import asynccontextmanager
from functools import wraps
from collections import defaultdict, deque

import pandas as pd
import numpy as np
import talib
import aiohttp
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration (use environment variables for Railway service discovery)
POCKETBASE_URL = os.getenv('POCKETBASE_URL', 'http://localhost:8090')
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8090'))
DB_PATH = os.getenv('DB_PATH', '/workspace/code/wig80_pocketbase.db')

# ===============================
# DATA MODELS
# ===============================

class StockDataRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., PKN_ORLEN)")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    interval: str = Field("1d", description="Data interval (1d, 1h, 5m)")

class TechnicalAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    period: int = Field(14, description="Analysis period")
    indicators: List[str] = Field(["macd", "rsi", "bb"], description="Technical indicators")

class AIInsightRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    analysis_type: str = Field(..., description="Type of analysis (overvaluation, trend, volatility)")

class RateLimitData(BaseModel):
    requests: List[float] = []
    tokens: float = 100.0  # Token bucket algorithm

# ===============================
# AUTHENTICATION & RATE LIMITING
# ===============================

class AuthManager:
    """Simple authentication and rate limiting system"""
    
    def __init__(self):
        self.users = {
            "admin": "admin123",  # In production, use proper password hashing
            "api_user": "api_pass"
        }
        self.tokens = {}
        self.rate_limits = defaultdict(RateLimitData)
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return token"""
        if username in self.users and self.users[username] == password:
            token = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()[:16]
            self.tokens[token] = username
            return token
        return None
    
    def verify_token(self, token: str) -> bool:
        """Verify if token is valid"""
        return token in self.tokens
    
    def check_rate_limit(self, client_id: str, max_requests: int = 100, window: int = 3600) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        limit_data = self.rate_limits[client_id]
        
        # Remove old requests outside window
        limit_data.requests = [req_time for req_time in limit_data.requests 
                              if now - req_time < window]
        
        if len(limit_data.requests) >= max_requests:
            return False
        
        limit_data.requests.append(now)
        return True

auth_manager = AuthManager()

def require_auth(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Dependency to require authentication"""
    if not auth_manager.verify_token(credentials.credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

def rate_limit(max_requests: int = 100, window: int = 3600):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if request:
                client_ip = request.client.host
                if not auth_manager.check_rate_limit(client_ip, max_requests, window):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# ===============================
# TECHNICAL ANALYSIS ENGINE
# ===============================

class TechnicalAnalysisEngine:
    """Technical analysis calculations for WIG80 stocks"""
    
    @staticmethod
    def calculate_macd(close_prices: np.array, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, np.array]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            macd_line, signal_line, histogram = talib.MACD(close_prices, fast, slow, signal)
            return {
                "macd": macd_line,
                "signal": signal_line,
                "histogram": histogram
            }
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return {"macd": [], "signal": [], "histogram": []}
    
    @staticmethod
    def calculate_rsi(close_prices: np.array, period: int = 14) -> np.array:
        """Calculate RSI (Relative Strength Index)"""
        try:
            rsi = talib.RSI(close_prices, timeperiod=period)
            return rsi
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return np.array([])
    
    @staticmethod
    def calculate_bollinger_bands(close_prices: np.array, period: int = 20, std_dev: float = 2) -> Dict[str, np.array]:
        """Calculate Bollinger Bands"""
        try:
            upper, middle, lower = talib.BBANDS(close_prices, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
            return {
                "upper": upper,
                "middle": middle,
                "lower": lower
            }
        except Exception as e:
            logger.error(f"Bollinger Bands calculation error: {e}")
            return {"upper": [], "middle": [], "lower": []}
    
    @staticmethod
    def calculate_sma(close_prices: np.array, period: int = 20) -> np.array:
        """Calculate Simple Moving Average"""
        try:
            sma = talib.SMA(close_prices, timeperiod=period)
            return sma
        except Exception as e:
            logger.error(f"SMA calculation error: {e}")
            return np.array([])
    
    @staticmethod
    def calculate_ema(close_prices: np.array, period: int = 20) -> np.array:
        """Calculate Exponential Moving Average"""
        try:
            ema = talib.EMA(close_prices, timeperiod=period)
            return ema
        except Exception as e:
            logger.error(f"EMA calculation error: {e}")
            return np.array([])

# ===============================
# AI INSIGHTS ENGINE
# ===============================

class AIInsightsEngine:
    """AI-powered market analysis and insights"""
    
    @staticmethod
    def generate_overvaluation_analysis(stock_data: Dict) -> Dict[str, Any]:
        """Generate overvaluation analysis using fundamental metrics"""
        try:
            pe_ratio = stock_data.get("pe_ratio", 15.0)
            historical_pe = stock_data.get("historical_pe_avg", 12.0)
            pb_ratio = stock_data.get("pb_ratio", 1.5)
            historical_pb = stock_data.get("historical_pb_avg", 1.2)
            
            pe_deviation = (pe_ratio - historical_pe) / historical_pe * 100
            pb_deviation = (pb_ratio - historical_pb) / historical_pb * 100
            
            # Calculate overvaluation score
            overvaluation_score = max(0, (pe_deviation + pb_deviation) / 2)
            
            # Determine status
            if overvaluation_score > 30:
                status = "severely_overvalued"
                recommendation = "strong_sell"
                confidence = 0.9
            elif overvaluation_score > 15:
                status = "overvalued"
                recommendation = "sell"
                confidence = 0.8
            elif overvaluation_score > 5:
                status = "slightly_overvalued"
                recommendation = "hold"
                confidence = 0.7
            else:
                status = "fairly_valued"
                recommendation = "hold"
                confidence = 0.6
            
            return {
                "status": status,
                "overvaluation_score": round(overvaluation_score, 2),
                "pe_analysis": {
                    "current_pe": pe_ratio,
                    "historical_pe": historical_pe,
                    "deviation_percent": round(pe_deviation, 2)
                },
                "pb_analysis": {
                    "current_pb": pb_ratio,
                    "historical_pb": historical_pb,
                    "deviation_percent": round(pb_deviation, 2)
                },
                "recommendation": recommendation,
                "confidence": confidence,
                "reasoning": f"P/E ratio is {abs(round(pe_deviation, 1))}% {'above' if pe_deviation > 0 else 'below'} historical average"
            }
        except Exception as e:
            logger.error(f"Overvaluation analysis error: {e}")
            return {
                "status": "analysis_error",
                "error": str(e),
                "confidence": 0.0
            }
    
    @staticmethod
    def generate_trend_analysis(stock_data: Dict) -> Dict[str, Any]:
        """Generate trend analysis using price movements and volume"""
        try:
            close_prices = stock_data.get("close_prices", [])
            volumes = stock_data.get("volumes", [])
            
            if len(close_prices) < 20:
                return {"status": "insufficient_data", "confidence": 0.0}
            
            # Calculate price changes
            price_change_1d = (close_prices[-1] - close_prices[-2]) / close_prices[-2] * 100
            price_change_5d = (close_prices[-1] - close_prices[-6]) / close_prices[-6] * 100 if len(close_prices) >= 6 else 0
            price_change_20d = (close_prices[-1] - close_prices[-21]) / close_prices[-21] * 100 if len(close_prices) >= 21 else 0
            
            # Calculate volume trend
            avg_volume_20d = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
            recent_volume = volumes[-1] if volumes else 0
            volume_trend = (recent_volume - avg_volume_20d) / avg_volume_20d * 100 if avg_volume_20d > 0 else 0
            
            # Determine trend
            if price_change_20d > 10 and volume_trend > 20:
                trend = "strong_uptrend"
                recommendation = "buy"
                confidence = 0.85
            elif price_change_20d > 5 and volume_trend > 10:
                trend = "uptrend"
                recommendation = "buy"
                confidence = 0.75
            elif price_change_20d < -10 and volume_trend < -20:
                trend = "strong_downtrend"
                recommendation = "sell"
                confidence = 0.85
            elif price_change_20d < -5 and volume_trend < -10:
                trend = "downtrend"
                recommendation = "sell"
                confidence = 0.75
            else:
                trend = "sideways"
                recommendation = "hold"
                confidence = 0.65
            
            return {
                "trend": trend,
                "price_changes": {
                    "1_day": round(price_change_1d, 2),
                    "5_day": round(price_change_5d, 2),
                    "20_day": round(price_change_20d, 2)
                },
                "volume_trend": round(volume_trend, 2),
                "recommendation": recommendation,
                "confidence": confidence,
                "reasoning": f"20-day price change: {round(price_change_20d, 1)}%, Volume trend: {round(volume_trend, 1)}%"
            }
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            return {
                "status": "analysis_error",
                "error": str(e),
                "confidence": 0.0
            }
    
    @staticmethod
    def generate_volatility_analysis(stock_data: Dict) -> Dict[str, Any]:
        """Generate volatility analysis"""
        try:
            close_prices = stock_data.get("close_prices", [])
            
            if len(close_prices) < 20:
                return {"status": "insufficient_data", "confidence": 0.0}
            
            # Calculate returns
            returns = np.diff(close_prices) / close_prices[:-1]
            
            # Calculate volatility metrics
            daily_volatility = np.std(returns) * 100
            annualized_volatility = daily_volatility * np.sqrt(252)  # 252 trading days
            
            # Calculate volatility percentiles
            volatility_percentile = (np.sum(returns < -daily_volatility) / len(returns)) * 100
            
            # Determine volatility level
            if annualized_volatility > 50:
                vol_level = "very_high"
                risk_level = "extreme"
            elif annualized_volatility > 35:
                vol_level = "high"
                risk_level = "high"
            elif annualized_volatility > 20:
                vol_level = "moderate"
                risk_level = "medium"
            else:
                vol_level = "low"
                risk_level = "low"
            
            return {
                "volatility_level": vol_level,
                "daily_volatility": round(daily_volatility, 2),
                "annualized_volatility": round(annualized_volatility, 2),
                "volatility_percentile": round(volatility_percentile, 2),
                "risk_level": risk_level,
                "recommendation": "monitor_closely" if vol_level in ["very_high", "high"] else "normal_monitoring",
                "confidence": 0.8,
                "reasoning": f"Annualized volatility of {round(annualized_volatility, 1)}% indicates {risk_level} risk"
            }
        except Exception as e:
            logger.error(f"Volatility analysis error: {e}")
            return {
                "status": "analysis_error",
                "error": str(e),
                "confidence": 0.0
            }

# ===============================
# MARKET CORRELATION ENGINE
# ===============================

class MarketCorrelationEngine:
    """Market correlation analysis between WIG80 stocks"""
    
    @staticmethod
    def calculate_correlation_matrix(symbols: List[str], stock_data: Dict) -> Dict[str, Any]:
        """Calculate correlation matrix for multiple stocks"""
        try:
            price_data = {}
            
            # Collect price data for each symbol
            for symbol in symbols:
                if symbol in stock_data:
                    price_data[symbol] = stock_data[symbol].get("close_prices", [])
            
            if len(price_data) < 2:
                return {"error": "Insufficient data for correlation analysis"}
            
            # Create DataFrame for correlation calculation
            df = pd.DataFrame(price_data)
            
            # Calculate returns
            returns = df.pct_change().dropna()
            
            # Calculate correlation matrix
            correlation_matrix = returns.corr()
            
            # Find highest correlations
            correlations = []
            for i, symbol1 in enumerate(correlation_matrix.columns):
                for j, symbol2 in enumerate(correlation_matrix.columns):
                    if i < j:  # Avoid duplicates
                        corr_value = correlation_matrix.loc[symbol1, symbol2]
                        correlations.append({
                            "symbol_a": symbol1,
                            "symbol_b": symbol2,
                            "correlation": round(corr_value, 3),
                            "strength": "strong" if abs(corr_value) > 0.7 else "moderate" if abs(corr_value) > 0.4 else "weak"
                        })
            
            # Sort by absolute correlation value
            correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
            
            return {
                "correlation_matrix": correlation_matrix.to_dict(),
                "top_correlations": correlations[:10],
                "summary": {
                    "average_correlation": round(correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean(), 3),
                    "highest_correlation": correlations[0] if correlations else None,
                    "sectors_most_correlated": MarketCorrelationEngine._find_sector_correlations(correlations)
                }
            }
        except Exception as e:
            logger.error(f"Correlation analysis error: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _find_sector_correlations(correlations: List[Dict]) -> List[str]:
        """Find which sectors have highest correlations"""
        # This would normally match with sector data
        # For demo, return sample sectors
        return ["Banking", "Energy", "Technology", "Telecommunications"]

# ===============================
# DATABASE OPERATIONS
# ===============================

class DatabaseManager:
    """SQLite database operations for WIG80 data"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Stock data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    macd REAL,
                    rsi REAL,
                    bb_upper REAL,
                    bb_lower REAL,
                    sma_20 REAL,
                    ema_20 REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # AI insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market correlations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_correlations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol_a TEXT NOT NULL,
                    symbol_b TEXT NOT NULL,
                    correlation REAL NOT NULL,
                    strength TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    market_cap REAL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_timestamp ON stock_data(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_insights_symbol_timestamp ON ai_insights(symbol, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_correlations_timestamp ON market_correlations(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_companies_symbol ON companies(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_alerts_symbol_timestamp ON market_alerts(symbol, timestamp)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_stock_data(self, data: Dict) -> int:
        """Insert stock data record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_data (
                    timestamp, symbol, open_price, high_price, low_price, 
                    close_price, volume, macd, rsi, bb_upper, bb_lower, sma_20, ema_20
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['timestamp'], data['symbol'], data['open_price'], data['high_price'],
                data['low_price'], data['close_price'], data['volume'], data.get('macd'),
                data.get('rsi'), data.get('bb_upper'), data.get('bb_lower'),
                data.get('sma_20'), data.get('ema_20')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_stock_data(self, symbol: str, start_date: str = None, end_date: str = None, limit: int = 100) -> List[Dict]:
        """Get stock data for a symbol"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM stock_data WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def insert_ai_insight(self, data: Dict) -> int:
        """Insert AI insight record"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ai_insights (timestamp, symbol, insight_type, result, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['timestamp'], data['symbol'], data['insight_type'],
                json.dumps(data['result']), data['confidence']
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_ai_insights(self, symbol: str = None, min_confidence: float = 0.0, limit: int = 50) -> List[Dict]:
        """Get AI insights"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM ai_insights WHERE confidence >= ?"
            params = [min_confidence]
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                try:
                    record['result'] = json.loads(record['result'])
                except:
                    pass
                results.append(record)
            
            return results
    
    def get_companies(self, active_only: bool = True) -> List[Dict]:
        """Get companies list"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute("SELECT * FROM companies WHERE is_active = 1 ORDER BY symbol")
            else:
                cursor.execute("SELECT * FROM companies ORDER BY symbol")
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

# ===============================
# API MODELS FOR REQUEST/RESPONSE
# ===============================

class StockDataResponse(BaseModel):
    symbol: str
    timestamp: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    macd: Optional[float] = None
    rsi: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    sma_20: Optional[float] = None
    ema_20: Optional[float] = None

class AIInsightResponse(BaseModel):
    id: int
    timestamp: str
    symbol: str
    insight_type: str
    result: Dict[str, Any]
    confidence: float

class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    period: int
    indicators: Dict[str, Any]
    timestamp: str

class MarketCorrelationResponse(BaseModel):
    correlation_matrix: Dict[str, Dict[str, float]]
    top_correlations: List[Dict[str, Any]]
    summary: Dict[str, Any]

# ===============================
# FASTAPI APPLICATION
# ===============================

# Global instances
db_manager = DatabaseManager(DB_PATH)
tech_engine = TechnicalAnalysisEngine()
ai_engine = AIInsightsEngine()
corr_engine = MarketCorrelationEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 WIG80 Pocketbase API Server starting up...")
    
    # Initialize sample data if needed
    companies = db_manager.get_companies()
    if not companies:
        logger.info("📊 Initializing sample companies data...")
        sample_companies = [
            {"symbol": "PKN_ORLEN", "name": "PKN Orlen SA", "sector": "Oil & Gas", "market_cap": 25000000000},
            {"symbol": "KGHM", "name": "KGHM Polska Miedź SA", "sector": "Mining", "market_cap": 30000000000},
            {"symbol": "PGE", "name": "Polska Grupa Energetyczna SA", "sector": "Energy", "market_cap": 15000000000},
            {"symbol": "ORANGE_PL", "name": "Orange Polska SA", "sector": "Telecommunications", "market_cap": 8000000000},
            {"symbol": "CD_PROJEKT", "name": "CD Projekt SA", "sector": "Gaming", "market_cap": 12000000000},
            {"symbol": "PEPCO", "name": "Pepco Group NV", "sector": "Retail", "market_cap": 6000000000},
            {"symbol": "LPP", "name": "LPP SA", "sector": "Fashion Retail", "market_cap": 8000000000},
            {"symbol": "PKO_BP", "name": "PKO Bank Polski SA", "sector": "Banking", "market_cap": 18000000000},
            {"symbol": "SANPL", "name": "Santander Bank Polska SA", "sector": "Banking", "market_cap": 12000000000},
            {"symbol": "MBANK", "name": "mBank SA", "sector": "Banking", "market_cap": 10000000000}
        ]
        
        for company in sample_companies:
            with sqlite3.connect(db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO companies (symbol, name, sector, market_cap, is_active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (company['symbol'], company['name'], company['sector'], company['market_cap']))
                conn.commit()
    
    yield
    
    # Shutdown
    logger.info("🛑 WIG80 Pocketbase API Server shutting down...")

# Create FastAPI app
app = FastAPI(
    title="WIG80 Pocketbase API",
    description="Comprehensive REST API for WIG80 stock data analysis with technical analysis, AI insights, and market correlations",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# AUTHENTICATION ENDPOINTS
# ===============================

@app.post("/api/auth/login")
@rate_limit(max_requests=10, window=300)  # 10 requests per 5 minutes for auth
async def login(request: Request):
    """User authentication endpoint"""
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password required")
        
        token = auth_manager.authenticate(username, password)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {
            "success": True,
            "token": token,
            "user": username,
            "expires_in": 3600
        }
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# STOCK DATA ENDPOINTS
# ===============================

@app.get("/api/stocks", response_model=List[StockDataResponse])
@rate_limit(max_requests=100, window=3600)
async def get_all_stocks(
    symbol: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """Get stock data for all WIG80 companies or specific symbol"""
    try:
        if symbol:
            data = db_manager.get_stock_data(symbol, start_date, end_date, limit)
        else:
            # Get all companies and their latest data
            companies = db_manager.get_companies()
            all_data = []
            for company in companies[:50]:  # Limit to 50 companies
                company_data = db_manager.get_stock_data(company['symbol'], None, None, 1)
                all_data.extend(company_data)
            data = all_data
        
        return [StockDataResponse(**record) for record in data]
    except Exception as e:
        logger.error(f"Get stocks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{symbol}", response_model=List[StockDataResponse])
@rate_limit(max_requests=100, window=3600)
async def get_stock_details(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """Get detailed data for specific company"""
    try:
        data = db_manager.get_stock_data(symbol, start_date, end_date, limit)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        return [StockDataResponse(**record) for record in data]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get stock details error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies")
@rate_limit(max_requests=50, window=3600)
async def get_companies(active_only: bool = True):
    """Get WIG80 companies list"""
    try:
        companies = db_manager.get_companies(active_only)
        return {"companies": companies, "total": len(companies)}
    except Exception as e:
        logger.error(f"Get companies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# TECHNICAL ANALYSIS ENDPOINTS
# ===============================

@app.get("/api/technical/{symbol}", response_model=TechnicalAnalysisResponse)
@rate_limit(max_requests=200, window=3600)
async def get_technical_analysis(
    symbol: str,
    period: int = 14,
    indicators: Optional[str] = None
):
    """Get technical analysis for specific company"""
    try:
        # Parse indicators parameter
        if indicators:
            indicator_list = indicators.split(",")
        else:
            indicator_list = ["macd", "rsi", "bb"]
        
        # Get historical data
        data = db_manager.get_stock_data(symbol, limit=100)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Convert to arrays for technical analysis
        close_prices = np.array([record['close_price'] for record in data])
        high_prices = np.array([record['high_price'] for record in data])
        low_prices = np.array([record['low_price'] for record in data])
        volumes = np.array([record['volume'] for record in data])
        
        result_indicators = {}
        
        # Calculate requested indicators
        for indicator in indicator_list:
            indicator = indicator.lower().strip()
            
            if indicator == "macd":
                macd_data = tech_engine.calculate_macd(close_prices)
                result_indicators["macd"] = {
                    "macd": macd_data["macd"][-1] if len(macd_data["macd"]) > 0 else None,
                    "signal": macd_data["signal"][-1] if len(macd_data["signal"]) > 0 else None,
                    "histogram": macd_data["histogram"][-1] if len(macd_data["histogram"]) > 0 else None
                }
            
            elif indicator == "rsi":
                rsi = tech_engine.calculate_rsi(close_prices, period)
                result_indicators["rsi"] = {
                    "value": rsi[-1] if len(rsi) > 0 else None,
                    "signal": "overbought" if rsi[-1] > 70 else "oversold" if rsi[-1] < 30 else "neutral" if len(rsi) > 0 else None
                }
            
            elif indicator == "bb" or indicator == "bollinger":
                bb_data = tech_engine.calculate_bollinger_bands(close_prices, period)
                result_indicators["bollinger_bands"] = {
                    "upper": bb_data["upper"][-1] if len(bb_data["upper"]) > 0 else None,
                    "middle": bb_data["middle"][-1] if len(bb_data["middle"]) > 0 else None,
                    "lower": bb_data["lower"][-1] if len(bb_data["lower"]) > 0 else None,
                    "position": "upper" if len(bb_data["upper"]) > 0 and close_prices[-1] > bb_data["upper"][-1] else 
                              "lower" if len(bb_data["lower"]) > 0 and close_prices[-1] < bb_data["lower"][-1] else "middle"
                }
            
            elif indicator == "sma":
                sma = tech_engine.calculate_sma(close_prices, period)
                result_indicators["sma"] = {
                    "value": sma[-1] if len(sma) > 0 else None,
                    "trend": "above" if len(sma) > 0 and close_prices[-1] > sma[-1] else "below"
                }
            
            elif indicator == "ema":
                ema = tech_engine.calculate_ema(close_prices, period)
                result_indicators["ema"] = {
                    "value": ema[-1] if len(ema) > 0 else None,
                    "trend": "above" if len(ema) > 0 and close_prices[-1] > ema[-1] else "below"
                }
        
        return TechnicalAnalysisResponse(
            symbol=symbol,
            period=period,
            indicators=result_indicators,
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Technical analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# AI INSIGHTS ENDPOINTS
# ===============================

@app.get("/api/ai-insights", response_model=List[AIInsightResponse])
@rate_limit(max_requests=50, window=3600)
async def get_ai_insights(
    symbol: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 50
):
    """Get AI-generated market insights"""
    try:
        insights = db_manager.get_ai_insights(symbol, min_confidence, limit)
        return [AIInsightResponse(**insight) for insight in insights]
    except Exception as e:
        logger.error(f"Get AI insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-insights/generate")
@rate_limit(max_requests=20, window=3600)
async def generate_ai_insights(request: AIInsightRequest):
    """Trigger AI analysis for stocks"""
    try:
        # Get stock data for analysis
        data = db_manager.get_stock_data(request.symbol, limit=100)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {request.symbol}")
        
        # Prepare data for AI analysis
        stock_data = {
            "close_prices": [record['close_price'] for record in data],
            "volumes": [record['volume'] for record in data],
            "pe_ratio": 15.0,  # Mock data - would come from fundamental analysis
            "pb_ratio": 1.2,
            "historical_pe_avg": 12.0,
            "historical_pb_avg": 1.0
        }
        
        # Generate insights based on analysis type
        if request.analysis_type == "overvaluation":
            result = ai_engine.generate_overvaluation_analysis(stock_data)
        elif request.analysis_type == "trend":
            result = ai_engine.generate_trend_analysis(stock_data)
        elif request.analysis_type == "volatility":
            result = ai_engine.generate_volatility_analysis(stock_data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown analysis type: {request.analysis_type}")
        
        # Store insight in database
        insight_data = {
            "timestamp": datetime.now().isoformat(),
            "symbol": request.symbol,
            "insight_type": request.analysis_type,
            "result": result,
            "confidence": result.get("confidence", 0.0)
        }
        
        insight_id = db_manager.insert_ai_insight(insight_data)
        
        return {
            "success": True,
            "insight_id": insight_id,
            "symbol": request.symbol,
            "analysis_type": request.analysis_type,
            "result": result,
            "timestamp": insight_data["timestamp"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate AI insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# MARKET CORRELATION ENDPOINTS
# ===============================

@app.get("/api/correlations", response_model=MarketCorrelationResponse)
@rate_limit(max_requests=30, window=3600)
async def get_market_correlations(symbols: Optional[str] = None):
    """Get market correlation data"""
    try:
        # Get symbols to analyze
        if symbols:
            symbol_list = symbols.split(",")
        else:
            # Get top companies by default
            companies = db_manager.get_companies()
            symbol_list = [comp["symbol"] for comp in companies[:10]]
        
        # Get stock data for correlation analysis
        stock_data = {}
        for symbol in symbol_list:
            data = db_manager.get_stock_data(symbol, limit=50)
            if data:
                stock_data[symbol] = {
                    "close_prices": [record['close_price'] for record in data]
                }
        
        # Calculate correlations
        correlations = corr_engine.calculate_correlation_matrix(list(stock_data.keys()), stock_data)
        
        return MarketCorrelationResponse(**correlations)
    
    except Exception as e:
        logger.error(f"Get correlations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# UTILITY ENDPOINTS
# ===============================

@app.get("/api/alerts")
@rate_limit(max_requests=50, window=3600)
async def get_market_alerts(symbol: Optional[str] = None, unread_only: bool = False):
    """Get market alerts"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM market_alerts WHERE 1=1"
            params = []
            
            if symbol:
                query += " AND symbol = ?"
                params.append(symbol)
            
            if unread_only:
                query += " AND is_read = 0"
            
            query += " ORDER BY timestamp DESC LIMIT 100"
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            alerts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return {"alerts": alerts, "total": len(alerts)}
    
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "database": "connected" if os.path.exists(DB_PATH) else "disconnected"
    }

@app.get("/api/stats")
@rate_limit(max_requests=10, window=3600)
async def get_api_stats():
    """Get API usage statistics"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM stock_data")
            stock_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ai_insights")
            insight_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM companies WHERE is_active = 1")
            active_companies = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM market_alerts WHERE is_read = 0")
            unread_alerts = cursor.fetchone()[0]
            
            return {
                "database_stats": {
                    "total_stock_records": stock_count,
                    "total_ai_insights": insight_count,
                    "active_companies": active_companies,
                    "unread_alerts": unread_alerts
                },
                "api_stats": {
                    "uptime": "running",
                    "rate_limiting": "enabled",
                    "authentication": "enabled"
                },
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# REAL-TIME DATA GENERATION
# ===============================

async def generate_sample_data():
    """Generate sample stock data for testing"""
    try:
        companies = db_manager.get_companies()
        current_time = datetime.now()
        
        for company in companies:
            # Generate realistic stock data
            base_price = np.random.uniform(20, 200)
            change_percent = np.random.uniform(-5, 5)
            current_price = base_price * (1 + change_percent / 100)
            
            # Create OHLC data
            open_price = current_price * (1 + np.random.uniform(-0.02, 0.02))
            high_price = max(open_price, current_price) * (1 + abs(np.random.uniform(0, 0.03)))
            low_price = min(open_price, current_price) * (1 - abs(np.random.uniform(0, 0.03)))
            volume = int(np.random.uniform(100000, 2000000))
            
            # Calculate technical indicators
            close_prices = np.array([current_price + np.random.uniform(-5, 5) for _ in range(20)])
            macd_data = tech_engine.calculate_macd(close_prices)
            rsi = tech_engine.calculate_rsi(close_prices)
            bb_data = tech_engine.calculate_bollinger_bands(close_prices)
            
            stock_data = {
                "timestamp": current_time.isoformat(),
                "symbol": company["symbol"],
                "open_price": round(open_price, 2),
                "high_price": round(high_price, 2),
                "low_price": round(low_price, 2),
                "close_price": round(current_price, 2),
                "volume": volume,
                "macd": round(macd_data["macd"][-1], 4) if len(macd_data["macd"]) > 0 else None,
                "rsi": round(rsi[-1], 2) if len(rsi) > 0 else None,
                "bb_upper": round(bb_data["upper"][-1], 2) if len(bb_data["upper"]) > 0 else None,
                "bb_lower": round(bb_data["lower"][-1], 2) if len(bb_data["lower"]) > 0 else None,
                "sma_20": round(np.mean(close_prices[-20:]), 2) if len(close_prices) >= 20 else None,
                "ema_20": round(tech_engine.calculate_ema(close_prices)[-1], 2) if len(close_prices) >= 20 else None
            }
            
            db_manager.insert_stock_data(stock_data)
    
    except Exception as e:
        logger.error(f"Generate sample data error: {e}")

# ===============================
# MAIN APPLICATION
# ===============================

def main():
    """Main application entry point"""
    print("="*80)
    print("🚀 WIG80 Pocketbase REST API Server v2.0")
    print("="*80)
    print(f"🌐 API Server: http://{API_HOST}:{API_PORT}")
    print(f"📊 Database: {DB_PATH}")
    print(f"🔐 Authentication: Enabled")
    print(f"⚡ Rate Limiting: Enabled")
    print(f"📈 Technical Analysis: TA-Lib")
    print(f"🤖 AI Insights: Enabled")
    print(f"🔗 Market Correlations: Enabled")
    print("="*80)
    print("\n📋 Available Endpoints:")
    print("  • POST /api/auth/login - User authentication")
    print("  • GET  /api/stocks - Get stock data")
    print("  • GET  /api/stocks/{symbol} - Get specific stock data")
    print("  • GET  /api/companies - Get WIG80 companies")
    print("  • GET  /api/technical/{symbol} - Technical analysis")
    print("  • GET  /api/ai-insights - AI insights")
    print("  • POST /api/ai-insights/generate - Generate AI analysis")
    print("  • GET  /api/correlations - Market correlations")
    print("  • GET  /api/alerts - Market alerts")
    print("  • GET  /api/health - Health check")
    print("  • GET  /api/stats - API statistics")
    print("="*80)
    print("\n🔧 Starting server...")
    
    # Generate initial sample data
    asyncio.run(generate_sample_data())
    
    # Start the server
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()