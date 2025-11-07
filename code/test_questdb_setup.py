#!/usr/bin/env python3
"""
WIG80 QuestDB Test Script
Verifies the QuestDB setup and runs comprehensive tests
"""

import asyncio
import aiohttp
import logging
import json
import sys
from datetime import datetime, timedelta
from wig80_questdb_client import QuestDBClient, WIG80_COMPANIES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuestDBTester:
    """QuestDB testing and verification"""
    
    def __init__(self, host: str = "localhost", port: int = 8812, auth: tuple = ("admin", "quest")):
        self.base_url = f"http://{host}:{port}"
        self.auth = auth
        self.session = None
        self.test_results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(*self.auth))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def test_connection(self) -> bool:
        """Test basic connection to QuestDB"""
        logger.info("🔍 Testing QuestDB connection...")
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    logger.info("✅ QuestDB connection successful")
                    self.test_results['connection'] = True
                    return True
                else:
                    logger.error(f"❌ QuestDB responded with status {response.status}")
                    self.test_results['connection'] = False
                    return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            self.test_results['connection'] = False
            return False
            
    async def test_table_creation(self) -> bool:
        """Test if all required tables exist"""
        logger.info("🔍 Testing table creation...")
        
        tables_to_check = [
            'wig80_historical',
            'ai_insights', 
            'market_correlations',
            'valuation_analysis'
        ]
        
        all_tables_exist = True
        existing_tables = []
        
        for table in tables_to_check:
            try:
                async with self.session.get(f"{self.base_url}/exec", 
                                          params={"query": f"SELECT COUNT(*) FROM {table} LIMIT 1"}) as response:
                    if response.status == 200:
                        existing_tables.append(table)
                        logger.info(f"✅ Table '{table}' exists")
                    else:
                        logger.error(f"❌ Table '{table}' not found")
                        all_tables_exist = False
            except Exception as e:
                logger.error(f"❌ Error checking table '{table}': {e}")
                all_tables_exist = False
                
        self.test_results['tables'] = all_tables_exist
        self.test_results['existing_tables'] = existing_tables
        return all_tables_exist
        
    async def test_data_insertion(self) -> bool:
        """Test data insertion with sample records"""
        logger.info("🔍 Testing data insertion...")
        
        try:
            # Insert test record into wig80_historical
            test_data = {
                'ts': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'symbol': 'TEST',
                'open': 100.0,
                'high': 105.0,
                'low': 98.0,
                'close': 102.0,
                'volume': 10000,
                'macd': 0.5,
                'rsi': 55.0,
                'bb_upper': 110.0,
                'bb_lower': 90.0
            }
            
            query = f"""
            INSERT INTO wig80_historical (ts, symbol, open, high, low, close, volume, macd, rsi, bb_upper, bb_lower)
            VALUES ('{test_data['ts']}', '{test_data['symbol']}', {test_data['open']}, {test_data['high']}, 
                    {test_data['low']}, {test_data['close']}, {test_data['volume']}, {test_data['macd']}, 
                    {test_data['rsi']}, {test_data['bb_upper']}, {test_data['bb_lower']})
            """
            
            async with self.session.get(f"{self.base_url}/exec", params={"query": query}) as response:
                if response.status == 200:
                    # Verify insertion
                    verify_query = "SELECT * FROM wig80_historical WHERE symbol = 'TEST' ORDER BY ts DESC LIMIT 1"
                    async with self.session.get(f"{self.base_url}/exec", params={"query": verify_query}) as verify_response:
                        if verify_response.status == 200:
                            data = await verify_response.json()
                            if data.get('dataset') and len(data['dataset']) > 0:
                                logger.info("✅ Data insertion successful")
                                self.test_results['insertion'] = True
                                
                                # Clean up test data
                                cleanup_query = "DELETE FROM wig80_historical WHERE symbol = 'TEST'"
                                await self.session.get(f"{self.base_url}/exec", params={"query": cleanup_query})
                                
                                return True
                                
                logger.error("❌ Data insertion test failed")
                self.test_results['insertion'] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Data insertion test error: {e}")
            self.test_results['insertion'] = False
            return False
            
    async def test_queries(self) -> bool:
        """Test various query types"""
        logger.info("🔍 Testing query performance...")
        
        test_queries = [
            {
                'name': 'Basic SELECT',
                'query': 'SELECT COUNT(*) as count FROM wig80_historical LIMIT 1'
            },
            {
                'name': 'Symbol filtering',
                'query': "SELECT symbol, COUNT(*) FROM wig80_historical WHERE symbol = 'PKN' LIMIT 1"
            },
            {
                'name': 'Time range filtering',
                'query': 'SELECT * FROM wig80_historical WHERE ts >= dateadd(day, -7, now()) LIMIT 1'
            },
            {
                'name': 'Aggregation',
                'query': 'SELECT symbol, SUM(volume) FROM wig80_historical GROUP BY symbol LIMIT 1'
            },
            {
                'name': 'Technical indicators',
                'query': 'SELECT symbol, AVG(rsi), AVG(macd) FROM wig80_historical GROUP BY symbol LIMIT 1'
            }
        ]
        
        all_queries_pass = True
        for test_query in test_queries:
            try:
                async with self.session.get(f"{self.base_url}/exec", 
                                          params={"query": test_query['query']}) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ {test_query['name']} - Query executed successfully")
                    else:
                        logger.error(f"❌ {test_query['name']} - Query failed with status {response.status}")
                        all_queries_pass = False
            except Exception as e:
                logger.error(f"❌ {test_query['name']} - Query error: {e}")
                all_queries_pass = False
                
        self.test_results['queries'] = all_queries_pass
        return all_queries_pass
        
    async def test_wig80_data(self) -> bool:
        """Test if WIG80 companies data is present"""
        logger.info("🔍 Testing WIG80 company data...")
        
        try:
            # Get unique symbols from database
            query = "SELECT DISTINCT symbol FROM wig80_historical LIMIT 100"
            async with self.session.get(f"{self.base_url}/exec", params={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    db_symbols = set()
                    if data.get('dataset'):
                        for row in data['dataset']:
                            if len(row) > 0:
                                db_symbols.add(row[0])
                    
                    expected_symbols = set(company.symbol for company in WIG80_COMPANIES)
                    missing_symbols = expected_symbols - db_symbols
                    
                    if missing_symbols:
                        logger.warning(f"⚠️  Missing symbols: {len(missing_symbols)}")
                        logger.info(f"   Found {len(db_symbols)} symbols, expected {len(expected_symbols)}")
                    else:
                        logger.info("✅ All expected WIG80 symbols found")
                        
                    self.test_results['wig80_data'] = len(db_symbols) > 0
                    self.test_results['symbol_count'] = len(db_symbols)
                    return len(db_symbols) > 0
                else:
                    logger.error("❌ Failed to query symbols")
                    self.test_results['wig80_data'] = False
                    return False
                    
        except Exception as e:
            logger.error(f"❌ WIG80 data test error: {e}")
            self.test_results['wig80_data'] = False
            return False
            
    async def test_performance(self) -> bool:
        """Test query performance"""
        logger.info("🔍 Testing query performance...")
        
        performance_tests = [
            {
                'name': 'Time range query',
                'query': 'SELECT * FROM wig80_historical WHERE ts >= dateadd(day, -30, now()) LIMIT 1000'
            },
            {
                'name': 'Aggregation query',
                'query': 'SELECT symbol, AVG(close), SUM(volume) FROM wig80_historical GROUP BY symbol'
            },
            {
                'name': 'Technical analysis',
                'query': 'SELECT symbol, AVG(rsi), AVG(macd), COUNT(*) FROM wig80_historical WHERE ts >= dateadd(day, -7, now()) GROUP BY symbol'
            }
        ]
        
        all_performance_ok = True
        for perf_test in performance_tests:
            try:
                start_time = datetime.now()
                async with self.session.get(f"{self.base_url}/exec", 
                                          params={"query": perf_test['query']}) as response:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    if response.status == 200:
                        if duration < 5.0:  # 5 second threshold
                            logger.info(f"✅ {perf_test['name']} - Completed in {duration:.2f}s")
                        else:
                            logger.warning(f"⚠️  {perf_test['name']} - Slow query: {duration:.2f}s")
                            all_performance_ok = False
                    else:
                        logger.error(f"❌ {perf_test['name']} - Query failed")
                        all_performance_ok = False
            except Exception as e:
                logger.error(f"❌ {perf_test['name']} - Performance test error: {e}")
                all_performance_ok = False
                
        self.test_results['performance'] = all_performance_ok
        return all_performance_ok
        
    async def test_web_console_access(self) -> bool:
        """Test web console accessibility"""
        logger.info("🔍 Testing web console access...")
        try:
            # Test web console endpoint
            async with self.session.get("http://localhost:9009") as response:
                if response.status in [200, 401]:  # 401 is expected with auth
                    logger.info("✅ Web console is accessible")
                    self.test_results['web_console'] = True
                    return True
                else:
                    logger.error(f"❌ Web console returned status {response.status}")
                    self.test_results['web_console'] = False
                    return False
        except Exception as e:
            logger.error(f"❌ Web console test error: {e}")
            self.test_results['web_console'] = False
            return False
            
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        logger.info("🚀 Starting comprehensive QuestDB testing...")
        logger.info("=" * 50)
        
        tests = [
            ("Connection", self.test_connection),
            ("Table Creation", self.test_table_creation),
            ("Data Insertion", self.test_data_insertion),
            ("Query Performance", self.test_queries),
            ("WIG80 Data", self.test_wig80_data),
            ("Query Performance", self.test_performance),
            ("Web Console", self.test_web_console_access)
        ]
        
        all_passed = True
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if not result:
                    all_passed = False
                logger.info("-" * 30)
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {e}")
                all_passed = False
                logger.info("-" * 30)
                
        return all_passed
        
    def generate_test_report(self) -> str:
        """Generate test report"""
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'overall_status': 'PASS' if all([
                self.test_results.get('connection', False),
                self.test_results.get('tables', False),
                self.test_results.get('insertion', False),
                self.test_results.get('queries', False)
            ]) else 'FAIL',
            'test_results': self.test_results,
            'recommendations': []
        }
        
        # Add recommendations based on results
        if not self.test_results.get('connection', False):
            report['recommendations'].append("Check QuestDB service status and network connectivity")
            
        if not self.test_results.get('tables', False):
            report['recommendations'].append("Run database setup script to create required tables")
            
        if not self.test_results.get('insertion', False):
            report['recommendations'].append("Check table schema and permissions")
            
        if self.test_results.get('symbol_count', 0) < 10:
            report['recommendations'].append("Populate database with sample WIG80 data")
            
        if not self.test_results.get('web_console', False):
            report['recommendations'].append("Check web console configuration and port accessibility")
            
        return json.dumps(report, indent=2)

async def main():
    """Main test execution"""
    logger.info("🎯 WIG80 QuestDB Test Suite")
    logger.info("Testing QuestDB setup for Polish Stock Market Analysis")
    logger.info("=" * 60)
    
    tester = QuestDBTester()
    
    async with tester:
        # Run all tests
        all_tests_passed = await tester.run_all_tests()
        
        # Generate and display report
        report = tester.generate_test_report()
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        
        if all_tests_passed:
            logger.info("🎉 ALL TESTS PASSED! QuestDB is ready for WIG80 analysis")
        else:
            logger.warning("⚠️  SOME TESTS FAILED. Check recommendations below")
            
        logger.info("\nDetailed Results:")
        print(report)
        
        # Final recommendations
        logger.info("\n💡 NEXT STEPS:")
        if all_tests_passed:
            logger.info("✅ QuestDB is properly configured and ready for use")
            logger.info("🔗 Access the web console at: http://localhost:9009")
            logger.info("📈 Start analyzing WIG80 Polish stock market data!")
        else:
            logger.info("🔧 Address the failed tests before proceeding")
            logger.info("📚 Check README_QuestDB.md for troubleshooting")
            logger.info("🛠️  Run setup script: ./setup_questdb.sh")
            
        return all_tests_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed with error: {e}")
        sys.exit(1)
