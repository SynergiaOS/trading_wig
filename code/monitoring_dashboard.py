#!/usr/bin/env python3
"""
QuestDB-Pocketbase Monitoring Dashboard
=======================================

Real-time web dashboard for monitoring the QuestDB-Pocketbase integration system.
Provides comprehensive visualization of system health, data integrity, performance
metrics, backup status, and alerts.

Features:
- Real-time system health monitoring
- Data consistency visualization
- Performance metrics dashboard
- Backup status and history
- Alert management interface
- Data integrity reports
- System resource monitoring

Author: Data Engineering Team
Date: 2025-11-06
Version: 1.0.0
"""

import asyncio
import aiohttp
import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# Import monitoring system
import sys
sys.path.append('/workspace/code')
from monitoring_system import MonitoringSystem, DEFAULT_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/logs/monitoring_dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MonitoringDashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the monitoring dashboard"""
    
    def __init__(self, *args, monitoring_system=None, **kwargs):
        self.monitoring_system = monitoring_system
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if path == '/' or path == '/dashboard':
                # Main dashboard
                html = self._generate_dashboard_html()
            elif path == '/api/status':
                # API status endpoint
                status_data = self._get_api_status()
                self.wfile.write(json.dumps(status_data, default=str).encode('utf-8'))
                return
            elif path == '/api/health':
                # Health check endpoint
                health_data = self._get_health_data()
                self.wfile.write(json.dumps(health_data, default=str).encode('utf-8'))
                return
            elif path == '/api/integrity':
                # Data integrity endpoint
                integrity_data = self._get_integrity_data()
                self.wfile.write(json.dumps(integrity_data, default=str).encode('utf-8'))
                return
            elif path == '/api/backups':
                # Backup status endpoint
                backup_data = self._get_backup_data()
                self.wfile.write(json.dumps(backup_data, default=str).encode('utf-8'))
                return
            elif path == '/api/alerts':
                # Alerts endpoint
                alert_data = self._get_alert_data()
                self.wfile.write(json.dumps(alert_data, default=str).encode('utf-8'))
                return
            elif path == '/api/performance':
                # Performance metrics endpoint
                performance_data = self._get_performance_data()
                self.wfile.write(json.dumps(performance_data, default=str).encode('utf-8'))
                return
            elif path == '/favicon.ico':
                # Favicon
                self.send_error(404)
                return
            else:
                # 404 for other paths
                self.send_error(404, "Not Found")
                return
            
            # Send HTML content
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Dashboard request error: {e}")
            error_html = self._generate_error_html(str(e))
            self.wfile.write(error_html.encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            if path == '/api/trigger_backup':
                # Trigger backup
                backup_data = self._trigger_backup()
                self.wfile.write(json.dumps(backup_data, default=str).encode('utf-8'))
            elif path == '/api/acknowledge_alert':
                # Acknowledge alert
                alert_data = self._acknowledge_alert()
                self.wfile.write(json.dumps(alert_data, default=str).encode('utf-8'))
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"Dashboard POST error: {e}")
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        logger.debug(f"[Dashboard] {self.client_address[0]} - {format % args}")
    
    def _generate_dashboard_html(self) -> str:
        """Generate the main dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QuestDB-Pocketbase Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2rem;
            font-weight: 700;
        }
        
        .header p {
            color: #7f8c8d;
            margin-top: 0.5rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 1rem;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-healthy {
            background: #27ae60;
            box-shadow: 0 0 10px rgba(39, 174, 96, 0.5);
        }
        
        .status-warning {
            background: #f39c12;
            box-shadow: 0 0 10px rgba(243, 156, 18, 0.5);
        }
        
        .status-critical {
            background: #e74c3c;
            box-shadow: 0 0 10px rgba(231, 76, 60, 0.5);
        }
        
        .status-unknown {
            background: #95a5a6;
            box-shadow: 0 0 10px rgba(149, 165, 166, 0.5);
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #34495e;
        }
        
        .metric-value {
            font-weight: 600;
            color: #2c3e50;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .alert-item {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
        }
        
        .alert-critical {
            border-left-color: #e74c3c;
            background: #fdf2f2;
        }
        
        .alert-warning {
            border-left-color: #f39c12;
            background: #fffbf0;
        }
        
        .alert-info {
            border-left-color: #3498db;
            background: #f0f8ff;
        }
        
        .button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }
        
        .button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .refresh-info {
            text-align: center;
            margin-top: 2rem;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .chart-placeholder {
            height: 200px;
            background: linear-gradient(45deg, #ecf0f1, #bdc3c7);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #7f8c8d;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .header {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
            
            .container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 QuestDB-Pocketbase Monitoring</h1>
        <p>Real-time system health and data integrity monitoring</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- System Health -->
            <div class="card">
                <h2>🏥 System Health</h2>
                <div id="health-status">
                    <div class="metric">
                        <span class="metric-label">
                            <span class="status-indicator status-healthy"></span>QuestDB
                        </span>
                        <span class="metric-value" id="questdb-status">Checking...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">
                            <span class="status-indicator status-healthy"></span>Pocketbase
                        </span>
                        <span class="metric-value" id="pocketbase-status">Checking...</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">
                            <span class="status-indicator status-healthy"></span>System Resources
                        </span>
                        <span class="metric-value" id="system-status">Checking...</span>
                    </div>
                </div>
            </div>
            
            <!-- Data Integrity -->
            <div class="card">
                <h2>🔍 Data Integrity</h2>
                <div id="integrity-status">
                    <div class="chart-placeholder">Data consistency charts will appear here</div>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="card">
                <h2>⚡ Performance</h2>
                <div id="performance-metrics">
                    <div class="metric">
                        <span class="metric-label">CPU Usage</span>
                        <span class="metric-value" id="cpu-usage">--%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cpu-progress" style="width: 0%"></div>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Memory Usage</span>
                        <span class="metric-value" id="memory-usage">--%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="memory-progress" style="width: 0%"></div>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Disk Usage</span>
                        <span class="metric-value" id="disk-usage">--%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="disk-progress" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <!-- Active Alerts -->
            <div class="card">
                <h2>🚨 Active Alerts</h2>
                <div id="active-alerts">
                    <div class="metric">
                        <span class="metric-label">No active alerts</span>
                        <span class="metric-value">✅</span>
                    </div>
                </div>
            </div>
            
            <!-- Backup Status -->
            <div class="card">
                <h2>💾 Backup Status</h2>
                <div id="backup-status">
                    <div class="metric">
                        <span class="metric-label">Last Backup</span>
                        <span class="metric-value" id="last-backup">No backups yet</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value" id="backup-system-status">--</span>
                    </div>
                    <button class="button" onclick="triggerBackup()" style="margin-top: 1rem; width: 100%;">
                        Trigger Manual Backup
                    </button>
                </div>
            </div>
            
            <!-- Data Statistics -->
            <div class="card">
                <h2>📊 Data Statistics</h2>
                <div id="data-statistics">
                    <div class="metric">
                        <span class="metric-label">Total Records</span>
                        <span class="metric-value" id="total-records">--</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Quality Score</span>
                        <span class="metric-value" id="quality-score">--</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Sync Success Rate</span>
                        <span class="metric-value" id="sync-rate">--%</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="refresh-info">
            <p>Auto-refreshing every 30 seconds | Last updated: <span id="last-update">--</span></p>
        </div>
    </div>

    <script>
        // Auto-refresh dashboard data
        function refreshDashboard() {
            Promise.all([
                fetch('/api/status').then(r => r.json()),
                fetch('/api/health').then(r => r.json()),
                fetch('/api/performance').then(r => r.json()),
                fetch('/api/integrity').then(r => r.json()),
                fetch('/api/alerts').then(r => r.json()),
                fetch('/api/backups').then(r => r.json())
            ]).then(([status, health, performance, integrity, alerts, backups]) => {
                updateStatus(status);
                updateHealth(health);
                updatePerformance(performance);
                updateIntegrity(integrity);
                updateAlerts(alerts);
                updateBackups(backups);
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            }).catch(error => {
                console.error('Failed to refresh dashboard:', error);
            });
        }
        
        function updateStatus(status) {
            console.log('Status update:', status);
        }
        
        function updateHealth(health) {
            const healthElements = {
                'questdb': 'questdb-status',
                'pocketbase': 'pocketbase-status',
                'system_resources': 'system-status'
            };
            
            Object.keys(healthElements).forEach(component => {
                const element = document.getElementById(healthElements[component]);
                const healthData = health[component];
                if (healthData) {
                    element.textContent = `${healthData.status} (${healthData.response_time?.toFixed(2) || '--'}s)`;
                    
                    // Update status indicator
                    const indicator = element.parentNode.querySelector('.status-indicator');
                    indicator.className = `status-indicator status-${healthData.status}`;
                }
            });
        }
        
        function updatePerformance(performance) {
            if (performance.cpu_percent !== undefined) {
                document.getElementById('cpu-usage').textContent = performance.cpu_percent.toFixed(1) + '%';
                document.getElementById('cpu-progress').style.width = performance.cpu_percent + '%';
            }
            
            if (performance.memory_percent !== undefined) {
                document.getElementById('memory-usage').textContent = performance.memory_percent.toFixed(1) + '%';
                document.getElementById('memory-progress').style.width = performance.memory_percent + '%';
            }
            
            if (performance.disk_percent !== undefined) {
                document.getElementById('disk-usage').textContent = performance.disk_percent.toFixed(1) + '%';
                document.getElementById('disk-progress').style.width = performance.disk_percent + '%';
            }
        }
        
        function updateIntegrity(integrity) {
            const container = document.getElementById('integrity-status');
            if (integrity.length > 0) {
                container.innerHTML = integrity.map(report => `
                    <div class="metric">
                        <span class="metric-label">${report.collection}</span>
                        <span class="metric-value">${(report.data_quality_score * 100).toFixed(1)}%</span>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<div class="metric"><span class="metric-label">No integrity data</span><span class="metric-value">--</span></div>';
            }
        }
        
        function updateAlerts(alerts) {
            const container = document.getElementById('active-alerts');
            if (alerts.length > 0) {
                container.innerHTML = alerts.map(alert => `
                    <div class="alert-item alert-${alert.severity}">
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">${alert.component}</div>
                        <div style="font-size: 0.9rem; color: #666;">${alert.message}</div>
                        <div style="font-size: 0.8rem; color: #999; margin-top: 0.5rem;">${new Date(alert.timestamp).toLocaleString()}</div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<div class="metric"><span class="metric-label">No active alerts</span><span class="metric-value">✅</span></div>';
            }
        }
        
        function updateBackups(backups) {
            if (backups.length > 0) {
                const lastBackup = backups[0];
                document.getElementById('last-backup').textContent = new Date(lastBackup.timestamp).toLocaleString();
                document.getElementById('backup-system-status').textContent = lastBackup.status;
            }
        }
        
        function triggerBackup() {
            const button = event.target;
            button.disabled = true;
            button.textContent = 'Creating Backup...';
            
            fetch('/api/trigger_backup', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    setTimeout(() => {
                        button.disabled = false;
                        button.textContent = 'Trigger Manual Backup';
                        refreshDashboard();
                    }, 2000);
                })
                .catch(error => {
                    console.error('Backup failed:', error);
                    button.disabled = false;
                    button.textContent = 'Backup Failed - Retry';
                });
        }
        
        // Initialize dashboard
        refreshDashboard();
        
        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);
    </script>
</body>
</html>
        """
    
    def _generate_error_html(self, error_message: str) -> str:
        """Generate error page HTML"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Error</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }}
        .error-container {{
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }}
        h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
        p {{ font-size: 1.1rem; opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1>⚠️ Dashboard Error</h1>
        <p>{error_message}</p>
    </div>
</body>
</html>
        """
    
    def _get_api_status(self) -> Dict[str, Any]:
        """Get API status information"""
        try:
            if self.monitoring_system:
                return asyncio.run(self.monitoring_system.get_monitoring_status())
            else:
                return {
                    'error': 'Monitoring system not available',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_health_data(self) -> Dict[str, Any]:
        """Get health check data"""
        try:
            if self.monitoring_system:
                # This would run a health check synchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                health_data = loop.run_until_complete(
                    self.monitoring_system.perform_comprehensive_health_check()
                )
                loop.close()
                return {k: asdict(v) if hasattr(v, '__dict__') else v for k, v in health_data.items()}
            else:
                return {'error': 'Monitoring system not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_integrity_data(self) -> List[Dict[str, Any]]:
        """Get data integrity reports"""
        try:
            if self.monitoring_system:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                integrity_data = loop.run_until_complete(
                    self.monitoring_system.validate_data_consistency()
                )
                loop.close()
                return [asdict(report) for report in integrity_data]
            else:
                return []
        except Exception as e:
            logger.error(f"Integrity data error: {e}")
            return []
    
    def _get_backup_data(self) -> List[Dict[str, Any]]:
        """Get backup status data"""
        try:
            if self.monitoring_system:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                recent_backups = loop.run_until_complete(
                    self.monitoring_system._get_recent_backups(10)
                )
                loop.close()
                return recent_backups
            else:
                return []
        except Exception as e:
            logger.error(f"Backup data error: {e}")
            return []
    
    def _get_alert_data(self) -> List[Dict[str, Any]]:
        """Get active alerts data"""
        try:
            if self.monitoring_system and self.monitoring_system.active_alerts:
                return [asdict(alert) for alert in self.monitoring_system.active_alerts.values()]
            else:
                return []
        except Exception as e:
            logger.error(f"Alert data error: {e}")
            return []
    
    def _get_performance_data(self) -> Dict[str, Any]:
        """Get performance metrics data"""
        try:
            if self.monitoring_system:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                performance_data = loop.run_until_complete(
                    self.monitoring_system.collect_performance_metrics()
                )
                loop.close()
                return performance_data
            else:
                return {}
        except Exception as e:
            logger.error(f"Performance data error: {e}")
            return {}
    
    def _trigger_backup(self) -> Dict[str, Any]:
        """Trigger a manual backup"""
        try:
            if self.monitoring_system:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                backup_result = loop.run_until_complete(
                    self.monitoring_system.create_backup("questdb", "manual")
                )
                loop.close()
                return asdict(backup_result)
            else:
                return {'error': 'Monitoring system not available'}
        except Exception as e:
            logger.error(f"Backup trigger error: {e}")
            return {'error': str(e)}
    
    def _acknowledge_alert(self) -> Dict[str, Any]:
        """Acknowledge an alert"""
        try:
            # This would need to be implemented to actually acknowledge alerts
            return {'status': 'acknowledged', 'message': 'Alert acknowledged successfully'}
        except Exception as e:
            return {'error': str(e)}


class MonitoringDashboard:
    """Main dashboard server class"""
    
    def __init__(self, port: int = 8080, config: Dict[str, Any] = None):
        """Initialize dashboard with configuration"""
        self.port = port
        self.config = config or DEFAULT_CONFIG
        self.monitoring_system = None
        self.server = None
        
        # Initialize monitoring system
        self.monitoring_system = MonitoringSystem(self.config)
        
        logger.info(f"Monitoring dashboard initialized on port {port}")
    
    def start_server(self):
        """Start the dashboard server"""
        try:
            # Create handler class with monitoring system reference
            def handler_factory(*args, **kwargs):
                return MonitoringDashboardHandler(*args, monitoring_system=self.monitoring_system, **kwargs)
            
            # Start server
            self.server = HTTPServer(('', self.port), handler_factory)
            
            print(f"\n{'='*70}")
            print(f"QuestDB-Pocketbase Monitoring Dashboard")
            print(f"Dashboard URL: http://localhost:{self.port}/")
            print(f"API Endpoints:")
            print(f"  Health:     http://localhost:{self.port}/api/health")
            print(f"  Status:     http://localhost:{self.port}/api/status")
            print(f"  Performance: http://localhost:{self.port}/api/performance")
            print(f"  Integrity:  http://localhost:{self.port}/api/integrity")
            print(f"  Backups:    http://localhost:{self.port}/api/backups")
            print(f"  Alerts:     http://localhost:{self.port}/api/alerts")
            print(f"{'='*70}\n")
            
            # Try to open browser
            try:
                webbrowser.open(f'http://localhost:{self.port}/')
            except:
                pass  # Ignore if browser can't be opened
            
            # Start monitoring system in background
            monitoring_thread = threading.Thread(
                target=self._run_monitoring_system,
                daemon=True
            )
            monitoring_thread.start()
            
            # Start server
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("Dashboard server stopped by user")
        except Exception as e:
            logger.error(f"Dashboard server error: {e}")
        finally:
            self.stop_server()
    
    def _run_monitoring_system(self):
        """Run the monitoring system in background"""
        try:
            # Create new event loop for monitoring thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Start monitoring
            loop.run_until_complete(self.monitoring_system.start_monitoring(check_interval=300))
            
        except Exception as e:
            logger.error(f"Monitoring system thread error: {e}")
        finally:
            loop.close()
    
    def stop_server(self):
        """Stop the dashboard server"""
        if self.server:
            logger.info("Stopping dashboard server...")
            self.server.shutdown()
            self.server.server_close()
        
        if self.monitoring_system:
            asyncio.run(self.monitoring_system.cleanup())


def main():
    """Main function to run the monitoring dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='QuestDB-Pocketbase Monitoring Dashboard')
    parser.add_argument('--port', type=int, default=8080, help='Dashboard port (default: 8080)')
    parser.add_argument('--questdb-path', type=str, help='QuestDB database path')
    parser.add_argument('--pocketbase-url', type=str, help='Pocketbase URL')
    parser.add_argument('--config-file', type=str, help='Configuration file path')
    
    args = parser.parse_args()
    
    # Load configuration
    config = DEFAULT_CONFIG.copy()
    
    if args.questdb_path:
        config['questdb_path'] = args.questdb_path
    
    if args.pocketbase_url:
        config['pocketbase_url'] = args.pocketbase_url
    
    if args.config_file:
        try:
            with open(args.config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
    
    # Create necessary directories
    Path('/workspace/logs').mkdir(exist_ok=True)
    Path('/workspace/backups').mkdir(exist_ok=True)
    Path('/workspace/monitoring').mkdir(exist_ok=True)
    
    # Start dashboard
    dashboard = MonitoringDashboard(port=args.port, config=config)
    dashboard.start_server()


if __name__ == "__main__":
    main()