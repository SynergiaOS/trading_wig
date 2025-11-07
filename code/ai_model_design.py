"""
AI Model Architecture Implementation for Spectral Bias Neural Networks and RAG Integration

This module provides the complete technical implementation of the AI model architecture
for the WIG80 Polish financial market platform, including spectral bias neural networks,
RAG integration, and real-time processing capabilities.

Author: AI System Architecture Team
Version: 1.0
Date: 2025-11-06
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
import pickle
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import redis
import websockets
from fastapi import FastAPI, WebSocket, BackgroundTasks
from pydantic import BaseModel
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import faiss
import numpy as np
from questdb.ingress import LineSender, TimestampNanos
import httpx
from quantum import QuestDBClient, PocketbaseClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# Data Models and Configurations
# =============================================================================

@dataclass
class AIConfig:
    """Configuration for AI model architecture"""
    # Model Architecture
    input_dim: int = 50
    spectral_dim: int = 128
    hidden_dim: int = 256
    output_dim: int = 4  # price, volume, volatility, sentiment
    num_heads: int = 8
    num_layers: int = 6
    dropout_rate: float = 0.1
    
    # Spectral Bias Parameters
    spectral_lambda_low: float = 0.1
    spectral_lambda_mid: float = 0.2
    spectral_lambda_high: float = 0.3
    spectral_norm_bound: float = 1.0
    
    # RAG Parameters
    embedding_dim: int = 512
    top_k_retrieval: int = 10
    similarity_threshold: float = 0.7
    context_window_size: int = 2048
    
    # Training Parameters
    learning_rate: float = 0.001
    batch_size: int = 32
    num_epochs: int = 100
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    
    # Real-time Processing
    window_size: int = 252  # 1 year of trading days
    step_size: int = 1
    overlap_ratio: float = 0.8
    max_latency_ms: int = 100
    
    # Database Configuration
    questdb_host: str = "localhost"
    questdb_port: int = 9009
    pocketbase_url: str = "http://localhost:8090"
    redis_url: str = "redis://localhost:6379"
    
    # Monitoring
    metrics_interval_seconds: int = 60
    drift_detection_threshold: float = 0.05
    alert_webhook_url: str = ""

class MarketEvent(BaseModel):
    """Market event data model"""
    symbol: str
    timestamp: datetime
    price: float
    volume: float
    high: float
    low: float
    open: float
    event_type: str = "price_update"

class PredictionResult(BaseModel):
    """AI prediction result model"""
    symbol: str
    timestamp: datetime
    prediction_type: str
    value: float
    confidence: float
    spectral_components: Dict[str, float]
    rag_context: List[Dict[str, Any]]
    model_version: str
    latency_ms: float

# =============================================================================
# Spectral Bias Neural Network Components
# =============================================================================

class SpectralTransformLayer(nn.Module):
    """Spectral transformation layer for frequency domain analysis"""
    
    def __init__(self, input_dim: int, spectral_dim: int, num_frequencies: int = 64):
        super().__init__()
        self.input_dim = input_dim
        self.spectral_dim = spectral_dim
        self.num_frequencies = num_frequencies
        
        # FFT-based feature extraction
        self.fft_weights_real = nn.Parameter(torch.randn(num_frequencies, input_dim))
        self.fft_weights_imag = nn.Parameter(torch.randn(num_frequencies, input_dim))
        
        # Learnable frequency filters
        self.frequency_filters = nn.Parameter(torch.ones(num_frequencies))
        
        # Output projection
        self.output_projection = nn.Linear(num_frequencies * 2, spectral_dim)
        self.layer_norm = nn.LayerNorm(spectral_dim)
        self.dropout = nn.Dropout(0.1)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply spectral transformation to input tensor
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_dim)
            
        Returns:
            Spectral features of shape (batch_size, sequence_length, spectral_dim)
        """
        batch_size, seq_len, input_dim = x.shape
        
        # Apply FFT weights
        fft_real = torch.matmul(x, self.fft_weights_real.t())
        fft_imag = torch.matmul(x, self.fft_weights_imag.t())
        
        # Apply frequency filters
        fft_real = fft_real * self.frequency_filters.view(1, 1, -1)
        fft_imag = fft_imag * self.frequency_filters.view(1, 1, -1)
        
        # Concatenate real and imaginary parts
        fft_features = torch.cat([fft_real, fft_imag], dim=-1)
        
        # Project to spectral dimension
        spectral_features = self.output_projection(fft_features)
        spectral_features = self.layer_norm(spectral_features)
        spectral_features = self.dropout(spectral_features)
        
        return spectral_features

