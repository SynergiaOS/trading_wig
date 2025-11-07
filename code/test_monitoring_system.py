#!/usr/bin/env python3
"""
Monitoring System Test Script
=============================

Simple test script to verify the monitoring system components work correctly.
Run this before starting the full monitoring system to ensure everything is
properly configured.

Usage:
    python /workspace/code/test_monitoring_system.py
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add the code directory to the Python path
sys.path.append('/workspace/code')

try:
    from monitoring_system import MonitoringSystem, DEFAULT_CONFIG
except ImportError as e:
    print(f"❌ Failed to import monitoring system: {e}")
    print("Make sure you're running this from the correct directory")
    sys.exit(1)

def print_test_header(name):
    """Print a test header"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print('='*60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

async def test_imports():
    """Test if all required modules can be imported"""
    print_test_header("Module Imports")
    
    try:
        import aiohttp
        print_success("aiohttp imported successfully")
    except ImportError:
        print_error("aiohttp not found - install with: pip install aiohttp")
        return False
    
    try:
        import psutil
        print_success("psutil imported successfully")
    except ImportError:
        print_error("psutil not found - install with: pip install psutil")
        return False
    
    # Test other standard library modules
    std_modules = ['asyncio', 'json', 'logging', 'sqlite3', 'smtplib', 'ssl']
    for module in std_modules:
        try:
            __import__(module)
            print_success(f"Standard library module '{module}' available")
        except ImportError:
            print_error(f"Standard library module '{module}' not available")
            return False
    
    return True

async def test_configuration():
    """Test configuration loading"""
    print_test_header("Configuration")
    
    # Test default config
    config = DEFAULT_CONFIG.copy()
    print_success("Default configuration loaded")
    
    # Check required keys
    required_keys = ['questdb_path', 'pocketbase_url', 'pocketbase_admin_email']
    for key in required_keys:
        if key in config:
            print_info(f"{key}: {config[key]}")
        else:
            print_error(f"Required configuration key missing: {key}")
            return False
    
    return True

async def test_questdb_access():
    """Test QuestDB database access"""
    print_test_header("QuestDB Database Access")
    
    questdb_path = "/workspace/code/questdb_wig80_test.db"
    
    if not os.path.exists(questdb_path):
        print_warning(f"QuestDB database not found at: {questdb_path}")
        print_info("This is expected if you haven't run the sync service yet")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(questdb_path)
        cursor = conn.execute("SELECT COUNT(*) as count FROM wig80_historical")
        count = cursor.fetchone()['count']
        conn.close()
        
        print_success(f"QuestDB database accessible with {count} records")
        return True
        
    except Exception as e:
        print_error(f"Failed to access QuestDB database: {e}")
        return False

async def test_pocketbase_connection():
    """Test Pocketbase connection"""
    print_test_header("Pocketbase Connection")
    
    pocketbase_url = "http://localhost:8090"
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{pocketbase_url}/api/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print_success("Pocketbase service is accessible")
                    return True
                else:
                    print_warning(f"Pocketbase responded with status: {response.status}")
                    return False
                    
    except Exception as e:
        print_warning(f"Pocketbase connection failed: {e}")
        print_info("This is expected if Pocketbase is not running")
        return False

async def test_system_resources():
    """Test system resource monitoring"""
    print_test_header("System Resources")
    
    try:
        import psutil
        
        # Test CPU monitoring
        cpu_percent = psutil.cpu_percent(interval=1)
        print_success(f"CPU monitoring works: {cpu_percent:.1f}%")
        
        # Test memory monitoring
        memory = psutil.virtual_memory()
        print_success(f"Memory monitoring works: {memory.percent:.1f}% used")
        
        # Test disk monitoring
        disk = psutil.disk_usage('/workspace')
        print_success(f"Disk monitoring works: {disk.percent:.1f}% used")
        
        return True
        
    except Exception as e:
        print_error(f"System resource monitoring failed: {e}")
        return False

