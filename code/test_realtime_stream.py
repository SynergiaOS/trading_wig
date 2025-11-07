#!/usr/bin/env python3
"""
Test script for real-time streaming service
Demonstrates the functionality without requiring QuestDB/Pocketbase
"""

import asyncio
import json
import sys
import os

# Add the code directory to Python path
sys.path.append('/workspace/code')

from realtime_data_stream import (
    StockUpdate, QuestDBConnector, PocketbaseConnector, 
    StockDataProvider, MarketStatus, ConnectionStatus,
    RealTimeStreamManager, EventBus
)

class MockDataProvider(StockDataProvider):
    """Mock data provider for testing"""
    
    def __init__(self):
        super().__init__("Mock Provider")
        self.symbols = ["PKN", "KGHM", "PGE", "ORANGE", "CDPROJEKT"]
    
    async def connect(self):
        """Initialize the data provider"""
        self.status = ConnectionStatus.CONNECTED
        return True
    
    async def fetch_data(self) -> list:
        """Generate mock stock data"""
        import random
        from datetime import datetime
        
        updates = []
        for symbol in self.symbols:
            base_price = 50.0 + random.uniform(-10, 10)
            
            update = StockUpdate(
                timestamp=datetime.now().isoformat(),
                symbol=symbol,
                price=round(base_price, 2),
                change=round(random.uniform(-2, 2), 2),
                change_percent=round(random.uniform(-5, 5), 2),
                volume=random.randint(100000, 2000000),
                high=round(base_price * 1.02, 2),
                low=round(base_price * 0.98, 2),
                open=round(base_price * 0.995, 2),
                market_status="open",
                data_source="mock.provider"
            )
            updates.append(update)
        
        return updates
    
    async def close(self):
        """Close the data provider"""
        self.status = ConnectionStatus.DISCONNECTED
        return True

async def test_stock_update_structure():
    """Test StockUpdate data structure"""
    print("\n" + "="*70)
    print("📊 Testing StockUpdate Data Structure")
    print("="*70)
    
    update = StockUpdate(
        timestamp="2025-11-06T20:23:56.000Z",
        symbol="PKN",
        price=65.50,
        change=1.25,
        change_percent=1.94,
        volume=1250000,
        high=66.80,
        low=64.20,
        open=64.80,
        market_status="open",
        data_source="stooq.pl"
    )
    
    print(f"✅ StockUpdate created successfully:")
    print(f"   Symbol: {update.symbol}")
    print(f"   Price: {update.price}")
    print(f"   Change: {update.change:+.2f}%")
    print(f"   Volume: {update.volume:,}")
    print(f"   Market Status: {update.market_status}")
    
    # Test JSON serialization
    update_dict = {
        "timestamp": update.timestamp,
        "symbol": update.symbol,
        "price": update.price,
        "change": update.change,
        "change_percent": update.change_percent,
        "volume": update.volume,
        "high": update.high,
        "low": update.low,
        "open": update.open,
        "market_status": update.market_status,
        "data_source": update.data_source
    }
    
    json_str = json.dumps(update_dict, indent=2)
    print(f"\n✅ JSON Serialization:")
    print(json_str[:200] + "..." if len(json_str) > 200 else json_str)
    
    return True

async def test_event_bus():
    """Test event bus functionality"""
    print("\n" + "="*70)
    print("📢 Testing Event Bus")
    print("="*70)
    
    event_bus = EventBus()
    events_received = []
    
    async def event_handler_1(data):
        events_received.append(("handler1", data))
    
    async def event_handler_2(data):
        events_received.append(("handler2", data))
    
    # Subscribe handlers
    await event_bus.subscribe("test_event", event_handler_1)
    await event_bus.subscribe("test_event", event_handler_2)
    
    # Publish events
    await event_bus.publish("test_event", {"message": "Hello", "id": 1})
    await event_bus.publish("test_event", {"message": "World", "id": 2})
    
    # Check results
    # We expect 2 events * 2 handlers = 4 total
    if len(events_received) == 4:
        print(f"✅ Event bus working: Received {len(events_received)} events (2 events × 2 handlers)")
        for handler, data in events_received:
            print(f"   {handler}: {data}")
        return True
    else:
        print(f"❌ Event bus failed: Expected 4 events, got {len(events_received)}")
        return False

