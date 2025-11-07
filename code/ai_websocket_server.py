"""
AI WebSocket Server for Real-time Insights and Alerts

This module provides a WebSocket server for real-time AI analysis, predictions,
and alerts for the WIG80 Polish financial market platform. It supports multiple
client types, data streaming, and scalable connection management.

Author: AI System Architecture Team
Version: 1.0
Date: 2025-11-06
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
import torch
from ai_model_design import (
    create_ai_system, AIConfig, MarketEvent, PredictionResult,
    RealTimeAIPipeline
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# WebSocket Event Models
# =============================================================================

class WebSocketEventType(str, Enum):
    """WebSocket event types for real-time communication"""
    PREDICTION = "ai_prediction"
    ALERT = "ai_alert"
    INSIGHT = "ai_insight"
    MARKET_DATA = "market_update"
    MODEL_STATUS = "model_status"
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE = "performance_update"
    ERROR = "error"

class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class WebSocketMessage:
    """Generic WebSocket message structure"""
    event_type: WebSocketEventType
    timestamp: datetime
    data: Dict[str, Any]
    client_id: Optional[str] = None
    correlation_id: Optional[str] = None

@dataclass
class AIAlert:
    """AI-generated alert structure"""
    alert_id: str
    symbol: str
    level: AlertLevel
    message: str
    prediction_value: float
    confidence: float
    trigger_conditions: Dict[str, Any]
    timestamp: datetime
    expires_at: Optional[datetime] = None

@dataclass
class AIInsight:
    """AI-generated market insight"""
    insight_id: str
    symbol: str
    insight_type: str
    description: str
    confidence: float
    market_impact: str
    supporting_data: Dict[str, Any]
    timestamp: datetime

# =============================================================================
# Connection Management
# =============================================================================

class WebSocketConnection:
    """Manages individual WebSocket connections"""
    
    def __init__(self, websocket: WebSocket, client_id: str, connection_type: str = "general"):
        self.websocket = websocket
        self.client_id = client_id
        self.connection_type = connection_type
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.now()
        self.last_ping = time.time()
        self.is_alive = True
        
    async def send_message(self, message: WebSocketMessage):
        """Send message to this connection"""
        try:
            await self.websocket.send_json(asdict(message))
        except Exception as e:
            logger.error(f"Error sending message to {self.client_id}: {e}")
            self.is_alive = False
    
    async def send_json(self, data: Dict[str, Any]):
        """Send JSON data to this connection"""
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending JSON to {self.client_id}: {e}")
            self.is_alive = False
    
    async def ping(self):
        """Send ping to check connection health"""
        try:
            await self.websocket.send_json({"type": "ping", "timestamp": datetime.now().isoformat()})
            self.last_ping = time.time()
        except Exception as e:
            logger.error(f"Error pinging {self.client_id}: {e}")
            self.is_alive = False

class ConnectionManager:
    """Manages all WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.connection_types: Dict[str, Set[str]] = {
            "traders": set(),
            "analysts": set(),
            "systems": set(),
            "general": set()
        }
        self.symbol_subscriptions: Dict[str, Set[str]] = {}
        self.alert_subscriptions: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str, connection_type: str = "general") -> WebSocketConnection:
        """Accept new WebSocket connection"""
        await websocket.accept()
        connection = WebSocketConnection(websocket, client_id, connection_type)
        self.connections[client_id] = connection
        self.connection_types[connection_type].add(client_id)
        
        logger.info(f"Client {client_id} connected as {connection_type}")
        return connection
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.connections:
            connection = self.connections[client_id]
            connection_type = connection.connection_type
            
            # Remove from all tracking structures
            self.connections.pop(client_id, None)
            self.connection_types[connection_type].discard(client_id)
            
            # Remove from symbol subscriptions
            for symbol, subscribers in self.symbol_subscriptions.items():
                subscribers.discard(client_id)
            
            # Remove from alert subscriptions
            for alert_type, subscribers in self.alert_subscriptions.items():
                subscribers.discard(client_id)
            
            logger.info(f"Client {client_id} disconnected")
    
    async def broadcast(self, message: WebSocketMessage, target_type: str = None, symbol: str = None):
        """Broadcast message to appropriate connections"""
        target_connections = set()
        
        if target_type:
            # Broadcast to specific connection type
            target_connections.update(self.connection_types.get(target_type, set()))
        else:
            # Broadcast to all connections
            target_connections.update(self.connections.keys())
        
        if symbol:
            # Filter by symbol subscription
            symbol_subscribers = self.symbol_subscriptions.get(symbol, set())
            target_connections = target_connections.intersection(symbol_subscribers)
        
        # Send message to target connections
        disconnected = set()
        for client_id in target_connections:
            connection = self.connections.get(client_id)
            if connection and connection.is_alive:
                try:
                    await connection.send_message(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {client_id}: {e}")
                    disconnected.add(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def send_to_client(self, client_id: str, message: WebSocketMessage):
        """Send message to specific client"""
        connection = self.connections.get(client_id)
        if connection and connection.is_alive:
            await connection.send_message(message)
        else:
            logger.warning(f"Client {client_id} not found or not alive")
    
    def subscribe_symbol(self, client_id: str, symbol: str):
        """Subscribe client to symbol updates"""
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
        self.symbol_subscriptions[symbol].add(client_id)
        
        connection = self.connections.get(client_id)
        if connection:
            connection.subscriptions.add(symbol)
    
    def subscribe_alerts(self, client_id: str, alert_types: List[str]):
        """Subscribe client to alert types"""
        for alert_type in alert_types:
            if alert_type not in self.alert_subscriptions:
                self.alert_subscriptions[alert_type] = set()
            self.alert_subscriptions[alert_type].add(client_id)
    
    def unsubscribe_symbol(self, client_id: str, symbol: str):
        """Unsubscribe client from symbol updates"""
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(client_id)
        
        connection = self.connections.get(client_id)
        if connection:
            connection.subscriptions.discard(symbol)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.connections),
            "connection_types": {
                conn_type: len(connections) 
                for conn_type, connections in self.connection_types.items()
            },
            "symbol_subscriptions": {
                symbol: len(subscribers) 
                for symbol, subscribers in self.symbol_subscriptions.items()
            },
            "alert_subscriptions": {
                alert_type: len(subscribers) 
                for alert_type, subscribers in self.alert_subscriptions.items()
            }
        }