class MultiHeadSpectralAttention(nn.Module):
    """Multi-head attention mechanism for spectral features"""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len, d_model = x.size()
        
        # Linear transformations for Q, K, V
        Q = self.w_q(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(x).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(
            batch_size, seq_len, d_model
        )
        
        # Output projection
        output = self.w_o(context)
        output = self.layer_norm(output + x)  # Residual connection
        
        return output

class SpectralBiasRegularization(nn.Module):
    """Spectral bias regularization layer"""
    
    def __init__(self, spectral_lambda_low: float, spectral_lambda_mid: float, 
                 spectral_lambda_high: float, freq_bands: List[Tuple[int, int]] = None):
        super().__init__()
        self.lambda_low = spectral_lambda_low
        self.lambda_mid = spectral_lambda_mid  
        self.lambda_high = spectral_lambda_high
        
        # Default frequency bands (Hz)
        if freq_bands is None:
            self.freq_bands = [
                (0, 10),    # Low frequency: long-term trends
                (10, 30),   # Mid frequency: weekly patterns
                (30, 50)    # High frequency: daily volatility
            ]
        else:
            self.freq_bands = freq_bands
            
    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """
        Apply spectral bias regularization to weights
        
        Args:
            weights: Model weights to regularize
            
        Returns:
            Spectral regularization loss
        """
        spectral_loss = 0.0
        
        # Get frequency domain representation via FFT
        fft_weights = torch.fft.fft(weights, dim=-1)
        freqs = torch.fft.fftfreq(weights.size(-1))
        
        # Apply regularization to different frequency bands
        for i, (low_freq, high_freq) in enumerate(self.freq_bands):
            # Create frequency band mask
            band_mask = ((freqs >= low_freq/100) & (freqs < high_freq/100))
            
            # Select weights in this frequency band
            band_weights = fft_weights * band_mask
            
            # Apply regularization coefficient
            if i == 0:  # Low frequency
                reg_coeff = self.lambda_low
            elif i == 1:  # Mid frequency
                reg_coeff = self.lambda_mid
            else:  # High frequency
                reg_coeff = self.lambda_high
                
            spectral_loss += reg_coeff * torch.sum(torch.abs(band_weights) ** 2)
            
        return spectral_loss

class SpectralBiasNeuralNetwork(nn.Module):
    """Complete spectral bias neural network for financial time series"""
    
    def __init__(self, config: AIConfig):
        super().__init__()
        self.config = config
        
        # Input layer
        self.input_projection = nn.Linear(config.input_dim, config.hidden_dim)
        
        # Spectral transformation
        self.spectral_transform = SpectralTransformLayer(
            config.hidden_dim, config.spectral_dim
        )
        
        # Multi-head spectral attention
        self.spectral_attention_layers = nn.ModuleList([
            MultiHeadSpectralAttention(config.spectral_dim, config.num_heads, config.dropout_rate)
            for _ in range(config.num_layers // 2)
        ])
        
        # Hidden layers
        self.hidden_layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(config.spectral_dim if i == 0 else config.hidden_dim, 
                         config.hidden_dim),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate),
                nn.LayerNorm(config.hidden_dim)
            ) for i in range(3)
        ])
        
        # Spectral bias regularization
        self.spectral_regularization = SpectralBiasRegularization(
            config.spectral_lambda_low,
            config.spectral_lambda_mid,
            config.spectral_lambda_high
        )
        
        # Output layer
        self.output_projection = nn.Linear(config.hidden_dim, config.output_dim)
        
        # Confidence estimation
        self.confidence_estimator = nn.Sequential(
            nn.Linear(config.hidden_dim, config.hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dim // 2, 1),
            nn.Sigmoid()  # Output confidence between 0 and 1
        )
        
    def forward(self, x: torch.Tensor, return_spectral: bool = False) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through the network
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_dim)
            return_spectral: Whether to return spectral components
            
        Returns:
            predictions: Model predictions
            confidence: Prediction confidence scores
            spectral_features: Optional spectral components
        """
        # Input projection
        x = self.input_projection(x)
        
        # Spectral transformation
        spectral_features = self.spectral_transform(x)
        
        # Multi-head spectral attention
        for attention_layer in self.spectral_attention_layers:
            spectral_features = attention_layer(spectral_features)
        
        # Hidden layers
        for hidden_layer in self.hidden_layers:
            x = hidden_layer(x)
        
        # Combine spectral and hidden features
        combined_features = x + spectral_features
        
        # Output projection
        predictions = self.output_projection(combined_features)
        
        # Confidence estimation
        confidence = self.confidence_estimator(combined_features)
        
        if return_spectral:
            return predictions, confidence, spectral_features
        else:
            return predictions, confidence
    
    def get_spectral_loss(self) -> torch.Tensor:
        """Calculate spectral bias regularization loss"""
        spectral_loss = 0.0
        
        for module in self.modules():
            if isinstance(module, nn.Linear):
                spectral_loss += self.spectral_regularization(module.weight)
                
        return spectral_loss

# =============================================================================
# RAG Integration Components
# =============================================================================

class FinancialEmbeddingModel(nn.Module):
    """Financial domain-specific embedding model"""
    
    def __init__(self, vocab_size: int, embedding_dim: int, max_length: int = 512):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.max_length = max_length
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, embedding_dim)
        
        # Positional embedding
        self.positional_embedding = nn.Embedding(max_length, embedding_dim)
        
        # Financial domain adaptation
        self.domain_adapter = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim * 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(embedding_dim * 2, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )
        
        # Context fusion
        self.context_fusion = nn.MultiheadAttention(
            embedding_dim, 
            num_heads=8, 
            dropout=0.1,
            batch_first=True
        )
        
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Generate embeddings for financial text
        
        Args:
            input_ids: Token IDs of shape (batch_size, sequence_length)
            attention_mask: Attention mask of shape (batch_size, sequence_length)
            
        Returns:
            Text embeddings of shape (batch_size, embedding_dim)
        """
        batch_size, seq_len = input_ids.shape
        
        # Create position indices
        position_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).expand(batch_size, -1)
        
        # Token and positional embeddings
        token_embeds = self.token_embedding(input_ids)
        pos_embeds = self.positional_embedding(position_ids)
        
        # Combine embeddings
        embeddings = token_embeds + pos_embeds
        
        # Apply financial domain adaptation
        embeddings = self.domain_adapter(embeddings)
        
        # Context fusion
        if attention_mask is not None:
            # Expand attention mask for multi-head attention
            attn_mask = attention_mask.unsqueeze(1).expand(-1, seq_len, -1)
        else:
            attn_mask = None
            
        context_embeddings, _ = self.context_fusion(embeddings, embeddings, embeddings, attn_mask=attn_mask)
        
        # Pool to get sentence embeddings (using mean pooling)
        if attention_mask is not None:
            mask_expanded = attention_mask.unsqueeze(-1).expand(context_embeddings.size())
            sum_embeddings = torch.sum(context_embeddings * mask_expanded, 1)
            sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
            pooled_embeddings = sum_embeddings / sum_mask
        else:
            pooled_embeddings = torch.mean(context_embeddings, 1)
            
        return pooled_embeddings

