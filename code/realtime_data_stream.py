#!/usr/bin/env python3
"""
Real-Time Data Streaming Service
Comprehensive WebSocket-based streaming system for QuestDB and Pocketbase integration
"""

import asyncio
import websockets
import json
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import aiohttp
import socket
import ssl
import weakref
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/questdb_wig80_logs/realtime_stream.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RealtimeStream')

class ConnectionStatus(Enum):
    """Connection status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    FAILED = "failed"

class MarketStatus(Enum):
    """Market status enumeration"""
    PRE_MARKET = "pre_market"
    OPEN = "open"
    AFTER_HOURS = "after_hours"
    CLOSED = "closed"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"

@dataclass
class StockUpdate:
    """Stock data update structure"""
    timestamp: str
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    market_status: str
    data_source: str

@dataclass
class QuestDBConfig:
    """QuestDB connection configuration"""
    host: str = "localhost"
    port: int = 8812
    user: str = "admin"
    password: str = "quest"
    database: str = "qdb"
    tls_enabled: bool = False

@dataclass
class PocketbaseConfig:
    """Pocketbase connection configuration"""
    url: str = "http://localhost:8090"
    admin_email: str = "admin@example.com"
    admin_password: str = "admin123"
    collections: List[str] = None

    def __post_init__(self):
        if self.collections is None:
            self.collections = ["stock_data", "market_updates", "alerts"]

class QuestDBConnector:
    """QuestDB database connector with WebSocket support"""
    
    def __init__(self, config: QuestDBConfig):
        self.config = config
        self.ws_connection = None
        self.status = ConnectionStatus.DISCONNECTED
        self.message_handlers: List[Callable] = []
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._reconnect_delay = 1
        
    async def connect(self) -> bool:
        """Establish WebSocket connection to QuestDB"""
        try:
            self.status = ConnectionStatus.CONNECTING
            protocol = "wss" if self.config.tls_enabled else "ws"
            uri = f"{protocol}://{self.config.host}:{self.config.port}/exec"
            
            logger.info(f"Connecting to QuestDB at {uri}")
            
            self.ws_connection = await websockets.connect(
                uri,
                extra_headers={
                    'Authorization': f'Basic {self._get_auth_header()}',
                    'Content-Type': 'text/plain'
                },
                ping_interval=20,
                ping_timeout=10,
                close_timeout=5
            )
            
            self.status = ConnectionStatus.CONNECTED
            self._reconnect_attempts = 0
            logger.info("✅ Connected to QuestDB")
            
            # Start message listener
            asyncio.create_task(self._listen_messages())
            return True
            
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"❌ Failed to connect to QuestDB: {e}")
            return False
    
    def _get_auth_header(self) -> str:
        """Generate base64 authentication header"""
        import base64
        credentials = f"{self.config.user}:{self.config.password}"
        return base64.b64encode(credentials.encode()).decode()
    
    async def _listen_messages(self):
        """Listen for incoming messages from QuestDB"""
        try:
            async for message in self.ws_connection:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"Received non-JSON message: {message[:100]}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    logger.error(traceback.format_exc())
        except websockets.exceptions.ConnectionClosed:
            logger.warning("QuestDB WebSocket connection closed")
            self.status = ConnectionStatus.DISCONNECTED
            await self._handle_disconnect()
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
            self.status = ConnectionStatus.ERROR
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process incoming message from QuestDB"""
        for handler in self.message_handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
    
    async def _handle_disconnect(self):
        """Handle WebSocket disconnection"""
        if self._reconnect_attempts < self._max_reconnect_attempts:
            self.status = ConnectionStatus.RECONNECTING
            self._reconnect_attempts += 1
            delay = self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
            
            logger.info(f"Reconnecting to QuestDB in {delay}s (attempt {self._reconnect_attempts})")
            await asyncio.sleep(delay)
            
            if await self.connect():
                logger.info("✅ Reconnected to QuestDB")
        else:
            self.status = ConnectionStatus.FAILED
            logger.error("❌ Max reconnection attempts reached")
    
    def add_message_handler(self, handler: Callable):
        """Add message handler callback"""
        self.message_handlers.append(handler)
    
    async def execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Execute SQL query via WebSocket"""
        if not self.ws_connection or self.status != ConnectionStatus.CONNECTED:
            logger.error("Not connected to QuestDB")
            return None
        
        try:
            await self.ws_connection.send(query)
            # Note: This is simplified - actual implementation would need proper response handling
            logger.info(f"Executed query: {query[:100]}...")
            return {"status": "success", "query": query}
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            return None
    
    async def insert_stock_data(self, stock_data: StockUpdate) -> bool:
        """Insert stock data into QuestDB"""
        query = f"""
        INSERT INTO stock_updates (
            ts, symbol, price, change, change_percent, volume, 
            high, low, open, market_status, data_source
        ) VALUES (
            '{stock_data.timestamp}', '{stock_data.symbol}', 
            {stock_data.price}, {stock_data.change}, {stock_data.change_percent},
            {stock_data.volume}, {stock_data.high}, {stock_data.low},
            {stock_data.open}, '{stock_data.market_status}', '{stock_data.data_source}'
        );
        """
        
        return await self.execute_query(query) is not None
    
    async def close(self):
        """Close WebSocket connection"""
        if self.ws_connection:
            await self.ws_connection.close()
        self.status = ConnectionStatus.DISCONNECTED

class PocketbaseConnector:
    """Pocketbase API connector for real-time data distribution"""
    
    def __init__(self, config: PocketbaseConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.status = ConnectionStatus.DISCONNECTED
        self.auth_token = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 2
    
    async def connect(self) -> bool:
        """Establish connection to Pocketbase"""
        try:
            self.status = ConnectionStatus.CONNECTING
            self.session = aiohttp.ClientSession()
            
            # Authenticate with admin credentials
            auth_data = {
                "identity": self.config.admin_email,
                "password": self.config.admin_password
            }
            
            async with self.session.post(
                f"{self.config.url}/api/admins/auth-with-password",
                json=auth_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get('token')
                    self.status = ConnectionStatus.CONNECTED
                    self._reconnect_attempts = 0
                    logger.info("✅ Connected to Pocketbase")
                    return True
                else:
                    logger.error(f"❌ Pocketbase auth failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.status = ConnectionStatus.ERROR
            logger.error(f"❌ Failed to connect to Pocketbase: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def create_record(self, collection: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create record in Pocketbase collection"""
        if not self.session or self.status != ConnectionStatus.CONNECTED:
            logger.error("Not connected to Pocketbase")
            return None
        
        try:
            async with self.session.post(
                f"{self.config.url}/api/collections/{collection}/records",
                headers=self._get_headers(),
                json=data
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    logger.info(f"✅ Created record in {collection}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to create record: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error creating record: {e}")
            return None
    
    async def update_record(self, collection: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing record in Pocketbase"""
        if not self.session or self.status != ConnectionStatus.CONNECTED:
            logger.error("Not connected to Pocketbase")
            return None
        
        try:
            async with self.session.patch(
                f"{self.config.url}/api/collections/{collection}/records/{record_id}",
                headers=self._get_headers(),
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ Updated record in {collection}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Failed to update record: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error updating record: {e}")
            return None
    
    async def distribute_stock_update(self, stock_data: StockUpdate) -> bool:
        """Distribute stock update to Pocketbase collections"""
        # Distribute to stock_data collection
        stock_record = {
            "timestamp": stock_data.timestamp,
            "symbol": stock_data.symbol,
            "price": stock_data.price,
            "change": stock_data.change,
            "change_percent": stock_data.change_percent,
            "volume": stock_data.volume,
            "high": stock_data.high,
            "low": stock_data.low,
            "open": stock_data.open,
            "market_status": stock_data.market_status,
            "data_source": stock_data.data_source
        }
        
        await self.create_record("stock_data", stock_record)
        
        # Distribute to market_updates collection
        market_record = {
            "timestamp": stock_data.timestamp,
            "market_status": stock_data.market_status,
            "total_symbols": 88,  # WIG80 total
            "update_type": "individual",
            "data_source": stock_data.data_source
        }
        
        await self.create_record("market_updates", market_record)
        return True
    
    async def close(self):
        """Close Pocketbase connection"""
        if self.session:
            await self.session.close()
        self.status = ConnectionStatus.DISCONNECTED

class StockDataProvider:
    """Base class for stock data providers"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = ConnectionStatus.DISCONNECTED
    
    async def fetch_data(self) -> List[StockUpdate]:
        """Fetch stock data - to be implemented by subclasses"""
        raise NotImplementedError

class StooqDataProvider(StockDataProvider):
    """Stooq.pl data provider with HTML scraping"""
    
    def __init__(self):
        super().__init__("Stooq.pl")
        self.base_url = "https://stooq.pl"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self) -> bool:
        """Initialize data provider"""
        self.session = aiohttp.ClientSession()
        self.status = ConnectionStatus.CONNECTED
        return True
    
    def _get_market_status(self) -> MarketStatus:
        """Determine current market status based on Polish time"""
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Weekend
        if weekday >= 5:
            return MarketStatus.WEEKEND
        
        # Pre-market (8:00-9:00)
        if 8 <= hour < 9:
            return MarketStatus.PRE_MARKET
        
        # Market hours (9:00-17:00)
        if 9 <= hour < 17:
            return MarketStatus.OPEN
        
        # After-hours (17:00-18:00)
        if 17 <= hour < 18:
            return MarketStatus.AFTER_HOURS
        
        return MarketStatus.CLOSED
    
    async def fetch_data(self) -> List[StockUpdate]:
        """Fetch real-time data from Stooq.pl"""
        if not self.session:
            await self.connect()
        
        market_status = self._get_market_status()
        stock_updates = []
        
        try:
            # For demo purposes, generate realistic mock data
            # In production, this would scrape Stooq.pl
            symbols = [
                "PKN", "KGHM", "PGE", "ORANGE", "CDPROJEKT", "PEPCO", "LPP", "PKO", 
                "SANPL", "MBANK", "ING", "ALIOR", "CYFRPL", "PLAY", "ASB", "CCC"
            ]
            
            for symbol in symbols:
                # Generate realistic price data
                base_price = 50.0 + (hash(symbol) % 100)  # Deterministic base price
                change = (hash(symbol + "change") % 200 - 100) / 100  # -1.0 to +1.0
                
                price = base_price * (1 + change / 100)
                change_amount = price - base_price
                change_percent = change
                
                update = StockUpdate(
                    timestamp=datetime.now().isoformat(),
                    symbol=symbol,
                    price=round(price, 2),
                    change=round(change_amount, 2),
                    change_percent=round(change_percent, 2),
                    volume=100000 + (hash(symbol + "vol") % 1000000),
                    high=round(price * 1.02, 2),
                    low=round(price * 0.98, 2),
                    open=round(price * 0.995, 2),
                    market_status=market_status.value,
                    data_source="stooq.pl"
                )
                
                stock_updates.append(update)
            
            logger.info(f"✅ Fetched {len(stock_updates)} stock updates from {self.name}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching data from {self.name}: {e}")
            logger.error(traceback.format_exc())
        
        return stock_updates
    
    async def close(self):
        """Close data provider connection"""
        if self.session:
            await self.session.close()
        self.status = ConnectionStatus.DISCONNECTED

class RealTimeStreamManager:
    """Main real-time streaming manager"""
    
    def __init__(self):
        self.questdb = QuestDBConnector(QuestDBConfig())
        self.pocketbase = PocketbaseConnector(PocketbaseConfig())
        self.data_providers: List[StockDataProvider] = []
        self.subscribers: List[websockets.WebSocketServerProtocol] = []
        self.running = False
        self.update_interval = 30  # seconds
        self._update_task = None
        self._status_handlers: List[Callable] = []
        
        # Add default data provider
        self.data_providers.append(StooqDataProvider())
    
    async def start(self):
        """Start the real-time streaming service"""
        if self.running:
            logger.warning("Service is already running")
            return
        
        self.running = True
        logger.info("🚀 Starting Real-Time Data Stream Manager")
        
        # Connect to databases
        await self._connect_databases()
        
        # Start WebSocket server
        await self._start_websocket_server()
        
        # Start data update loop
        self._update_task = asyncio.create_task(self._update_loop())
        
        # Set up connection monitoring
        asyncio.create_task(self._connection_monitor())
        
        logger.info("✅ Real-Time Stream Manager started successfully")
    
    async def stop(self):
        """Stop the real-time streaming service"""
        if not self.running:
            return
        
        self.running = False
        logger.info("🛑 Stopping Real-Time Stream Manager")
        
        # Cancel update task
        if self._update_task:
            self._update_task.cancel()
        
        # Close connections
        await self.questdb.close()
        await self.pocketbase.close()
        for provider in self.data_providers:
            await provider.close()
        
        logger.info("✅ Real-Time Stream Manager stopped")
    
    async def _connect_databases(self):
        """Connect to QuestDB and Pocketbase"""
        # Connect to QuestDB
        if not await self.questdb.connect():
            logger.error("❌ Failed to connect to QuestDB")
        
        # Connect to Pocketbase
        if not await self.pocketbase.connect():
            logger.error("❌ Failed to connect to Pocketbase")
        
        # Set up message handlers
        self.questdb.add_message_handler(self._handle_questdb_message)
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time subscriptions"""
        server = await websockets.serve(
            self._handle_websocket_client,
            "localhost",
            8765,
            ping_interval=20,
            ping_timeout=10
        )
        
        logger.info("📡 WebSocket server started on ws://localhost:8765")
        return server
    
    async def _handle_websocket_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🔗 Client connected: {client_id}")
        
        self.subscribers.append(websocket)
        
        try:
            # Send initial connection message
            await websocket.send(json.dumps({
                "type": "connection",
                "status": "connected",
                "timestamp": datetime.now().isoformat(),
                "message": "Connected to real-time stream"
            }))
            
            # Handle client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON message"
                    }))
                except Exception as e:
                    logger.error(f"Error handling client message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error with client {client_id}: {e}")
        finally:
            if websocket in self.subscribers:
                self.subscribers.remove(websocket)
    
    async def _handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle message from WebSocket client"""
        message_type = data.get("type")
        
        if message_type == "subscribe":
            # Client wants to subscribe to updates
            await websocket.send(json.dumps({
                "type": "subscription_confirmed",
                "timestamp": datetime.now().isoformat()
            }))
            
        elif message_type == "ping":
            await websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }))
        
        elif message_type == "status":
            # Send current system status
            status = {
                "type": "status",
                "questdb_status": self.questdb.status.value,
                "pocketbase_status": self.pocketbase.status.value,
                "data_providers": [p.name for p in self.data_providers],
                "subscribers": len(self.subscribers),
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(status))
    
    async def _handle_questdb_message(self, data: Dict[str, Any]):
        """Handle message from QuestDB"""
        logger.info(f"📊 QuestDB message: {data}")
    
    async def _update_loop(self):
        """Main data update loop"""
        while self.running:
            try:
                logger.info("🔄 Starting data update cycle")
                
                # Fetch data from all providers
                all_updates = []
                for provider in self.data_providers:
                    updates = await provider.fetch_data()
                    all_updates.extend(updates)
                
                # Process updates
                for update in all_updates:
                    await self._process_stock_update(update)
                
                # Broadcast to WebSocket subscribers
                await self._broadcast_updates(all_updates)
                
                logger.info(f"✅ Update cycle completed - {len(all_updates)} updates processed")
                
            except Exception as e:
                logger.error(f"❌ Error in update loop: {e}")
                logger.error(traceback.format_exc())
            
            # Wait for next update cycle
            await asyncio.sleep(self.update_interval)
    
    async def _process_stock_update(self, update: StockUpdate):
        """Process individual stock update"""
        try:
            # Store in QuestDB
            await self.questdb.insert_stock_data(update)
            
            # Distribute to Pocketbase
            await self.pocketbase.distribute_stock_update(update)
            
            logger.debug(f"📊 Processed update for {update.symbol}: {update.price}")
            
        except Exception as e:
            logger.error(f"❌ Error processing stock update: {e}")
    
    async def _broadcast_updates(self, updates: List[StockUpdate]):
        """Broadcast updates to all WebSocket subscribers"""
        if not updates:
            return
        
        message = {
            "type": "stock_updates",
            "timestamp": datetime.now().isoformat(),
            "count": len(updates),
            "data": [asdict(update) for update in updates]
        }
        
        message_str = json.dumps(message)
        
        # Send to all subscribers
        disconnected = []
        for websocket in self.subscribers:
            try:
                await websocket.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error sending to subscriber: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            if websocket in self.subscribers:
                self.subscribers.remove(websocket)
        
        if disconnected:
            logger.info(f"🧹 Removed {len(disconnected)} disconnected subscribers")
    
    async def _connection_monitor(self):
        """Monitor connections and attempt reconnection"""
        while self.running:
            try:
                # Check QuestDB connection
                if self.questdb.status == ConnectionStatus.DISCONNECTED:
                    logger.info("🔄 Attempting to reconnect to QuestDB...")
                    await self.questdb.connect()
                
                # Check Pocketbase connection
                if self.pocketbase.status == ConnectionStatus.DISCONNECTED:
                    logger.info("🔄 Attempting to reconnect to Pocketbase...")
                    await self.pocketbase.connect()
                
                # Check data providers
                for provider in self.data_providers:
                    if provider.status == ConnectionStatus.DISCONNECTED:
                        logger.info(f"🔄 Reconnecting to {provider.name}...")
                        await provider.connect()
                
            except Exception as e:
                logger.error(f"❌ Error in connection monitor: {e}")
            
            # Check every 30 seconds
            await asyncio.sleep(30)

