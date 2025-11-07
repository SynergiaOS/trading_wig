#!/usr/bin/env python3
"""
Telegram Alerts System for Polish Finance Platform
Sends alerts to Telegram when price thresholds are reached or recommendations change
"""

import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class TelegramBot:
    """Telegram Bot for sending alerts"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_pattern_alert(self, symbol: str, company_name: str, current_price: float, 
                           change_percent: float, pattern: Dict, recommendation: str, score: float) -> bool:
        """Send formatted alert with pattern information"""
        pattern_name = pattern.get('pattern_name', 'Unknown Pattern')
        pattern_direction = pattern.get('direction', 'neutral')
        pattern_strength = pattern.get('strength', 0)
        pattern_confidence = pattern.get('confidence', 0)
        
        # Emoji based on pattern direction
        if pattern_direction == 'bullish':
            emoji = "📈"
            direction_emoji = "🟢"
        elif pattern_direction == 'bearish':
            emoji = "📉"
            direction_emoji = "🔴"
        else:
            emoji = "📊"
            direction_emoji = "🟡"
        
        # Pattern type emoji
        pattern_emoji = "🚩" if "flag" in pattern_name.lower() else \
                       "🔺" if "triangle" in pattern_name.lower() else \
                       "📐" if "channel" in pattern_name.lower() else \
                       "⚡" if "breakout" in pattern_name.lower() else \
                       "📈" if "momentum" in pattern_name.lower() else "📊"
        
        message = f"""
{emoji} <b>WZORZEC TECHNICZNY WIG80</b> {direction_emoji}

<b>{symbol}</b> - {company_name}
💰 Cena: <b>{current_price:.2f} PLN</b>
📊 Zmiana: <b>{change_percent:+.2f}%</b>

{pattern_emoji} <b>Wzorzec: {pattern_name}</b>
📈 Kierunek: <b>{pattern_direction.upper()}</b>
💪 Siła: <b>{pattern_strength*100:.0f}%</b>
🎯 Pewność: <b>{pattern_confidence*100:.0f}%</b>

📈 Rekomendacja: <b>{recommendation}</b>
⭐ Score: <b>{score:.1f}/100</b>

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def send_top_opportunities(self, analyses: List[Dict], limit: int = 5) -> bool:
        """Send top opportunities summary"""
        message = f"🎯 <b>TOP {limit} OKAZJI WIG80</b>\n\n"
        
        for i, analysis in enumerate(analyses[:limit], 1):
            symbol = analysis.get('symbol', '')
            company = analysis.get('company_name', '')
            price = analysis.get('current_price', 0)
            change = analysis.get('change_percent', 0)
            rec = analysis.get('analysis', {}).get('recommendation', 'HOLD')
            score = analysis.get('analysis', {}).get('overall_score', 0)
            
            emoji = "🟢" if rec in ["STRONG_BUY", "BUY"] else "🟡" if rec == "HOLD" else "🔴"
            
            message += f"{i}. {emoji} <b>{symbol}</b> - {company}\n"
            message += f"   💰 {price:.2f} PLN ({change:+.2f}%) | {rec} | ⭐{score:.1f}\n\n"
        
        message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_message(message)

