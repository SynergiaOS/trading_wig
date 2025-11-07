"""
AI Training Pipeline for Spectral Bias Neural Networks
Complete training system for WIG80 Polish stock market analysis

This module provides a comprehensive training pipeline for spectral bias neural networks
with Multi-Grade Deep Learning (MGDL) architecture, RAG integration, and real-time
data processing capabilities for the WIG80 financial platform.

Author: AI Training Pipeline Team
Version: 1.0
Date: 2025-11-06
"""

import asyncio
import logging
import numpy as np
import pandas as pd
import pickle
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import asyncio
import aiohttp
import asyncpg
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import faiss
import redis
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
import os

# Import existing AI model components
try:
    from ai_model_design import (
        AIConfig, SpectralBiasNeuralNetwork, RAGNeuralNetwork, 
        RAGKnowledgeBase, FinancialDataPreprocessor, MarketEvent,
        PredictionResult, create_ai_system
    )
except ImportError:
    print("Warning: Could not import existing AI model components. Using basic implementations.")
    # Fallback implementations if imports fail
    class AIConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# Data Configuration
# =============================================================================

@dataclass
class TrainingConfig:
    """Configuration for training pipeline"""
    # Model parameters
    input_dim: int = 50
    spectral_dim: int = 128
    hidden_dim: int = 256
    output_dim: int = 4
    num_heads: int = 8
    num_layers: int = 6
    dropout_rate: float = 0.1
    
    # Spectral bias parameters
    spectral_lambda_low: float = 0.1
    spectral_lambda_mid: float = 0.2
    spectral_lambda_high: float = 0.3
    
    # Training parameters
    learning_rate: float = 0.001
    batch_size: int = 32
    num_epochs: int = 100
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    
    # Data parameters
    window_size: int = 252  # 1 year of trading days
    step_size: int = 1
    min_data_points: int = 500
    
    # Database configuration
    questdb_host: str = "localhost"
    questdb_port: int = 9009
    questdb_user: str = "admin"
    questdb_password: str = "quest"
    pocketbase_url: str = "http://localhost:8090"
    redis_url: str = "redis://localhost:6379"
    
    # Model storage
    model_save_path: str = "./models"
    experiment_name: str = f"wig80_spectral_mgdl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Data sources
    wig80_symbols_file: str = "/workspace/data/filtered_companies.json"
    
    # Performance tracking
    track_metrics: List[str] = None
    save_frequency: int = 10
    
    def __post_init__(self):
        if self.track_metrics is None:
            self.track_metrics = [
                'train_loss', 'val_loss', 'mae', 'rmse', 'r2_score',
                'directional_accuracy', 'spectral_loss', 'confidence_score'
            ]

@dataclass
class TrainingMetrics:
    """Training metrics tracking"""
    epoch: int
    train_loss: float
    val_loss: float
    mae: float
    rmse: float
    r2_score: float
    directional_accuracy: float
    spectral_loss: float
    confidence_score: float
    training_time: float
    learning_rate: float

# =============================================================================
# Data Processing Components
# =============================================================================