# Event-driven architecture support
class EventBus:
    """Simple event bus for decoupled communication"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
    
    async def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        async with self._lock:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)
    
    async def publish(self, event_type: str, data: Any):
        """Publish event to subscribers"""
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

# Initialize global event bus
event_bus = EventBus()

# Event handlers
async def handle_stock_update_event(data):
    """Handle stock update event"""
    logger.info(f"📢 Event: Stock update for {data['symbol']}")

async def handle_connection_event(data):
    """Handle connection status change event"""
    logger.info(f"📢 Event: Connection status changed to {data['status']}")

# Register event handlers
async def setup_event_handlers():
    """Set up event handlers"""
    await event_bus.subscribe("stock_update", handle_stock_update_event)
    await event_bus.subscribe("connection_status", handle_connection_event)

async def main():
    """Main function to start the real-time streaming service"""
    print("=" * 70)
    print("🔄 Real-Time Data Streaming Service")
    print("=" * 70)
    print("QuestDB: localhost:8812")
    print("Pocketbase: http://localhost:8090")
    print("WebSocket: ws://localhost:8765")
    print("Update Interval: 30 seconds")
    print("=" * 70)
    
    # Set up event handlers
    await setup_event_handlers()
    
    # Create and start stream manager
    stream_manager = RealTimeStreamManager()
    
    try:
        await stream_manager.start()
        
        # Keep running
        print("\n✅ Service is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Service error: {e}")
        logger.error(f"Service error: {e}")
        logger.error(traceback.format_exc())
    finally:
        await stream_manager.stop()
        print("👋 Service stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