class PatternDetector:
    """Detect technical patterns in stock data"""
    
    @staticmethod
    def detect_patterns(company: Dict) -> List[Dict]:
        """Detect technical patterns for a company"""
        patterns = []
        change = company.get('change_percent', 0)
        price = company.get('current_price', 0)
        high = company.get('high_price', price)
        low = company.get('low_price', price)
        volume = company.get('trading_volume', '0')
        
        # Convert volume to number
        try:
            volume_num = float(str(volume).replace('K', '').replace('M', '').replace(',', ''))
            if 'M' in str(volume):
                volume_num *= 1000
        except:
            volume_num = 0
        
        # 1. Trend wzrostowy (Uptrend)
        if change > 5 and price > low * 1.02:
            patterns.append({
                'pattern_name': 'Trend Wzrostowy',
                'direction': 'bullish',
                'strength': min(abs(change) / 15, 1.0),
                'confidence': 0.75,
                'duration': 'short',
                'key_levels': {
                    'support': low,
                    'resistance': high,
                    'current': price
                },
                'probability': min(abs(change) / 20, 1.0)
            })
        
        # 2. Trend spadkowy (Downtrend)
        if change < -5 and price < high * 0.98:
            patterns.append({
                'pattern_name': 'Trend Spadkowy',
                'direction': 'bearish',
                'strength': min(abs(change) / 15, 1.0),
                'confidence': 0.75,
                'duration': 'short',
                'key_levels': {
                    'support': low,
                    'resistance': high,
                    'current': price
                },
                'probability': min(abs(change) / 20, 1.0)
            })
        
        # 3. Flaga (Flag Pattern) - konsolidacja po silnym ruchu
        range_pct = ((high - low) / low) * 100 if low > 0 else 0
        if abs(change) > 3 and range_pct < 5 and volume_num > 100:
            patterns.append({
                'pattern_name': 'Flaga',
                'direction': 'bullish' if change > 0 else 'bearish',
                'strength': 0.7,
                'confidence': 0.65,
                'duration': 'short',
                'key_levels': {
                    'flag_top': high,
                    'flag_bottom': low,
                    'breakout_target': price * (1.1 if change > 0 else 0.9)
                },
                'probability': 0.6
            })
        
        # 4. Trójkąt wzrostowy (Ascending Triangle)
        if change > 2 and price > low * 1.015 and high - low < price * 0.03:
            patterns.append({
                'pattern_name': 'Trójkąt Wzrostowy',
                'direction': 'bullish',
                'strength': 0.75,
                'confidence': 0.7,
                'duration': 'medium',
                'key_levels': {
                    'support': low,
                    'resistance': high,
                    'breakout_target': high * 1.05
                },
                'probability': 0.65
            })
        
        # 5. Trójkąt spadkowy (Descending Triangle)
        if change < -2 and price < high * 0.985 and high - low < price * 0.03:
            patterns.append({
                'pattern_name': 'Trójkąt Spadkowy',
                'direction': 'bearish',
                'strength': 0.75,
                'confidence': 0.7,
                'duration': 'medium',
                'key_levels': {
                    'support': low,
                    'resistance': high,
                    'breakdown_target': low * 0.95
                },
                'probability': 0.65
            })
        
        # 6. Kanał (Channel)
        if abs(change) < 3 and range_pct > 2 and range_pct < 8:
            patterns.append({
                'pattern_name': 'Kanał Poziomy',
                'direction': 'neutral',
                'strength': 0.6,
                'confidence': 0.6,
                'duration': 'medium',
                'key_levels': {
                    'upper_channel': high,
                    'lower_channel': low,
                    'middle': price
                },
                'probability': 0.5
            })
        
        # 7. Breakout (Wyłamanie)
        if abs(change) > 7 and volume_num > 500:
            patterns.append({
                'pattern_name': 'Breakout',
                'direction': 'bullish' if change > 0 else 'bearish',
                'strength': min(abs(change) / 12, 1.0),
                'confidence': 0.8,
                'duration': 'short',
                'key_levels': {
                    'breakout_level': price,
                    'target': price * (1.15 if change > 0 else 0.85),
                    'stop_loss': price * (0.95 if change > 0 else 1.05)
                },
                'probability': 0.7
            })
        
        # 8. Momentum (Pęd)
        if abs(change) > 8:
            patterns.append({
                'pattern_name': 'Silny Momentum',
                'direction': 'bullish' if change > 0 else 'bearish',
                'strength': min(abs(change) / 15, 1.0),
                'confidence': 0.75,
                'duration': 'short',
                'key_levels': {
                    'momentum_level': price,
                    'extension_target': price * (1.2 if change > 0 else 0.8)
                },
                'probability': 0.65
            })
        
        return patterns