class RAGKnowledgeBase:
    """RAG knowledge base for financial information"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.embedding_model = FinancialEmbeddingModel(
            vocab_size=50000,  # Financial domain vocabulary size
            embedding_dim=config.embedding_dim
        )
        
        # Vector database (FAISS)
        self.index = faiss.IndexHNSWFlat(config.embedding_dim, 32)
        self.knowledge_store = []
        self.metadata_store = []
        
        # Redis cache for frequently accessed information
        self.redis_client = redis.from_url(config.redis_url)
        
    def add_document(self, document: str, metadata: Dict[str, Any], source_id: str):
        """
        Add a document to the knowledge base
        
        Args:
            document: Text content
            metadata: Document metadata
            source_id: Unique source identifier
        """
        # Convert document to embeddings
        # This would typically use a tokenizer and the embedding model
        # For simplicity, we'll use a placeholder approach
        embedding = self._get_placeholder_embedding(document)
        
        # Normalize embedding
        embedding = embedding / np.linalg.norm(embedding)
        
        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))
        
        # Store document and metadata
        self.knowledge_store.append(document)
        self.metadata_store.append({
            'source_id': source_id,
            'timestamp': datetime.now(),
            'metadata': metadata,
            'embedding_id': len(self.knowledge_store) - 1
        })
        
        logger.info(f"Added document {source_id} to knowledge base")
        
    def _get_placeholder_embedding(self, text: str) -> np.ndarray:
        """Placeholder for text embedding generation"""
        # In a real implementation, this would use the actual embedding model
        # For now, return a random embedding for demonstration
        return np.random.randn(self.config.embedding_dim)
        
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Query text
            top_k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents with scores and metadata
        """
        if top_k is None:
            top_k = self.config.top_k_retrieval
            
        # Generate query embedding
        query_embedding = self._get_placeholder_embedding(query)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        
        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.knowledge_store):
                result = {
                    'document': self.knowledge_store[idx],
                    'score': float(score),
                    'metadata': self.metadata_store[idx],
                    'similarity': float(score)  # FAISS returns L2 distance
                }
                results.append(result)
                
        return results
    
    def update_with_market_data(self, symbol: str, data: Dict[str, Any]):
        """Update knowledge base with real-time market data"""
        # Convert market data to text
        market_text = self._format_market_data(symbol, data)
        
        # Add to knowledge base
        self.add_document(
            document=market_text,
            metadata={'type': 'market_data', 'symbol': symbol},
            source_id=f"market_{symbol}_{datetime.now().timestamp()}"
        )
        
    def _format_market_data(self, symbol: str, data: Dict[str, Any]) -> str:
        """Format market data as text for the knowledge base"""
        formatted = f"Market data for {symbol}:\n"
        for key, value in data.items():
            formatted += f"- {key}: {value}\n"
        return formatted

class RAGNeuralNetwork(nn.Module):
    """RAG-enhanced neural network for financial prediction"""
    
    def __init__(self, spectral_model: SpectralBiasNeuralNetwork, 
                 knowledge_base: RAGKnowledgeBase, config: AIConfig):
        super().__init__()
        self.spectral_model = spectral_model
        self.knowledge_base = knowledge_base
        self.config = config
        
        # Context fusion layer
        self.context_fusion = nn.Sequential(
            nn.Linear(config.hidden_dim + config.embedding_dim, config.hidden_dim),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.LayerNorm(config.hidden_dim)
        )
        
        # RAG attention mechanism
        self.rag_attention = nn.MultiheadAttention(
            config.hidden_dim,
            num_heads=8,
            dropout=config.dropout_rate,
            batch_first=True
        )
        
        # Final prediction layer
        self.final_prediction = nn.Linear(config.hidden_dim, config.output_dim)
        self.final_confidence = nn.Linear(config.hidden_dim, 1)
        
    def forward(self, x: torch.Tensor, query: str = None) -> Tuple[torch.Tensor, torch.Tensor, List[Dict[str, Any]]]:
        """
        Forward pass with RAG integration
        
        Args:
            x: Input market data
            query: Optional query for RAG retrieval
            
        Returns:
            predictions: Model predictions
            confidence: Confidence scores
            retrieved_context: Retrieved knowledge context
        """
        # Get spectral model predictions
        spectral_pred, spectral_conf, spectral_features = self.spectral_model(x, return_spectral=True)
        
        # Retrieve relevant knowledge if query is provided
        retrieved_context = []
        if query is not None:
            retrieved_context = self.knowledge_base.retrieve(query)
            
            # Convert retrieved context to embeddings (placeholder)
            context_embeddings = torch.randn(
                len(retrieved_context), self.config.embedding_dim
            )
            
            # Apply RAG attention
            if len(retrieved_context) > 0:
                # Expand spectral features for attention
                expanded_spectral = spectral_features.mean(dim=1, keepdim=True)
                expanded_spectral = expanded_spectral.expand(-1, len(retrieved_context), -1)
                
                # Apply attention between market data and retrieved knowledge
                attended_features, attention_weights = self.rag_attention(
                    expanded_spectral, 
                    context_embeddings.unsqueeze(0).expand(expanded_spectral.size(0), -1, -1),
                    context_embeddings.unsqueeze(0).expand(expanded_spectral.size(0), -1, -1)
                )
                
                # Fuse spectral and retrieved features
                combined_features = self.context_fusion(
                    torch.cat([spectral_features.mean(dim=1), 
                              attended_features.mean(dim=1)], dim=-1)
                )
            else:
                combined_features = spectral_features.mean(dim=1)
        else:
            combined_features = spectral_features.mean(dim=1)
        
        # Final predictions
        final_predictions = self.final_prediction(combined_features)
        final_confidence = self.final_confidence(combined_features).squeeze()
        
        return final_predictions, final_confidence, retrieved_context

# =============================================================================
# Data Preprocessing Pipeline
# =============================================================================

