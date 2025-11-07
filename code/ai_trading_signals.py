#!/usr/bin/env python3
"""
AI Trading Signals System for Polish Market
Advanced AI-powered trading signals and investment recommendations for WIG80 companies.

Features:
- Multi-factor AI trading signals
- Risk-adjusted position sizing
- Entry/exit point optimization
- Portfolio correlation management
- Real-time signal generation
- Performance tracking and backtesting

Author: AI Trading Systems
Version: 1.0.0
Date: 2025-11-06
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Import our main AI system
import sys
import os
sys.path.append('/workspace/code')
from polish_market_ai import PolishMarketAI, OvervaluationResult, SentimentScore, TrendPattern

class SignalStrength(Enum):
    """Signal strength levels"""
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5

class SignalType(Enum):
    """Trading signal types"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"

class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TradingSignal:
    """Individual trading signal"""
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    confidence: float  # 0-1
    target_price: float
    stop_loss: float
    position_size: float  # percentage of portfolio
    risk_level: RiskLevel
    time_horizon: str  # short, medium, long
    key_factors: List[str]
    entry_criteria: List[str]
    exit_criteria: List[str]
    expected_return: float
    max_drawdown_risk: float
    generated_at: datetime
    expires_at: datetime

@dataclass
class PortfolioSignal:
    """Portfolio-level signals and recommendations"""
    overall_sentiment: str
    recommended_allocation: Dict[str, float]  # symbol -> allocation %
    risk_score: float  # 0-100
    expected_portfolio_return: float
    max_portfolio_risk: float
    diversification_score: float
    rebalancing_recommendations: List[str]
    market_timing: str
    top_picks: List[str]
    avoid_list: List[str]
    generated_at: datetime

@dataclass
class SignalPerformance:
    """Signal performance tracking"""
    symbol: str
    signal_type: SignalType
    entry_price: float
    exit_price: Optional[float]
    entry_date: datetime
    exit_date: Optional[float]
    actual_return: float
    expected_return: float
    hit_target: bool
    hit_stop_loss: bool
    duration_days: int
    sharpe_ratio: float
    max_favorable_excursion: float
    max_adverse_excursion: float