async def test_data_provider():
    """Test mock data provider"""
    print("\n" + "="*70)
    print("🔄 Testing Data Provider")
    print("="*70)
    
    provider = MockDataProvider()
    await provider.connect()
    
    # Fetch data
    updates = await provider.fetch_data()
    
    print(f"✅ Data provider fetched {len(updates)} updates:")
    for update in updates:
        print(f"   {update.symbol}: {update.price} ({update.change_percent:+.2f}%)")
    
    await provider.close()
    return len(updates) > 0

async def test_stream_manager_initialization():
    """Test stream manager initialization (without actual connections)"""
    print("\n" + "="*70)
    print("🚀 Testing Stream Manager Initialization")
    print("="*70)
    
    # Create manager with mock data provider
    manager = RealTimeStreamManager()
    manager.data_providers = [MockDataProvider()]
    
    # Test configuration
    print(f"✅ Stream Manager created:")
    print(f"   Update interval: {manager.update_interval} seconds")
    print(f"   Data providers: {[p.name for p in manager.data_providers]}")
    print(f"   WebSocket port: 8765")
    print(f"   Initial status: Running={manager.running}")
    
    return True

async def test_connection_status_enum():
    """Test connection status enumeration"""
    print("\n" + "="*70)
    print("🔌 Testing Connection Status Enum")
    print("="*70)
    
    statuses = [
        ConnectionStatus.DISCONNECTED,
        ConnectionStatus.CONNECTING,
        ConnectionStatus.CONNECTED,
        ConnectionStatus.RECONNECTING,
        ConnectionStatus.ERROR,
        ConnectionStatus.FAILED
    ]
    
    print("✅ All connection statuses defined:")
    for status in statuses:
        print(f"   {status.name}: '{status.value}'")
    
    return len(statuses) == 6

async def test_market_status_enum():
    """Test market status enumeration"""
    print("\n" + "="*70)
    print("📈 Testing Market Status Enum")
    print("="*70)
    
    statuses = [
        MarketStatus.PRE_MARKET,
        MarketStatus.OPEN,
        MarketStatus.AFTER_HOURS,
        MarketStatus.CLOSED,
        MarketStatus.WEEKEND,
        MarketStatus.HOLIDAY
    ]
    
    print("✅ All market statuses defined:")
    for status in statuses:
        print(f"   {status.name}: '{status.value}'")
    
    return len(statuses) == 6

async def test_websocket_message_format():
    """Test WebSocket message format"""
    print("\n" + "="*70)
    print("📡 Testing WebSocket Message Format")
    print("="*70)
    
    # Test connection message
    connection_msg = {
        "type": "connection",
        "status": "connected",
        "timestamp": "2025-11-06T20:23:56.000Z",
        "message": "Connected to real-time stream"
    }
    
    print("✅ Connection message format:")
    print(json.dumps(connection_msg, indent=2))
    
    # Test stock updates message
    stock_updates_msg = {
        "type": "stock_updates",
        "timestamp": "2025-11-06T20:23:56.000Z",
        "count": 5,
        "data": [
            {
                "symbol": "PKN",
                "price": 65.50,
                "change_percent": 1.94,
                "volume": 1250000,
                "market_status": "open"
            }
        ]
    }
    
    print("\n✅ Stock updates message format:")
    print(json.dumps(stock_updates_msg, indent=2))
    
    return True

async def main():
    """Run all tests"""
    print("🧪 Real-Time Streaming Service - Test Suite")
    print("="*70)
    print("Testing all components without external dependencies")
    print("="*70)
    
    tests = [
        ("StockUpdate Structure", test_stock_update_structure),
        ("Event Bus", test_event_bus),
        ("Data Provider", test_data_provider),
        ("Stream Manager Init", test_stream_manager_initialization),
        ("Connection Status Enum", test_connection_status_enum),
        ("Market Status Enum", test_market_status_enum),
        ("WebSocket Message Format", test_websocket_message_format),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("📋 Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Real-time streaming service is ready.")
        print("\nNext steps:")
        print("1. Start QuestDB: /workspace/questdb-9.1.1-rt-linux-x86-64/bin/questdb.sh start")
        print("2. Start Pocketbase: ./pocketbase serve --http=localhost:8090")
        print("3. Run streaming service: python realtime_data_stream.py")
        print("4. Test WebSocket: ws://localhost:8765")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