class FinancialDataPreprocessor:
    """Comprehensive data preprocessing pipeline for financial time series"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.scalers = {
            'price': MinMaxScaler(),
            'volume': RobustScaler(),
            'technical': StandardScaler(),
            'spectral': MinMaxScaler()
        }
        self.feature_cache = {}
        self.data_quality_threshold = 0.8
        
    def preprocess_market_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess raw market data
        
        Args:
            data: Raw market data DataFrame
            
        Returns:
            Preprocessed data with features
        """
        # Data quality validation
        data = self._validate_data_quality(data)
        
        # Handle missing values
        data = self._handle_missing_values(data)
        
        # Detect and handle outliers
        data = self._handle_outliers(data)
        
        # Feature engineering
        data = self._compute_technical_indicators(data)
        data = self._compute_spectral_features(data)
        
        # Normalization
        data = self._normalize_features(data)
        
        return data
    
    def _validate_data_quality(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate data quality and flag issues"""
        quality_issues = []
        
        # Check for missing values
        missing_ratio = data.isnull().sum() / len(data)
        for col, ratio in missing_ratio.items():
            if ratio > 0.1:  # More than 10% missing
                quality_issues.append(f"Column {col}: {ratio:.2%} missing values")
                
        # Check for price anomalies
        if 'price' in data.columns:
            price_changes = data['price'].pct_change().abs()
            extreme_changes = (price_changes > 0.1).sum()  # 10% price changes
            if extreme_changes > len(data) * 0.05:  # More than 5% extreme changes
                quality_issues.append(f"Extreme price changes detected: {extreme_changes}")
        
        # Log quality issues
        if quality_issues:
            logger.warning(f"Data quality issues detected: {quality_issues}")
            
        return data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values based on market context"""
        # Forward fill for short gaps (within market hours)
        data = data.fillna(method='ffill', limit=5)
        
        # Interpolate for medium gaps
        data = data.interpolate(method='linear', limit=10)
        
        # Drop rows with excessive missing values
        data = data.dropna(thresh=len(data.columns) * 0.8)
        
        return data
    
    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Detect and handle outliers in financial data"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in ['price', 'volume', 'high', 'low']:
                # Use IQR method for price and volume data
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Cap extreme values
                data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)
                
        return data
    
    def _compute_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Compute technical indicators for financial analysis"""
        # Moving averages
        for period in [5, 10, 20, 50]:
            data[f'sma_{period}'] = data['price'].rolling(window=period).mean()
            data[f'ema_{period}'] = data['price'].ewm(span=period).mean()
        
        # RSI
        delta = data['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = data['price'].ewm(span=12).mean()
        ema_26 = data['price'].ewm(span=26).mean()
        data['macd'] = ema_12 - ema_26
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        # Bollinger Bands
        data['bb_middle'] = data['price'].rolling(window=20).mean()
        bb_std = data['price'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        data['bb_position'] = (data['price'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        # Volume indicators
        data['volume_sma_20'] = data['volume'].rolling(window=20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma_20']
        
        # Volatility
        data['returns'] = data['price'].pct_change()
        data['volatility_20'] = data['returns'].rolling(window=20).std() * np.sqrt(252)
        
        return data
    
    def _compute_spectral_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Compute frequency domain features for spectral analysis"""
        price_series = data['price'].values
        
        # FFT analysis
        fft_values = np.fft.fft(price_series)
        fft_magnitude = np.abs(fft_values)
        fft_phase = np.angle(fft_values)
        
        # Power spectral density
        psd = fft_magnitude ** 2 / len(fft_magnitude)
        frequencies = np.fft.fftfreq(len(price_series))
        
        # Extract frequency bands
        positive_freq_idx = frequencies > 0
        positive_frequencies = frequencies[positive_freq_idx]
        positive_psd = psd[positive_freq_idx]
        
        # Low frequency component (trends)
        low_freq_mask = (positive_frequencies >= 0) & (positive_frequencies <= 0.1)
        data['spectral_low'] = np.sum(positive_psd[low_freq_mask])
        
        # Mid frequency component (cycles)
        mid_freq_mask = (positive_frequencies > 0.1) & (positive_frequencies <= 0.5)
        data['spectral_mid'] = np.sum(positive_psd[mid_freq_mask])
        
        # High frequency component (noise)
        high_freq_mask = positive_frequencies > 0.5
        data['spectral_high'] = np.sum(positive_psd[high_freq_mask])
        
        # Spectral features
        data['spectral_centroid'] = np.sum(positive_frequencies * positive_psd) / np.sum(positive_psd)
        data['spectral_rolloff'] = self._compute_spectral_rolloff(positive_frequencies, positive_psd)
        data['spectral_flatness'] = self._compute_spectral_flatness(fft_magnitude)
        data['spectral_entropy'] = self._compute_spectral_entropy(fft_magnitude)
        
        return data
    
    def _compute_spectral_rolloff(self, frequencies: np.ndarray, psd: np.ndarray, rolloff_percent: float = 0.85) -> float:
        """Compute spectral rolloff frequency"""
        cumulative_psd = np.cumsum(psd)
        total_psd = cumulative_psd[-1]
        rolloff_threshold = rolloff_percent * total_psd
        
        rolloff_idx = np.where(cumulative_psd >= rolloff_threshold)[0]
        if len(rolloff_idx) > 0:
            return frequencies[rolloff_idx[0]]
        else:
            return frequencies[-1]
    
    def _compute_spectral_flatness(self, fft_magnitude: np.ndarray) -> float:
        """Compute spectral flatness measure"""
        # Remove DC component
        fft_magnitude = fft_magnitude[1:]
        
        # Geometric mean
        geometric_mean = np.exp(np.mean(np.log(fft_magnitude + 1e-10)))
        
        # Arithmetic mean
        arithmetic_mean = np.mean(fft_magnitude)
        
        # Spectral flatness
        return geometric_mean / (arithmetic_mean + 1e-10)
    
    def _compute_spectral_entropy(self, fft_magnitude: np.ndarray) -> float:
        """Compute spectral entropy"""
        # Normalize to probability distribution
        psd = fft_magnitude ** 2
        psd = psd / np.sum(psd)
        
        # Compute entropy
        entropy = -np.sum(psd * np.log2(psd + 1e-10))
        return entropy
    
    def _normalize_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normalize features using appropriate scalers"""
        # Price-based features
        price_features = [col for col in data.columns if any(x in col for x in ['price', 'sma', 'ema', 'bb', 'macd'])]
        for feature in price_features:
            if feature in data.columns and not data[feature].isna().all():
                data[feature] = self.scalers['price'].fit_transform(data[feature].values.reshape(-1, 1)).flatten()
        
        # Volume features
        volume_features = [col for col in data.columns if 'volume' in col]
        for feature in volume_features:
            if feature in data.columns and not data[feature].isna().all():
                data[feature] = self.scalers['volume'].fit_transform(data[feature].values.reshape(-1, 1)).flatten()
        
        # Technical indicators
        technical_features = [col for col in data.columns if any(x in col for x in ['rsi', 'volatility', 'returns'])]
        for feature in technical_features:
            if feature in data.columns and not data[feature].isna().all():
                data[feature] = self.scalers['technical'].fit_transform(data[feature].values.reshape(-1, 1)).flatten()
        
        # Spectral features
        spectral_features = [col for col in data.columns if 'spectral' in col]
        for feature in spectral_features:
            if feature in data.columns and not data[feature].isna().all():
                data[feature] = self.scalers['spectral'].fit_transform(data[feature].values.reshape(-1, 1)).flatten()
        
        return data
    
    def create_sequences(self, data: pd.DataFrame, target_column: str = 'price') -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time series prediction
        
        Args:
            data: Preprocessed data
            target_column: Target variable column
            
        Returns:
            X: Input sequences
            y: Target values
        """
        features = data.drop([target_column, 'timestamp'], axis=1, errors='ignore')
        target = data[target_column].values
        
        # Create sequences
        X, y = [], []
        for i in range(self.config.window_size, len(data) - self.config.step_size, self.config.step_size):
            # Use overlapping windows
            start_idx = max(0, i - self.config.window_size)
            end_idx = i
            
            # Extract sequence
            sequence = features.iloc[start_idx:end_idx].values
            if len(sequence) == self.config.window_size:
                X.append(sequence)
                y.append(target[i])
        
        return np.array(X), np.array(y)