async def test_monitoring_system_initialization():
    """Test monitoring system initialization"""
    print_test_header("Monitoring System Initialization")
    
    try:
        config = DEFAULT_CONFIG.copy()
        config['questdb_path'] = "/workspace/code/questdb_wig80_test.db"  # Use test path
        
        monitoring = MonitoringSystem(config)
        print_success("Monitoring system initialized successfully")
        
        # Test database creation
        if os.path.exists(monitoring.monitoring_db_path):
            print_success("Monitoring database created")
        else:
            print_warning("Monitoring database not created")
        
        return True
        
    except Exception as e:
        print_error(f"Monitoring system initialization failed: {e}")
        return False

async def test_health_check():
    """Test health check functionality"""
    print_test_header("Health Check")
    
    try:
        config = DEFAULT_CONFIG.copy()
        config['questdb_path'] = "/workspace/code/questdb_wig80_test.db"
        
        monitoring = MonitoringSystem(config)
        
        # Test QuestDB health check
        questdb_health = await monitoring.check_questdb_health()
        print_info(f"QuestDB health: {questdb_health.status} ({questdb_health.response_time:.3f}s)")
        
        # Test system resources health check
        system_health = await monitoring.check_system_resources()
        print_info(f"System health: {system_health.status} ({system_health.response_time:.3f}s)")
        
        print_success("Health checks completed")
        return True
        
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False

async def test_data_integrity():
    """Test data integrity validation"""
    print_test_header("Data Integrity Validation")
    
    try:
        config = DEFAULT_CONFIG.copy()
        config['questdb_path'] = "/workspace/code/questdb_wig80_test.db"
        
        monitoring = MonitoringSystem(config)
        
        # Test data integrity validation
        integrity_reports = await monitoring.validate_data_consistency()
        
        if integrity_reports:
            for report in integrity_reports:
                print_info(f"{report.collection}: {report.data_quality_score:.1%} quality score")
            print_success(f"Data integrity validation completed ({len(integrity_reports)} collections)")
        else:
            print_warning("No data integrity reports generated")
        
        return True
        
    except Exception as e:
        print_error(f"Data integrity validation failed: {e}")
        return False

async def test_directory_creation():
    """Test required directory creation"""
    print_test_header("Directory Creation")
    
    directories = [
        "/workspace/logs",
        "/workspace/backups", 
        "/workspace/monitoring"
    ]
    
    all_created = True
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
            if os.path.exists(directory):
                print_success(f"Directory ready: {directory}")
            else:
                print_error(f"Directory not created: {directory}")
                all_created = False
                
        except Exception as e:
            print_error(f"Failed to create directory {directory}: {e}")
            all_created = False
    
    return all_created

def print_test_summary(results):
    """Print test summary"""
    print_test_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if failed_tests == 0:
        print_success("All tests passed! Monitoring system is ready to use.")
        print_info("\n🚀 You can now start the monitoring system:")
        print_info("   python /workspace/code/monitoring_system.py")
        print_info("   python /workspace/code/monitoring_dashboard.py")
        print_info("\n   Or use the startup script:")
        print_info("   bash /workspace/code/start_monitoring.sh start")
    else:
        print_warning("Some tests failed. Check the output above for details.")
        print_info("\nCommon issues:")
        print_info("- Missing dependencies: pip install aiohttp psutil")
        print_info("- QuestDB database not initialized: Run the sync service first")
        print_info("- Pocketbase not running: Start Pocketbase service")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main test function"""
    print("🔍 QuestDB-Pocketbase Monitoring System Test")
    print("This script verifies that all components are properly configured.")
    
    # Run all tests
    results = {}
    
    results["imports"] = await test_imports()
    results["configuration"] = await test_configuration()
    results["directories"] = await test_directory_creation()
    results["questdb"] = await test_questdb_access()
    results["pocketbase"] = await test_pocketbase_connection()
    results["system_resources"] = await test_system_resources()
    results["monitoring_init"] = await test_monitoring_system_initialization()
    results["health_check"] = await test_health_check()
    results["data_integrity"] = await test_data_integrity()
    
    # Print summary
    print_test_summary(results)
    
    # Return exit code
    if all(results.values()):
        return 0
    else:
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        sys.exit(1)