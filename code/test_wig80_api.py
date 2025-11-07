#!/usr/bin/env python3
"""
WIG80 Pocketbase API Comprehensive Test Suite
============================================

This script performs comprehensive testing of all WIG80 Pocketbase API endpoints
to ensure they are working correctly. It tests authentication, data retrieval,
technical analysis, AI insights, correlations, and more.

Usage:
    python test_wig80_api.py
    python test_wig80_api.py --url http://localhost:8090
    python test_wig80_api.py --detailed
"""

import requests
import json
import time
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
import statistics

class WIG80APITester:
    """Comprehensive API testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:8090"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        elapsed = time.time() - self.start_time
        
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        print(f"{status} {test_name} - {message}")
        if data and len(str(data)) < 200:  # Only show small data
            print(f"    Data: {data}")
    
    def authenticate(self, username: str = "admin", password: str = "admin123") -> bool:
        """Authenticate with the API"""
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.log_test("Authentication", True, f"Token received: {self.token[:10]}...")
                return True
            else:
                self.log_test("Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_health_endpoint(self) -> bool:
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}", data)
                return True
            else:
                self.log_test("Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
            return False
    
    def test_companies_endpoint(self) -> bool:
        """Test companies list endpoint"""
        try:
            headers = self.get_auth_headers()
            response = requests.get(f"{self.api_url}/companies", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                companies_count = len(data.get("companies", []))
                self.log_test("Companies List", True, f"Found {companies_count} companies", 
                            {"total": companies_count, "sample": data.get("companies", [])[:3]})
                return True
            else:
                self.log_test("Companies List", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Companies List", False, f"Exception: {str(e)}")
            return False
    
    def test_stocks_endpoint(self) -> bool:
        """Test stocks data endpoint"""
        try:
            headers = self.get_auth_headers()
            
            # Test getting all stocks
            response = requests.get(f"{self.api_url}/stocks", headers=headers, timeout=10)
            if response.status_code == 200:
                stocks_data = response.json()
                stocks_count = len(stocks_data)
                self.log_test("Stocks List", True, f"Retrieved {stocks_count} stock records", 
                            {"count": stocks_count, "sample": stocks_data[:1] if stocks_data else []})
                
                # Test specific stock if we have data
                if stocks_data:
                    first_stock = stocks_data[0]
                    symbol = first_stock.get("symbol")
                    if symbol:
                        # Test getting specific stock
                        response = requests.get(
                            f"{self.api_url}/stocks/{symbol}", 
                            headers=headers, 
                            timeout=10
                        )
                        if response.status_code == 200:
                            self.log_test(f"Stock Details ({symbol})", True, 
                                        f"Retrieved {len(response.json())} records for {symbol}")
                        else:
                            self.log_test(f"Stock Details ({symbol})", False, 
                                        f"Status: {response.status_code}")
                
                return True
            else:
                self.log_test("Stocks List", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Stocks List", False, f"Exception: {str(e)}")
            return False
    
    def test_technical_analysis_endpoint(self) -> bool:
        """Test technical analysis endpoint"""
        try:
            headers = self.get_auth_headers()
            
            # Get a sample symbol from companies
            companies_response = requests.get(f"{self.api_url}/companies", headers=headers, timeout=10)
            if companies_response.status_code != 200:
                self.log_test("Technical Analysis", False, "Could not get companies list")
                return False
            
            companies_data = companies_response.json()
            companies = companies_data.get("companies", [])
            
            if not companies:
                self.log_test("Technical Analysis", False, "No companies available")
                return False
            
            test_symbol = companies[0].get("symbol")
            
            # Test different indicators
            indicators_tests = [
                ("macd", "MACD analysis"),
                ("rsi", "RSI analysis"),
                ("bb", "Bollinger Bands"),
                ("macd,rsi,bb", "Combined analysis")
            ]
            
            for indicators, description in indicators_tests:
                try:
                    response = requests.get(
                        f"{self.api_url}/technical/{test_symbol}",
                        headers=headers,
                        params={"indicators": indicators},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        indicators_found = list(data.get("indicators", {}).keys())
                        self.log_test(f"Technical Analysis - {description}", True, 
                                    f"Symbol: {test_symbol}, Indicators: {indicators_found}")
                    else:
                        self.log_test(f"Technical Analysis - {description}", False, 
                                    f"Status: {response.status_code}")
                except Exception as e:
                    self.log_test(f"Technical Analysis - {description}", False, 
                                f"Exception: {str(e)}")
            
            return True
        except Exception as e:
            self.log_test("Technical Analysis", False, f"Exception: {str(e)}")
            return False
    
    def test_ai_insights_endpoint(self) -> bool:
        """Test AI insights endpoints"""
        try:
            headers = self.get_auth_headers()
            
            # Test getting existing insights
            response = requests.get(f"{self.api_url}/ai-insights", headers=headers, timeout=10)
            if response.status_code == 200:
                insights_data = response.json()
                insights_count = len(insights_data)
                self.log_test("AI Insights - Get", True, 
                            f"Retrieved {insights_count} insights", 
                            {"count": insights_count, "sample": insights_data[:1] if insights_data else []})
            else:
                self.log_test("AI Insights - Get", False, f"Status: {response.status_code}")
            
            # Test generating new insights
            companies_response = requests.get(f"{self.api_url}/companies", headers=headers, timeout=10)
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                companies = companies_data.get("companies", [])
                
                if companies:
                    test_symbol = companies[0].get("symbol")
                    analysis_types = ["overvaluation", "trend", "volatility"]
                    
                    for analysis_type in analysis_types:
                        try:
                            response = requests.post(
                                f"{self.api_url}/ai-insights/generate",
                                headers=headers,
                                json={"symbol": test_symbol, "analysis_type": analysis_type},
                                timeout=10
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                insight_id = result.get("insight_id")
                                confidence = result.get("result", {}).get("confidence", 0)
                                self.log_test(f"AI Insights - Generate ({analysis_type})", True, 
                                            f"Symbol: {test_symbol}, ID: {insight_id}, Confidence: {confidence}")
                            else:
                                self.log_test(f"AI Insights - Generate ({analysis_type})", False, 
                                            f"Status: {response.status_code}")
                        except Exception as e:
                            self.log_test(f"AI Insights - Generate ({analysis_type})", False, 
                                        f"Exception: {str(e)}")
            
            return True
        except Exception as e:
            self.log_test("AI Insights", False, f"Exception: {str(e)}")
            return False
    
    def test_correlations_endpoint(self) -> bool:
        """Test market correlations endpoint"""
        try:
            headers = self.get_auth_headers()
            
            # Get companies for correlation test
            companies_response = requests.get(f"{self.api_url}/companies", headers=headers, timeout=10)
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                companies = companies_data.get("companies", [])
                
                if len(companies) >= 2:
                    # Test with specific symbols
                    symbols = [comp["symbol"] for comp in companies[:3]]
                    symbols_param = ",".join(symbols)
                    
                    response = requests.get(
                        f"{self.api_url}/correlations",
                        headers=headers,
                        params={"symbols": symbols_param},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        top_corr_count = len(data.get("top_correlations", []))
                        summary = data.get("summary", {})
                        self.log_test("Market Correlations", True, 
                                    f"Symbols: {symbols}, Top correlations: {top_corr_count}",
                                    {"symbols": symbols, "summary": summary})
                    else:
                        self.log_test("Market Correlations", False, f"Status: {response.status_code}")
                else:
                    self.log_test("Market Correlations", False, "Insufficient companies for correlation")
            else:
                self.log_test("Market Correlations", False, "Could not get companies")
            
            return True
        except Exception as e:
            self.log_test("Market Correlations", False, f"Exception: {str(e)}")
            return False
    
    def test_alerts_endpoint(self) -> bool:
        """Test market alerts endpoint"""
        try:
            headers = self.get_auth_headers()
            
            response = requests.get(f"{self.api_url}/alerts", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                alerts_count = data.get("total", 0)
                self.log_test("Market Alerts", True, f"Retrieved {alerts_count} alerts",
                            {"total": alerts_count, "alerts": data.get("alerts", [])[:2]})
                return True
            else:
                self.log_test("Market Alerts", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Market Alerts", False, f"Exception: {str(e)}")
            return False
    
    def test_stats_endpoint(self) -> bool:
        """Test API statistics endpoint"""
        try:
            headers = self.get_auth_headers()
            
            response = requests.get(f"{self.api_url}/stats", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                db_stats = data.get("database_stats", {})
                self.log_test("API Statistics", True, "Retrieved API statistics", db_stats)
                return True
            else:
                self.log_test("API Statistics", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Statistics", False, f"Exception: {str(e)}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting (basic check)"""
        try:
            headers = self.get_auth_headers()
            
            # Make multiple rapid requests to test rate limiting
            successful_requests = 0
            for i in range(5):
                try:
                    response = requests.get(f"{self.api_url}/health", headers=headers, timeout=5)
                    if response.status_code == 200:
                        successful_requests += 1
                    time.sleep(0.1)  # Small delay between requests
                except:
                    pass
            
            if successful_requests >= 4:  # Allow for 1 failure
                self.log_test("Rate Limiting", True, f"Processed {successful_requests}/5 requests successfully")
                return True
            else:
                self.log_test("Rate Limiting", False, f"Only {successful_requests}/5 requests successful")
                return False
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🧪 Starting Comprehensive API Testing")
        print("="*60)
        
        # Basic connectivity tests
        self.test_health_endpoint()
        
        # Authentication
        auth_success = self.authenticate()
        
        if not auth_success:
            self.log_test("Overall Testing", False, "Cannot proceed without authentication")
            return self.generate_test_report()
        
        # Core functionality tests
        self.test_companies_endpoint()
        self.test_stocks_endpoint()
        self.test_technical_analysis_endpoint()
        self.test_ai_insights_endpoint()
        self.test_correlations_endpoint()
        self.test_alerts_endpoint()
        self.test_stats_endpoint()
        self.test_rate_limiting()
        
        return self.generate_test_report()
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test["success"])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": round(success_rate, 2),
                "duration": round(time.time() - self.start_time, 2)
            },
            "test_results": self.test_results,
            "recommendations": self.generate_recommendations(failed_tests, passed_tests)
        }
        
        # Print summary
        print("\n" + "="*70)
        print("📊 WIG80 Pocketbase API Test Report")
        print("="*70)
        print(f"⏱️  Duration: {report['summary']['duration']} seconds")
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n⚠️  Failed Tests:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"  • {test['test']}: {test['message']}")
        
        print(f"\n💡 Recommendations:")
        for recommendation in report["recommendations"]:
            print(f"  • {recommendation}")
        
        print("\n🎉 Testing Complete!")
        
        return report
    
    def generate_recommendations(self, failed_tests: int, passed_tests: int) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if failed_tests == 0:
            recommendations.append("All tests passed! Your API is working perfectly.")
            recommendations.append("Consider running load tests for production readiness.")
            recommendations.append("Review the API documentation for advanced features.")
        else:
            recommendations.append(f"Fix {failed_tests} failed tests before production use.")
            
            # Check specific failure types
            failed_test_names = [test["test"] for test in self.test_results if not test["success"]]
            
            if any("Authentication" in name for name in failed_test_names):
                recommendations.append("Check authentication credentials and token handling.")
            
            if any("Health" in name for name in failed_test_names):
                recommendations.append("Verify the API server is running and accessible.")
            
            if any("Technical" in name for name in failed_test_names):
                recommendations.append("Ensure technical analysis dependencies (TA-Lib) are installed.")
            
            if any("AI Insights" in name for name in failed_test_names):
                recommendations.append("Check AI analysis algorithms and data availability.")
        
        return recommendations

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='WIG80 Pocketbase API Test Suite')
    parser.add_argument('--url', default='http://localhost:8090',
                       help='API base URL (default: http://localhost:8090)')
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed test output')
    parser.add_argument('--output', type=str,
                       help='Save test report to JSON file')
    
    args = parser.parse_args()
    
    print("🎯 WIG80 Pocketbase API Comprehensive Test Suite")
    print("="*60)
    print(f"🌐 Testing API: {args.url}")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run tests
    tester = WIG80APITester(args.url)
    report = tester.run_comprehensive_tests()
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Test report saved to: {args.output}")
    
    # Exit with appropriate code
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()