# =============================================================================
# Training Pipeline
# =============================================================================

class AITrainingPipeline:
    """Complete training pipeline for spectral bias neural networks with RAG"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.preprocessor = FinancialDataPreprocessor(config)
        
        # Initialize models
        self.spectral_model = SpectralBiasNeuralNetwork(config)
        self.knowledge_base = RAGKnowledgeBase(config)
        self.rag_model = RAGNeuralNetwork(self.spectral_model, self.knowledge_base, config)
        
        # Training utilities
        self.optimizer = optim.AdamW(self.rag_model.parameters(), lr=config.learning_rate)
        self.scheduler = optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=config.num_epochs
        )
        self.criterion = nn.HuberLoss(delta=1.0)  # Robust to outliers
        self.confidence_criterion = nn.BCELoss()
        
        # Training metrics
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'spectral_loss': [],
            'accuracy': [],
            'sharpe_ratio': []
        }
        
    def prepare_training_data(self, market_data: pd.DataFrame) -> Tuple[DataLoader, DataLoader]:
        """
        Prepare training and validation data loaders
        
        Args:
            market_data: Historical market data
            
        Returns:
            train_loader, val_loader: Data loaders for training and validation
        """
        # Preprocess data
        processed_data = self.preprocessor.preprocess_market_data(market_data)
        
        # Create sequences
        X, y = self.preprocessor.create_sequences(processed_data)
        
        # Convert to tensors
        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.FloatTensor(y)
        
        # Create datasets
        dataset = TensorDataset(X_tensor, y_tensor)
        
        # Split into train/validation
        split_idx = int(len(dataset) * (1 - self.config.validation_split))
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [split_idx, len(dataset) - split_idx]
        )
        
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
        
        return train_loader, val_loader
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.rag_model.train()
        total_loss = 0.0
        total_spectral_loss = 0.0
        total_samples = 0
        
        for batch_idx, (X_batch, y_batch) in enumerate(train_loader):
            self.optimizer.zero_grad()
            
            # Forward pass
            predictions, confidence, context = self.rag_model(X_batch)
            
            # Calculate losses
            prediction_loss = self.criterion(predictions.squeeze(), y_batch)
            confidence_loss = self.confidence_criterion(
                confidence, torch.ones_like(confidence) * 0.8  # Target high confidence
            )
            spectral_loss = self.spectral_model.get_spectral_loss()
            
            # Total loss
            total_loss_batch = (
                prediction_loss + 
                0.1 * confidence_loss + 
                0.01 * spectral_loss
            )
            
            # Backward pass
            total_loss_batch.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.rag_model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            # Accumulate losses
            total_loss += prediction_loss.item() * X_batch.size(0)
            total_spectral_loss += spectral_loss.item() * X_batch.size(0)
            total_samples += X_batch.size(0)
            
        # Calculate epoch averages
        avg_loss = total_loss / total_samples
        avg_spectral_loss = total_spectral_loss / total_samples
        
        return {
            'train_loss': avg_loss,
            'spectral_loss': avg_spectral_loss
        }
    
    def validate_epoch(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate for one epoch"""
        self.rag_model.eval()
        total_loss = 0.0
        predictions_list = []
        targets_list = []
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                # Forward pass
                predictions, confidence, context = self.rag_model(X_batch)
                
                # Calculate loss
                loss = self.criterion(predictions.squeeze(), y_batch)
                total_loss += loss.item() * X_batch.size(0)
                
                # Store for metrics
                predictions_list.extend(predictions.squeeze().cpu().numpy())
                targets_list.extend(y_batch.cpu().numpy())
        
        # Calculate metrics
        avg_loss = total_loss / len(val_loader.dataset)
        
        # Calculate accuracy and Sharpe ratio
        predictions_array = np.array(predictions_list)
        targets_array = np.array(targets_list)
        
        # Directional accuracy
        pred_direction = np.sign(np.diff(predictions_array))
        target_direction = np.sign(np.diff(targets_array))
        directional_accuracy = np.mean(pred_direction == target_direction)
        
        # Sharpe ratio (simplified)
        returns = np.diff(targets_array) / targets_array[:-1]
        sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-10) if len(returns) > 1 else 0
        
        return {
            'val_loss': avg_loss,
            'accuracy': directional_accuracy,
            'sharpe_ratio': sharpe_ratio
        }
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict[str, List[float]]:
        """Complete training loop"""
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.num_epochs):
            # Training
            train_metrics = self.train_epoch(train_loader)
            
            # Validation
            val_metrics = self.validate_epoch(val_loader)
            
            # Update scheduler
            self.scheduler.step()
            
            # Store metrics
            self.training_history['train_loss'].append(train_metrics['train_loss'])
            self.training_history['val_loss'].append(val_metrics['val_loss'])
            self.training_history['spectral_loss'].append(train_metrics['spectral_loss'])
            self.training_history['accuracy'].append(val_metrics['accuracy'])
            self.training_history['sharpe_ratio'].append(val_metrics['sharpe_ratio'])
            
            # Early stopping
            if val_metrics['val_loss'] < best_val_loss:
                best_val_loss = val_metrics['val_loss']
                patience_counter = 0
                
                # Save best model
                torch.save(self.rag_model.state_dict(), 'best_model.pth')
            else:
                patience_counter += 1
                
            if patience_counter >= self.config.early_stopping_patience:
                logger.info(f"Early stopping triggered at epoch {epoch}")
                break
            
            # Log progress
            if epoch % 10 == 0:
                logger.info(
                    f"Epoch {epoch}: Train Loss: {train_metrics['train_loss']:.6f}, "
                    f"Val Loss: {val_metrics['val_loss']:.6f}, "
                    f"Accuracy: {val_metrics['accuracy']:.3f}"
                )
        
        # Load best model
        self.rag_model.load_state_dict(torch.load('best_model.pth'))
        
        return self.training_history

# =============================================================================
# Real-time Inference Pipeline
# =============================================================================