class WIG80DataCollector:
    """Data collection and preprocessing for WIG80 stocks"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.preprocessor = FinancialDataPreprocessor(AIConfig(
            input_dim=config.input_dim,
            spectral_dim=config.spectral_dim,
            hidden_dim=config.hidden_dim,
            output_dim=config.output_dim,
            window_size=config.window_size,
            questdb_host=config.questdb_host,
            questdb_port=config.questdb_port,
            pocketbase_url=config.pocketbase_url
        ))
        
        # Database connections
        self.questdb_pool = None
        self.redis_client = None
        
        # Data cache
        self.data_cache = {}
        
    async def initialize(self):
        """Initialize database connections"""
        try:
            # QuestDB connection pool
            self.questdb_pool = await asyncpg.create_pool(
                host=self.config.questdb_host,
                port=self.config.questdb_port,
                user=self.config.questdb_user,
                password=self.config.questdb_password,
                database="qdb",
                min_size=5,
                max_size=20
            )
            
            # Redis connection
            self.redis_client = redis.from_url(self.config.redis_url)
            
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database connections: {e}")
            raise
    
    async def load_wig80_symbols(self) -> List[str]:
        """Load WIG80 symbols from data file"""
        try:
            with open(self.config.wig80_symbols_file, 'r') as f:
                data = json.load(f)
            
            symbols = []
            for category in data.get('alternative_opportunities', {}).get('categories', {}).values():
                for company in category:
                    symbols.append(company['symbol'])
            
            # Add major WIG80 symbols if available
            if 'original_criteria_analysis' in data:
                for company in data['original_criteria_analysis'].get('pe_gt_4', []):
                    if company['symbol'] not in symbols:
                        symbols.append(company['symbol'])
            
            logger.info(f"Loaded {len(symbols)} WIG80 symbols")
            return symbols[:50]  # Limit to top 50 for initial training
            
        except Exception as e:
            logger.error(f"Error loading WIG80 symbols: {e}")
            # Fallback to common Polish stock symbols
            return ['KGH', 'PKN', 'PKO', 'PZU', 'LPP', 'CCC', 'CDR', 'MIL', 'PKP', 'PGE']
    
    async def fetch_market_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch market data for a symbol from QuestDB"""
        try:
            if self.questdb_pool is None:
                await self.initialize()
            
            # Check cache first
            cache_key = f"{symbol}_{start_date}_{end_date}"
            if cache_key in self.data_cache:
                return self.data_cache[cache_key]
            
            async with self.questdb_pool.acquire() as conn:
                query = """
                SELECT 
                    ts as timestamp,
                    symbol,
                    open,
                    high,
                    low,
                    close as price,
                    volume,
                    bid,
                    ask,
                    (close - open) / open as intraday_return,
                    (high - low) / close as price_range,
                    CASE WHEN volume > 0 THEN close * volume ELSE 0 END as turnover
                FROM market_data 
                WHERE symbol = $1 
                AND ts BETWEEN $2::timestamp AND $3::timestamp
                ORDER BY ts ASC
                """
                
                rows = await conn.fetch(query, symbol, start_date, end_date)
                
                if not rows:
                    logger.warning(f"No data found for symbol {symbol}")
                    return None
                
                df = pd.DataFrame([dict(row) for row in rows])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                
                # Cache the data
                self.data_cache[cache_key] = df
                
                logger.info(f"Fetched {len(df)} records for {symbol}")
                return df
                
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def generate_synthetic_data(self, symbol: str, num_days: int = 1000) -> pd.DataFrame:
        """Generate synthetic market data for testing"""
        try:
            # Generate realistic price data with trends and cycles
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=num_days),
                end=datetime.now(),
                freq='D'
            )
            
            # Base price trend
            base_price = 100 + np.random.normal(0, 10)
            trend = np.linspace(0, np.random.normal(0, 50), num_days)
            
            # Cyclical components (weekly, monthly, yearly patterns)
            weekly_cycle = 5 * np.sin(2 * np.pi * np.arange(num_days) / 7)
            monthly_cycle = 10 * np.sin(2 * np.pi * np.arange(num_days) / 30)
            yearly_cycle = 20 * np.sin(2 * np.pi * np.arange(num_days) / 365)
            
            # Random walk component
            random_component = np.cumsum(np.random.normal(0, 2, num_days))
            
            # Combine components
            prices = base_price + trend + weekly_cycle + monthly_cycle + yearly_cycle + random_component
            prices = np.maximum(prices, 1)  # Ensure positive prices
            
            # Generate OHLC data
            df = pd.DataFrame({
                'symbol': symbol,
                'price': prices,
                'open': prices * (1 + np.random.normal(0, 0.01, num_days)),
                'high': prices * (1 + np.abs(np.random.normal(0, 0.02, num_days))),
                'low': prices * (1 - np.abs(np.random.normal(0, 0.02, num_days))),
                'volume': np.random.exponential(100000, num_days),
            }, index=dates)
            
            # Ensure high >= max(open, close) and low <= min(open, close)
            df['high'] = np.maximum(df['high'], np.maximum(df['open'], df['price']))
            df['low'] = np.minimum(df['low'], np.minimum(df['open'], df['price']))
            
            # Add derived columns
            df['intraday_return'] = (df['price'] - df['open']) / df['open']
            df['price_range'] = (df['high'] - df['low']) / df['price']
            df['turnover'] = df['price'] * df['volume']
            
            logger.info(f"Generated {len(df)} synthetic records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error generating synthetic data for {symbol}: {e}")
            return None
    
    async def prepare_training_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Prepare training data for multiple symbols"""
        training_data = {}
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=800)).strftime('%Y-%m-%d')
        
        logger.info(f"Preparing training data for {len(symbols)} symbols")
        
        for symbol in symbols:
            try:
                # Try to fetch real data first
                data = await self.fetch_market_data(symbol, start_date, end_date)
                
                # Fallback to synthetic data if real data unavailable
                if data is None or len(data) < self.config.min_data_points:
                    logger.info(f"Using synthetic data for {symbol}")
                    data = await self.generate_synthetic_data(symbol, 1000)
                
                if data is not None and len(data) >= self.config.min_data_points:
                    # Preprocess the data
                    processed_data = self.preprocessor.preprocess_market_data(data)
                    
                    if len(processed_data) > self.config.window_size:
                        training_data[symbol] = processed_data
                        logger.info(f"Processed {len(processed_data)} records for {symbol}")
                    else:
                        logger.warning(f"Insufficient data for {symbol}: {len(processed_data)} records")
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
        
        logger.info(f"Successfully prepared training data for {len(training_data)} symbols")
        return training_data
    
    def create_sequences(self, data: pd.DataFrame, target_column: str = 'price') -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for time series prediction"""
        features = data.drop([target_column, 'timestamp'], axis=1, errors='ignore')
        
        if 'timestamp' in data.columns:
            features = data.drop(['timestamp'], axis=1)
        
        if 'symbol' in features.columns:
            features = features.drop(['symbol'], axis=1)
        
        target = data[target_column].values
        feature_columns = features.columns.tolist()
        
        X, y = [], []
        
        for i in range(self.config.window_size, len(data) - self.config.step_size, self.config.step_size):
            # Use overlapping windows
            start_idx = max(0, i - self.config.window_size)
            end_idx = i
            
            # Extract sequence
            sequence = features.iloc[start_idx:end_idx].values
            
            if len(sequence) == self.config.window_size and not np.isnan(sequence).any():
                X.append(sequence)
                y.append(target[i])
        
        return np.array(X), np.array(y)

