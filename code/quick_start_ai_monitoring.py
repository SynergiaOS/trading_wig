#!/usr/bin/env python3
"""
AI Monitoring Dashboard - Quick Start Script
Author: AI Monitoring System
Date: 2025-11-06

This script provides a simple way to start the AI monitoring dashboard
with sample data for demonstration purposes.
"""

import sys
import os
import time
import logging
import argparse
from pathlib import Path

# Add the code directory to Python path
code_dir = Path(__file__).parent
sys.path.insert(0, str(code_dir))

try:
    from ai_performance_tracker import AIPerformanceTracker
    from ai_monitoring_dashboard import AIMonitoringDashboard
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required dependencies:")
    print("pip install -r ai_monitoring_requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ai_monitoring.log')
        ]
    )

def create_sample_environment():
    """Create sample environment configuration"""
    env_content = """# AI Monitoring Dashboard Configuration
# Copy this to .env and modify as needed

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
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env configuration file")
    print("   You can modify these settings as needed")

def run_demo():
    """Run the dashboard with sample data"""
    print("\n🚀 Starting AI Monitoring Dashboard Demo...")
    print("=" * 50)
    
    # Initialize components
    print("📊 Initializing Performance Tracker...")
    tracker = AIPerformanceTracker(db_path="ai_performance_demo.db")
    
    print("🌐 Initializing Dashboard...")
    dashboard = AIMonitoringDashboard(tracker, port=8080)
    
    # Create sample data
    print("🎲 Creating sample data for demonstration...")
    dashboard.create_sample_data(num_models=4, num_signals=150)
    
    print("✅ Sample data created successfully!")
    print("\n📈 Available Models:")
    for model_id, model_info in tracker.models.items():
        print(f"   - {model_id} (registered: {model_info['registered_at']:.0f})")
    
    print(f"\n💾 Database file: {tracker.db_path}")
    print(f"🌍 Dashboard URL: http://localhost:8080")
    print("\nFeatures available:")
    print("   • Real-time AI model performance monitoring")
    print("   • Spectral bias analysis visualization")
    print("   • Polish market insights and overvaluation alerts")
    print("   • Trading signal performance tracking")
    print("   • AI model health and accuracy metrics")
    print("   • Interactive charts and real-time updates")
    
    print("\n📱 Dashboard Sections:")
    print("   • Overview - System status and alerts")
    print("   • AI Models - Performance charts and metrics")
    print("   • Trading Signals - Signal performance analysis")
    print("   • Polish Market - Market insights (WIG80)")
    print("   • Spectral Bias - Bias analysis visualizations")
    
    print("\n⏰ Starting dashboard server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the dashboard
    try:
        dashboard.run(debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        sys.exit(1)

def run_production():
    """Run the dashboard for production use"""
    print("\n🏭 Starting AI Monitoring Dashboard in Production Mode...")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env configuration file found.")
        create_sample_environment()
        print("\n📝 Please review and update the .env file, then run again.")
        return
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Using default configuration.")
    
    # Read configuration
    db_path = os.getenv('AI_DB_PATH', 'ai_performance.db')
    port = int(os.getenv('DASHBOARD_PORT', '8080'))
    debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Initialize components
    print("📊 Initializing Performance Tracker...")
    tracker = AIPerformanceTracker(db_path=db_path)
    
    print("🌐 Initializing Dashboard...")
    dashboard = AIMonitoringDashboard(tracker, port=port)
    
    print(f"💾 Database: {db_path}")
    print(f"🌍 Dashboard URL: http://localhost:{port}")
    print(f"🐛 Debug Mode: {debug_mode}")
    
    if not tracker.models:
        print("⚠️  No models registered. Add models to the system before starting.")
        print("   Use tracker.register_model('model_id', config) to register models.")
        return
    
    print(f"📈 Registered Models: {len(tracker.models)}")
    for model_id in tracker.models.keys():
        print(f"   • {model_id}")
    
    print("\n⏰ Starting production dashboard...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the dashboard
    try:
        dashboard.run(debug=debug_mode)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        sys.exit(1)

def show_status():
    """Show system status"""
    print("\n🔍 AI Monitoring System Status")
    print("=" * 40)
    
    # Check database
    db_path = "ai_performance_demo.db"
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024  # KB
        print(f"📁 Demo Database: {db_path} ({size:.1f} KB)")
        
        try:
            tracker = AIPerformanceTracker(db_path=db_path)
            print(f"📊 Registered Models: {len(tracker.models)}")
            print(f"📈 Total Signals: {len(tracker.trading_signals)}")
            
            if tracker.alerts:
                print(f"🚨 Recent Alerts: {len(tracker.alerts)}")
            else:
                print("🚨 Recent Alerts: None")
                
        except Exception as e:
            print(f"❌ Error reading database: {e}")
    else:
        print("📁 Demo Database: Not found (run demo first)")
    
    # Check configuration
    if os.path.exists('.env'):
        print("⚙️  Configuration: .env file found")
    else:
        print("⚙️  Configuration: Using defaults")
    
    print("=" * 40)

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing AI Monitoring Dashboard dependencies...")
    
    requirements_file = code_dir / "ai_monitoring_requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="AI Monitoring Dashboard - Quick Start",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_start.py demo          # Run with sample data
  python quick_start.py production    # Run in production mode
  python quick_start.py status        # Show system status
  python quick_start.py install       # Install dependencies
  python quick_start.py setup         # Create configuration file
        """
    )
    
    parser.add_argument(
        'action',
        choices=['demo', 'production', 'status', 'install', 'setup'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Dashboard port (default: 8080)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    print("🤖 AI Monitoring Dashboard - Quick Start")
    print("=" * 50)
    
    if args.action == 'install':
        success = install_dependencies()
        if success:
            print("\n🎉 Installation complete! You can now run the dashboard.")
            print("   Try: python quick_start.py demo")
        else:
            print("\n❌ Installation failed. Please check the error messages above.")
            
    elif args.action == 'setup':
        create_sample_environment()
        print("\n📝 Configuration setup complete!")
        print("   Review and update the .env file as needed.")
        
    elif args.action == 'status':
        show_status()
        
    elif args.action == 'demo':
        if args.port != 8080:
            print(f"🎯 Demo mode will use port {args.port}")
        
        # Check if dependencies are available
        try:
            import flask
            import plotly
            import numpy
            import pandas
        except ImportError as e:
            print(f"❌ Missing dependencies: {e}")
            print("   Run: python quick_start.py install")
            return
        
        run_demo()
        
    elif args.action == 'production':
        if args.port != 8080:
            print(f"🎯 Production mode will use port {args.port}")
        if args.debug:
            print("🐛 Debug mode enabled")
            
        run_production()
    
    print("\n👋 Thanks for using AI Monitoring Dashboard!")

if __name__ == "__main__":
    main()