class AlertMonitor:
    """Monitor price changes and send alerts only for technical patterns"""
    
    def __init__(self, telegram_bot: TelegramBot, data_api_url: str = "http://localhost:8000/data",
                 analysis_api_url: str = "http://localhost:8001/api/analysis"):
        self.telegram_bot = telegram_bot
        self.data_api_url = data_api_url
        self.analysis_api_url = analysis_api_url
        self.last_prices = {}
        self.pattern_detector = PatternDetector()
        self.detected_patterns = {}  # Track detected patterns to avoid duplicates
        self.running = False
        
    def fetch_data(self) -> Optional[Dict]:
        """Fetch current market data"""
        try:
            response = requests.get(self.data_api_url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching data: {e}")
        return None
    
    def fetch_analysis(self, symbol: str) -> Optional[Dict]:
        """Fetch analysis for symbol"""
        try:
            url = f"{self.analysis_api_url}/{symbol}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching analysis: {e}")
        return None
    
    def check_alerts(self):
        """Check for technical patterns and send alerts only for detected patterns"""
        data = self.fetch_data()
        if not data or 'companies' not in data:
            return
        
        for company in data.get('companies', []):
            symbol = company.get('symbol', '')
            current_price = company.get('current_price', 0)
            change_percent = company.get('change_percent', 0)
            
            # Detect technical patterns
            patterns = self.pattern_detector.detect_patterns(company)
            
            # Only send alerts if patterns detected
            if patterns:
                # Get analysis
                analysis_data = self.fetch_analysis(symbol)
                if analysis_data and 'analysis' in analysis_data:
                    analysis = analysis_data['analysis']
                    recommendation = analysis.get('analysis', {}).get('recommendation', 'HOLD')
                    score = analysis.get('analysis', {}).get('overall_score', 0)
                    
                    # Send alert for each detected pattern
                    for pattern in patterns:
                        # Check if we already sent alert for this pattern (avoid duplicates)
                        pattern_key = f"{symbol}_{pattern['pattern_name']}"
                        if pattern_key not in self.detected_patterns:
                            self.telegram_bot.send_pattern_alert(
                                symbol=symbol,
                                company_name=company.get('company_name', ''),
                                current_price=current_price,
                                change_percent=change_percent,
                                pattern=pattern,
                                recommendation=recommendation,
                                score=score
                            )
                            self.detected_patterns[pattern_key] = datetime.now()
                            time.sleep(1)  # Rate limiting
                    
                    # Clean old patterns (older than 1 hour)
                    cutoff_time = datetime.now().timestamp() - 3600
                    self.detected_patterns = {
                        k: v for k, v in self.detected_patterns.items() 
                        if v.timestamp() > cutoff_time
                    }
    
    def send_daily_summary(self):
        """Send daily summary of top opportunities"""
        try:
            url = f"{self.analysis_api_url}/top?limit=5"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                analyses = data.get('analyses', [])
                if analyses:
                    self.telegram_bot.send_top_opportunities(analyses, limit=5)
        except Exception as e:
            print(f"Error sending daily summary: {e}")
    
    def start_monitoring(self, interval: int = 60):
        """Start monitoring loop"""
        self.running = True
        print(f"🔔 Starting alert monitoring (checking every {interval}s)")
        
        while self.running:
            try:
                self.check_alerts()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)