class AITradingSignals:
    """
    Advanced AI-powered trading signals system for Polish market
    """
    
    def __init__(self, data_source: str = "local"):
        """
        Initialize the AI trading signals system
        
        Args:
            data_source: Data source type
        """
        self.ai_system = PolishMarketAI(data_source)
        self.signal_history = []
        self.performance_cache = {}
        
        # Trading parameters
        self.default_position_size = 0.05  # 5% max per position
        self.risk_free_rate = 0.02  # 2% for Poland
        self.market_beta = 1.2  # WIG80 beta estimate
        
        # Signal weighting parameters
        self.signal_weights = {
            'overvaluation': 0.25,
            'sentiment': 0.30,
            'technical': 0.20,
            'fundamental': 0.15,
            'volume': 0.10
        }
        
    def generate_trading_signals(self, symbols: List[str] = None, 
                                min_confidence: float = 0.6) -> List[TradingSignal]:
        """
        Generate AI-powered trading signals for WIG80 companies
        
        Args:
            symbols: List of symbols to analyze (analyzes all if None)
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of trading signals
        """
        
        # Load data
        self.ai_system.load_wig80_data()
        
        if symbols is None:
            symbols = self.ai_system.wig80_data['symbol'].tolist()
        
        signals = []
        
        for symbol in symbols:
            try:
                signal = self._generate_single_signal(symbol, min_confidence)
                if signal:
                    signals.append(signal)
            except Exception as e:
                print(f"Error generating signal for {symbol}: {e}")
        
        # Sort by confidence and strength
        signals.sort(key=lambda x: (x.confidence, x.strength.value), reverse=True)
        
        return signals
    
    def _generate_single_signal(self, symbol: str, min_confidence: float) -> Optional[TradingSignal]:
        """Generate trading signal for a single stock"""
        
        # Get analysis data
        overvaluation = self.ai_system.detect_overvaluation(symbol)
        sentiment = self.ai_system.analyze_market_sentiment(symbol)
        patterns = self.ai_system.detect_trend_patterns(symbol)
        
        # Current price data
        company = self.ai_system.wig80_data[self.ai_system.wig80_data['symbol'] == symbol]
        if company.empty:
            return None
        
        company = company.iloc[0]
        current_price = company['current_price']
        
        # Calculate signal components
        signal_components = self._calculate_signal_components(
            symbol, overvaluation, sentiment, patterns, company
        )
        
        # Determine overall signal
        signal_type, strength, confidence = self._determine_signal(
            signal_components, overvaluation, sentiment
        )
        
        if confidence < min_confidence:
            return None
        
        # Calculate trading parameters
        target_price, stop_loss, position_size, risk_level = self._calculate_trading_params(
            company, signal_components, signal_type, overvaluation, confidence
        )
        
        # Time horizon
        time_horizon = self._determine_time_horizon(signal_components, patterns)
        
        # Entry and exit criteria
        entry_criteria, exit_criteria = self._define_criteria(
            signal_type, target_price, stop_loss, sentiment, patterns
        )
        
        # Expected return and risk
        expected_return = ((target_price - current_price) / current_price) * 100
        max_drawdown_risk = self._calculate_drawdown_risk(
            current_price, stop_loss, overvaluation, sentiment
        )
        
        # Signal expiration (typically 1-4 weeks)
        expires_at = datetime.now() + timedelta(weeks=int(np.random.choice([1, 2, 4], p=[0.3, 0.5, 0.2])))
        
        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            confidence=confidence,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=position_size,
            risk_level=risk_level,
            time_horizon=time_horizon,
            key_factors=signal_components['key_factors'],
            entry_criteria=entry_criteria,
            exit_criteria=exit_criteria,
            expected_return=expected_return,
            max_drawdown_risk=max_drawdown_risk,
            generated_at=datetime.now(),
            expires_at=expires_at
        )
    
    def _calculate_signal_components(self, symbol: str, overvaluation: OvervaluationResult,
                                   sentiment: SentimentScore, patterns: List[TrendPattern],
                                   company: pd.Series) -> Dict:
        """Calculate individual signal components"""
        
        components = {
            'overvaluation_score': 100 - overvaluation.overvaluation_score,  # Invert
            'sentiment_score': (sentiment.score + 100) / 2,  # Normalize to 0-100
            'volume_score': company['volume_score'] * 100,
            'momentum_score': self._calculate_momentum_score(company),
            'volatility_score': max(0, 100 - (company['estimated_volatility'] * 10)),
            'key_factors': []
        }
        
        # Key factors analysis
        if abs(company['change_percent']) > 5:
            components['key_factors'].append(f"Strong momentum: {company['change_percent']:+.1f}%")
        
        if company['volume_score'] > 0.7:
            components['key_factors'].append("High liquidity confirms interest")
        elif company['volume_score'] < 0.3:
            components['key_factors'].append("Low volume requires caution")
        
        if overvaluation.risk_level in ['high', 'critical']:
            components['key_factors'].append(f"Overvaluation risk: {overvaluation.risk_level}")
        
        if sentiment.overall_sentiment in ['very_bullish', 'bullish']:
            components['key_factors'].append(f"Positive sentiment: {sentiment.overall_sentiment}")
        
        # Technical pattern analysis
        strong_patterns = [p for p in patterns if p.strength > 0.7]
        if strong_patterns:
            components['key_factors'].append(f"Strong pattern: {strong_patterns[0].pattern_name}")
        
        return components
    
    def _calculate_momentum_score(self, company: pd.Series) -> float:
        """Calculate momentum-based score"""
        score = 50  # Base score
        
        # Price momentum
        change_pct = company['change_percent']
        if change_pct > 10:
            score += 30
        elif change_pct > 5:
            score += 20
        elif change_pct > 2:
            score += 10
        elif change_pct < -10:
            score -= 30
        elif change_pct < -5:
            score -= 20
        elif change_pct < -2:
            score -= 10
        
        # Range momentum (how close to high/low)
        daily_range = company['daily_range']
        if daily_range > 0:
            position_in_range = (company['current_price'] - company['low_price']) / daily_range
            score += (position_in_range - 0.5) * 20  # Reward being near high, penalize near low
        
        return max(0, min(100, score))
    
    def _determine_signal(self, components: Dict, overvaluation: OvervaluationResult,
                         sentiment: SentimentScore) -> Tuple[SignalType, SignalStrength, float]:
        """Determine overall trading signal"""
        
        # Weighted composite score
        composite_score = (
            components['sentiment_score'] * self.signal_weights['sentiment'] +
            components['momentum_score'] * self.signal_weights['technical'] +
            components['overvaluation_score'] * self.signal_weights['overvaluation'] +
            components['volume_score'] * self.signal_weights['volume']
        )
        
        # Adjust for overvaluation (risk penalty)
        if overvaluation.risk_level in ['high', 'critical']:
            composite_score -= 20
        elif overvaluation.risk_level == 'medium':
            composite_score -= 10
        
        # Adjust for sentiment
        if sentiment.overall_sentiment in ['very_bullish', 'very_bearish']:
            composite_score *= 1.2  # Amplify strong sentiment
        
        # Determine signal type
        if composite_score >= 80:
            signal_type = SignalType.STRONG_BUY
            strength = SignalStrength.VERY_STRONG
        elif composite_score >= 65:
            signal_type = SignalType.BUY
            strength = SignalStrength.STRONG
        elif composite_score >= 50:
            signal_type = SignalType.HOLD
            strength = SignalStrength.MODERATE
        elif composite_score >= 35:
            signal_type = SignalType.SELL
            strength = SignalStrength.WEAK
        else:
            signal_type = SignalType.STRONG_SELL
            strength = SignalStrength.VERY_WEAK
        
        # Confidence based on signal strength and data quality
        confidence = min(0.95, max(0.3, composite_score / 100))
        
        # Boost confidence if multiple indicators align
        aligned_indicators = 0
        if components['sentiment_score'] > 70: aligned_indicators += 1
        if components['momentum_score'] > 70: aligned_indicators += 1
        if components['volume_score'] > 60: aligned_indicators += 1
        if overvaluation.risk_level == 'low': aligned_indicators += 1
        
        if aligned_indicators >= 3:
            confidence = min(0.95, confidence * 1.2)
        
        return signal_type, strength, confidence
    
    def _calculate_trading_params(self, company: pd.Series, components: Dict,
                                signal_type: SignalType, overvaluation: OvervaluationResult, confidence: float) -> Tuple[float, float, float, RiskLevel]:
        """Calculate trading parameters (target, stop loss, position size, risk)"""
        
        current_price = company['current_price']
        daily_range = company['daily_range']
        
        # Target price calculation
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            # For buy signals, target above current price
            base_target = current_price * (1 + (confidence * 0.15))
            if components['momentum_score'] > 70:
                base_target *= 1.05  # Extra upside for strong momentum
        else:
            # For sell signals, target below current price
            base_target = current_price * (1 - (confidence * 0.12))
        
        # Stop loss calculation
        volatility_buffer = max(daily_range * 0.3, current_price * 0.02)  # Min 2% stop
        
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            stop_loss = current_price - volatility_buffer
        else:
            stop_loss = current_price + volatility_buffer
        
        # Position sizing based on risk and conviction
        base_position = self.default_position_size
        
        # Adjust for confidence
        position_size = base_position * confidence
        
        # Adjust for risk level
        if overvaluation.risk_level == 'high':
            position_size *= 0.7
        elif overvaluation.risk_level == 'critical':
            position_size *= 0.5
        elif overvaluation.risk_level == 'low':
            position_size *= 1.2
        
        # Adjust for liquidity
        if company['volume_score'] < 0.3:
            position_size *= 0.8  # Reduce size for illiquid stocks
        
        position_size = min(position_size, 0.15)  # Max 15% per position
        position_size = max(position_size, 0.01)  # Min 1% per position
        
        # Risk level determination
        risk_score = 0
        if overvaluation.risk_level in ['high', 'critical']:
            risk_score += 30
        if components['volatility_score'] < 40:
            risk_score += 25
        if company['volume_score'] < 0.3:
            risk_score += 20
        if abs(company['change_percent']) > 8:
            risk_score += 15
        
        if risk_score >= 70:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 50:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 30:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return base_target, stop_loss, position_size, risk_level
    
    def _determine_time_horizon(self, components: Dict, patterns: List[TrendPattern]) -> str:
        """Determine signal time horizon"""
        
        # Base on signal strength
        if components['sentiment_score'] > 80 or components['momentum_score'] > 80:
            return "short"  # 1-2 weeks
        elif components['sentiment_score'] > 60:
            return "medium"  # 1-3 months
        else:
            return "long"  # 3-6 months
    
    def _define_criteria(self, signal_type: SignalType, target_price: float,
                        stop_loss: float, sentiment: SentimentScore,
                        patterns: List[TrendPattern]) -> Tuple[List[str], List[str]]:
        """Define entry and exit criteria"""
        
        entry_criteria = []
        exit_criteria = []
        
        if signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            entry_criteria = [
                f"Buy on pullback to {target_price * 0.98:.2f} or breakout above {target_price * 1.02:.2f}",
                "Confirm with volume increase",
                f"Stop loss at {stop_loss:.2f}"
            ]
            exit_criteria = [
                f"Take profit at {target_price:.2f}",
                f"Trail stop if price moves to {target_price * 1.1:.2f}",
                f"Emergency exit if price falls below {stop_loss:.2f}"
            ]
        else:
            entry_criteria = [
                f"Sell on bounce to {target_price * 0.98:.2f} or breakdown below {target_price * 0.98:.2f}",
                "Confirm with volume increase",
                f"Stop loss at {stop_loss:.2f}"
            ]
            exit_criteria = [
                f"Cover position at {target_price:.2f}",
                f"Trailing stop if price declines to {target_price * 0.9:.2f}",
                f"Emergency cover if price rises above {stop_loss:.2f}"
            ]
        
        # Add sentiment-based criteria
        if sentiment.overall_sentiment in ['very_bullish', 'very_bearish']:
            exit_criteria.append("Monitor for sentiment reversal")
        
        return entry_criteria, exit_criteria
    
    def _calculate_drawdown_risk(self, current_price: float, stop_loss: float,
                               overvaluation: OvervaluationResult, sentiment: SentimentScore) -> float:
        """Calculate maximum drawdown risk"""
        
        # Base drawdown from stop loss
        base_drawdown = abs((stop_loss - current_price) / current_price) * 100
        
        # Risk multipliers
        risk_multiplier = 1.0
        
        if overvaluation.risk_level == 'critical':
            risk_multiplier = 1.5
        elif overvaluation.risk_level == 'high':
            risk_multiplier = 1.3
        elif overvaluation.risk_level == 'medium':
            risk_multiplier = 1.1
        
        if sentiment.confidence < 0.5:
            risk_multiplier *= 1.2
        
        return base_drawdown * risk_multiplier
    
    def generate_portfolio_signals(self, signals: List[TradingSignal]) -> PortfolioSignal:
        """Generate portfolio-level trading recommendations"""
        
        if not signals:
            return PortfolioSignal(
                overall_sentiment="neutral",
                recommended_allocation={},
                risk_score=50,
                expected_portfolio_return=0,
                max_portfolio_risk=10,
                diversification_score=0.5,
                rebalancing_recommendations=["No clear signals generated"],
                market_timing="wait",
                top_picks=[],
                avoid_list=[],
                generated_at=datetime.now()
            )
        
        # Calculate portfolio metrics
        buy_signals = [s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]]
        sell_signals = [s for s in signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]]
        hold_signals = [s for s in signals if s.signal_type == SignalType.HOLD]
        
        # Overall sentiment
        total_weighted_sentiment = sum(
            s.confidence * (1 if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY] else -1)
            for s in signals
        ) / len(signals)
        
        if total_weighted_sentiment > 0.3:
            overall_sentiment = "bullish"
        elif total_weighted_sentiment < -0.3:
            overall_sentiment = "bearish"
        else:
            overall_sentiment = "neutral"
        
        # Recommended allocation
        recommended_allocation = {}
        total_allocation = 0
        
        # Allocate to strong buy signals first
        strong_buys = [s for s in signals if s.signal_type == SignalType.STRONG_BUY]
        for signal in strong_buys:
            recommended_allocation[signal.symbol] = signal.position_size * 1.5
            total_allocation += signal.position_size * 1.5
        
        # Then to regular buy signals
        regular_buys = [s for s in signals if s.signal_type == SignalType.BUY]
        for signal in regular_buys:
            if total_allocation < 0.8:  # Max 80% allocation
                remaining = 0.8 - total_allocation
                allocation = min(signal.position_size, remaining)
                recommended_allocation[signal.symbol] = allocation
                total_allocation += allocation
        
        # Risk score calculation
        risk_scores = [self._signal_risk_score(s) for s in signals]
        portfolio_risk = np.mean(risk_scores) if risk_scores else 50
        
        # Expected return
        expected_returns = [s.expected_return * s.position_size for s in buy_signals]
        expected_portfolio_return = sum(expected_returns) if expected_returns else 0
        
        # Maximum portfolio risk
        max_risks = [s.max_drawdown_risk * s.position_size for s in signals if s.position_size > 0.02]
        max_portfolio_risk = sum(max_risks) if max_risks else 10
        
        # Diversification score
        sector_diversification = self._calculate_diversification_score(list(recommended_allocation.keys()))
        
        # Rebalancing recommendations
        rebalancing_recommendations = self._generate_rebalancing_recommendations(signals, recommended_allocation)
        
        # Market timing
        market_timing = self._determine_market_timing(signals)
        
        # Top picks and avoid list
        top_picks = [s.symbol for s in sorted(buy_signals, key=lambda x: x.confidence * x.expected_return, reverse=True)[:5]]
        avoid_list = [s.symbol for s in sell_signals if s.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        
        return PortfolioSignal(
            overall_sentiment=overall_sentiment,
            recommended_allocation=recommended_allocation,
            risk_score=portfolio_risk,
            expected_portfolio_return=expected_portfolio_return,
            max_portfolio_risk=max_portfolio_risk,
            diversification_score=sector_diversification,
            rebalancing_recommendations=rebalancing_recommendations,
            market_timing=market_timing,
            top_picks=top_picks,
            avoid_list=avoid_list,
            generated_at=datetime.now()
        )
    
    def _signal_risk_score(self, signal: TradingSignal) -> float:
        """Calculate risk score for a signal"""
        base_risk = {
            RiskLevel.LOW: 20,
            RiskLevel.MEDIUM: 40,
            RiskLevel.HIGH: 70,
            RiskLevel.CRITICAL: 90
        }[signal.risk_level]
        
        # Adjust for confidence (higher confidence = lower risk)
        risk_adjustment = (1 - signal.confidence) * 20
        
        # Adjust for position size (larger position = higher portfolio risk)
        position_adjustment = signal.position_size * 100
        
        return min(100, base_risk + risk_adjustment + position_adjustment)
    
    def _calculate_diversification_score(self, symbols: List[str]) -> float:
        """Calculate portfolio diversification score"""
        if len(symbols) < 2:
            return 0.2
        
        # Simple diversification based on number of positions
        # In production, would use sector/size diversification
        optimal_positions = 8
        if len(symbols) >= optimal_positions:
            return 0.9
        else:
            return len(symbols) / optimal_positions
    
    def _generate_rebalancing_recommendations(self, signals: List[TradingSignal], 
                                            allocation: Dict[str, float]) -> List[str]:
        """Generate portfolio rebalancing recommendations"""
        recommendations = []
        
        total_allocation = sum(allocation.values())
        
        if total_allocation > 0.9:
            recommendations.append("Consider taking profits - portfolio near maximum allocation")
        elif total_allocation < 0.3:
            recommendations.append("Look for additional opportunities - portfolio underallocated")
        
        # Check for concentration risk
        max_position = max(allocation.values()) if allocation else 0
        if max_position > 0.15:
            recommendations.append("Reduce position sizing due to concentration risk")
        
        # Risk level recommendations
        high_risk_signals = [s for s in signals if s.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if len(high_risk_signals) > len(signals) * 0.3:
            recommendations.append("High-risk signals dominant - consider defensive positioning")
        
        return recommendations
    
    def _determine_market_timing(self, signals: List[TradingSignal]) -> str:
        """Determine market timing recommendation"""
        
        buy_signals = len([s for s in signals if s.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]])
        sell_signals = len([s for s in signals if s.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]])
        total_signals = len(signals)
        
        if total_signals == 0:
            return "wait"
        
        buy_ratio = buy_signals / total_signals
        sell_ratio = sell_signals / total_signals
        avg_confidence = np.mean([s.confidence for s in signals])
        
        if buy_ratio > 0.6 and avg_confidence > 0.7:
            return "aggressive_buy"
        elif buy_ratio > 0.5:
            return "selective_buy"
        elif sell_ratio > 0.6:
            return "defensive"
        else:
            return "neutral"
    
    def backtest_signals(self, signals: List[TradingSignal], 
                        historical_data: Dict[str, List[Dict]] = None) -> List[SignalPerformance]:
        """
        Backtest trading signals (simplified version)
        
        Args:
            signals: List of signals to backtest
            historical_data: Historical price data (simulated if None)
            
        Returns:
            Performance results
        """
        
        performance_results = []
        
        for signal in signals:
            # Simulate performance (in production, would use real historical data)
            performance = self._simulate_signal_performance(signal)
            performance_results.append(performance)
            
            # Store in history
            self.signal_history.append(performance)
        
        return performance_results
    
    def _simulate_signal_performance(self, signal: TradingSignal) -> SignalPerformance:
        """Simulate signal performance (for demo purposes)"""
        
        # Simulate exit price based on signal success probability
        success_probability = signal.confidence
        
        np.random.seed(hash(signal.symbol) % 2**32)  # Deterministic per symbol
        
        if np.random.random() < success_probability:
            # Successful signal
            if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                # Price moves towards target
                exit_price = signal.target_price * (0.9 + np.random.random() * 0.2)
                actual_return = ((exit_price - signal.target_price) / signal.target_price) * 100
            else:
                # Price moves towards target (lower)
                exit_price = signal.target_price * (1.1 - np.random.random() * 0.2)
                actual_return = ((exit_price - signal.target_price) / signal.target_price) * 100
        else:
            # Unsuccessful signal
            if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
                exit_price = signal.stop_loss * (0.95 + np.random.random() * 0.1)
                actual_return = ((exit_price - signal.target_price) / signal.target_price) * 100
            else:
                exit_price = signal.stop_loss * (0.95 + np.random.random() * 0.1)
                actual_return = ((exit_price - signal.target_price) / signal.target_price) * 100
        
        # Calculate performance metrics
        entry_price = signal.target_price * 0.98  # Simulate entry slightly before target
        duration_days = np.random.randint(5, 30)
        
        return SignalPerformance(
            symbol=signal.symbol,
            signal_type=signal.signal_type,
            entry_price=entry_price,
            exit_price=exit_price,
            entry_date=signal.generated_at,
            exit_date=signal.generated_at + timedelta(days=duration_days),
            actual_return=actual_return,
            expected_return=signal.expected_return,
            hit_target=actual_return > 0,
            hit_stop_loss=exit_price == signal.stop_loss,
            duration_days=duration_days,
            sharpe_ratio=np.random.normal(0.5, 0.3),
            max_favorable_excursion=abs(actual_return) * 1.5,
            max_adverse_excursion=abs(actual_return) * 0.8
        )
    
    def export_signals(self, signals: List[TradingSignal], output_path: str, 
                      portfolio_signal: PortfolioSignal = None) -> bool:
        """Export trading signals to file"""
        try:
            # Convert signals to dictionaries
            signal_data = {
                "individual_signals": [asdict(signal) for signal in signals],
                "portfolio_signal": asdict(portfolio_signal) if portfolio_signal else None,
                "export_metadata": {
                    "total_signals": len(signals),
                    "exported_at": datetime.now().isoformat(),
                    "signal_types": {
                        signal_type.value: len([s for s in signals if s.signal_type == signal_type])
                        for signal_type in SignalType
                    }
                }
            }
            
            # Convert datetime objects to strings
            def serialize_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object {obj} is not JSON serializable")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(signal_data, f, indent=2, ensure_ascii=False, default=serialize_datetime)
            
            print(f"✓ Trading signals exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting signals: {e}")
            return False