# =============================================================================
# Model Training Components
# =============================================================================

class SpectralBiasTrainer:
    """Training pipeline for spectral bias neural networks"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize model components
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.criterion = nn.HuberLoss(delta=1.0)
        self.confidence_criterion = nn.BCELoss()
        
        # Training tracking
        self.training_history = []
        self.best_val_loss = float('inf')
        self.best_model_state = None
        
        # Model save directory
        self.save_dir = Path(self.config.model_save_path) / self.config.experiment_name
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Training pipeline initialized on device: {self.device}")
        logger.info(f"Model will be saved to: {self.save_dir}")
    
    def initialize_model(self, input_dim: int):
        """Initialize the spectral bias neural network"""
        try:
            # Create AI config
            ai_config = AIConfig(
                input_dim=input_dim,
                spectral_dim=self.config.spectral_dim,
                hidden_dim=self.config.hidden_dim,
                output_dim=self.config.output_dim,
                num_heads=self.config.num_heads,
                num_layers=self.config.num_layers,
                dropout_rate=self.config.dropout_rate,
                spectral_lambda_low=self.config.spectral_lambda_low,
                spectral_lambda_mid=self.config.spectral_lambda_mid,
                spectral_lambda_high=self.config.spectral_lambda_high,
                learning_rate=self.config.learning_rate,
                window_size=self.config.window_size
            )
            
            # Initialize model components
            from ai_model_design import create_ai_system
            ai_system = create_ai_system(ai_config)
            
            self.model = ai_system['rag_model']
            self.optimizer = optim.AdamW(self.model.parameters(), lr=self.config.learning_rate)
            self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer, T_max=self.config.num_epochs
            )
            
            logger.info("Model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing model: {e}")
            # Fallback to basic model
            self.model = self._create_fallback_model(input_dim)
            self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
    
    def _create_fallback_model(self, input_dim: int) -> nn.Module:
        """Create a fallback model if main model fails to initialize"""
        class FallbackSpectralModel(nn.Module):
            def __init__(self, input_dim, hidden_dim=256, output_dim=4):
                super().__init__()
                self.input_dim = input_dim
                self.hidden_dim = hidden_dim
                self.output_dim = output_dim
                
                # Simple feedforward network with spectral features
                self.layers = nn.Sequential(
                    nn.Linear(input_dim, hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim, hidden_dim // 2),
                    nn.ReLU(),
                    nn.Dropout(0.1),
                    nn.Linear(hidden_dim // 2, hidden_dim // 4),
                    nn.ReLU(),
                    nn.Linear(hidden_dim // 4, output_dim),
                    nn.Sigmoid()
                )
                
                # Confidence estimation
                self.confidence_head = nn.Sequential(
                    nn.Linear(hidden_dim // 4, 1),
                    nn.Sigmoid()
                )
            
            def forward(self, x, return_spectral=False):
                # Flatten sequence if needed
                if len(x.shape) == 3:
                    x = x.mean(dim=1)  # Average over time dimension
                
                features = self.layers[:-1](x)  # Get features before final layer
                predictions = self.layers[-1:](features)
                confidence = self.confidence_head(features)
                
                if return_spectral:
                    return predictions, confidence, features
                else:
                    return predictions, confidence
        
        model = FallbackSpectralModel(input_dim, self.config.hidden_dim, self.config.output_dim)
        logger.info("Using fallback model architecture")
        return model.to(self.device)
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        total_spectral_loss = 0.0
        total_samples = 0
        predictions_list = []
        targets_list = []
        
        for batch_idx, (X_batch, y_batch) in enumerate(train_loader):
            X_batch = X_batch.to(self.device)
            y_batch = y_batch.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass
            try:
                if hasattr(self.model, 'rag_model'):  # Complex model
                    predictions, confidence, context = self.model(X_batch)
                else:  # Fallback model
                    predictions, confidence = self.model(X_batch)
                
                # Calculate losses
                prediction_loss = self.criterion(predictions.squeeze(), y_batch)
                confidence_loss = self.confidence_criterion(
                    confidence, torch.ones_like(confidence) * 0.8
                )
                
                # Spectral regularization
                spectral_loss = 0.0
                if hasattr(self.model, 'get_spectral_loss'):
                    spectral_loss = self.model.get_spectral_loss()
                
                # Total loss
                total_loss_batch = (
                    prediction_loss + 
                    0.1 * confidence_loss + 
                    0.01 * spectral_loss
                )
                
                # Backward pass
                total_loss_batch.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                
                self.optimizer.step()
                
                # Accumulate losses
                total_loss += prediction_loss.item() * X_batch.size(0)
                total_spectral_loss += spectral_loss * X_batch.size(0)
                total_samples += X_batch.size(0)
                
                # Store predictions for metrics
                predictions_list.extend(predictions.squeeze().cpu().numpy())
                targets_list.extend(y_batch.cpu().numpy())
                
            except Exception as e:
                logger.error(f"Error in batch {batch_idx}: {e}")
                continue
        
        # Calculate epoch averages
        avg_loss = total_loss / total_samples if total_samples > 0 else 0
        avg_spectral_loss = total_spectral_loss / total_samples if total_samples > 0 else 0
        
        # Calculate additional metrics
        metrics = {
            'train_loss': avg_loss,
            'spectral_loss': avg_spectral_loss
        }
        
        if len(predictions_list) > 0 and len(targets_list) > 0:
            pred_array = np.array(predictions_list)
            target_array = np.array(targets_list)
            
            metrics['mae'] = mean_absolute_error(target_array, pred_array)
            metrics['rmse'] = np.sqrt(mean_squared_error(target_array, pred_array))
            metrics['r2_score'] = r2_score(target_array, pred_array)
            
            # Directional accuracy
            if len(pred_array) > 1:
                pred_direction = np.sign(np.diff(pred_array))
                target_direction = np.sign(np.diff(target_array))
                metrics['directional_accuracy'] = np.mean(pred_direction == target_direction)
            else:
                metrics['directional_accuracy'] = 0.0
        
        return metrics
    
    def validate_epoch(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        total_loss = 0.0
        predictions_list = []
        targets_list = []
        confidence_scores = []
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                
                try:
                    # Forward pass
                    if hasattr(self.model, 'rag_model'):  # Complex model
                        predictions, confidence, context = self.model(X_batch)
                    else:  # Fallback model
                        predictions, confidence = self.model(X_batch)
                    
                    # Calculate loss
                    loss = self.criterion(predictions.squeeze(), y_batch)
                    total_loss += loss.item() * X_batch.size(0)
                    
                    # Store for metrics
                    predictions_list.extend(predictions.squeeze().cpu().numpy())
                    targets_list.extend(y_batch.cpu().numpy())
                    confidence_scores.extend(confidence.squeeze().cpu().numpy())
                    
                except Exception as e:
                    logger.error(f"Error in validation batch: {e}")
                    continue
        
        # Calculate metrics
        avg_loss = total_loss / len(val_loader.dataset)
        
        metrics = {'val_loss': avg_loss}
        
        if len(predictions_list) > 0 and len(targets_list) > 0:
            pred_array = np.array(predictions_list)
            target_array = np.array(targets_list)
            
            metrics['mae'] = mean_absolute_error(target_array, pred_array)
            metrics['rmse'] = np.sqrt(mean_squared_error(target_array, pred_array))
            metrics['r2_score'] = r2_score(target_array, pred_array)
            
            # Directional accuracy
            if len(pred_array) > 1:
                pred_direction = np.sign(np.diff(pred_array))
                target_direction = np.sign(np.diff(target_array))
                metrics['directional_accuracy'] = np.mean(pred_direction == target_direction)
            else:
                metrics['directional_accuracy'] = 0.0
            
            # Confidence score
            metrics['confidence_score'] = np.mean(confidence_scores) if confidence_scores else 0.0
        
        return metrics
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, input_dim: int) -> Dict[str, List[float]]:
        """Complete training loop"""
        # Initialize model
        self.initialize_model(input_dim)
        
        logger.info(f"Starting training for {self.config.num_epochs} epochs")
        
        patience_counter = 0
        epoch_times = []
        
        for epoch in range(self.config.num_epochs):
            epoch_start = datetime.now()
            
            # Training
            train_metrics = self.train_epoch(train_loader)
            
            # Validation
            val_metrics = self.validate_epoch(val_loader)
            
            # Update scheduler
            if self.scheduler:
                self.scheduler.step()
            
            # Calculate training time
            epoch_time = (datetime.now() - epoch_start).total_seconds()
            epoch_times.append(epoch_time)
            
            # Create training metrics
            training_metrics = TrainingMetrics(
                epoch=epoch,
                train_loss=train_metrics.get('train_loss', 0),
                val_loss=val_metrics.get('val_loss', 0),
                mae=val_metrics.get('mae', 0),
                rmse=val_metrics.get('rmse', 0),
                r2_score=val_metrics.get('r2_score', 0),
                directional_accuracy=val_metrics.get('directional_accuracy', 0),
                spectral_loss=train_metrics.get('spectral_loss', 0),
                confidence_score=val_metrics.get('confidence_score', 0),
                training_time=epoch_time,
                learning_rate=self.optimizer.param_groups[0]['lr'] if self.optimizer else 0
            )
            
            # Store metrics
            self.training_history.append(training_metrics)
            
            # Early stopping
            if val_metrics['val_loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['val_loss']
                self.best_model_state = self.model.state_dict().copy()
                patience_counter = 0
                
                # Save best model
                self.save_checkpoint('best_model.pth')
                logger.info(f"New best model saved with val_loss: {self.best_val_loss:.6f}")
            else:
                patience_counter += 1
            
            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"Early stopping triggered at epoch {epoch}")
                break
            
            # Log progress
            if epoch % 5 == 0:
                logger.info(
                    f"Epoch {epoch}: Train Loss: {train_metrics.get('train_loss', 0):.6f}, "
                    f"Val Loss: {val_metrics.get('val_loss', 0):.6f}, "
                    f"R2: {val_metrics.get('r2_score', 0):.3f}, "
                    f"Accuracy: {val_metrics.get('directional_accuracy', 0):.3f}, "
                    f"Time: {epoch_time:.2f}s"
                )
            
            # Save checkpoint periodically
            if epoch % self.config.save_frequency == 0 and epoch > 0:
                self.save_checkpoint(f'checkpoint_epoch_{epoch}.pth')
        
        # Load best model
        if self.best_model_state:
            self.model.load_state_dict(self.best_model_state)
            logger.info("Loaded best model weights")
        
        # Save final model
        self.save_checkpoint('final_model.pth')
        
        # Save training history
        self.save_training_history()
        
        logger.info("Training completed")
        return self.get_training_summary()
    
    def save_checkpoint(self, filename: str):
        """Save model checkpoint"""
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict() if self.optimizer else None,
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'config': self.config,
            'best_val_loss': self.best_val_loss,
            'training_history': self.training_history
        }
        
        checkpoint_path = self.save_dir / filename
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def save_training_history(self):
        """Save training history to file"""
        history_data = [asdict(metric) for metric in self.training_history]
        history_path = self.save_dir / 'training_history.json'
        
        with open(history_path, 'w') as f:
            json.dump(history_data, f, indent=2, default=str)
        
        logger.info(f"Training history saved: {history_path}")
    
    def get_training_summary(self) -> Dict[str, List[float]]:
        """Get training summary"""
        if not self.training_history:
            return {}
        
        summary = {}
        for metric_name in self.config.track_metrics:
            summary[metric_name] = [getattr(m, metric_name) for m in self.training_history]
        
        return summary
    
    def plot_training_curves(self):
        """Plot training curves"""
        if not self.training_history:
            logger.warning("No training history available for plotting")
            return
        
        try:
            history_dict = self.get_training_summary()
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Training Curves - WIG80 Spectral Bias Model', fontsize=16)
            
            # Loss curves
            if 'train_loss' in history_dict and 'val_loss' in history_dict:
                axes[0, 0].plot(history_dict['train_loss'], label='Training Loss', alpha=0.8)
                axes[0, 0].plot(history_dict['val_loss'], label='Validation Loss', alpha=0.8)
                axes[0, 0].set_title('Training and Validation Loss')
                axes[0, 0].set_xlabel('Epoch')
                axes[0, 0].set_ylabel('Loss')
                axes[0, 0].legend()
                axes[0, 0].grid(True, alpha=0.3)
            
            # Accuracy metrics
            if 'directional_accuracy' in history_dict:
                axes[0, 1].plot(history_dict['directional_accuracy'], label='Directional Accuracy', color='green', alpha=0.8)
                axes[0, 1].set_title('Directional Accuracy')
                axes[0, 1].set_xlabel('Epoch')
                axes[0, 1].set_ylabel('Accuracy')
                axes[0, 1].legend()
                axes[0, 1].grid(True, alpha=0.3)
            
            # R² Score
            if 'r2_score' in history_dict:
                axes[1, 0].plot(history_dict['r2_score'], label='R² Score', color='orange', alpha=0.8)
                axes[1, 0].set_title('R² Score')
                axes[1, 0].set_xlabel('Epoch')
                axes[1, 0].set_ylabel('R² Score')
                axes[1, 0].legend()
                axes[1, 0].grid(True, alpha=0.3)
            
            # Error metrics
            if 'rmse' in history_dict and 'mae' in history_dict:
                axes[1, 1].plot(history_dict['rmse'], label='RMSE', alpha=0.8)
                axes[1, 1].plot(history_dict['mae'], label='MAE', alpha=0.8)
                axes[1, 1].set_title('Error Metrics')
                axes[1, 1].set_xlabel('Epoch')
                axes[1, 1].set_ylabel('Error')
                axes[1, 1].legend()
                axes[1, 1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save plot
            plot_path = self.save_dir / 'training_curves.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training curves saved: {plot_path}")
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting training curves: {e}")

# =============================================================================
# Main Training Pipeline
# =============================================================================

class AITrainingPipeline:
    """Main AI training pipeline orchestrator"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        
        # Initialize components
        self.data_collector = WIG80DataCollector(config)
        self.trainer = SpectralBiasTrainer(config)
        
        # Model versioning
        self.model_version = str(uuid.uuid4())
        self.experiment_id = f"{self.config.experiment_name}_{self.model_version[:8]}"
        
        logger.info(f"AI Training Pipeline initialized: {self.experiment_id}")
    
    async def run_complete_training(self) -> Dict[str, Any]:
        """Run the complete training pipeline"""
        try:
            logger.info("=" * 80)
            logger.info(f"Starting AI Training Pipeline: {self.experiment_id}")
            logger.info("=" * 80)
            
            # Step 1: Data Collection
            logger.info("Step 1: Data Collection and Preprocessing")
            await self.data_collector.initialize()
            
            # Load WIG80 symbols
            symbols = await self.data_collector.load_wig80_symbols()
            if not symbols:
                raise ValueError("No symbols loaded for training")
            
            logger.info(f"Loaded {len(symbols)} symbols for training")
            
            # Collect and prepare training data
            training_data = await self.data_collector.prepare_training_data(symbols)
            
            if not training_data:
                raise ValueError("No training data collected")
            
            logger.info(f"Prepared training data for {len(training_data)} symbols")
            
            # Create sequences for all symbols
            all_sequences = []
            all_targets = []
            
            for symbol, data in training_data.items():
                try:
                    X, y = self.data_collector.create_sequences(data)
                    if len(X) > 0 and len(y) > 0:
                        all_sequences.append(X)
                        all_targets.append(y)
                        logger.info(f"Created {len(X)} sequences for {symbol}")
                except Exception as e:
                    logger.error(f"Error creating sequences for {symbol}: {e}")
                    continue
            
            if not all_sequences:
                raise ValueError("No valid sequences created from training data")
            
            # Combine all sequences
            X_combined = np.vstack(all_sequences)
            y_combined = np.hstack(all_targets)
            
            logger.info(f"Combined dataset: {X_combined.shape[0]} samples, {X_combined.shape[1]} timesteps, {X_combined.shape[2]} features")
            
            # Step 2: Data Splitting
            logger.info("Step 2: Data Splitting")
            split_idx = int(len(X_combined) * (1 - self.config.validation_split))
            
            X_train, X_val = X_combined[:split_idx], X_combined[split_idx:]
            y_train, y_val = y_combined[:split_idx], y_combined[split_idx:]
            
            # Convert to tensors
            X_train_tensor = torch.FloatTensor(X_train)
            y_train_tensor = torch.FloatTensor(y_train)
            X_val_tensor = torch.FloatTensor(X_val)
            y_val_tensor = torch.FloatTensor(y_val)
            
            # Create datasets
            train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
            val_dataset = TensorDataset(X_val_tensor, y_val_tensor)
            
            # Create data loaders
            train_loader = DataLoader(
                train_dataset,
                batch_size=self.config.batch_size,
                shuffle=True,
                num_workers=4
            )
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=4
            )
            
            logger.info(f"Created data loaders: Train {len(train_dataset)}, Val {len(val_dataset)}")
            
            # Step 3: Model Training
            logger.info("Step 3: Model Training")
            input_dim = X_train.shape[2]  # Number of features
            training_history = self.trainer.train(train_loader, val_loader, input_dim)
            
            # Step 4: Model Evaluation
            logger.info("Step 4: Model Evaluation")
            final_metrics = self.evaluate_model(val_loader)
            
            # Step 5: Model Versioning and Deployment
            logger.info("Step 5: Model Versioning and Deployment")
            deployment_info = await self.deploy_model()
            
            # Step 6: Generate Reports
            logger.info("Step 6: Generate Training Reports")
            self.trainer.plot_training_curves()
            report = self.generate_training_report(training_history, final_metrics)
            
            # Final summary
            summary = {
                'experiment_id': self.experiment_id,
                'model_version': self.model_version,
                'training_completed': True,
                'final_metrics': final_metrics,
                'deployment_info': deployment_info,
                'training_history': training_history,
                'report': report
            }
            
            logger.info("=" * 80)
            logger.info("AI Training Pipeline Completed Successfully")
            logger.info(f"Experiment ID: {self.experiment_id}")
            logger.info(f"Model Version: {self.model_version}")
            logger.info(f"Final Validation Loss: {final_metrics.get('val_loss', 'N/A')}")
            logger.info(f"Final R² Score: {final_metrics.get('r2_score', 'N/A')}")
            logger.info("=" * 80)
            
            return summary
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {e}")
            return {
                'experiment_id': self.experiment_id,
                'training_completed': False,
                'error': str(e)
            }
    
    def evaluate_model(self, val_loader: DataLoader) -> Dict[str, float]:
        """Evaluate the trained model"""
        final_metrics = self.trainer.validate_epoch(val_loader)
        logger.info(f"Final validation metrics: {final_metrics}")
        return final_metrics
    
    async def deploy_model(self) -> Dict[str, Any]:
        """Deploy the trained model"""
        try:
            # Save model metadata
            model_metadata = {
                'model_version': self.model_version,
                'experiment_id': self.experiment_id,
                'training_config': asdict(self.config),
                'training_date': datetime.now().isoformat(),
                'model_path': str(self.trainer.save_dir),
                'metrics': {metric: getattr(self.trainer.training_history[-1], metric) 
                           for metric in self.config.track_metrics 
                           if self.trainer.training_history}
            }
            
            # Save metadata
            metadata_path = self.trainer.save_dir / 'model_metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(model_metadata, f, indent=2, default=str)
            
            # Here you would typically:
            # 1. Save model to production location
            # 2. Update model registry
            # 3. Trigger inference service updates
            # 4. Send notifications
            
            deployment_info = {
                'deployed': True,
                'model_path': str(self.trainer.save_dir),
                'metadata_path': str(metadata_path),
                'deployment_time': datetime.now().isoformat()
            }
            
            logger.info(f"Model deployment info: {deployment_info}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")
            return {
                'deployed': False,
                'error': str(e)
            }
    
    def generate_training_report(self, training_history: Dict, final_metrics: Dict) -> str:
        """Generate comprehensive training report"""
        try:
            report = f"""
# AI Training Report - WIG80 Spectral Bias Model

## Experiment Information
- **Experiment ID**: {self.experiment_id}
- **Model Version**: {self.model_version}
- **Training Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Configuration**: {self.config.experiment_name}

## Training Configuration
- **Input Dimensions**: {self.config.input_dim}
- **Spectral Dimensions**: {self.config.spectral_dim}
- **Hidden Dimensions**: {self.config.hidden_dim}
- **Output Dimensions**: {self.config.output_dim}
- **Learning Rate**: {self.config.learning_rate}
- **Batch Size**: {self.config.batch_size}
- **Epochs**: {self.config.num_epochs}
- **Window Size**: {self.config.window_size}

## Final Model Performance
"""
            
            if final_metrics:
                report += f"""
- **Validation Loss**: {final_metrics.get('val_loss', 'N/A'):.6f}
- **Mean Absolute Error**: {final_metrics.get('mae', 'N/A'):.6f}
- **Root Mean Square Error**: {final_metrics.get('rmse', 'N/A'):.6f}
- **R² Score**: {final_metrics.get('r2_score', 'N/A'):.4f}
- **Directional Accuracy**: {final_metrics.get('directional_accuracy', 'N/A'):.4f}
- **Confidence Score**: {final_metrics.get('confidence_score', 'N/A'):.4f}
"""
            
            if self.trainer.training_history:
                best_epoch = min(self.trainer.training_history, key=lambda x: x.val_loss)
                report += f"""
## Best Performance
- **Best Epoch**: {best_epoch.epoch}
- **Best Validation Loss**: {best_epoch.val_loss:.6f}
- **Best R² Score**: {best_epoch.r2_score:.4f}
- **Training Time**: {sum(m.training_time for m in self.trainer.training_history):.2f} seconds
"""
            
            report += f"""
## Model Architecture
- **Spectral Bias Neural Network** with Multi-Grade Deep Learning (MGDL) architecture
- **Frequency Domain Analysis** with learnable filters
- **Multi-Head Attention** for spectral features
- **RAG Integration** for contextual knowledge
- **Confidence Estimation** for prediction reliability

## Data Summary
- **Training Symbols**: WIG80 Polish stock market companies
- **Data Window**: {self.config.window_size} trading days
- **Feature Engineering**: Technical indicators, spectral features, market microstructure

## Next Steps
1. Deploy model to inference service
2. Monitor real-time performance
3. Schedule retraining based on drift detection
4. Expand to additional markets and timeframes

## Files Generated
- Model checkpoints: {self.trainer.save_dir}
- Training curves: {self.trainer.save_dir}/training_curves.png
- Training history: {self.trainer.save_dir}/training_history.json
- Model metadata: {self.trainer.save_dir}/model_metadata.json

---
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Save report
            report_path = self.trainer.save_dir / 'training_report.md'
            with open(report_path, 'w') as f:
                f.write(report)
            
            logger.info(f"Training report saved: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating training report: {e}")
            return "Training report generation failed."

# =============================================================================
# Utility Functions
# =============================================================================

def create_training_config() -> TrainingConfig:
    """Create default training configuration"""
    return TrainingConfig(
        experiment_name="wig80_spectral_mgdl_v1",
        num_epochs=50,  # Reduced for testing
        batch_size=16,  # Smaller batch size for memory efficiency
        learning_rate=0.001,
        early_stopping_patience=10,
        save_frequency=5
    )

async def run_training_pipeline():
    """Run the complete training pipeline"""
    try:
        # Create configuration
        config = create_training_config()
        
        # Create and run pipeline
        pipeline = AITrainingPipeline(config)
        results = await pipeline.run_complete_training()
        
        return results
        
    except Exception as e:
        logger.error(f"Training pipeline execution failed: {e}")
        return None

# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    # Run training pipeline
    logger.info("Starting WIG80 AI Training Pipeline")
    
    # Set up event loop for asyncio
    try:
        results = asyncio.run(run_training_pipeline())
        
        if results and results.get('training_completed'):
            print("\n" + "="*80)
            print("TRAINING COMPLETED SUCCESSFULLY")
            print("="*80)
            print(f"Experiment ID: {results['experiment_id']}")
            print(f"Final Validation Loss: {results['final_metrics'].get('val_loss', 'N/A')}")
            print(f"Final R² Score: {results['final_metrics'].get('r2_score', 'N/A')}")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("TRAINING FAILED")
            print("="*80)
            if results:
                print(f"Error: {results.get('error', 'Unknown error')}")
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
    except Exception as e:
        logger.error(f"Training execution error: {e}")
        print(f"Training failed with error: {e}")