class TelegramAlertsAPIHandler(BaseHTTPRequestHandler):
    """API handler for Telegram alerts"""
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            if path == '/api/telegram/send':
                # Send custom message
                bot_token = data.get('bot_token') or os.environ.get('TELEGRAM_BOT_TOKEN')
                chat_id = data.get('chat_id') or os.environ.get('TELEGRAM_CHAT_ID')
                message = data.get('message', '')
                
                if not bot_token or not chat_id:
                    response = {"error": "Missing bot_token or chat_id"}
                else:
                    bot = TelegramBot(bot_token, chat_id)
                    success = bot.send_message(message)
                    response = {"success": success, "message": "Message sent" if success else "Failed to send"}
                    
            elif path == '/api/telegram/alert':
                # Send alert for symbol (only if patterns detected)
                bot_token = data.get('bot_token') or os.environ.get('TELEGRAM_BOT_TOKEN')
                chat_id = data.get('chat_id') or os.environ.get('TELEGRAM_CHAT_ID')
                symbol = data.get('symbol')
                
                if not bot_token or not chat_id or not symbol:
                    response = {"error": "Missing required parameters"}
                else:
                    # Fetch company data
                    data_url = "http://localhost:8000/data"
                    data_resp = requests.get(data_url, timeout=5)
                    
                    if data_resp.status_code == 200:
                        market_data = data_resp.json()
                        companies = market_data.get('companies', [])
                        company = next((c for c in companies if c.get('symbol', '').upper() == symbol.upper()), None)
                        
                        if company:
                            # Detect patterns
                            pattern_detector = PatternDetector()
                            patterns = pattern_detector.detect_patterns(company)
                            
                            if patterns:
                                # Fetch analysis
                                analysis_url = f"http://localhost:8001/api/analysis/{symbol}"
                                analysis_resp = requests.get(analysis_url, timeout=5)
                                
                                if analysis_resp.status_code == 200:
                                    analysis_data = analysis_resp.json().get('analysis', {})
                                    bot = TelegramBot(bot_token, chat_id)
                                    
                                    # Send alert for first pattern
                                    pattern = patterns[0]
                                    success = bot.send_pattern_alert(
                                        symbol=analysis_data.get('symbol', ''),
                                        company_name=analysis_data.get('company_name', ''),
                                        current_price=analysis_data.get('current_price', 0),
                                        change_percent=analysis_data.get('change_percent', 0),
                                        pattern=pattern,
                                        recommendation=analysis_data.get('analysis', {}).get('recommendation', 'HOLD'),
                                        score=analysis_data.get('analysis', {}).get('overall_score', 0)
                                    )
                                    response = {
                                        "success": success,
                                        "pattern": pattern['pattern_name'],
                                        "patterns_detected": len(patterns)
                                    }
                                else:
                                    response = {"error": "Analysis not found"}
                            else:
                                response = {
                                    "success": False,
                                    "message": "No technical patterns detected for this symbol",
                                    "patterns_detected": 0
                                }
                        else:
                            response = {"error": "Company not found"}
                    else:
                        response = {"error": "Failed to fetch market data"}
                        
            elif path == '/api/telegram/top':
                # Send top opportunities with patterns only
                bot_token = data.get('bot_token') or os.environ.get('TELEGRAM_BOT_TOKEN')
                chat_id = data.get('chat_id') or os.environ.get('TELEGRAM_CHAT_ID')
                limit = data.get('limit', 5)
                
                if not bot_token or not chat_id:
                    response = {"error": "Missing bot_token or chat_id"}
                else:
                    # Fetch market data
                    data_url = "http://localhost:8000/data"
                    data_resp = requests.get(data_url, timeout=10)
                    
                    if data_resp.status_code == 200:
                        market_data = data_resp.json()
                        companies = market_data.get('companies', [])
                        
                        # Detect patterns for all companies
                        pattern_detector = PatternDetector()
                        companies_with_patterns = []
                        
                        for company in companies:
                            patterns = pattern_detector.detect_patterns(company)
                            if patterns:
                                # Get analysis
                                symbol = company.get('symbol', '')
                                analysis_url = f"http://localhost:8001/api/analysis/{symbol}"
                                analysis_resp = requests.get(analysis_url, timeout=5)
                                
                                if analysis_resp.status_code == 200:
                                    analysis_data = analysis_resp.json().get('analysis', {})
                                    analysis_data['patterns'] = patterns
                                    companies_with_patterns.append(analysis_data)
                        
                        # Sort by pattern strength and limit
                        companies_with_patterns.sort(
                            key=lambda x: max([p.get('strength', 0) for p in x.get('patterns', [])]),
                            reverse=True
                        )
                        top_companies = companies_with_patterns[:limit]
                        
                        if top_companies:
                            bot = TelegramBot(bot_token, chat_id)
                            # Send formatted message with patterns
                            message = f"🎯 <b>TOP {len(top_companies)} WZORCÓW TECHNICZNYCH WIG80</b>\n\n"
                            
                            for i, company in enumerate(top_companies, 1):
                                symbol = company.get('symbol', '')
                                company_name = company.get('company_name', '')
                                price = company.get('current_price', 0)
                                change = company.get('change_percent', 0)
                                patterns = company.get('patterns', [])
                                main_pattern = patterns[0] if patterns else {}
                                
                                pattern_emoji = "🚩" if "flag" in main_pattern.get('pattern_name', '').lower() else \
                                               "🔺" if "triangle" in main_pattern.get('pattern_name', '').lower() else \
                                               "📐" if "channel" in main_pattern.get('pattern_name', '').lower() else \
                                               "⚡" if "breakout" in main_pattern.get('pattern_name', '').lower() else \
                                               "📈" if "momentum" in main_pattern.get('pattern_name', '').lower() else "📊"
                                
                                direction_emoji = "🟢" if main_pattern.get('direction') == 'bullish' else \
                                                 "🔴" if main_pattern.get('direction') == 'bearish' else "🟡"
                                
                                message += f"{i}. {pattern_emoji} <b>{symbol}</b> - {company_name}\n"
                                message += f"   {pattern_emoji} {main_pattern.get('pattern_name', 'Pattern')} {direction_emoji}\n"
                                message += f"   💰 {price:.2f} PLN ({change:+.2f}%) | Siła: {main_pattern.get('strength', 0)*100:.0f}%\n\n"
                            
                            message += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                            success = bot.send_message(message)
                            response = {"success": success, "count": len(top_companies), "patterns_found": len(companies_with_patterns)}
                        else:
                            response = {"success": False, "message": "No technical patterns detected", "count": 0}
                    else:
                        response = {"error": "Failed to fetch market data"}
            else:
                response = {"error": "Unknown endpoint"}
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "service": "Telegram Alerts API",
            "endpoints": {
                "POST /api/telegram/send": "Send custom message",
                "POST /api/telegram/alert": "Send alert for symbol",
                "POST /api/telegram/top": "Send top opportunities"
            },
            "status": "running"
        }
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[Telegram API] {self.client_address[0]} - {format % args}")