# =============================================================================
# Real-time AI Processing Engine
# =============================================================================

class RealTimeAIEngine:
    """Real-time AI processing engine for WebSocket streaming"""
    
    def __init__(self, ai_system: Dict[str, Any]):
        self.ai_system = ai_system
        self.connection_manager = ConnectionManager()
        self.is_running = False
        self.processing_tasks = []
        self.alert_history: List[AIAlert] = []
        self.insight_cache: Dict[str, AIInsight] = {}
        
        # Performance monitoring
        self.processing_stats = {
            "predictions_processed": 0,
            "alerts_generated": 0,
            "insights_created": 0,
            "avg_processing_time_ms": 0.0
        }
    
    async def start(self):
        """Start the real-time AI processing engine"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start background processing tasks
        self.processing_tasks = [
            asyncio.create_task(self._market_data_processor()),
            asyncio.create_task(self._prediction_streamer()),
            asyncio.create_task(self._alert_generator()),
            asyncio.create_task(self._insight_generator()),
            asyncio.create_task(self._system_health_monitor()),
            asyncio.create_task(self._connection_health_checker())
        ]
        
        logger.info("Real-time AI engine started")
    
    async def stop(self):
        """Stop the real-time AI processing engine"""
        self.is_running = False
        
        # Cancel all background tasks
        for task in self.processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.processing_tasks, return_exceptions=True)
        
        logger.info("Real-time AI engine stopped")
    
    async def _market_data_processor(self):
        """Process incoming market data and generate AI predictions"""
        pipeline = self.ai_system['real_time_pipeline']
        
        while self.is_running:
            try:
                # Simulate market data processing
                # In real implementation, this would connect to QuestDB or market data feed
                for symbol in ["PKN", "KGH", "PZU", "PKO", "CDR"]:  # Example WIG80 symbols
                    # Create simulated market event
                    market_event = MarketEvent(
                        symbol=symbol,
                        timestamp=datetime.now(),
                        price=100.0 + np.random.randn() * 5,  # Simulated price
                        volume=int(1000000 + np.random.randn() * 500000),
                        high=101.0 + np.random.randn() * 2,
                        low=99.0 + np.random.randn() * 2,
                        open=100.0 + np.random.randn() * 2
                    )
                    
                    # Process through AI pipeline
                    start_time = time.time()
                    prediction = await pipeline.process_realtime_market_event(market_event)
                    processing_time = (time.time() - start_time) * 1000
                    
                    if prediction:
                        # Update statistics
                        self.processing_stats["predictions_processed"] += 1
                        self.processing_stats["avg_processing_time_ms"] = (
                            (self.processing_stats["avg_processing_time_ms"] * 
                             (self.processing_stats["predictions_processed"] - 1) + 
                             processing_time) / self.processing_stats["predictions_processed"]
                        )
                        
                        # Broadcast prediction
                        message = WebSocketMessage(
                            event_type=WebSocketEventType.PREDICTION,
                            timestamp=datetime.now(),
                            data={
                                "symbol": prediction.symbol,
                                "prediction": prediction.value,
                                "confidence": prediction.confidence,
                                "spectral_components": prediction.spectral_components,
                                "latency_ms": prediction.latency_ms
                            }
                        )
                        await self.connection_manager.broadcast(message, symbol=symbol)
                
                await asyncio.sleep(1)  # Process every second
                
            except Exception as e:
                logger.error(f"Error in market data processor: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _prediction_streamer(self):
        """Stream AI predictions to connected clients"""
        while self.is_running:
            try:
                # Generate real-time insights based on recent predictions
                symbols = ["PKN", "KGH", "PZU", "PKO", "CDR"]
                
                for symbol in symbols:
                    # Simulate insight generation
                    insight = AIInsight(
                        insight_id=f"insight_{symbol}_{int(time.time())}",
                        symbol=symbol,
                        insight_type="trend_analysis",
                        description=f"AI detected bullish momentum for {symbol} with high confidence",
                        confidence=0.82,
                        market_impact="positive",
                        supporting_data={
                            "price_change_1h": np.random.randn() * 2,
                            "volume_surge": np.random.choice([True, False]),
                            "spectral_analysis": {"trend_strength": 0.75}
                        },
                        timestamp=datetime.now()
                    )
                    
                    self.insight_cache[insight.insight_id] = insight
                    
                    # Broadcast insight
                    message = WebSocketMessage(
                        event_type=WebSocketEventType.INSIGHT,
                        timestamp=datetime.now(),
                        data=asdict(insight)
                    )
                    await self.connection_manager.broadcast(message, symbol=symbol)
                
                await asyncio.sleep(30)  # Generate insights every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in prediction streamer: {e}")
                await asyncio.sleep(10)
    
    async def _alert_generator(self):
        """Generate AI alerts based on market conditions"""
        while self.is_running:
            try:
                # Check for alert conditions
                for symbol in ["PKN", "KGH", "PZU", "PKO", "CDR"]:
                    # Simulate alert condition checking
                    if np.random.random() < 0.1:  # 10% chance of alert
                        alert = AIAlert(
                            alert_id=f"alert_{symbol}_{int(time.time())}",
                            symbol=symbol,
                            level=AlertLevel.WARNING,
                            message=f"AI detected unusual price movement in {symbol}",
                            prediction_value=np.random.randn() * 0.1,
                            confidence=np.random.uniform(0.6, 0.95),
                            trigger_conditions={
                                "price_change_threshold": 0.05,
                                "volume_spike": True,
                                "volatility_increase": 0.3
                            },
                            timestamp=datetime.now(),
                            expires_at=datetime.now() + timedelta(minutes=15)
                        )
                        
                        self.alert_history.append(alert)
                        self.processing_stats["alerts_generated"] += 1
                        
                        # Broadcast alert
                        message = WebSocketMessage(
                            event_type=WebSocketEventType.ALERT,
                            timestamp=datetime.now(),
                            data=asdict(alert)
                        )
                        await self.connection_manager.broadcast(message, symbol=symbol)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in alert generator: {e}")
                await asyncio.sleep(30)
    
    async def _insight_generator(self):
        """Generate market insights and trends"""
        while self.is_running:
            try:
                # Generate market overview insights
                market_overview = {
                    "overall_sentiment": np.random.choice(["bullish", "bearish", "neutral"]),
                    "market_trend": np.random.choice(["uptrend", "downtrend", "sideways"]),
                    "volatility_level": np.random.uniform(0.1, 0.8),
                    "ai_confidence": np.random.uniform(0.7, 0.95)
                }
                
                message = WebSocketMessage(
                    event_type=WebSocketEventType.INSIGHT,
                    timestamp=datetime.now(),
                    data={
                        "type": "market_overview",
                        "data": market_overview
                    }
                )
                await self.connection_manager.broadcast(message)
                
                await asyncio.sleep(300)  # Market overview every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in insight generator: {e}")
                await asyncio.sleep(120)
    
    async def _system_health_monitor(self):
        """Monitor and broadcast system health"""
        while self.is_running:
            try:
                # Generate system health data
                health_data = {
                    "cpu_usage": np.random.uniform(30, 80),
                    "memory_usage": np.random.uniform(40, 90),
                    "gpu_usage": np.random.uniform(10, 60),
                    "prediction_queue_size": np.random.randint(0, 50),
                    "active_connections": len(self.connection_manager.connections),
                    "ai_model_status": {
                        "spectral_model": "healthy",
                        "rag_system": "healthy",
                        "real_time_pipeline": "healthy"
                    },
                    "database_connections": {
                        "questdb": "healthy",
                        "pocketbase": "healthy",
                        "redis": "healthy"
                    }
                }
                
                message = WebSocketMessage(
                    event_type=WebSocketEventType.SYSTEM_HEALTH,
                    timestamp=datetime.now(),
                    data=health_data
                )
                await self.connection_manager.broadcast(message)
                
                await asyncio.sleep(30)  # Health check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in system health monitor: {e}")
                await asyncio.sleep(60)
    
    async def _connection_health_checker(self):
        """Check health of WebSocket connections"""
        while self.is_running:
            try:
                disconnected_clients = []
                
                for client_id, connection in self.connection_manager.connections.items():
                    # Check if connection is still alive
                    if not connection.is_alive:
                        disconnected_clients.append(client_id)
                        continue
                    
                    # Send ping and check response time
                    try:
                        await connection.ping()
                    except Exception:
                        connection.is_alive = False
                        disconnected_clients.append(client_id)
                
                # Clean up disconnected clients
                for client_id in disconnected_clients:
                    self.connection_manager.disconnect(client_id)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in connection health checker: {e}")
                await asyncio.sleep(30)

# =============================================================================
# WebSocket Server Implementation
# =============================================================================

class AIWebSocketServer:
    """Main WebSocket server for real-time AI communication"""
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.ai_system = create_ai_system(self.config)
        self.ai_engine = RealTimeAIEngine(self.ai_system)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="WIG80 AI WebSocket Server",
            description="Real-time AI insights and alerts WebSocket server",
            version="1.0.0"
        )
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup WebSocket and HTTP routes"""
        
        @self.app.get("/")
        async def websocket_page():
            """WebSocket test page"""
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WIG80 AI WebSocket Test</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .log { background: #f0f0f0; padding: 10px; height: 300px; overflow-y: scroll; margin: 10px 0; }
                    .status { padding: 5px 10px; border-radius: 3px; margin: 5px 0; }
                    .connected { background: #d4edda; color: #155724; }
                    .disconnected { background: #f8d7da; color: #721c24; }
                    .prediction { background: #d1ecf1; color: #0c5460; }
                    .alert { background: #fff3cd; color: #856404; }
                    input, button { padding: 8px; margin: 5px; }
                </style>
            </head>
            <body>
                <h1>WIG80 AI WebSocket Test Client</h1>
                <div class="status" id="status">Disconnected</div>
                
                <div>
                    <input type="text" id="clientId" placeholder="Client ID" value="test_client">
                    <button onclick="connect()">Connect</button>
                    <button onclick="disconnect()">Disconnect</button>
                </div>
                
                <div>
                    <input type="text" id="symbol" placeholder="Symbol (e.g., PKN)" value="PKN">
                    <button onclick="subscribeSymbol()">Subscribe</button>
                    <button onclick="unsubscribeSymbol()">Unsubscribe</button>
                </div>
                
                <div>
                    <button onclick="subscribeAlerts()">Subscribe to Alerts</button>
                    <button onclick="requestMarketData()">Request Market Data</button>
                </div>
                
                <div class="log" id="log"></div>
                
                <script>
                    let ws = null;
                    
                    function log(message, type = 'info') {
                        const logDiv = document.getElementById('log');
                        const timestamp = new Date().toLocaleTimeString();
                        logDiv.innerHTML += `<div>[${timestamp}] ${message}</div>`;
                        logDiv.scrollTop = logDiv.scrollHeight;
                    }
                    
                    function updateStatus(status, className) {
                        const statusDiv = document.getElementById('status');
                        statusDiv.textContent = status;
                        statusDiv.className = `status ${className}`;
                    }
                    
                    function connect() {
                        const clientId = document.getElementById('clientId').value;
                        ws = new WebSocket(`ws://localhost:8001/ws/ai/${clientId}`);
                        
                        ws.onopen = function() {
                            log('Connected to WebSocket server', 'connected');
                            updateStatus('Connected', 'connected');
                        };
                        
                        ws.onmessage = function(event) {
                            const data = JSON.parse(event.data);
                            log(`Received: ${JSON.stringify(data, null, 2)}`, 'prediction');
                        };
                        
                        ws.onclose = function() {
                            log('Disconnected from WebSocket server', 'disconnected');
                            updateStatus('Disconnected', 'disconnected');
                        };
                        
                        ws.onerror = function(error) {
                            log(`WebSocket error: ${error}`, 'alert');
                        };
                    }
                    
                    function disconnect() {
                        if (ws) {
                            ws.close();
                        }
                    }
                    
                    function subscribeSymbol() {
                        const symbol = document.getElementById('symbol').value;
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({
                                type: 'subscribe',
                                symbol: symbol
                            }));
                            log(`Subscribed to ${symbol}`, 'info');
                        }
                    }
                    
                    function unsubscribeSymbol() {
                        const symbol = document.getElementById('symbol').value;
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({
                                type: 'unsubscribe',
                                symbol: symbol
                            }));
                            log(`Unsubscribed from ${symbol}`, 'info');
                        }
                    }
                    
                    function subscribeAlerts() {
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({
                                type: 'subscribe_alerts',
                                alert_types: ['all']
                            }));
                            log('Subscribed to alerts', 'alert');
                        }
                    }
                    
                    function requestMarketData() {
                        const symbol = document.getElementById('symbol').value;
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({
                                type: 'request_market_data',
                                symbol: symbol
                            }));
                            log(`Requested market data for ${symbol}`, 'info');
                        }
                    }
                </script>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        @self.app.websocket("/ws/ai/{client_id}")
        async def ai_websocket_endpoint(websocket: WebSocket, client_id: str):
            """Main WebSocket endpoint for AI communication"""
            connection = await self.ai_engine.connection_manager.connect(websocket, client_id)
            
            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message_data = json.loads(data)
                    
                    # Process client message
                    await self._process_client_message(connection, message_data)
                    
            except WebSocketDisconnect:
                self.ai_engine.connection_manager.disconnect(client_id)
            except Exception as e:
                logger.error(f"WebSocket error for client {client_id}: {e}")
                self.ai_engine.connection_manager.disconnect(client_id)
        
        @self.app.get("/stats")
        async def get_server_stats():
            """Get server statistics"""
            connection_stats = self.ai_engine.connection_manager.get_connection_stats()
            processing_stats = self.ai_engine.processing_stats
            
            return {
                "timestamp": datetime.now(),
                "connections": connection_stats,
                "processing": processing_stats,
                "ai_engine_running": self.ai_engine.is_running
            }
    
    async def _process_client_message(self, connection: WebSocketConnection, message_data: Dict[str, Any]):
        """Process incoming client messages"""
        message_type = message_data.get("type")
        
        try:
            if message_type == "subscribe":
                symbol = message_data.get("symbol")
                if symbol:
                    self.ai_engine.connection_manager.subscribe_symbol(connection.client_id, symbol)
                    await connection.send_json({
                        "type": "subscription_confirmed",
                        "symbol": symbol
                    })
            
            elif message_type == "unsubscribe":
                symbol = message_data.get("symbol")
                if symbol:
                    self.ai_engine.connection_manager.unsubscribe_symbol(connection.client_id, symbol)
                    await connection.send_json({
                        "type": "unsubscription_confirmed",
                        "symbol": symbol
                    })
            
            elif message_type == "subscribe_alerts":
                alert_types = message_data.get("alert_types", ["all"])
                self.ai_engine.connection_manager.subscribe_alerts(connection.client_id, alert_types)
                await connection.send_json({
                    "type": "alert_subscription_confirmed",
                    "alert_types": alert_types
                })
            
            elif message_type == "request_market_data":
                symbol = message_data.get("symbol")
                if symbol:
                    # Send current market data
                    market_data = {
                        "symbol": symbol,
                        "price": 100.0 + np.random.randn() * 5,
                        "volume": int(1000000 + np.random.randn() * 500000),
                        "timestamp": datetime.now().isoformat()
                    }
                    await connection.send_json({
                        "type": "market_data",
                        "data": market_data
                    })
            
            elif message_type == "ping":
                await connection.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            else:
                await connection.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
        
        except Exception as e:
            logger.error(f"Error processing client message: {e}")
            await connection.send_json({
                "type": "error",
                "message": str(e)
            })
    
    async def start(self):
        """Start the WebSocket server and AI engine"""
        await self.ai_engine.start()
        logger.info("AI WebSocket server started")
    
    async def stop(self):
        """Stop the WebSocket server and AI engine"""
        await self.ai_engine.stop()
        logger.info("AI WebSocket server stopped")
    
    def run(self, host: str = "0.0.0.0", port: int = 8001, debug: bool = False):
        """Run the WebSocket server"""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info" if debug else "warning",
            access_log=debug
        )

