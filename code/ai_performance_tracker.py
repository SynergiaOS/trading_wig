#!/usr/bin/env python3
"""
AI Performance Tracker - Real-time AI model monitoring and analytics
Author: AI Monitoring System
Date: 2025-11-06
"""

import asyncio
import logging
import time
import json
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from collections import deque, defaultdict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ModelMetrics:
    """Data class for storing model performance metrics"""
    model_id: str
    timestamp: float
    accuracy: float
    loss: float
    precision: float
    recall: float
    f1_score: float
    inference_time: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    error_rate: float
    predictions: int
    correct_predictions: int

@dataclass
class SpectralBiasMetrics:
    """Data class for spectral bias analysis results"""
    model_id: str
    timestamp: float
    frequency_bands: List[float]
    learning_rates: List[float]
    convergence_times: List[float]
    bias_score: float
    overfitting_risk: float
    generalization_gap: float

@dataclass
class TradingSignalMetrics:
    """Data class for trading signal performance tracking"""
    signal_id: str
    timestamp: float
    model_id: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    target_price: float
    actual_price: float
    profit_loss: float
    accuracy: bool
    execution_time: float

class AIPerformanceTracker:
    """Main performance tracking system for AI models"""
    
    def __init__(self, db_path: str = "ai_performance.db", max_history: int = 10000):
        self.db_path = db_path
        self.max_history = max_history
        self.models = {}
        self.current_metrics = {}
        self.metrics_history = defaultdict(lambda: deque(maxlen=max_history))
        self.spectral_bias_history = defaultdict(lambda: deque(maxlen=1000))
        self.trading_signals = deque(maxlen=10000)
        self.alert_thresholds = {
            'accuracy_drop': 0.1,
            'error_rate_increase': 0.05,
            'memory_usage': 80.0,
            'cpu_usage': 80.0,
            'spectral_bias_threshold': 0.7
        }
        self.alerts = []
        self.is_running = False
        self._setup_database()
        self._start_background_tasks()
        
    def _setup_database(self):
        """Initialize SQLite database for storing metrics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS model_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    accuracy REAL,
                    loss REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    inference_time REAL,
                    memory_usage REAL,
                    cpu_usage REAL,
                    throughput REAL,
                    error_rate REAL,
                    predictions INTEGER,
                    correct_predictions INTEGER
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS spectral_bias_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    frequency_bands TEXT,
                    learning_rates TEXT,
                    convergence_times TEXT,
                    bias_score REAL,
                    overfitting_risk REAL,
                    generalization_gap REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trading_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    model_id TEXT NOT NULL,
                    signal_type TEXT,
                    confidence REAL,
                    target_price REAL,
                    actual_price REAL,
                    profit_loss REAL,
                    accuracy BOOLEAN,
                    execution_time REAL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    model_id TEXT,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    value REAL,
                    threshold REAL
                )
            ''')
            
    def register_model(self, model_id: str, model_config: Dict[str, Any] = None):
        """Register a new AI model for monitoring"""
        self.models[model_id] = {
            'config': model_config or {},
            'registered_at': time.time(),
            'status': 'active',
            'metrics_count': 0
        }
        self.current_metrics[model_id] = None
        logging.info(f"Registered model: {model_id}")
        
    def update_model_metrics(self, model_id: str, metrics: Dict[str, float]):
        """Update real-time metrics for a model"""
        if model_id not in self.models:
            self.register_model(model_id)
            
        # Create ModelMetrics object
        model_metrics = ModelMetrics(
            model_id=model_id,
            timestamp=time.time(),
            accuracy=metrics.get('accuracy', 0.0),
            loss=metrics.get('loss', 0.0),
            precision=metrics.get('precision', 0.0),
            recall=metrics.get('recall', 0.0),
            f1_score=metrics.get('f1_score', 0.0),
            inference_time=metrics.get('inference_time', 0.0),
            memory_usage=metrics.get('memory_usage', 0.0),
            cpu_usage=metrics.get('cpu_usage', 0.0),
            throughput=metrics.get('throughput', 0.0),
            error_rate=metrics.get('error_rate', 0.0),
            predictions=metrics.get('predictions', 0),
            correct_predictions=metrics.get('correct_predictions', 0)
        )
        
        # Store metrics
        self.current_metrics[model_id] = model_metrics
        self.metrics_history[model_id].append(model_metrics)
        self.models[model_id]['metrics_count'] += 1
        
        # Save to database
        self._save_model_metrics(model_metrics)
        
        # Check for alerts
        self._check_alerts(model_id, model_metrics)
        
    def update_spectral_bias_analysis(self, model_id: str, analysis: Dict[str, Any]):
        """Update spectral bias analysis results"""
        spectral_metrics = SpectralBiasMetrics(
            model_id=model_id,
            timestamp=time.time(),
            frequency_bands=analysis.get('frequency_bands', []),
            learning_rates=analysis.get('learning_rates', []),
            convergence_times=analysis.get('convergence_times', []),
            bias_score=analysis.get('bias_score', 0.0),
            overfitting_risk=analysis.get('overfitting_risk', 0.0),
            generalization_gap=analysis.get('generalization_gap', 0.0)
        )
        
        self.spectral_bias_history[model_id].append(spectral_metrics)
        self._save_spectral_bias_metrics(spectral_metrics)
        
    def add_trading_signal(self, signal: TradingSignalMetrics):
        """Add a new trading signal for performance tracking"""
        self.trading_signals.append(signal)
        self._save_trading_signal(signal)
        
    def _save_model_metrics(self, metrics: ModelMetrics):
        """Save model metrics to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO model_metrics (
                    model_id, timestamp, accuracy, loss, precision, recall, f1_score,
                    inference_time, memory_usage, cpu_usage, throughput, error_rate,
                    predictions, correct_predictions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.model_id, metrics.timestamp, metrics.accuracy, metrics.loss,
                metrics.precision, metrics.recall, metrics.f1_score, metrics.inference_time,
                metrics.memory_usage, metrics.cpu_usage, metrics.throughput, metrics.error_rate,
                metrics.predictions, metrics.correct_predictions
            ))
            
    def _save_spectral_bias_metrics(self, metrics: SpectralBiasMetrics):
        """Save spectral bias metrics to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO spectral_bias_metrics (
                    model_id, timestamp, frequency_bands, learning_rates, convergence_times,
                    bias_score, overfitting_risk, generalization_gap
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.model_id, metrics.timestamp,
                json.dumps(metrics.frequency_bands),
                json.dumps(metrics.learning_rates),
                json.dumps(metrics.convergence_times),
                metrics.bias_score, metrics.overfitting_risk, metrics.generalization_gap
            ))
            
    def _save_trading_signal(self, signal: TradingSignalMetrics):
        """Save trading signal to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO trading_signals (
                    signal_id, timestamp, model_id, signal_type, confidence,
                    target_price, actual_price, profit_loss, accuracy, execution_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.signal_id, signal.timestamp, signal.model_id, signal.signal_type,
                signal.confidence, signal.target_price, signal.actual_price,
                signal.profit_loss, signal.accuracy, signal.execution_time
            ))
            
    def _save_alert(self, alert_type: str, model_id: str, message: str, 
                   severity: str, value: float, threshold: float):
        """Save alert to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO alerts (timestamp, model_id, alert_type, severity, message, value, threshold)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (time.time(), model_id, alert_type, severity, message, value, threshold))
            
    def _check_alerts(self, model_id: str, metrics: ModelMetrics):
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # Accuracy drop alert
        if len(self.metrics_history[model_id]) >= 2:
            prev_accuracy = list(self.metrics_history[model_id])[-2].accuracy
            accuracy_drop = prev_accuracy - metrics.accuracy
            if accuracy_drop > self.alert_thresholds['accuracy_drop']:
                alerts.append({
                    'type': 'accuracy_drop',
                    'severity': 'HIGH',
                    'message': f'Accuracy dropped by {accuracy_drop:.3f} for model {model_id}',
                    'value': accuracy_drop,
                    'threshold': self.alert_thresholds['accuracy_drop']
                })
                
        # Error rate increase alert
        if metrics.error_rate > self.alert_thresholds['error_rate_increase']:
            alerts.append({
                'type': 'error_rate_high',
                'severity': 'MEDIUM',
                'message': f'Error rate {metrics.error_rate:.3f} exceeds threshold for model {model_id}',
                'value': metrics.error_rate,
                'threshold': self.alert_thresholds['error_rate_increase']
            })
            
        # Memory usage alert
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_usage_high',
                'severity': 'MEDIUM',
                'message': f'Memory usage {metrics.memory_usage:.1f}% exceeds threshold for model {model_id}',
                'value': metrics.memory_usage,
                'threshold': self.alert_thresholds['memory_usage']
            })
            
        # CPU usage alert
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_usage_high',
                'severity': 'MEDIUM',
                'message': f'CPU usage {metrics.cpu_usage:.1f}% exceeds threshold for model {model_id}',
                'value': metrics.cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage']
            })
            
        # Spectral bias alert (if available)
        if model_id in self.spectral_bias_history and self.spectral_bias_history[model_id]:
            latest_bias = self.spectral_bias_history[model_id][-1]
            if latest_bias.bias_score > self.alert_thresholds['spectral_bias_threshold']:
                alerts.append({
                    'type': 'spectral_bias_high',
                    'severity': 'LOW',
                    'message': f'Spectral bias score {latest_bias.bias_score:.3f} indicates potential overfitting for model {model_id}',
                    'value': latest_bias.bias_score,
                    'threshold': self.alert_thresholds['spectral_bias_threshold']
                })
                
        # Save and store alerts
        for alert in alerts:
            self.alerts.append(alert)
            self._save_alert(alert['type'], model_id, alert['message'], 
                           alert['severity'], alert['value'], alert['threshold'])
            
    def get_model_health_status(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive health status for a model"""
        if model_id not in self.models or model_id not in self.metrics_history:
            return {'status': 'not_found', 'health_score': 0.0}
            
        recent_metrics = list(self.metrics_history[model_id])[-10:]  # Last 10 metrics
        if not recent_metrics:
            return {'status': 'no_metrics', 'health_score': 0.0}
            
        # Calculate health metrics
        avg_accuracy = np.mean([m.accuracy for m in recent_metrics])
        avg_error_rate = np.mean([m.error_rate for m in recent_metrics])
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        avg_inference_time = np.mean([m.inference_time for m in recent_metrics])
        
        # Calculate health score (0-100)
        accuracy_score = avg_accuracy * 100
        error_score = max(0, (1 - avg_error_rate) * 100)
        memory_score = max(0, (1 - avg_memory/100) * 100)
        cpu_score = max(0, (1 - avg_cpu/100) * 100)
        performance_score = max(0, (1 - avg_inference_time/10) * 100)  # Normalize to 10s max
        
        health_score = (accuracy_score + error_score + memory_score + cpu_score + performance_score) / 5
        
        # Determine status
        if health_score >= 80:
            status = 'excellent'
        elif health_score >= 60:
            status = 'good'
        elif health_score >= 40:
            status = 'fair'
        else:
            status = 'poor'
            
        return {
            'status': status,
            'health_score': health_score,
            'accuracy': avg_accuracy,
            'error_rate': avg_error_rate,
            'memory_usage': avg_memory,
            'cpu_usage': avg_cpu,
            'inference_time': avg_inference_time,
            'sample_count': len(recent_metrics)
        }
        
    def get_trading_performance_summary(self, model_id: str = None, 
                                      days: int = 7) -> Dict[str, Any]:
        """Get trading signal performance summary"""
        cutoff_time = time.time() - (days * 24 * 3600)
        
        # Filter signals by time and optionally by model
        if model_id:
            signals = [s for s in self.trading_signals if s.model_id == model_id and s.timestamp > cutoff_time]
        else:
            signals = [s for s in self.trading_signals if s.timestamp > cutoff_time]
            
        if not signals:
            return {'total_signals': 0, 'message': 'No signals found'}
            
        # Calculate performance metrics
        total_signals = len(signals)
        accuracy = sum(1 for s in signals if s.accuracy) / total_signals
        total_profit = sum(s.profit_loss for s in signals)
        avg_confidence = np.mean([s.confidence for s in signals])
        
        # Performance by signal type
        signal_types = {}
        for signal_type in ['BUY', 'SELL', 'HOLD']:
            type_signals = [s for s in signals if s.signal_type == signal_type]
            if type_signals:
                type_accuracy = sum(1 for s in type_signals if s.accuracy) / len(type_signals)
                type_profit = sum(s.profit_loss for s in type_signals)
                signal_types[signal_type] = {
                    'count': len(type_signals),
                    'accuracy': type_accuracy,
                    'profit': type_profit
                }
                
        # Model comparison
        model_performance = {}
        for model in set(s.model_id for s in signals):
            model_signals = [s for s in signals if s.model_id == model]
            model_performance[model] = {
                'count': len(model_signals),
                'accuracy': sum(1 for s in model_signals if s.accuracy) / len(model_signals),
                'profit': sum(s.profit_loss for s in model_signals)
            }
            
        return {
            'total_signals': total_signals,
            'overall_accuracy': accuracy,
            'total_profit': total_profit,
            'avg_confidence': avg_confidence,
            'signal_types': signal_types,
            'model_performance': model_performance,
            'analysis_period_days': days
        }
        
    def get_spectral_bias_analysis(self, model_id: str) -> Dict[str, Any]:
        """Get spectral bias analysis results for a model"""
        if model_id not in self.spectral_bias_history:
            return {'status': 'no_analysis', 'message': 'No spectral bias analysis available'}
            
        bias_metrics = list(self.spectral_bias_history[model_id])
        if not bias_metrics:
            return {'status': 'no_metrics', 'message': 'No spectral bias metrics found'}
            
        # Get latest analysis
        latest = bias_metrics[-1]
        
        # Calculate trends
        if len(bias_metrics) > 1:
            prev_bias_score = bias_metrics[-2].bias_score
            bias_trend = latest.bias_score - prev_bias_score
        else:
            bias_trend = 0
            
        return {
            'status': 'available',
            'latest_bias_score': latest.bias_score,
            'latest_overfitting_risk': latest.overfitting_risk,
            'latest_generalization_gap': latest.generalization_gap,
            'bias_trend': bias_trend,
            'frequency_bands': latest.frequency_bands,
            'learning_rates': latest.learning_rates,
            'convergence_times': latest.convergence_times,
            'analysis_count': len(bias_metrics),
            'recommendations': self._generate_bias_recommendations(latest)
        }
        
    def _generate_bias_recommendations(self, bias_metrics: SpectralBiasMetrics) -> List[str]:
        """Generate recommendations based on spectral bias analysis"""
        recommendations = []
        
        if bias_metrics.bias_score > 0.7:
            recommendations.append("High spectral bias detected - consider regularization techniques")
            
        if bias_metrics.overfitting_risk > 0.5:
            recommendations.append("High overfitting risk - increase training data or use dropout")
            
        if bias_metrics.generalization_gap > 0.3:
            recommendations.append("Large generalization gap - consider early stopping or data augmentation")
            
        if bias_metrics.convergence_times and len(bias_metrics.convergence_times) > 5:
            # Check for slow convergence in higher frequencies
            if np.mean(bias_metrics.convergence_times[2:]) > np.mean(bias_metrics.convergence_times[:2]) * 2:
                recommendations.append("Slow convergence in high frequencies - adjust learning rate schedule")
                
        return recommendations
        
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts within specified time window"""
        cutoff_time = time.time() - (hours * 3600)
        return [alert for alert in self.alerts if alert.get('timestamp', 0) > cutoff_time]
        
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary for dashboard display"""
        summary = {
            'total_models': len(self.models),
            'active_models': sum(1 for model in self.models.values() if model['status'] == 'active'),
            'total_signals': len(self.trading_signals),
            'recent_alerts': len(self.get_recent_alerts()),
            'models_health': {}
        }
        
        # Health status for each model
        for model_id in self.models:
            summary['models_health'][model_id] = self.get_model_health_status(model_id)
            
        # Overall trading performance
        summary['trading_performance'] = self.get_trading_performance_summary()
        
        # Spectral bias analysis for models with analysis
        summary['spectral_bias'] = {
            model_id: self.get_spectral_bias_analysis(model_id)
            for model_id in self.models
            if model_id in self.spectral_bias_history
        }
        
        return summary
        
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        self.is_running = True
        
        def health_check_worker():
            """Background worker for periodic health checks"""
            while self.is_running:
                try:
                    self._perform_health_checks()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logging.error(f"Health check error: {e}")
                    time.sleep(60)
                    
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
        
    def _perform_health_checks(self):
        """Perform periodic health checks on all models"""
        for model_id in self.models:
            if model_id in self.current_metrics:
                health = self.get_model_health_status(model_id)
                if health['status'] in ['poor', 'fair']:
                    # Log health warnings
                    logging.warning(f"Model {model_id} health status: {health['status']} "
                                  f"(score: {health['health_score']:.1f})")
                                  
    def simulate_trading_signals(self, model_id: str, num_signals: int = 100):
        """Generate simulated trading signals for testing"""
        import random
        
        signal_types = ['BUY', 'SELL', 'HOLD']
        
        for i in range(num_signals):
            signal = TradingSignalMetrics(
                signal_id=f"{model_id}_signal_{i}",
                timestamp=time.time() - random.randint(0, 7*24*3600),  # Last 7 days
                model_id=model_id,
                signal_type=random.choice(signal_types),
                confidence=random.uniform(0.5, 1.0),
                target_price=random.uniform(50, 200),
                actual_price=random.uniform(45, 210),
                profit_loss=random.uniform(-50, 100),
                accuracy=random.choice([True, False]),
                execution_time=random.uniform(0.1, 2.0)
            )
            self.add_trading_signal(signal)
            
    def simulate_spectral_bias_analysis(self, model_id: str):
        """Generate simulated spectral bias analysis for testing"""
        analysis = {
            'frequency_bands': [1.0, 2.0, 4.0, 8.0, 16.0, 32.0],
            'learning_rates': [0.01, 0.005, 0.0025, 0.001, 0.0005, 0.0001],
            'convergence_times': [10, 25, 60, 120, 200, 300],
            'bias_score': random.uniform(0.3, 0.8),
            'overfitting_risk': random.uniform(0.2, 0.7),
            'generalization_gap': random.uniform(0.1, 0.5)
        }
        
        self.update_spectral_bias_analysis(model_id, analysis)
        
    def export_metrics(self, model_id: str, format: str = 'json', 
                      output_file: str = None) -> str:
        """Export model metrics to file"""
        if model_id not in self.metrics_history:
            return f"No metrics found for model {model_id}"
            
        metrics_data = [asdict(m) for m in self.metrics_history[model_id]]
        
        if not output_file:
            output_file = f"{model_id}_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            
        if format.lower() == 'json':
            with open(output_file, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
        elif format.lower() == 'csv':
            df = pd.DataFrame(metrics_data)
            df.to_csv(output_file, index=False)
        else:
            return f"Unsupported export format: {format}"
            
        return f"Metrics exported to {output_file}"
        
    def __del__(self):
        """Cleanup when tracker is destroyed"""
        self.is_running = False

if __name__ == "__main__":
    # Example usage and testing
    logging.basicConfig(level=logging.INFO)
    
    # Initialize tracker
    tracker = AIPerformanceTracker()
    
    # Register test models
    tracker.register_model("polish_market_predictor")
    tracker.register_model("spectral_bias_model")
    tracker.register_model("trading_signal_generator")
    
    # Simulate some metrics
    import random
    for i in range(10):
        for model_id in ["polish_market_predictor", "spectral_bias_model", "trading_signal_generator"]:
            metrics = {
                'accuracy': random.uniform(0.7, 0.95),
                'loss': random.uniform(0.1, 0.5),
                'precision': random.uniform(0.6, 0.9),
                'recall': random.uniform(0.5, 0.85),
                'f1_score': random.uniform(0.5, 0.9),
                'inference_time': random.uniform(0.05, 0.5),
                'memory_usage': random.uniform(30, 80),
                'cpu_usage': random.uniform(20, 70),
                'throughput': random.uniform(10, 100),
                'error_rate': random.uniform(0, 0.1),
                'predictions': random.randint(50, 500),
                'correct_predictions': random.randint(40, 450)
            }
            tracker.update_model_metrics(model_id, metrics)
            
    # Add trading signals
    tracker.simulate_trading_signals("trading_signal_generator", 50)
    
    # Add spectral bias analysis
    tracker.simulate_spectral_bias_analysis("spectral_bias_model")
    
    # Get dashboard summary
    summary = tracker.get_dashboard_summary()
    print("\n=== AI Performance Tracker Dashboard Summary ===")
    print(json.dumps(summary, indent=2, default=str))
    
    # Get health status for a specific model
    health = tracker.get_model_health_status("polish_market_predictor")
    print(f"\nPolish Market Predictor Health: {health}")
    
    # Get trading performance
    trading_perf = tracker.get_trading_performance_summary("trading_signal_generator")
    print(f"\nTrading Performance: {trading_perf}")
    
    # Get spectral bias analysis
    bias_analysis = tracker.get_spectral_bias_analysis("spectral_bias_model")
    print(f"\nSpectral Bias Analysis: {bias_analysis}")
    
    # Export metrics
    export_result = tracker.export_metrics("polish_market_predictor", "json")
    print(f"\nExport result: {export_result}")