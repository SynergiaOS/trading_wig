#!/usr/bin/env python3
"""
Analysis API Server - Serves AI analysis results for clients
Provides endpoints for displaying analysis results in the frontend
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Add code directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class AnalysisAPIHandler(BaseHTTPRequestHandler):
    """Handler for analysis API endpoints"""
    
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _data_paths = [
        os.path.join(_base_dir, "data/wig80_current_data.json"),
        os.path.join(_base_dir, "polish-finance-platform/polish-finance-app/public/wig80_current_data.json"),
    ]
    
    @classmethod
    def get_data_file(cls):
        """Find the first available data file"""
        for path in cls._data_paths:
            if os.path.exists(path):
                return path
        return cls._data_paths[0]
    
    def _load_wig80_data(self):
        """Load WIG80 data"""
        try:
            data_file = self.get_data_file()
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {'error': str(e), 'companies': []}
    
    def _generate_analysis(self, company):
        """Generate analysis for a single company"""
        change = company.get('change_percent', 0)
        pe = company.get('pe_ratio')
        pb = company.get('pb_ratio')
        price = company.get('current_price', 0)
        
        # Calculate scores
        value_score = 0
        growth_score = 0
        momentum_score = 0
        
        # Value analysis
        if pe and pe > 0:
            if pe < 15:
                value_score += 30
            elif pe < 25:
                value_score += 20
            else:
                value_score += 10
        
        if pb and pb > 0:
            if pb < 1.5:
                value_score += 30
            elif pb < 2.5:
                value_score += 20
            else:
                value_score += 10
        
        # Growth analysis
        if change > 5:
            growth_score = 40
        elif change > 2:
            growth_score = 30
        elif change > 0:
            growth_score = 20
        elif change > -2:
            growth_score = 10
        else:
            growth_score = 0
        
        # Momentum analysis
        if change > 3:
            momentum_score = 30
        elif change > 1:
            momentum_score = 20
        elif change > -1:
            momentum_score = 10
        else:
            momentum_score = 0
        
        overall_score = (value_score + growth_score + momentum_score) / 3
        
        # Generate recommendation
        if overall_score >= 70:
            recommendation = "STRONG_BUY"
            sentiment = "very_bullish"
        elif overall_score >= 55:
            recommendation = "BUY"
            sentiment = "bullish"
        elif overall_score >= 40:
            recommendation = "HOLD"
            sentiment = "neutral"
        elif overall_score >= 25:
            recommendation = "SELL"
            sentiment = "bearish"
        else:
            recommendation = "STRONG_SELL"
            sentiment = "very_bearish"
        
        # Risk assessment
        volatility = abs(change)
        if volatility < 2:
            risk_level = "low"
        elif volatility < 5:
            risk_level = "medium"
        elif volatility < 10:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return {
            "symbol": company.get('symbol', ''),
            "company_name": company.get('company_name', ''),
            "current_price": price,
            "change_percent": change,
            "analysis": {
                "value_score": round(value_score, 1),
                "growth_score": round(growth_score, 1),
                "momentum_score": round(momentum_score, 1),
                "overall_score": round(overall_score, 1),
                "recommendation": recommendation,
                "sentiment": sentiment,
                "risk_level": risk_level,
                "confidence": min(95, max(60, overall_score + 20))
            },
            "metrics": {
                "pe_ratio": pe,
                "pb_ratio": pb,
                "volatility": round(volatility, 2),
                "price_momentum": "up" if change > 0 else "down"
            },
            "insights": self._generate_insights(company, overall_score, recommendation)
        }
    
    def _generate_insights(self, company, score, recommendation):
        """Generate human-readable insights"""
        insights = []
        change = company.get('change_percent', 0)
        pe = company.get('pe_ratio')
        pb = company.get('pb_ratio')
        
        if change > 5:
            insights.append(f"Silny wzrost o {change:.2f}% - pozytywny momentum")
        elif change > 2:
            insights.append(f"Umiarkowany wzrost o {change:.2f}%")
        elif change < -5:
            insights.append(f"Znaczny spadek o {abs(change):.2f}% - wymaga uwagi")
        
        if pe and pe < 15:
            insights.append("Niska wycena P/E - potencjalna okazja wartościowa")
        elif pe and pe > 30:
            insights.append("Wysoka wycena P/E - możliwe przeszacowanie")
        
        if pb and pb < 1.5:
            insights.append("Niski wskaźnik P/B - atrakcyjna wycena")
        
        if score >= 70:
            insights.append("Wysoki ogólny wynik - silna rekomendacja kupna")
        elif score < 30:
            insights.append("Niski ogólny wynik - rozważ sprzedaż")
        
        return insights
    
    def _get_cors_origin(self):
        """Get CORS origin from environment or default to *"""
        return os.environ.get('ALLOWED_ORIGIN', '*')
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Determine status code and response before sending headers
        status_code = 200
        response = None
        error_message = None
        
        try:
            if path == '/api/analysis' or path == '/api/analysis/':
                # Get all companies analysis
                data = self._load_wig80_data()
                companies = data.get('companies', [])
                
                analyses = []
                for company in companies:
                    analysis = self._generate_analysis(company)
                    analyses.append(analysis)
                
                # Sort by overall score
                analyses.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)
                
                response = {
                    "timestamp": datetime.now().isoformat(),
                    "total_analyses": len(analyses),
                    "analyses": analyses
                }
                status_code = 200
                
            elif path == '/api/analysis/top' or path == '/api/analysis/top/':
                # Get top opportunities
                query_params = parse_qs(parsed_path.query)
                limit = int(query_params.get('limit', ['10'])[0])
                
                data = self._load_wig80_data()
                companies = data.get('companies', [])
                
                analyses = []
                for company in companies:
                    analysis = self._generate_analysis(company)
                    analyses.append(analysis)
                
                # Sort by overall score and get top
                analyses.sort(key=lambda x: x['analysis']['overall_score'], reverse=True)
                top_analyses = analyses[:limit]
                
                response = {
                    "timestamp": datetime.now().isoformat(),
                    "limit": limit,
                    "analyses": top_analyses
                }
                status_code = 200
                
            elif path == '/api/analysis/patterns' or path == '/api/analysis/patterns/':
                # Get all companies with detected patterns
                try:
                    from telegram_alerts import PatternDetector
                    
                    data = self._load_wig80_data()
                    companies = data.get('companies', [])
                    
                    pattern_detector = PatternDetector()
                    companies_with_patterns = []
                    
                    for company in companies:
                        try:
                            patterns = pattern_detector.detect_patterns(company)
                            if patterns:
                                analysis = self._generate_analysis(company)
                                analysis['patterns'] = patterns
                                companies_with_patterns.append(analysis)
                        except Exception as e:
                            print(f"Error processing {company.get('symbol', 'unknown')}: {e}")
                            continue
                    
                    # Sort by pattern strength
                    companies_with_patterns.sort(
                        key=lambda x: max([p.get('strength', 0) for p in x.get('patterns', [])] or [0]),
                        reverse=True
                    )
                    
                    response = {
                        "timestamp": datetime.now().isoformat(),
                        "total_with_patterns": len(companies_with_patterns),
                        "companies": companies_with_patterns
                    }
                    status_code = 200
                except Exception as e:
                    status_code = 500
                    response = {
                        "error": {
                            "code": "PATTERNS_ERROR",
                            "message": str(e)
                        },
                        "timestamp": datetime.now().isoformat(),
                        "total_with_patterns": 0,
                        "companies": []
                    }
                
            elif path.startswith('/api/analysis/'):
                # Get analysis for specific symbol (but not /top or /patterns)
                symbol = path.split('/')[-1].upper()
                if symbol in ['TOP', 'PATTERNS']:
                    status_code = 404
                    error_message = f"Use /api/analysis/{symbol.lower()} endpoint"
                else:
                    data = self._load_wig80_data()
                    companies = data.get('companies', [])
                    
                    company = next((c for c in companies if c.get('symbol', '').upper() == symbol), None)
                    
                    if company:
                        analysis = self._generate_analysis(company)
                        # Add patterns
                        try:
                            from telegram_alerts import PatternDetector
                            pattern_detector = PatternDetector()
                            patterns = pattern_detector.detect_patterns(company)
                            analysis['patterns'] = patterns
                        except Exception as e:
                            print(f"Error detecting patterns for {symbol}: {e}")
                            analysis['patterns'] = []
                        
                        response = {
                            "timestamp": datetime.now().isoformat(),
                            "analysis": analysis
                        }
                        status_code = 200
                    else:
                        status_code = 404
                        error_message = "Company not found"
            else:
                status_code = 404
                error_message = "Not Found"
            
            # Send response with proper status code
            if error_message:
                self.send_error(status_code, error_message)
                return
            
            # Send success response with headers
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if response:
                self.wfile.write(json.dumps(response, ensure_ascii=False, indent=2).encode('utf-8'))
            
        except Exception as e:
            # Send error response
            status_code = 500
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            error_response = {
                "error": {
                    "code": "ANALYSIS_ERROR",
                    "message": str(e)
                },
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[Analysis API] {self.client_address[0]} - {format % args}")

def run_server(port=8001, host='0.0.0.0'):
    """Run the Analysis API server"""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, AnalysisAPIHandler)
    
    print(f"\n{'='*70}")
    print(f"AI Analysis API Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Endpoints:")
    print(f"  http://{host}:{port}/api/analysis - All analyses")
    print(f"  http://{host}:{port}/api/analysis/{'{symbol}'} - Single company")
    print(f"  http://{host}:{port}/api/analysis/top?limit=10 - Top opportunities")
    print(f"{'='*70}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    import sys
    port = int(os.environ.get('PORT', 8001))
    host = os.environ.get('HOST', '0.0.0.0')
    run_server(port=port, host=host)

