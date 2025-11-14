#!/usr/bin/env python3
"""
Simple API server to serve real-time WIG80 data
Allows deployed frontend to access live-updating data
"""

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

class RealTimeDataAPIHandler(BaseHTTPRequestHandler):
    # Try multiple possible paths for the data file
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _possible_paths = [
        os.path.join(_base_dir, "polish-finance-platform/polish-finance-app/public/wig80_current_data.json"),
        os.path.join(_base_dir, "data/wig80_current_data.json"),
        os.path.join(_base_dir, "polish-finance-platform/polish-finance-app/dist/wig80_current_data.json"),
    ]
    
    @classmethod
    def get_data_file(cls):
        """Find the first available data file"""
        for path in cls._possible_paths:
            if os.path.exists(path):
                return path
        return cls._possible_paths[0]  # Return first as fallback
    
    def _get_cors_origin(self):
        """Get CORS origin from environment or default to *"""
        return os.environ.get('ALLOWED_ORIGIN', '*')
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Determine status code and response before sending headers
        status_code = 200
        response_data = None
        error_message = None
        
        # Serve the data file
        if path in ['/', '/data', '/wig80']:
            try:
                data_file = self.get_data_file()
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                response_data = data
                status_code = 200
            except Exception as e:
                status_code = 500
                response_data = {
                    'error': {
                        'code': 'DATA_LOAD_ERROR',
                        'message': str(e)
                    }
                }
        elif path == '/wig30':
            # Return top 30 companies (WIG30)
            try:
                data_file = self.get_data_file()
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Sort by volume (proxy for market cap) and take top 30
                companies = data.get('companies', [])
                
                def get_volume_num(vol_str):
                    try:
                        vol = str(vol_str).replace('K', '').replace('M', '').replace(',', '').replace(' ', '')
                        num = float(vol)
                        if 'M' in str(vol_str):
                            num *= 1000
                        return num
                    except:
                        return 0
                
                sorted_companies = sorted(companies, key=lambda x: get_volume_num(x.get('trading_volume', '0')), reverse=True)
                top_30 = sorted_companies[:30]
                
                wig30_data = {
                    'metadata': {
                        'collection_date': data['metadata']['collection_date'],
                        'data_source': data['metadata']['data_source'],
                        'index': 'WIG30',
                        'currency': data['metadata']['currency'],
                        'total_companies': 30
                    },
                    'companies': top_30
                }
                response_data = wig30_data
                status_code = 200
            except Exception as e:
                status_code = 500
                response_data = {
                    'error': {
                        'code': 'WIG30_ERROR',
                        'message': str(e)
                    }
                }
        else:
            # 404 for other paths
            status_code = 404
            error_message = "Not Found"
        
        # Send response with proper status code
        if error_message:
            self.send_error(status_code, error_message)
            return
        
        # Send response with headers
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        
        if response_data:
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', self._get_cors_origin())
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[API] {self.client_address[0]} - {format % args}")

def run_server(port=8000, host='0.0.0.0'):
    """Run the API server"""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, RealTimeDataAPIHandler)
    
    print(f"\n{'='*70}")
    print(f"Real-Time WIG80 Data API Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Endpoints:")
    print(f"  http://{host}:{port}/data - WIG80 (all 88 companies)")
    print(f"  http://{host}:{port}/wig80 - WIG80 (all 88 companies)")
    print(f"  http://{host}:{port}/wig30 - WIG30 (top 30 companies)")
    print(f"{'='*70}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    import sys
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    run_server(port=port, host=host)