def main():
    """Main execution function for testing"""
    
    print("\n" + "="*60)
    print("AI TRADING SIGNALS SYSTEM - POLISH MARKET")
    print("="*60)
    
    # Initialize system
    signals_system = AITradingSignals()
    
    # Generate trading signals
    print("\n🔄 Generating AI trading signals...")
    signals = signals_system.generate_trading_signals(min_confidence=0.5)
    
    print(f"✓ Generated {len(signals)} trading signals")
    
    # Show signal summary
    if signals:
        signal_types = {}
        for signal in signals:
            signal_type = signal.signal_type.value
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
        
        print(f"\n📊 Signal Distribution:")
        for signal_type, count in signal_types.items():
            print(f"  {signal_type.replace('_', ' ').title()}: {count}")
        
        # Show top signals
        print(f"\n🎯 Top Trading Signals:")
        for i, signal in enumerate(signals[:5]):
            print(f"{i+1}. {signal.symbol}: {signal.signal_type.value.replace('_', ' ').title()}")
            print(f"   Confidence: {signal.confidence:.1%} | Target: {signal.target_price:.2f} PLN")
            print(f"   Expected Return: {signal.expected_return:+.1f}% | Risk: {signal.risk_level.value}")
            print(f"   Key Factors: {', '.join(signal.key_factors[:2])}")
            print()
    
    # Generate portfolio signal
    print("\n🏛️ Generating portfolio-level recommendations...")
    portfolio_signal = signals_system.generate_portfolio_signals(signals)
    
    print(f"Portfolio Overview:")
    print(f"  Overall Sentiment: {portfolio_signal.overall_sentiment}")
    print(f"  Expected Return: {portfolio_signal.expected_portfolio_return:+.1f}%")
    print(f"  Risk Score: {portfolio_signal.risk_score:.1f}/100")
    print(f"  Market Timing: {portfolio_signal.market_timing}")
    
    if portfolio_signal.top_picks:
        print(f"  Top Picks: {', '.join(portfolio_signal.top_picks[:3])}")
    
    if portfolio_signal.recommended_allocation:
        print(f"  Recommended Allocation:")
        for symbol, allocation in list(portfolio_signal.recommended_allocation.items())[:3]:
            print(f"    {symbol}: {allocation:.1%}")
    
    # Test backtesting
    print(f"\n📈 Backtesting signals...")
    performance = signals_system.backtest_signals(signals)
    
    if performance:
        avg_return = np.mean([p.actual_return for p in performance])
        hit_rate = len([p for p in performance if p.hit_target]) / len(performance)
        
        print(f"Backtest Results:")
        print(f"  Average Return: {avg_return:+.1f}%")
        print(f"  Hit Rate: {hit_rate:.1%}")
        print(f"  Total Signals: {len(performance)}")
    
    return signals_system

if __name__ == "__main__":
    trading_system = main()