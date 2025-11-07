#!/usr/bin/env python3
"""
WIG80 Pocketbase Quick Start Script
===================================

This script provides a quick way to set up and launch the WIG80 Pocketbase API
with all components including database setup, sample data generation, and 
the enhanced REST API server.

Usage:
    python quick_start.py
    python quick_start.py --install-deps
    python quick_start.py --demo-data
"""

import subprocess
import sys
import os
import time
import argparse
import requests
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("="*70)
    print("🎯 WIG80 Pocketbase Quick Start")
    print("="*70)
    print("📈 Comprehensive Stock Data Analysis API")
    print("🔧 Enhanced REST API with Technical Analysis")
    print("🤖 AI-Powered Market Insights")
    print("🔗 Market Correlation Analysis")
    print("="*70)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - Compatible")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements_enhanced_api.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def generate_demo_data():
    """Generate comprehensive demo data"""
    print("\n📊 Generating demo data...")
    
    try:
        # Import the enhanced setup to generate sample data
        sys.path.append(str(Path(__file__).parent))
        from enhanced_pocketbase_setup import generate_sample_data, db_manager
        
        # Generate sample data for multiple companies
        asyncio_run = None
        try:
            import asyncio
            asyncio_run = asyncio.run
        except:
            # Fallback for environments without asyncio
            print("ℹ️ Running data generation synchronously...")
        
        if asyncio_run:
            asyncio_run(generate_sample_data())
        else:
            # Simple sync data generation for demo
            print("ℹ️ Creating basic demo data...")
            
            demo_stocks = [
                {
                    "timestamp": "2025-11-06T20:23:56",
                    "symbol": "PKN_ORLEN",
                    "open_price": 65.50,
                    "high_price": 67.20,
                    "low_price": 64.80,
                    "close_price": 66.90,
                    "volume": 1250000
                },
                {
                    "timestamp": "2025-11-06T20:23:56",
                    "symbol": "KGHM",
                    "open_price": 180.50,
                    "high_price": 185.20,
                    "low_price": 178.30,
                    "close_price": 183.75,
                    "volume": 850000
                },
                {
                    "timestamp": "2025-11-06T20:23:56",
                    "symbol": "PGE",
                    "open_price": 8.50,
                    "high_price": 8.85,
                    "low_price": 8.35,
                    "close_price": 8.72,
                    "volume": 2100000
                }
            ]
            
            for stock in demo_stocks:
                try:
                    db_manager.insert_stock_data(stock)
                except Exception as e:
                    print(f"⚠️ Could not insert {stock['symbol']}: {e}")
        
        print("✅ Demo data generated successfully")
        return True
    
    except Exception as e:
        print(f"❌ Failed to generate demo data: {e}")
        return False

def check_pocketbase():
    """Check if Pocketbase is accessible"""
    print("\n🔍 Checking Pocketbase connection...")
    
    pocketbase_url = "http://localhost:8090"
    
    try:
        response = requests.get(f"{pocketbase_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Pocketbase is running and accessible")
            return True
    except:
        pass
    
    # Try alternative endpoints
    try:
        response = requests.get(pocketbase_url, timeout=5)
        print("⚠️ Pocketbase is running but API might not be configured")
        print("💡 Make sure Pocketbase API is enabled")
        return True
    except:
        pass
    
    print("❌ Pocketbase is not accessible")
    print("\n💡 To start Pocketbase:")
    print("   1. Download from: https://pocketbase.io")
    print("   2. Run: ./pocketbase serve --http=0.0.0.0:8090")
    print("   3. Access admin panel: http://localhost:8090/_/")
    return False