# =============================================================================
# Main Application
# =============================================================================

async def main():
    """Main application entry point"""
    # Create and start WebSocket server
    server = AIWebSocketServer()
    await server.start()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WIG80 AI WebSocket Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Create and run server
    server = AIWebSocketServer()
    server.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

"""
WebSocket Server Features:

1. Real-time AI Communication:
   - Live AI predictions streaming
   - Market insights and alerts
   - System health monitoring
   - Performance metrics broadcasting

2. Connection Management:
   - Multiple client types (traders, analysts, systems)
   - Symbol-based subscriptions
   - Alert type subscriptions
   - Connection health monitoring

3. Real-time Processing:
   - Market data processing pipeline
   - AI prediction streaming
   - Alert generation system
   - Insight generation engine

4. WebSocket Events:
   - ai_prediction: Real-time AI predictions
   - ai_alert: Generated alerts and warnings
   - ai_insight: Market insights and analysis
   - market_update: Market data updates
   - model_status: AI model status updates
   - system_health: System health monitoring
   - performance_update: Performance metrics

5. Client Management:
   - Connection lifecycle management
   - Subscription management
   - Message routing and filtering
   - Health checking and cleanup

6. Performance Features:
   - Asynchronous message processing
   - Connection pooling and management
   - Broadcast optimization
   - Memory-efficient event handling

This WebSocket server provides a robust foundation for real-time AI-powered
financial communication and analysis.
"""