def run_api_server(port=8002, host='0.0.0.0'):
    """Run Telegram Alerts API server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, TelegramAlertsAPIHandler)
    
    print(f"\n{'='*70}")
    print(f"Telegram Alerts API Server")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Endpoints:")
    print(f"  POST http://{host}:{port}/api/telegram/send - Send message")
    print(f"  POST http://{host}:{port}/api/telegram/alert - Send alert")
    print(f"  POST http://{host}:{port}/api/telegram/top - Send top opportunities")
    print(f"{'='*70}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        httpd.shutdown()

if __name__ == "__main__":
    import sys
    
    # Check if monitoring mode
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            print("❌ Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
            print("\nSetup:")
            print("1. Create bot with @BotFather on Telegram")
            print("2. Get bot token")
            print("3. Get your chat ID (send message to bot, then visit: https://api.telegram.org/bot<TOKEN>/getUpdates)")
            print("4. Export variables:")
            print("   export TELEGRAM_BOT_TOKEN='your_token'")
            print("   export TELEGRAM_CHAT_ID='your_chat_id'")
            sys.exit(1)
        
        bot = TelegramBot(bot_token, chat_id)
        monitor = AlertMonitor(bot)
        
        # Send startup message
        bot.send_message("🔔 <b>Telegram Alerts Started</b>\n\nMonitoring WIG80 for price changes...")
        
        # Start monitoring
        monitor.start_monitoring(interval=60)  # Check every 60 seconds
    else:
        # Run API server
        port = int(os.environ.get('TELEGRAM_API_PORT', 8002))
        host = os.environ.get('TELEGRAM_API_HOST', '0.0.0.0')
        run_api_server(port=port, host=host)