def run_api_tests():
    """Run basic API tests"""
    print("\n🧪 Running API tests...")
    
    test_endpoints = [
        "http://localhost:8090/api/health",
        "http://localhost:8090/api/companies"
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(endpoint, timeout=3)
            if response.status_code == 200:
                print(f"  ✅ {endpoint} - OK")
            else:
                print(f"  ⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ❌ {endpoint} - Error: {str(e)[:50]}...")

def launch_api_server(port=8090):
    """Launch the API server"""
    print(f"\n🚀 Launching API server on port {port}...")
    
    enhanced_api_path = Path(__file__).parent / "enhanced_pocketbase_setup.py"
    
    if not enhanced_api_path.exists():
        print(f"❌ Enhanced API script not found: {enhanced_api_path}")
        return False
    
    try:
        print("📝 Server will be available at:")
        print(f"   🌐 API: http://localhost:{port}")
        print(f"   📚 Docs: /workspace/docs/pocketbase_api_documentation.md")
        print(f"   🏥 Health: http://localhost:{port}/api/health")
        print("\n⚡ Starting server... (Press Ctrl+C to stop)")
        print("="*60)
        
        subprocess.run([sys.executable, str(enhanced_api_path)])
        return True
    
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to launch server: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n" + "="*70)
    print("🎉 WIG80 Pocketbase API Setup Complete!")
    print("="*70)
    print("\n📋 Available Endpoints:")
    print("   • GET  /api/health - API health check")
    print("   • GET  /api/companies - WIG80 companies list")
    print("   • GET  /api/stocks - Stock data")
    print("   • GET  /api/technical/{symbol} - Technical analysis")
    print("   • GET  /api/ai-insights - AI insights")
    print("   • POST /api/ai-insights/generate - Generate AI analysis")
    print("   • GET  /api/correlations - Market correlations")
    print("   • GET  /api/alerts - Market alerts")
    print("   • POST /api/auth/login - User authentication")
    
    print("\n🔗 Integration Resources:")
    print("   📚 API Documentation: /workspace/docs/pocketbase_api_documentation.md")
    print("   ⚛️  React Integration: See documentation code examples")
    print("   🐍 Python Client: See documentation code examples")
    print("   📱 Vue.js Integration: See documentation code examples")
    
    print("\n💡 Quick Commands:")
    print("   # Check API health")
    print("   curl http://localhost:8090/api/health")
    print("\n   # Get companies list")
    print("   curl http://localhost:8090/api/companies")
    print("\n   # Get stock data for PKN_ORLEN")
    print("   curl http://localhost:8090/api/stocks?symbol=PKN_ORLEN")
    
    print("\n🆘 Support:")
    print("   • API Documentation: See pocketbase_api_documentation.md")
    print("   • Test the API: Run the test scripts in /workspace/code/")
    print("   • Report issues: Check logs and error messages")

def main():
    """Main quick start function"""
    parser = argparse.ArgumentParser(description='WIG80 Pocketbase Quick Start')
    parser.add_argument('--install-deps', action='store_true',
                       help='Install dependencies only')
    parser.add_argument('--demo-data', action='store_true',
                       help='Generate demo data only')
    parser.add_argument('--no-launch', action='store_true',
                       help='Skip server launch')
    parser.add_argument('--port', type=int, default=8090,
                       help='Server port (default: 8090)')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies if requested
    if args.install_deps:
        install_dependencies()
        return
    
    # Generate demo data if requested
    if args.demo_data:
        generate_demo_data()
        return
    
    # Full setup process
    print("\n🔧 Setting up WIG80 Pocketbase API...")
    
    # Check dependencies
    print("\n1️⃣ Checking dependencies...")
    if not install_dependencies():
        print("❌ Setup failed - dependency issues")
        return
    
    # Check Pocketbase
    print("\n2️⃣ Checking Pocketbase...")
    if not check_pocketbase():
        print("⚠️  Pocketbase not available - API may not work fully")
        print("   You can still test some endpoints once the API server starts")
    
    # Generate demo data
    print("\n3️⃣ Generating demo data...")
    generate_demo_data()
    
    # Show next steps
    show_next_steps()
    
    # Launch server if not skipped
    if not args.no_launch:
        print("\n4️⃣ Launching API server...")
        launch_api_server(args.port)
    else:
        print("\n4️⃣ Skipping server launch")
        print(f"   To start the server manually:")
        print(f"   python enhanced_pocketbase_setup.py")

if __name__ == "__main__":
    main()