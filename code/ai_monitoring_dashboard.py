#!/usr/bin/env python3
"""
AI Monitoring Dashboard - Real-time AI model performance visualization
Author: AI Monitoring System
Date: 2025-11-06
"""

import asyncio
import logging
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Third-party imports
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import threading
import queue

# Local imports
from ai_performance_tracker import AIPerformanceTracker, ModelMetrics, TradingSignalMetrics

class AIMonitoringDashboard:
    """Real-time AI monitoring dashboard with visualization capabilities"""
    
    def __init__(self, tracker: AIPerformanceTracker = None, port: int = 8080):
        self.tracker = tracker or AIPerformanceTracker()
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'ai_monitoring_dashboard_2025'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Polish market specific configurations
        self.polish_market_config = {
            'overvaluation_threshold': 1.5,  # P/E ratio threshold
            'volatility_threshold': 0.3,     # Daily volatility threshold
            'volume_anomaly_threshold': 2.0, # Volume ratio threshold
            'market_hours': {
                'start': '08:00',
                'end': '16:45',
                'timezone': 'Europe/Warsaw'
            }
        }
        
        # Alert configuration
        self.alert_levels = {
            'CRITICAL': {'color': '#ff0000', 'priority': 1},
            'HIGH': {'color': '#ff6600', 'priority': 2},
            'MEDIUM': {'color': '#ffcc00', 'priority': 3},
            'LOW': {'color': '#00ff00', 'priority': 4}
        }
        
        self._setup_routes()
        self._setup_socketio_events()
        self._start_background_updates()
        
    def _setup_routes(self):
        """Setup Flask routes for the dashboard"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
            
        @self.app.route('/api/dashboard/summary')
        def get_dashboard_summary():
            """Get dashboard summary data"""
            try:
                summary = self.tracker.get_dashboard_summary()
                return jsonify({
                    'status': 'success',
                    'data': summary,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/models/<model_id>/metrics')
        def get_model_metrics(model_id):
            """Get detailed metrics for a specific model"""
            try:
                if model_id not in self.tracker.metrics_history:
                    return jsonify({'status': 'error', 'message': 'Model not found'}), 404
                    
                metrics = list(self.tracker.metrics_history[model_id])
                health = self.tracker.get_model_health_status(model_id)
                
                return jsonify({
                    'status': 'success',
                    'data': {
                        'model_id': model_id,
                        'metrics': [self._metrics_to_dict(m) for m in metrics],
                        'health': health
                    },
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/trading/signals')
        def get_trading_signals():
            """Get trading signal performance data"""
            try:
                model_id = request.args.get('model_id')
                days = int(request.args.get('days', 7))
                
                performance = self.tracker.get_trading_performance_summary(model_id, days)
                
                return jsonify({
                    'status': 'success',
                    'data': performance,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/spectral-bias/<model_id>')
        def get_spectral_bias(model_id):
            """Get spectral bias analysis for a model"""
            try:
                analysis = self.tracker.get_spectral_bias_analysis(model_id)
                
                return jsonify({
                    'status': 'success',
                    'data': analysis,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            try:
                hours = int(request.args.get('hours', 24))
                alerts = self.tracker.get_recent_alerts(hours)
                
                return jsonify({
                    'status': 'success',
                    'data': alerts,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/polish-market/insights')
        def get_polish_market_insights():
            """Get Polish market insights and overvaluation alerts"""
            try:
                insights = self._generate_polish_market_insights()
                
                return jsonify({
                    'status': 'success',
                    'data': insights,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/charts/model-performance')
        def get_model_performance_chart():
            """Generate model performance visualization"""
            try:
                model_id = request.args.get('model_id')
                hours = int(request.args.get('hours', 24))
                
                chart_data = self._generate_model_performance_chart(model_id, hours)
                return jsonify({
                    'status': 'success',
                    'data': chart_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/charts/spectral-bias')
        def get_spectral_bias_chart():
            """Generate spectral bias visualization"""
            try:
                model_id = request.args.get('model_id')
                chart_data = self._generate_spectral_bias_chart(model_id)
                return jsonify({
                    'status': 'success',
                    'data': chart_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/charts/trading-performance')
        def get_trading_performance_chart():
            """Generate trading performance visualization"""
            try:
                model_id = request.args.get('model_id')
                days = int(request.args.get('days', 30))
                chart_data = self._generate_trading_performance_chart(model_id, days)
                return jsonify({
                    'status': 'success',
                    'data': chart_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/charts/polish-market')
        def get_polish_market_chart():
            """Generate Polish market insights visualization"""
            try:
                chart_data = self._generate_polish_market_chart()
                return jsonify({
                    'status': 'success',
                    'data': chart_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
        @self.app.route('/api/export/<model_id>')
        def export_model_data(model_id):
            """Export model data"""
            try:
                format = request.args.get('format', 'json')
                file_path = f"/tmp/{model_id}_export_{int(time.time())}.{format}"
                
                result = self.tracker.export_metrics(model_id, format, file_path)
                
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                return Response(
                    content,
                    mimetype='application/octet-stream',
                    headers={
                        'Content-Disposition': f'attachment; filename={os.path.basename(file_path)}'
                    }
                )
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
                
    def _setup_socketio_events(self):
        """Setup Socket.IO events for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logging.info(f"Client connected: {request.sid}")
            emit('connected', {'status': 'connected', 'timestamp': datetime.now().isoformat()})
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logging.info(f"Client disconnected: {request.sid}")
            
        @self.socketio.on('subscribe_model')
        def handle_subscribe_model(data):
            """Subscribe to real-time updates for a specific model"""
            model_id = data.get('model_id')
            if model_id:
                logging.info(f"Client {request.sid} subscribed to model {model_id}")
                emit('subscribed', {'model_id': model_id, 'status': 'subscribed'})
                
    def _metrics_to_dict(self, metrics: ModelMetrics) -> Dict[str, Any]:
        """Convert ModelMetrics to dictionary"""
        return {
            'timestamp': metrics.timestamp,
            'accuracy': metrics.accuracy,
            'loss': metrics.loss,
            'precision': metrics.precision,
            'recall': metrics.recall,
            'f1_score': metrics.f1_score,
            'inference_time': metrics.inference_time,
            'memory_usage': metrics.memory_usage,
            'cpu_usage': metrics.cpu_usage,
            'throughput': metrics.throughput,
            'error_rate': metrics.error_rate,
            'predictions': metrics.predictions,
            'correct_predictions': metrics.correct_predictions
        }
        
    def _generate_polish_market_insights(self) -> Dict[str, Any]:
        """Generate Polish market insights and overvaluation alerts"""
        # Simulate Polish market data (in real implementation, this would connect to GPW data)
        import random
        
        # WIG80 companies simulation
        companies = [
            'PKN ORLEN', 'PZU', 'KGHM', 'PGE', 'PKO BP', 'LOTOS', 'LPP', 'CD PROJEKT',
            'CCC', 'ORANGE', 'ALIOR', 'ENERGA', 'ASBIS', 'PLAY', 'AMICA', 'DĄBROWKA',
            'URBITY', 'DROGAS', 'FOTON', 'GAMING'
        ]
        
        market_insights = {
            'market_status': 'OPEN' if self._is_market_open() else 'CLOSED',
            'overvaluation_alerts': [],
            'volatility_alerts': [],
            'volume_anomalies': [],
            'top_movers': {'gainers': [], 'losers': []},
            'sector_analysis': {},
            'risk_metrics': {
                'market_volatility': random.uniform(0.15, 0.35),
                'correlation_risk': random.uniform(0.1, 0.6),
                'liquidity_risk': random.uniform(0.05, 0.3),
                'foreign_exposure': random.uniform(0.15, 0.45)
            }
        }
        
        # Generate simulated overvaluation alerts
        for company in companies[:5]:  # Check first 5 companies
            pe_ratio = random.uniform(1.0, 3.0)
            if pe_ratio > self.polish_market_config['overvaluation_threshold']:
                market_insights['overvaluation_alerts'].append({
                    'company': company,
                    'pe_ratio': pe_ratio,
                    'alert_type': 'OVERVALUATION',
                    'severity': 'MEDIUM' if pe_ratio < 2.0 else 'HIGH',
                    'recommendation': 'CONSIDER_SELL' if pe_ratio > 2.0 else 'MONITOR'
                })
                
        # Generate volatility alerts
        for company in companies[5:10]:  # Next 5 companies
            daily_volatility = random.uniform(0.05, 0.6)
            if daily_volatility > self.polish_market_config['volatility_threshold']:
                market_insights['volatility_alerts'].append({
                    'company': company,
                    'volatility': daily_volatility,
                    'alert_type': 'HIGH_VOLATILITY',
                    'severity': 'HIGH' if daily_volatility > 0.4 else 'MEDIUM',
                    'recommendation': 'REDUCE_POSITION' if daily_volatility > 0.5 else 'MONITOR'
                })
                
        # Generate volume anomalies
        for company in companies[10:15]:  # Next 5 companies
            volume_ratio = random.uniform(0.5, 3.5)
            if volume_ratio > self.polish_market_config['volume_anomaly_threshold']:
                market_insights['volume_anomalies'].append({
                    'company': company,
                    'volume_ratio': volume_ratio,
                    'alert_type': 'VOLUME_SPIKE',
                    'severity': 'MEDIUM',
                    'recommendation': 'INVESTIGATE_CAUSE'
                })
                
        # Generate top movers
        for company in companies:
            change = random.uniform(-5.0, 5.0)
            if change > 0:
                market_insights['top_movers']['gainers'].append({
                    'company': company,
                    'change': change,
                    'price': random.uniform(50, 200)
                })
            else:
                market_insights['top_movers']['losers'].append({
                    'company': company,
                    'change': change,
                    'price': random.uniform(50, 200)
                })
                
        # Sort and limit
        market_insights['top_movers']['gainers'] = sorted(
            market_insights['top_movers']['gainers'], 
            key=lambda x: x['change'], 
            reverse=True
        )[:5]
        
        market_insights['top_movers']['losers'] = sorted(
            market_insights['top_movers']['losers'], 
            key=lambda x: x['change']
        )[:5]
        
        # Sector analysis simulation
        sectors = ['Banking', 'Energy', 'Technology', 'Retail', 'Mining', 'Telecom']
        for sector in sectors:
            market_insights['sector_analysis'][sector] = {
                'performance': random.uniform(-3.0, 3.0),
                'volume': random.uniform(1000000, 10000000),
                'volatility': random.uniform(0.1, 0.4),
                'trend': random.choice(['BULLISH', 'BEARISH', 'SIDEWAYS'])
            }
            
        return market_insights
        
    def _is_market_open(self) -> bool:
        """Check if Polish market is currently open"""
        # Simplified market hours check
        # In real implementation, this would check actual GPW trading hours
        now = datetime.now()
        hour = now.hour
        return 8 <= hour <= 16  # Simplified market hours
        
    def _generate_model_performance_chart(self, model_id: str, hours: int) -> Dict[str, Any]:
        """Generate model performance visualization chart"""
        if model_id not in self.tracker.metrics_history:
            return {'error': 'Model not found'}
            
        # Get recent metrics
        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [
            m for m in self.tracker.metrics_history[model_id] 
            if m.timestamp > cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': 'No recent metrics found'}
            
        # Create time series
        timestamps = [datetime.fromtimestamp(m.timestamp) for m in recent_metrics]
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                'Accuracy & Loss', 'Precision, Recall & F1-Score',
                'Memory & CPU Usage', 'Inference Time & Throughput',
                'Error Rate', 'Predictions Volume'
            ],
            specs=[[{"secondary_y": True}], [{"secondary_y": False}],
                   [{"secondary_y": True}], [{"secondary_y": False}],
                   [{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Accuracy and Loss
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.accuracy for m in recent_metrics],
                      name='Accuracy', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.loss for m in recent_metrics],
                      name='Loss', line=dict(color='red'), yaxis='y2'),
            row=1, col=1
        )
        
        # Precision, Recall, F1-Score
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.precision for m in recent_metrics],
                      name='Precision', line=dict(color='green')),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.recall for m in recent_metrics],
                      name='Recall', line=dict(color='orange')),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.f1_score for m in recent_metrics],
                      name='F1-Score', line=dict(color='purple')),
            row=1, col=2
        )
        
        # Memory and CPU Usage
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.memory_usage for m in recent_metrics],
                      name='Memory %', line=dict(color='red')),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.cpu_usage for m in recent_metrics],
                      name='CPU %', line=dict(color='blue')),
            row=2, col=1
        )
        
        # Inference Time and Throughput
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.inference_time for m in recent_metrics],
                      name='Inference Time', line=dict(color='red'), yaxis='y2'),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.throughput for m in recent_metrics],
                      name='Throughput', line=dict(color='green'), yaxis='y3'),
            row=2, col=2
        )
        
        # Error Rate
        fig.add_trace(
            go.Scatter(x=timestamps, y=[m.error_rate for m in recent_metrics],
                      name='Error Rate', line=dict(color='red', dash='dash')),
            row=3, col=1
        )
        
        # Predictions Volume
        fig.add_trace(
            go.Bar(x=timestamps, y=[m.predictions for m in recent_metrics],
                  name='Predictions', marker_color='lightblue'),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=f'Model Performance Dashboard - {model_id}',
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())
        
    def _generate_spectral_bias_chart(self, model_id: str) -> Dict[str, Any]:
        """Generate spectral bias analysis visualization"""
        if model_id not in self.tracker.spectral_bias_history:
            return {'error': 'No spectral bias analysis found'}
            
        bias_metrics = list(self.tracker.spectral_bias_history[model_id])
        if not bias_metrics:
            return {'error': 'No spectral bias metrics found'}
            
        latest = bias_metrics[-1]
        
        # Create subplots for spectral bias analysis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Learning Rates by Frequency Band',
                'Convergence Times',
                'Bias Score Trend',
                'Risk Assessment'
            ]
        )
        
        # Learning rates by frequency
        fig.add_trace(
            go.Bar(
                x=latest.frequency_bands,
                y=latest.learning_rates,
                name='Learning Rates',
                marker_color='blue',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        # Convergence times
        fig.add_trace(
            go.Scatter(
                x=latest.frequency_bands,
                y=latest.convergence_times,
                mode='lines+markers',
                name='Convergence Times',
                line=dict(color='red', width=3)
            ),
            row=1, col=2
        )
        
        # Bias score trend (simulated if only one point)
        if len(bias_metrics) > 1:
            timestamps = [datetime.fromtimestamp(m.timestamp) for m in bias_metrics]
            bias_scores = [m.bias_score for m in bias_metrics]
        else:
            timestamps = [datetime.fromtimestamp(latest.timestamp)]
            bias_scores = [latest.bias_score]
            
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=bias_scores,
                mode='lines+markers',
                name='Bias Score',
                line=dict(color='purple', width=3)
            ),
            row=2, col=1
        )
        
        # Risk assessment gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=latest.overfitting_risk * 100,
                title={'text': "Overfitting Risk %"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f'Spectral Bias Analysis - {model_id}',
            height=600,
            showlegend=False,
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())
        
    def _generate_trading_performance_chart(self, model_id: str, days: int) -> Dict[str, Any]:
        """Generate trading performance visualization"""
        # Get trading performance data
        performance = self.tracker.get_trading_performance_summary(model_id, days)
        
        if not performance.get('total_signals', 0):
            return {'error': 'No trading signals found'}
            
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Signal Accuracy by Type',
                'Profit/Loss Distribution',
                'Performance by Model',
                'Signal Confidence Distribution'
            ]
        )
        
        # Signal accuracy by type
        signal_types = performance.get('signal_types', {})
        if signal_types:
            types = list(signal_types.keys())
            accuracies = [signal_types[t]['accuracy'] * 100 for t in types]
            colors = ['green' if a > 60 else 'yellow' if a > 40 else 'red' for a in accuracies]
            
            fig.add_trace(
                go.Bar(
                    x=types,
                    y=accuracies,
                    name='Accuracy %',
                    marker_color=colors
                ),
                row=1, col=1
            )
            
        # Profit/Loss distribution (simulated)
        profits = list(range(-50, 101, 10))
        frequencies = [max(0, 20 - abs(p//10)) for p in profits]
        
        fig.add_trace(
            go.Bar(
                x=profits,
                y=frequencies,
                name='Frequency',
                marker_color='lightblue'
            ),
            row=1, col=2
        )
        
        # Performance by model
        model_perf = performance.get('model_performance', {})
        if model_perf:
            models = list(model_perf.keys())
            model_profits = [model_perf[m]['profit'] for m in models]
            
            fig.add_trace(
                go.Bar(
                    x=models,
                    y=model_profits,
                    name='Total Profit',
                    marker_color=['green' if p > 0 else 'red' for p in model_profits]
                ),
                row=2, col=1
            )
            
        # Confidence distribution (simulated)
        confidence_bins = np.linspace(0.5, 1.0, 11)
        confidence_freq = [int(50 * np.exp(-(c-0.5)**2 * 10)) for c in confidence_bins]
        
        fig.add_trace(
            go.Histogram(
                x=np.random.normal(0.75, 0.15, 1000),
                nbinsx=20,
                name='Confidence',
                marker_color='orange'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title=f'Trading Performance Analysis - {model_id}',
            height=600,
            showlegend=False,
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())
        
    def _generate_polish_market_chart(self) -> Dict[str, Any]:
        """Generate Polish market insights visualization"""
        # Get market insights
        insights = self._generate_polish_market_insights()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Overvaluation Alerts',
                'Volatility Analysis',
                'Top Movers',
                'Sector Performance'
            ],
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Overvaluation alerts
        overvaluation = insights['overvaluation_alerts']
        if overvaluation:
            companies = [alert['company'] for alert in overvaluation]
            pe_ratios = [alert['pe_ratio'] for alert in overvaluation]
            colors = ['red' if alert['severity'] == 'HIGH' else 'orange' for alert in overvaluation]
            
            fig.add_trace(
                go.Bar(
                    x=companies,
                    y=pe_ratios,
                    name='P/E Ratio',
                    marker_color=colors,
                    text=pe_ratios,
                    textposition='outside'
                ),
                row=1, col=1
            )
            
        # Volatility analysis
        volatility = insights['volatility_alerts']
        if volatility:
            companies = [alert['company'] for alert in volatility]
            volatilities = [alert['volatility'] for alert in volatility]
            colors = ['darkred' if v > 0.4 else 'red' for v in volatilities]
            
            fig.add_trace(
                go.Bar(
                    x=companies,
                    y=volatilities,
                    name='Daily Volatility',
                    marker_color=colors,
                    text=[f"{v:.3f}" for v in volatilities],
                    textposition='outside'
                ),
                row=1, col=2
            )
            
        # Top movers
        gainers = insights['top_movers']['gainers'][:5]
        losers = insights['top_movers']['losers'][:5]
        
        if gainers:
            gainer_names = [g['company'] for g in gainers]
            gainer_changes = [g['change'] for g in gainers]
            
            fig.add_trace(
                go.Bar(
                    x=gainer_names,
                    y=gainer_changes,
                    name='Top Gainers',
                    marker_color='green',
                    text=[f"+{c:.2f}%" for c in gainer_changes],
                    textposition='outside'
                ),
                row=2, col=1
            )
            
        if losers:
            loser_names = [l['company'] for l in losers]
            loser_changes = [l['change'] for l in losers]
            
            fig.add_trace(
                go.Bar(
                    x=loser_names,
                    y=loser_changes,
                    name='Top Losers',
                    marker_color='red',
                    text=[f"{c:.2f}%" for c in loser_changes],
                    textposition='outside'
                ),
                row=2, col=1
            )
            
        # Sector performance
        sector_analysis = insights['sector_analysis']
        if sector_analysis:
            sectors = list(sector_analysis.keys())
            sector_performance = [sector_analysis[s]['performance'] for s in sectors]
            colors = ['green' if p > 0 else 'red' for p in sector_performance]
            
            fig.add_trace(
                go.Scatter(
                    x=sectors,
                    y=sector_performance,
                    mode='markers+lines',
                    name='Sector Performance',
                    marker=dict(size=10, color=colors),
                    line=dict(color='blue', width=2)
                ),
                row=2, col=2
            )
            
        fig.update_layout(
            title='Polish Market Insights Dashboard - WIG80 Analysis',
            height=600,
            showlegend=True,
            template='plotly_white'
        )
        
        return json.loads(fig.to_json())
        
    def _start_background_updates(self):
        """Start background tasks for real-time updates"""
        
        def update_worker():
            """Background worker for sending real-time updates"""
            while True:
                try:
                    # Send periodic updates to all connected clients
                    if hasattr(self, 'socketio'):
                        # Get fresh data
                        summary = self.tracker.get_dashboard_summary()
                        alerts = self.tracker.get_recent_alerts(1)  # Last hour
                        market_insights = self._generate_polish_market_insights()
                        
                        # Emit updates
                        self.socketio.emit('dashboard_update', {
                            'summary': summary,
                            'alerts': alerts,
                            'market_insights': market_insights,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                    time.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logging.error(f"Background update error: {e}")
                    time.sleep(30)
                    
        update_thread = threading.Thread(target=update_worker, daemon=True)
        update_thread.start()
        
    def run(self, debug: bool = False, threaded: bool = True):
        """Run the dashboard server"""
        logging.info(f"Starting AI Monitoring Dashboard on port {self.port}")
        
        # Create templates directory if it doesn't exist
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            self._create_dashboard_template()
            
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=debug, threaded=threaded)
        
    def _create_dashboard_template(self):
        """Create HTML template for the dashboard"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Monitoring Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; }
        .container { padding: 2rem; max-width: 1400px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card h3 { color: #333; margin-bottom: 1rem; border-bottom: 2px solid #667eea; padding-bottom: 0.5rem; }
        .metric { display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0; }
        .metric-value { font-size: 1.5rem; font-weight: bold; }
        .metric-label { color: #666; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; display: inline-block; margin-right: 0.5rem; }
        .status-excellent { background-color: #10b981; }
        .status-good { background-color: #3b82f6; }
        .status-fair { background-color: #f59e0b; }
        .status-poor { background-color: #ef4444; }
        .chart-container { width: 100%; height: 400px; }
        .alert { padding: 0.75rem; border-radius: 5px; margin: 0.5rem 0; }
        .alert-critical { background-color: #fee2e2; border-left: 4px solid #dc2626; }
        .alert-high { background-color: #fed7aa; border-left: 4px solid #ea580c; }
        .alert-medium { background-color: #fef3c7; border-left: 4px solid #d97706; }
        .alert-low { background-color: #dcfce7; border-left: 4px solid #16a34a; }
        .tabs { display: flex; border-bottom: 1px solid #ddd; margin-bottom: 1rem; }
        .tab { padding: 0.75rem 1.5rem; cursor: pointer; border-bottom: 2px solid transparent; }
        .tab.active { border-bottom-color: #667eea; color: #667eea; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .nav-tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
        .nav-tab { padding: 0.75rem 1.5rem; background: #e5e7eb; border: none; border-radius: 5px; cursor: pointer; }
        .nav-tab.active { background: #667eea; color: white; }
        .refresh-btn { background: #667eea; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; }
        .loading { text-align: center; padding: 2rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-chart-line"></i> AI Monitoring Dashboard</h1>
        <p>Real-time AI model performance, spectral bias analysis, and Polish market insights</p>
    </div>
    
    <div class="container">
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('overview')">Overview</button>
            <button class="nav-tab" onclick="switchTab('models')">AI Models</button>
            <button class="nav-tab" onclick="switchTab('trading')">Trading Signals</button>
            <button class="nav-tab" onclick="switchTab('market')">Polish Market</button>
            <button class="nav-tab" onclick="switchTab('spectral')">Spectral Bias</button>
        </div>
        
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h3>System Status</h3>
                    <div class="metric">
                        <span class="metric-label">Total Models</span>
                        <span class="metric-value" id="total-models">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Models</span>
                        <span class="metric-value" id="active-models">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Signals</span>
                        <span class="metric-value" id="total-signals">-</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Recent Alerts</span>
                        <span class="metric-value" id="recent-alerts">-</span>
                    </div>
                </div>
                
                <div class="card">
                    <h3>Model Health</h3>
                    <div id="model-health-container">
                        <div class="loading">Loading model health data...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>Recent Alerts</h3>
                    <div id="alerts-container">
                        <div class="loading">Loading alerts...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>Performance Summary</h3>
                    <div id="performance-summary">
                        <div class="loading">Loading performance data...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- AI Models Tab -->
        <div id="models" class="tab-content">
            <div class="card">
                <h3>Model Performance Charts</h3>
                <div style="margin-bottom: 1rem;">
                    <select id="model-selector" style="padding: 0.5rem; margin-right: 1rem;">
                        <option value="">Select a model</option>
                    </select>
                    <button class="refresh-btn" onclick="loadModelChart()">Load Chart</button>
                </div>
                <div id="model-chart" class="chart-container"></div>
            </div>
        </div>
        
        <!-- Trading Signals Tab -->
        <div id="trading" class="tab-content">
            <div class="card">
                <h3>Trading Signal Performance</h3>
                <div style="margin-bottom: 1rem;">
                    <select id="trading-model-selector" style="padding: 0.5rem; margin-right: 1rem;">
                        <option value="">All Models</option>
                    </select>
                    <input type="number" id="days-input" value="30" min="1" max="365" style="padding: 0.5rem; width: 100px; margin-right: 1rem;">
                    <button class="refresh-btn" onclick="loadTradingChart()">Load Chart</button>
                </div>
                <div id="trading-chart" class="chart-container"></div>
            </div>
        </div>
        
        <!-- Polish Market Tab -->
        <div id="market" class="tab-content">
            <div class="card">
                <h3>Polish Market Insights (WIG80)</h3>
                <div id="market-status" style="margin-bottom: 1rem; padding: 1rem; background: #f0f9ff; border-radius: 5px;">
                    <div class="loading">Loading market data...</div>
                </div>
                <div id="market-chart" class="chart-container"></div>
            </div>
        </div>
        
        <!-- Spectral Bias Tab -->
        <div id="spectral" class="tab-content">
            <div class="card">
                <h3>Spectral Bias Analysis</h3>
                <div style="margin-bottom: 1rem;">
                    <select id="spectral-model-selector" style="padding: 0.5rem; margin-right: 1rem;">
                        <option value="">Select a model</option>
                    </select>
                    <button class="refresh-btn" onclick="loadSpectralChart()">Load Analysis</button>
                </div>
                <div id="spectral-chart" class="chart-container"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        let dashboardData = {};
        
        socket.on('connect', function() {
            console.log('Connected to AI Monitoring Dashboard');
        });
        
        socket.on('dashboard_update', function(data) {
            dashboardData = data;
            updateOverview();
        });
        
        function switchTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Load specific tab data
            switch(tabName) {
                case 'models':
                    loadModelOptions();
                    break;
                case 'trading':
                    loadTradingOptions();
                    break;
                case 'spectral':
                    loadSpectralOptions();
                    break;
                case 'market':
                    loadMarketData();
                    break;
            }
        }
        
        function updateOverview() {
            if (!dashboardData.summary) return;
            
            const summary = dashboardData.summary;
            document.getElementById('total-models').textContent = summary.total_models || 0;
            document.getElementById('active-models').textContent = summary.active_models || 0;
            document.getElementById('total-signals').textContent = summary.total_signals || 0;
            document.getElementById('recent-alerts').textContent = dashboardData.alerts?.length || 0;
            
            // Update model health
            updateModelHealth(summary.models_health || {});
            
            // Update alerts
            updateAlerts(dashboardData.alerts || []);
            
            // Update performance summary
            updatePerformanceSummary(summary.trading_performance || {});
        }
        
        function updateModelHealth(healthData) {
            const container = document.getElementById('model-health-container');
            container.innerHTML = '';
            
            Object.entries(healthData).forEach(([modelId, health]) => {
                const statusClass = `status-${health.status || 'poor'}`;
                const statusText = health.status ? health.status.charAt(0).toUpperCase() + health.status.slice(1) : 'Unknown';
                
                const healthElement = document.createElement('div');
                healthElement.className = 'metric';
                healthElement.innerHTML = `
                    <div>
                        <span class="status-indicator ${statusClass}"></span>
                        <strong>${modelId}</strong>
                        <br>
                        <small>${statusText} - Score: ${health.health_score?.toFixed(1) || 'N/A'}</small>
                    </div>
                    <div class="metric-value">${health.accuracy?.toFixed(3) || 'N/A'}</div>
                `;
                container.appendChild(healthElement);
            });
        }
        
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';
            
            if (alerts.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: #666;">No recent alerts</div>';
                return;
            }
            
            alerts.slice(0, 5).forEach(alert => {
                const alertElement = document.createElement('div');
                alertElement.className = `alert alert-${alert.severity?.toLowerCase() || 'medium'}`;
                alertElement.innerHTML = `
                    <strong>${alert.type}</strong> - ${alert.message}
                    <br>
                    <small>${new Date(alert.timestamp * 1000).toLocaleString()}</small>
                `;
                container.appendChild(alertElement);
            });
        }
        
        function updatePerformanceSummary(performance) {
            const container = document.getElementById('performance-summary');
            container.innerHTML = `
                <div class="metric">
                    <span class="metric-label">Overall Accuracy</span>
                    <span class="metric-value">${(performance.overall_accuracy * 100)?.toFixed(1) || '0.0'}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Profit</span>
                    <span class="metric-value">${performance.total_profit?.toFixed(2) || '0.00'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Confidence</span>
                    <span class="metric-value">${performance.avg_confidence?.toFixed(3) || '0.000'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Analysis Period</span>
                    <span class="metric-value">${performance.analysis_period_days || 0} days</span>
                </div>
            `;
        }
        
        function loadModelOptions() {
            if (!dashboardData.summary) return;
            
            const models = Object.keys(dashboardData.summary.models_health || {});
            const selector = document.getElementById('model-selector');
            const spectralSelector = document.getElementById('spectral-model-selector');
            
            selector.innerHTML = '<option value="">Select a model</option>';
            spectralSelector.innerHTML = '<option value="">Select a model</option>';
            
            models.forEach(modelId => {
                selector.innerHTML += `<option value="${modelId}">${modelId}</option>`;
                spectralSelector.innerHTML += `<option value="${modelId}">${modelId}</option>`;
            });
        }
        
        function loadTradingOptions() {
            if (!dashboardData.summary) return;
            
            const models = Object.keys(dashboardData.summary.models_health || {});
            const selector = document.getElementById('trading-model-selector');
            
            selector.innerHTML = '<option value="">All Models</option>';
            models.forEach(modelId => {
                selector.innerHTML += `<option value="${modelId}">${modelId}</option>`;
            });
        }
        
        function loadSpectralOptions() {
            loadModelOptions();
        }
        
        async function loadModelChart() {
            const modelId = document.getElementById('model-selector').value;
            if (!modelId) return;
            
            try {
                const response = await fetch(`/api/charts/model-performance?model_id=${modelId}&hours=24`);
                const result = await response.json();
                
                if (result.status === 'success') {
                    Plotly.newPlot('model-chart', result.data.data, result.data.layout);
                } else {
                    document.getElementById('model-chart').innerHTML = '<div class="loading">Error loading chart data</div>';
                }
            } catch (error) {
                console.error('Error loading model chart:', error);
                document.getElementById('model-chart').innerHTML = '<div class="loading">Error loading chart data</div>';
            }
        }
        
        async function loadTradingChart() {
            const modelId = document.getElementById('trading-model-selector').value;
            const days = document.getElementById('days-input').value;
            const params = new URLSearchParams({ days });
            if (modelId) params.append('model_id', modelId);
            
            try {
                const response = await fetch(`/api/charts/trading-performance?${params}`);
                const result = await response.json();
                
                if (result.status === 'success') {
                    Plotly.newPlot('trading-chart', result.data.data, result.data.layout);
                } else {
                    document.getElementById('trading-chart').innerHTML = '<div class="loading">Error loading chart data</div>';
                }
            } catch (error) {
                console.error('Error loading trading chart:', error);
                document.getElementById('trading-chart').innerHTML = '<div class="loading">Error loading chart data</div>';
            }
        }
        
        async function loadSpectralChart() {
            const modelId = document.getElementById('spectral-model-selector').value;
            if (!modelId) return;
            
            try {
                const response = await fetch(`/api/charts/spectral-bias?model_id=${modelId}`);
                const result = await response.json();
                
                if (result.status === 'success') {
                    Plotly.newPlot('spectral-chart', result.data.data, result.data.layout);
                } else {
                    document.getElementById('spectral-chart').innerHTML = '<div class="loading">Error loading spectral bias data</div>';
                }
            } catch (error) {
                console.error('Error loading spectral chart:', error);
                document.getElementById('spectral-chart').innerHTML = '<div class="loading">Error loading chart data</div>';
            }
        }
        
        async function loadMarketData() {
            try {
                const response = await fetch('/api/polish-market/insights');
                const result = await response.json();
                
                if (result.status === 'success') {
                    const insights = result.data;
                    const statusElement = document.getElementById('market-status');
                    statusElement.innerHTML = `
                        <div class="metric">
                            <span class="metric-label">Market Status</span>
                            <span class="metric-value">${insights.market_status}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Overvaluation Alerts</span>
                            <span class="metric-value">${insights.overvaluation_alerts?.length || 0}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Volatility Alerts</span>
                            <span class="metric-value">${insights.volatility_alerts?.length || 0}</span>
                        </div>
                    `;
                    
                    // Load market chart
                    const chartResponse = await fetch('/api/charts/polish-market');
                    const chartResult = await chartResponse.json();
                    
                    if (chartResult.status === 'success') {
                        Plotly.newPlot('market-chart', chartResult.data.data, chartResult.data.layout);
                    }
                } else {
                    document.getElementById('market-status').innerHTML = '<div class="loading">Error loading market data</div>';
                }
            } catch (error) {
                console.error('Error loading market data:', error);
                document.getElementById('market-status').innerHTML = '<div class="loading">Error loading market data</div>';
            }
        }
        
        // Initial load
        document.addEventListener('DOMContentLoaded', function() {
            // Load initial data
            fetch('/api/dashboard/summary')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        dashboardData = { summary: data.data };
                        updateOverview();
                    }
                });
                
            // Load alerts
            fetch('/api/alerts')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        dashboardData.alerts = data.data;
                        updateAlerts(data.data);
                    }
                });
        });
    </script>
</body>
</html>'''
        
        with open(os.path.join(templates_dir, 'dashboard.html'), 'w') as f:
            f.write(template_content)
            
    def create_sample_data(self, num_models: int = 3, num_signals: int = 100):
        """Create sample data for demonstration purposes"""
        import random
        
        # Create sample models
        model_names = [
            "polish_market_predictor",
            "spectral_bias_model", 
            "trading_signal_generator",
            "risk_assessment_model",
            "volatility_predictor"
        ]
        
        for i in range(min(num_models, len(model_names))):
            model_id = model_names[i]
            self.tracker.register_model(model_id)
            
            # Generate sample metrics
            for j in range(50):  # 50 data points per model
                metrics = {
                    'accuracy': random.uniform(0.6, 0.95),
                    'loss': random.uniform(0.05, 0.4),
                    'precision': random.uniform(0.5, 0.9),
                    'recall': random.uniform(0.4, 0.85),
                    'f1_score': random.uniform(0.4, 0.9),
                    'inference_time': random.uniform(0.01, 0.8),
                    'memory_usage': random.uniform(20, 85),
                    'cpu_usage': random.uniform(15, 75),
                    'throughput': random.uniform(5, 150),
                    'error_rate': random.uniform(0, 0.15),
                    'predictions': random.randint(20, 800),
                    'correct_predictions': random.randint(15, 700)
                }
                self.tracker.update_model_metrics(model_id, metrics)
                
            # Generate spectral bias analysis
            if i == 1:  # Only for spectral bias model
                self.tracker.simulate_spectral_bias_analysis(model_id)
                
        # Generate trading signals
        for signal_id in range(num_signals):
            model_id = random.choice(model_names[:min(num_models, len(model_names))])
            signal = TradingSignalMetrics(
                signal_id=f"signal_{signal_id}",
                timestamp=time.time() - random.randint(0, 7*24*3600),  # Last 7 days
                model_id=model_id,
                signal_type=random.choice(['BUY', 'SELL', 'HOLD']),
                confidence=random.uniform(0.4, 1.0),
                target_price=random.uniform(50, 300),
                actual_price=random.uniform(45, 310),
                profit_loss=random.uniform(-100, 200),
                accuracy=random.choice([True, False]),
                execution_time=random.uniform(0.05, 3.0)
            )
            self.tracker.add_trading_signal(signal)

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize performance tracker
    tracker = AIPerformanceTracker()
    
    # Create dashboard with sample data
    dashboard = AIMonitoringDashboard(tracker, port=8080)
    
    # Create sample data for demonstration
    dashboard.create_sample_data(num_models=4, num_signals=200)
    
    print("AI Monitoring Dashboard starting...")
    print("Dashboard will be available at: http://localhost:8080")
    print("Features:")
    print("- Real-time AI model performance monitoring")
    print("- Spectral bias analysis visualization")
    print("- Polish market insights and overvaluation alerts")
    print("- Trading signal performance tracking")
    print("- AI model health and accuracy metrics")
    print("- Interactive charts and alerts")
    print("\nPress Ctrl+C to stop the dashboard")
    
    # Run the dashboard
    dashboard.run(debug=False)