class RealTimeAIPipeline:
    """Real-time AI inference pipeline for financial data"""
    
    def __init__(self, config: AIConfig, training_pipeline: AITrainingPipeline):
        self.config = config
        self.training_pipeline = training_pipeline
        
        # Load trained model
        self.rag_model = training_pipeline.rag_model
        self.rag_model.eval()
        
        # Initialize clients
        self.questdb_client = QuestDBClient(config.questdb_host, config.questdb_port)
        self.pocketbase_client = PocketbaseClient(config.pocketbase_url)
        self.redis_client = redis.from_url(config.redis_url)
        
        # WebSocket connections
        self.websocket_connections = set()
        self.websocket_app = FastAPI()
        self._setup_websocket_endpoint()
        
        # Feature cache
        self.feature_cache = {}
        self.context_cache = {}
        
    def _setup_websocket_endpoint(self):
        """Setup WebSocket endpoint for real-time updates"""
        @self.websocket_app.websocket("/ws/ai_updates")
        async def ai_websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_connections.add(websocket)
            
            try:
                while True:
                    # Keep connection alive
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                self.websocket_connections.discard(websocket)
    
    async def process_realtime_market_event(self, event: MarketEvent) -> Optional[PredictionResult]:
        """
        Process real-time market event and generate AI prediction
        
        Args:
            event: Market event data
            
        Returns:
            PredictionResult if successful, None otherwise
        """
        start_time = datetime.now()
        
        try:
            # Update feature cache
            await self._update_feature_cache(event)
            
            # Get recent data for context
            recent_data = await self._get_recent_market_data(event.symbol)
            
            if recent_data is None or len(recent_data) < self.config.window_size:
                logger.warning(f"Insufficient data for {event.symbol}")
                return None
            
            # Preprocess data
            processed_data = self.training_pipeline.preprocessor.preprocess_market_data(recent_data)
            
            # Create input sequence
            X, _ = self.training_pipeline.preprocessor.create_sequences(processed_data)
            if len(X) == 0:
                return None
            
            # Get latest sequence
            latest_sequence = torch.FloatTensor(X[-1:])  # Add batch dimension
            
            # Generate query for RAG
            query = self._generate_market_query(event, recent_data)
            
            # Make prediction
            with torch.no_grad():
                predictions, confidence, context = self.rag_model(latest_sequence, query)
            
            # Convert to results
            prediction_result = self._format_prediction_result(
                event, predictions, confidence, context, start_time
            )
            
            # Store prediction
            await self._store_prediction(prediction_result)
            
            # Broadcast to WebSocket clients
            await self._broadcast_prediction(prediction_result)
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error processing market event: {e}")
            return None
    
    async def _update_feature_cache(self, event: MarketEvent):
        """Update feature cache with new market event"""
        symbol = event.symbol
        
        if symbol not in self.feature_cache:
            self.feature_cache[symbol] = []
        
        # Add new event
        feature_data = {
            'timestamp': event.timestamp,
            'price': event.price,
            'volume': event.volume,
            'high': event.high,
            'low': event.low,
            'open': event.open
        }
        
        self.feature_cache[symbol].append(feature_data)
        
        # Keep only recent data
        cutoff_time = event.timestamp - timedelta(days=30)  # Keep 30 days
        self.feature_cache[symbol] = [
            item for item in self.feature_cache[symbol] 
            if item['timestamp'] > cutoff_time
        ]
    
    async def _get_recent_market_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get recent market data from QuestDB"""
        try:
            # Query recent data
            query = f"""
            SELECT timestamp, price, volume, high, low, open
            FROM market_data 
            WHERE symbol = '{symbol}'
            AND timestamp > NOW() - INTERVAL '30' DAY
            ORDER BY timestamp
            """
            
            result = await self.questdb_client.query(query)
            
            if result is None or len(result) == 0:
                return None
            
            return pd.DataFrame(result)
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def _generate_market_query(self, event: MarketEvent, recent_data: pd.DataFrame) -> str:
        """Generate query for RAG retrieval based on market context"""
        current_price = event.price
        recent_prices = recent_data['price'].tail(10)
        price_change = (current_price - recent_prices.iloc[0]) / recent_prices.iloc[0] * 100
        
        # Generate market analysis query
        if price_change > 5:
            query = f"{event.symbol} strong price increase bullish momentum breakout"
        elif price_change < -5:
            query = f"{event.symbol} price decline bearish pressure support levels"
        elif abs(price_change) < 1:
            query = f"{event.symbol} sideways movement consolidation range trading"
        else:
            query = f"{event.symbol} normal trading activity market conditions"
            
        return query
    
    def _format_prediction_result(self, event: MarketEvent, predictions: torch.Tensor, 
                                 confidence: torch.Tensor, context: List[Dict[str, Any]], 
                                 start_time: datetime) -> PredictionResult:
        """Format prediction result"""
        # Convert tensors to scalars
        pred_values = predictions.squeeze().cpu().numpy()
        conf_value = confidence.squeeze().cpu().numpy()
        
        # Map predictions to types
        prediction_types = ['price_direction', 'volatility', 'volume_forecast', 'sentiment']
        
        result = PredictionResult(
            symbol=event.symbol,
            timestamp=event.timestamp,
            prediction_type='comprehensive',
            value=float(pred_values[0]),  # Main prediction (price direction)
            confidence=float(conf_value),
            spectral_components={
                'low_freq_trend': float(pred_values[1]) if len(pred_values) > 1 else 0.0,
                'mid_freq_cycle': float(pred_values[2]) if len(pred_values) > 2 else 0.0,
                'high_freq_noise': float(pred_values[3]) if len(pred_values) > 3 else 0.0
            },
            rag_context=context,
            model_version="1.0",
            latency_ms=(datetime.now() - start_time).total_seconds() * 1000
        )
        
        return result
    
    async def _store_prediction(self, prediction: PredictionResult):
        """Store prediction in QuestDB and Pocketbase"""
        try:
            # Store in QuestDB
            await self.questdb_client.insert(
                'ai_predictions',
                {
                    'symbol': prediction.symbol,
                    'ts': prediction.timestamp,
                    'prediction_type': prediction.prediction_type,
                    'value': prediction.value,
                    'confidence': prediction.confidence,
                    'spectral_components': json.dumps(prediction.spectral_components),
                    'rag_context': json.dumps(prediction.rag_context),
                    'model_version': prediction.model_version,
                    'latency_ms': prediction.latency_ms
                }
            )
            
            # Store in Pocketbase for API access
            await self.pocketbase_client.create('ai_predictions', asdict(prediction))
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
    
    async def _broadcast_prediction(self, prediction: PredictionResult):
        """Broadcast prediction to WebSocket clients"""
        if not self.websocket_connections:
            return
            
        message = {
            'type': 'ai_prediction',
            'data': asdict(prediction)
        }
        
        # Send to all connected clients
        disconnected = set()
        for websocket in self.websocket_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected clients
        self.websocket_connections -= disconnected
    
    async def get_comprehensive_analysis(self, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        """Get comprehensive AI analysis for a symbol"""
        try:
            # Get recent predictions
            predictions_query = f"""
            SELECT * FROM ai_predictions 
            WHERE symbol = '{symbol}' 
            AND timestamp > NOW() - INTERVAL '7' DAY
            ORDER BY timestamp DESC
            """
            
            predictions = await self.questdb_client.query(predictions_query)
            
            # Get market context
            market_context = await self._get_market_context(symbol)
            
            # Analyze trends
            trend_analysis = self._analyze_prediction_trends(predictions)
            
            # Generate insights
            insights = self._generate_ai_insights(predictions, market_context)
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now(),
                'predictions': predictions,
                'market_context': market_context,
                'trend_analysis': trend_analysis,
                'insights': insights,
                'model_confidence': np.mean([p['confidence'] for p in predictions]) if predictions else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            return {}
    
    async def _get_market_context(self, symbol: str) -> Dict[str, Any]:
        """Get current market context for symbol"""
        try:
            # Get recent market data
            recent_data = await self._get_recent_market_data(symbol)
            
            if recent_data is None:
                return {}
            
            # Calculate market metrics
            current_price = recent_data['price'].iloc[-1]
            price_change_1d = (current_price - recent_data['price'].iloc[-2]) / recent_data['price'].iloc[-2] * 100
            price_change_7d = (current_price - recent_data['price'].iloc[-7]) / recent_data['price'].iloc[-7] * 100 if len(recent_data) >= 7 else 0
            
            return {
                'current_price': current_price,
                'change_1d': price_change_1d,
                'change_7d': price_change_7d,
                'volume_trend': recent_data['volume'].tail(10).mean() / recent_data['volume'].mean() - 1,
                'volatility': recent_data['price'].pct_change().rolling(20).std().iloc[-1] * np.sqrt(252)
            }
            
        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {}
    
    def _analyze_prediction_trends(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in predictions"""
        if not predictions:
            return {}
        
        pred_values = [p['value'] for p in predictions]
        confidences = [p['confidence'] for p in predictions]
        
        # Calculate trend metrics
        trend_direction = np.sign(np.mean(np.diff(pred_values))) if len(pred_values) > 1 else 0
        avg_confidence = np.mean(confidences)
        confidence_trend = np.mean(np.diff(confidences)) if len(confidences) > 1 else 0
        
        return {
            'trend_direction': 'bullish' if trend_direction > 0 else 'bearish' if trend_direction < 0 else 'neutral',
            'trend_strength': abs(trend_direction),
            'average_confidence': avg_confidence,
            'confidence_trend': 'improving' if confidence_trend > 0 else 'declining' if confidence_trend < 0 else 'stable',
            'prediction_volatility': np.std(pred_values)
        }
    
    def _generate_ai_insights(self, predictions: List[Dict[str, Any]], 
                            market_context: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights"""
        insights = []
        
        if not predictions or not market_context:
            return insights
        
        latest_prediction = predictions[0]
        price_change_1d = market_context.get('change_1d', 0)
        avg_confidence = np.mean([p['confidence'] for p in predictions])
        
        # Generate insights based on prediction confidence
        if avg_confidence > 0.8:
            insights.append(f"High confidence prediction ({avg_confidence:.2f}) indicates strong signal reliability")
        elif avg_confidence < 0.5:
            insights.append(f"Low confidence prediction ({avg_confidence:.2f}) suggests market uncertainty")
        
        # Generate insights based on trend
        if abs(price_change_1d) > 3:
            if price_change_1d > 0:
                insights.append("Significant price increase aligns with bullish AI prediction")
            else:
                insights.append("Significant price decrease aligns with bearish AI prediction")
        
        # Generate insights based on spectral analysis
        if 'spectral_components' in latest_prediction:
            spectral = latest_prediction['spectral_components']
            if spectral.get('low_freq_trend', 0) > 0.5:
                insights.append("Strong low-frequency trend component suggests sustained directional movement")
            if spectral.get('high_freq_noise', 0) > 0.7:
                insights.append("High frequency noise component indicates increased market volatility")
        
        return insights

# =============================================================================
# Integration with QuestDB and Pocketbase
# =============================================================================

class AIQuestDBIntegration:
    """Integration layer for AI components with QuestDB"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = QuestDBClient(config.questdb_host, config.questdb_port)
        self.sender = LineSender(host=config.questdb_host, port=config.questdb_port)
        
    async def setup_ai_tables(self):
        """Setup QuestDB tables for AI data"""
        # AI Predictions table
        create_predictions_table = """
        CREATE TABLE IF NOT EXISTS ai_predictions (
            symbol STRING,
            ts TIMESTAMP,
            prediction_type STRING,
            value DOUBLE,
            confidence DOUBLE,
            spectral_components STRING,
            rag_context STRING,
            model_version STRING,
            latency_ms DOUBLE
        ) TIMESTAMP(ts) PARTITION BY DAY;
        """
        
        # Model Metrics table
        create_metrics_table = """
        CREATE TABLE IF NOT EXISTS model_metrics (
            ts TIMESTAMP,
            metric_name STRING,
            metric_value DOUBLE,
            model_version STRING,
            market_condition STRING
        ) TIMESTAMP(ts) PARTITION BY DAY;
        """
        
        # Feature Store table
        create_features_table = """
        CREATE TABLE IF NOT EXISTS feature_store (
            symbol STRING,
            ts TIMESTAMP,
            features STRING,
            spectral_features STRING,
            data_quality_score DOUBLE
        ) TIMESTAMP(ts) PARTITION BY DAY;
        """
        
        try:
            await self.client.execute(create_predictions_table)
            await self.client.execute(create_metrics_table)
            await self.client.execute(create_features_table)
            logger.info("AI tables created successfully in QuestDB")
            
        except Exception as e:
            logger.error(f"Error creating AI tables: {e}")
    
    async def insert_prediction(self, prediction: PredictionResult):
        """Insert AI prediction into QuestDB"""
        try:
            self.sender.metric('ai_predictions') \
                .tag('symbol', prediction.symbol) \
                .tag('prediction_type', prediction.prediction_type) \
                .tag('model_version', prediction.model_version) \
                .field('value', prediction.value) \
                .field('confidence', prediction.confidence) \
                .field('spectral_components', json.dumps(prediction.spectral_components)) \
                .field('rag_context', json.dumps(prediction.rag_context)) \
                .field('latency_ms', prediction.latency_ms) \
                .at(TimestampNanos.from_datetime(prediction.timestamp))
            
            self.sender.flush()
            logger.info(f"Inserted prediction for {prediction.symbol}")
            
        except Exception as e:
            logger.error(f"Error inserting prediction: {e}")

class AIPocketbaseIntegration:
    """Integration layer for AI components with Pocketbase"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = PocketbaseClient(config.pocketbase_url)
        
    async def create_ai_collections(self):
        """Create AI-related collections in Pocketbase"""
        ai_collections = {
            'ai_models': {
                'name': 'AI Models',
                'type': 'base',
                'system': False,
                'schema': [
                    {
                        'name': 'name',
                        'type': 'text',
                        'required': True,
                        'options': {'min': 1, 'max': 255}
                    },
                    {
                        'name': 'version',
                        'type': 'text',
                        'required': True,
                        'options': {'min': 1, 'max': 50}
                    },
                    {
                        'name': 'architecture',
                        'type': 'text',
                        'required': True
                    },
                    {
                        'name': 'training_metrics',
                        'type': 'json',
                        'required': False
                    },
                    {
                        'name': 'deployment_status',
                        'type': 'select',
                        'required': True,
                        'options': {
                            'values': ['development', 'staging', 'production', 'deprecated']
                        }
                    }
                ]
            },
            'prediction_explanations': {
                'name': 'Prediction Explanations',
                'type': 'base',
                'system': False,
                'schema': [
                    {
                        'name': 'symbol',
                        'type': 'text',
                        'required': True,
                        'options': {'min': 1, 'max': 20}
                    },
                    {
                        'name': 'prediction_id',
                        'type': 'text',
                        'required': True
                    },
                    {
                        'name': 'explanation',
                        'type': 'text',
                        'required': True
                    },
                    {
                        'name': 'feature_importance',
                        'type': 'json',
                        'required': False
                    },
                    {
                        'name': 'spectral_analysis',
                        'type': 'json',
                        'required': False
                    },
                    {
                        'name': 'rag_sources',
                        'type': 'json',
                        'required': False
                    }
                ]
            }
        }
        
        try:
            for collection_name, schema in ai_collections.items():
                await self.client.create_collection(collection_name, schema)
            logger.info("AI collections created successfully in Pocketbase")
            
        except Exception as e:
            logger.error(f"Error creating AI collections: {e}")

# =============================================================================
# Main Application Factory
# =============================================================================

def create_ai_system(config: AIConfig = None) -> Dict[str, Any]:
    """
    Create complete AI system with all components
    
    Args:
        config: AI configuration (uses default if None)
        
    Returns:
        Dictionary containing all AI system components
    """
    if config is None:
        config = AIConfig()
    
    # Initialize components
    training_pipeline = AITrainingPipeline(config)
    real_time_pipeline = RealTimeAIPipeline(config, training_pipeline)
    questdb_integration = AIQuestDBIntegration(config)
    pocketbase_integration = AIPocketbaseIntegration(config)
    
    # Setup databases
    async def setup_systems():
        await questdb_integration.setup_ai_tables()
        await pocketbase_integration.create_ai_collections()
        return True
    
    # Run setup
    try:
        asyncio.run(setup_systems())
    except Exception as e:
        logger.error(f"Error setting up AI systems: {e}")
    
    return {
        'config': config,
        'training_pipeline': training_pipeline,
        'real_time_pipeline': real_time_pipeline,
        'questdb_integration': questdb_integration,
        'pocketbase_integration': pocketbase_integration,
        'spectral_model': training_pipeline.spectral_model,
        'rag_model': training_pipeline.rag_model,
        'knowledge_base': training_pipeline.knowledge_base,
        'preprocessor': training_pipeline.preprocessor
    }

# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example configuration
    config = AIConfig(
        input_dim=50,
        spectral_dim=128,
        hidden_dim=256,
        output_dim=4,
        learning_rate=0.001,
        batch_size=32,
        num_epochs=100,
        questdb_host="localhost",
        questdb_port=9009,
        pocketbase_url="http://localhost:8090"
    )
    
    # Create AI system
    ai_system = create_ai_system(config)
    
    # Example of processing a market event
    async def example_usage():
        # Create sample market event
        market_event = MarketEvent(
            symbol="PKN",
            timestamp=datetime.now(),
            price=45.67,
            volume=1000000,
            high=46.20,
            low=45.10,
            open=45.80
        )
        
        # Process event
        prediction = await ai_system['real_time_pipeline'].process_realtime_market_event(market_event)
        
        if prediction:
            print(f"Generated prediction for {prediction.symbol}: {prediction.value}")
            print(f"Confidence: {prediction.confidence:.2f}")
    
    # Run example
    try:
        asyncio.run(example_usage())
    except Exception as e:
        logger.error(f"Example usage error: {e}")

"""
Technical Specifications Summary:

1. Spectral Bias Neural Network:
   - Multi-layer architecture with spectral transformation
   - Frequency domain analysis with learnable filters
   - Multi-head spectral attention mechanism
   - Spectral bias regularization for controlled learning

2. RAG Integration:
   - Financial domain-specific embeddings
   - Vector database with FAISS indexing
   - Context fusion with attention mechanisms
   - Real-time knowledge retrieval

3. Data Preprocessing:
   - Comprehensive financial feature engineering
   - Technical indicators (RSI, MACD, Bollinger Bands)
   - Spectral features (FFT, power spectral density)
   - Data quality validation and normalization

4. Training Pipeline:
   - Distributed training with multiple loss functions
   - Spectral bias regularization
   - Early stopping and model checkpointing
   - Performance metrics tracking

5. Real-time Processing:
   - Event-driven architecture
   - WebSocket-based real-time updates
   - Feature caching and optimization
   - QuestDB and Pocketbase integration

6. Integration Architecture:
   - Seamless integration with existing QuestDB-Pocketbase flow
   - Real-time data streaming
   - Scalable microservices architecture
   - Monitoring and alerting capabilities

This implementation provides a production-ready foundation for AI-powered
financial analysis with spectral bias neural networks and RAG integration.
"""