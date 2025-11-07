#!/usr/bin/env python3
"""
WebSocket Client Example for Real-Time Streaming
Demonstrates how to connect and receive real-time stock updates
"""

import asyncio
import websockets
import json
from datetime import datetime

class RealtimeStockClient:
    """Example WebSocket client for real-time stock updates"""
    
    def __init__(self, uri='ws://localhost:8765'):
        self.uri = uri
        self.websocket = None
        self.running = False
        self.message_count = 0
        
    async def connect(self):
        """Connect to the WebSocket server"""
        try:
            print(f"🔗 Connecting to {self.uri}...")
            self.websocket = await websockets.connect(self.uri)
            self.running = True
            print("✅ Connected successfully!\n")
            
            # Start listening for messages
            await self.listen()
            
        except websockets.exceptions.WebSocketException as e:
            print(f"❌ WebSocket error: {e}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    async def listen(self):
        """Listen for messages from the server"""
        try:
            async for message in self.websocket:
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by server")
        except Exception as e:
            print(f"❌ Error listening: {e}")
    
    async def handle_message(self, message):
        """Process incoming message"""
        try:
            data = json.loads(message)
            self.message_count += 1
            
            message_type = data.get('type')
            
            if message_type == 'connection':
                self.handle_connection(data)
            elif message_type == 'stock_updates':
                await self.handle_stock_updates(data)
            elif message_type == 'status':
                self.handle_status(data)
            elif message_type == 'subscription_confirmed':
                print("📡 Subscription confirmed")
            elif message_type == 'pong':
                print("🏓 Pong received")
            elif message_type == 'error':
                print(f"❌ Server error: {data.get('message')}")
            else:
                print(f"📨 Unknown message type: {message_type}")
                print(json.dumps(data, indent=2))
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON: {message[:100]}")
        except Exception as e:
            print(f"❌ Error handling message: {e}")
    
    def handle_connection(self, data):
        """Handle connection confirmation"""
        print("🔗 Connection established:")
        print(f"   Status: {data.get('status')}")
        print(f"   Timestamp: {data.get('timestamp')}")
        print(f"   Message: {data.get('message')}")
        print()
    
    async def handle_stock_updates(self, data):
        """Handle stock updates"""
        timestamp = data.get('timestamp')
        count = data.get('count', 0)
        stocks = data.get('data', [])
        
        print(f"📊 Stock Update #{self.message_count}")
        print(f"   Time: {timestamp}")
        print(f"   Companies: {count}")
        print(f"   ─" + "─" * 50)
        
        # Display first 3 stocks
        for i, stock in enumerate(stocks[:3]):
            symbol = stock.get('symbol', 'N/A')
            price = stock.get('price', 0)
            change_pct = stock.get('change_percent', 0)
            volume = stock.get('volume', 0)
            market_status = stock.get('market_status', 'unknown')
            
            # Color coding
            status_indicator = "🟢" if change_pct >= 0 else "🔴"
            
            print(f"   {status_indicator} {symbol:12} {price:8.2f} PLN  {change_pct:+6.2f}%  "
                  f"Vol: {volume:>8,}  Market: {market_status}")
        
        if count > 3:
            print(f"   ... and {count - 3} more companies")
        
        print()
    
    def handle_status(self, data):
        """Handle status updates"""
        print("📈 System Status:")
        print(f"   QuestDB: {data.get('questdb_status', 'unknown')}")
        print(f"   Pocketbase: {data.get('pocketbase_status', 'unknown')}")
        print(f"   Data Providers: {', '.join(data.get('data_providers', []))}")
        print(f"   Active Subscribers: {data.get('subscribers', 0)}")
        print(f"   Timestamp: {data.get('timestamp')}")
        print()
    
    async def send_message(self, message_type, data=None):
        """Send message to server"""
        if not self.websocket:
            print("❌ Not connected to server")
            return
        
        message = {"type": message_type}
        if data:
            message.update(data)
        
        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
    
    async def request_status(self):
        """Request system status"""
        print("📊 Requesting system status...")
        await self.send_message("status")
    
    async def ping(self):
        """Send ping to server"""
        print("🏓 Sending ping...")
        await self.send_message("ping")
    
    async def subscribe(self):
        """Subscribe to updates"""
        print("📡 Subscribing to updates...")
        await self.send_message("subscribe")
    
    async def disconnect(self):
        """Disconnect from server"""
        if self.websocket:
            await self.websocket.close()
        self.running = False
        print("🔌 Disconnected from server")

async def interactive_mode(client):
    """Interactive mode for manual testing"""
    print("\n" + "="*70)
    print("🎮 Interactive Mode")
    print("="*70)
    print("Available commands:")
    print("  status  - Request system status")
    print("  ping    - Ping the server")
    print("  subscribe - Subscribe to updates")
    print("  count   - Show message count")
    print("  quit    - Exit")
    print("="*70 + "\n")
    
    while client.running:
        try:
            command = input("> ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'status':
                await client.request_status()
            elif command == 'ping':
                await client.ping()
            elif command == 'subscribe':
                await client.subscribe()
            elif command == 'count':
                print(f"📊 Received {client.message_count} messages\n")
            elif command == 'help':
                print("Available commands: status, ping, subscribe, count, quit")
            else:
                print(f"❌ Unknown command: {command}")
                
        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await client.disconnect()

async def demo_mode(client):
    """Demo mode - automatic testing"""
    print("\n" + "="*70)
    print("🎬 Demo Mode - Automatic Testing")
    print("="*70 + "\n")
    
    # Wait for connection
    await asyncio.sleep(1)
    
    # Request status
    await client.request_status()
    await asyncio.sleep(2)
    
    # Subscribe
    await client.subscribe()
    await asyncio.sleep(2)
    
    # Ping
    await client.ping()
    await asyncio.sleep(1)
    
    # Show message count periodically
    for i in range(3):
        await asyncio.sleep(10)
        print(f"\n📊 Received {client.message_count} messages so far...\n")
    
    print("\n✅ Demo completed. Press Ctrl+C to exit or wait for more updates.")

async def main():
    """Main function"""
    import sys
    
    print("="*70)
    print("📡 Real-Time Stock Data WebSocket Client")
    print("="*70)
    print()
    print("This client connects to the real-time streaming service")
    print("to receive live WIG80 stock data updates.")
    print()
    print(f"Server: ws://localhost:8765")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Determine mode
    mode = "interactive"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    
    # Create client
    client = RealtimeStockClient()
    
    try:
        # Connect
        await client.connect()
        
        # Run in selected mode
        if mode == "demo":
            await demo_mode(client)
        else:
            await interactive_mode(client)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client.running:
            await client.disconnect()
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
