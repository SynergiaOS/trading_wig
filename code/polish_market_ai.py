#!/usr/bin/env python3
"""
Polish Market AI Insights and Analysis System
Advanced AI-powered analysis tools for WIG80 companies and Polish stock market trends.

Features:
- Advanced overvaluation detection algorithms
- Pattern recognition for Polish stock market trends
- AI-powered correlation analysis between WIG80 stocks
- Market sentiment analysis using news and social data
- Comprehensive financial metrics analysis

Author: AI Trading Systems
Version: 1.0.0
Date: 2025-11-06
"""

import pandas as pd
import numpy as np
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

@dataclass
class CompanyMetrics:
    """Enhanced company metrics for AI analysis"""
    symbol: str
    company_name: str
    current_price: float
    high_price: float
    low_price: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    earnings_yield: Optional[float] = None
    price_to_sales: Optional[float] = None
    beta: Optional[float] = None
    volatility_30d: Optional[float] = None

@dataclass
class OvervaluationResult:
    """Results of overvaluation analysis"""
    symbol: str
    is_overvalued: bool
    overvaluation_score: float  # 0-100, higher = more overvalued
    risk_level: str  # low, medium, high, critical
    key_indicators: List[str]
    fair_value_estimate: float
    upside_downside: float  # percentage
    recommendation: str
    confidence: float

@dataclass
class TrendPattern:
    """Identified trend patterns"""
    pattern_name: str
    strength: float  # 0-1
    confidence: float  # 0-1
    direction: str  # bullish, bearish, neutral
    duration: str  # short, medium, long
    key_levels: Dict[str, float]
    probability: float  # 0-1

@dataclass
class CorrelationResult:
    """Stock correlation analysis results"""
    stock1: str
    stock2: str
    correlation: float
    relationship_type: str
    significance: float
    lead_lag: str
    insights: List[str]

@dataclass
class SentimentScore:
    """Market sentiment analysis results"""
    overall_sentiment: str  # very_bullish, bullish, neutral, bearish, very_bearish
    score: float  # -100 to +100
    confidence: float
    key_factors: List[str]
    news_impact: float
    technical_sentiment: float
    fundamental_sentiment: float

class PolishMarketAI:
    """
    Advanced AI-powered Polish market analysis system for WIG80 companies
    """
    
    def __init__(self, data_source: str = "local"):
        """
        Initialize the Polish Market AI system
        
        Args:
            data_source: Data source type - "local", "api", or "database"
        """
        self.data_source = data_source
        self.wig80_data = None
        self.correlation_matrix = None
        self.sentiment_cache = {}
        self.pattern_cache = {}
        
        # Polish market specific parameters
        self.market_tz = "Europe/Warsaw"
        self.session_hours = {
            "pre_market": "08:00-09:00",
            "main_session": "09:00-17:00", 
            "after_hours": "17:00-20:00"
        }
        
        # AI model parameters - reserved for future enhancement
        self.valuation_models = {}
        
    def load_wig80_data(self, data_path: str = None) -> pd.DataFrame:
        """
        Load WIG80 company data
        
        Args:
            data_path: Path to WIG80 data file
            
        Returns:
            DataFrame with WIG80 company data
        """
        try:
            if data_path is None:
                data_path = "/workspace/WIG80_Companies.csv"
            
            self.wig80_data = pd.read_csv(data_path)
            self.wig80_data.columns = self._standardize_columns(self.wig80_data.columns)
            
            # Enhance data with additional metrics
            self.wig80_data = self._enhance_company_data(self.wig80_data)
            
            print(f"✓ Loaded {len(self.wig80_data)} WIG80 companies")
            return self.wig80_data
            
        except Exception as e:
            print(f"Error loading WIG80 data: {e}")
            return pd.DataFrame()
    
    def _standardize_columns(self, columns: List[str]) -> List[str]:
        """Standardize column names for consistent processing"""
        mapping = {
            'Company Name': 'company_name',
            'Ticker': 'symbol', 
            'Current Price (PLN)': 'current_price',
            'High Price (PLN)': 'high_price',
            'Low Price (PLN)': 'low_price',
            'Change (%)': 'change_percent',
            'Volume': 'volume'
        }
        return [mapping.get(col, col.lower().replace(' ', '_')) for col in columns]
    
    def _enhance_company_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhance company data with additional calculated metrics"""
        
        # Calculate intraday metrics
        df['daily_range'] = df['high_price'] - df['low_price']
        df['range_percent'] = (df['daily_range'] / df['low_price']) * 100
        
        # Volume analysis
        df['volume_score'] = self._calculate_volume_score(df['volume'])
        
        # Volatility estimation (simplified)
        df['estimated_volatility'] = df['range_percent'] * 0.6  # Simplified estimate
        
        # Price momentum
        df['price_strength'] = np.where(df['change_percent'] > 0, 
                                      df['change_percent'] / (abs(df['change_percent']) + 1),
                                      df['change_percent'] / (abs(df['change_percent']) + 1))
        
        return df
    
    def _calculate_volume_score(self, volumes: pd.Series) -> pd.Series:
        """Calculate volume-based liquidity score"""
        # Rank volumes and create score
        volume_ranks = volumes.rank(pct=True)
        
        # High volume = high liquidity score
        volume_scores = {}
        for rank in volume_ranks:
            if rank >= 0.8:
                volume_scores[rank] = 0.9 + (rank - 0.8) * 0.1
            elif rank >= 0.5:
                volume_scores[rank] = 0.5 + (rank - 0.5) * 1.33
            else:
                volume_scores[rank] = rank * 1.0
        
        return volume_ranks.map(volume_scores)
    
    def detect_overvaluation(self, symbol: str = None, threshold: float = 0.7) -> Union[OvervaluationResult, List[OvervaluationResult]]:
        """
        Advanced overvaluation detection for WIG80 companies
        
        Args:
            symbol: Specific stock symbol (analyzes all if None)
            threshold: Overvaluation threshold (0-1)
            
        Returns:
            Overvaluation analysis results
        """
        if self.wig80_data is None:
            self.load_wig80_data()
        
        if symbol:
            return self._analyze_single_overvaluation(symbol, threshold)
        else:
            return self._analyze_all_overvaluations(threshold)
    
    def _analyze_single_overvaluation(self, symbol: str, threshold: float) -> OvervaluationResult:
        """Analyze overvaluation for a single stock"""
        
        company = self.wig80_data[self.wig80_data['symbol'] == symbol]
        if company.empty:
            raise ValueError(f"Symbol {symbol} not found in WIG80")
        
        company = company.iloc[0]
        
        # Multi-factor valuation analysis
        indicators = []
        risk_score = 0
        
        # Price momentum analysis
        if company['change_percent'] > 15:
            indicators.append("Exceptional recent price surge")
            risk_score += 20
        elif company['change_percent'] > 8:
            indicators.append("Strong recent price momentum")
            risk_score += 10
        
        # Volume analysis (low volume + high price = concern)
        if company['volume_score'] < 0.3 and company['change_percent'] > 5:
            indicators.append("High price movement with low liquidity")
            risk_score += 15
        
        # Volatility analysis
        if company['estimated_volatility'] > 8:
            indicators.append("Extremely high intraday volatility")
            risk_score += 10
        elif company['estimated_volatility'] > 5:
            indicators.append("Above-average volatility")
            risk_score += 5
        
        # Price range analysis
        daily_range_pct = (company['daily_range'] / company['current_price']) * 100
        if daily_range_pct > 10:
            indicators.append("Wide daily trading range - high uncertainty")
            risk_score += 8
        
        # Fair value estimation using multiple methods
        fair_value = self._estimate_fair_value(company)
        upside_downside = ((fair_value - company['current_price']) / company['current_price']) * 100
        
        # Overall overvaluation assessment
        is_overvalued = risk_score >= (threshold * 100) or upside_downside < -10
        
        if risk_score >= 80:
            risk_level = "critical"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Recommendation
        if risk_score >= 80 or upside_downside < -20:
            recommendation = "strong_sell"
        elif risk_score >= 60 or upside_downside < -10:
            recommendation = "sell"
        elif risk_score >= 40:
            recommendation = "hold"
        else:
            recommendation = "buy"
        
        confidence = min(max(1 - (risk_score / 200), 0.3), 0.95)
        
        return OvervaluationResult(
            symbol=symbol,
            is_overvalued=is_overvalued,
            overvaluation_score=risk_score,
            risk_level=risk_level,
            key_indicators=indicators,
            fair_value_estimate=fair_value,
            upside_downside=upside_downside,
            recommendation=recommendation,
            confidence=confidence
        )
    
    def _analyze_all_overvaluations(self, threshold: float) -> List[OvervaluationResult]:
        """Analyze overvaluation for all WIG80 companies"""
        results = []
        
        for _, company in self.wig80_data.iterrows():
            try:
                result = self._analyze_single_overvaluation(company['symbol'], threshold)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {company['symbol']}: {e}")
        
        return results
    
    def _estimate_fair_value(self, company: pd.Series) -> float:
        """
        Estimate fair value using multiple methodologies
        Simplified version for demonstration
        """
        
        # Technical-based fair value
        technical_fair = company['low_price'] + (company['daily_range'] * 0.3)
        
        # Volume-weighted fair value (more volume = more reliable price)
        volume_weight = company['volume_score']
        base_fair = company['current_price'] * (1 - 0.1 * (1 - volume_weight))
        
        # Momentum-adjusted fair value
        if company['change_percent'] > 10:
            momentum_discount = 0.15  # Overbought correction
        elif company['change_percent'] > 5:
            momentum_discount = 0.08
        elif company['change_percent'] < -5:
            momentum_discount = -0.05  # Oversold boost
        else:
            momentum_discount = 0
        
        fair_value = base_fair * (1 + momentum_discount)
        
        return max(fair_value, technical_fair)
    
    def detect_trend_patterns(self, symbol: str = None, lookback_days: int = 30) -> Union[List[TrendPattern], Dict[str, List[TrendPattern]]]:
        """
        Advanced pattern recognition for Polish stock market trends
        
        Args:
            symbol: Specific stock symbol (analyzes all if None)
            lookback_days: Days to look back for pattern analysis
            
        Returns:
            Identified trend patterns
        """
        
        if self.wig80_data is None:
            self.load_wig80_data()
        
        if symbol:
            return self._analyze_single_patterns(symbol, lookback_days)
        else:
            return self._analyze_all_patterns(lookback_days)
    
    def _analyze_single_patterns(self, symbol: str, lookback_days: int) -> List[TrendPattern]:
        """Analyze patterns for a single stock"""
        patterns = []
        
        company = self.wig80_data[self.wig80_data['symbol'] == symbol]
        if company.empty:
            return patterns
        
        company = company.iloc[0]
        
        # Price momentum pattern
        change_pct = company['change_percent']
        if abs(change_pct) > 5:
            strength = min(abs(change_pct) / 20, 1.0)
            direction = "bullish" if change_pct > 0 else "bearish"
            
            pattern = TrendPattern(
                pattern_name=f"{direction.title()} Momentum",
                strength=strength,
                confidence=0.8,
                direction=direction,
                duration="short",
                key_levels={
                    "support": company['low_price'],
                    "resistance": company['high_price'],
                    "current": company['current_price']
                },
                probability=strength
            )
            patterns.append(pattern)
        
        # Volatility breakout pattern
        if company['estimated_volatility'] > 6:
            pattern = TrendPattern(
                pattern_name="Volatility Breakout",
                strength=company['estimated_volatility'] / 10,
                confidence=0.7,
                direction="neutral",
                duration="medium",
                key_levels={
                    "breakout_level": company['current_price'] + (company['daily_range'] * 0.5),
                    "reversal_level": company['current_price'] - (company['daily_range'] * 0.5)
                },
                probability=0.6
            )
            patterns.append(pattern)
        
        # Volume-driven pattern
        if company['volume_score'] < 0.3:
            pattern = TrendPattern(
                pattern_name="Low Volume Accumulation/Distribution",
                strength=0.8,
                confidence=0.6,
                direction="neutral",
                duration="medium",
                key_levels={},
                probability=0.5
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_all_patterns(self, lookback_days: int) -> Dict[str, List[TrendPattern]]:
        """Analyze patterns for all WIG80 companies"""
        all_patterns = {}
        
        for _, company in self.wig80_data.iterrows():
            try:
                patterns = self._analyze_single_patterns(company['symbol'], lookback_days)
                all_patterns[company['symbol']] = patterns
            except Exception as e:
                print(f"Error analyzing patterns for {company['symbol']}: {e}")
        
        return all_patterns
    
    def calculate_correlations(self, symbols: List[str] = None) -> List[CorrelationResult]:
        """
        AI-powered correlation analysis between WIG80 stocks
        
        Args:
            symbols: List of symbols to analyze (uses top 20 by volume if None)
            
        Returns:
            Correlation analysis results
        """
        
        if self.wig80_data is None:
            self.load_wig80_data()
        
        if symbols is None:
            # Select top 20 most liquid stocks
            top_stocks = self.wig80_data.nlargest(20, 'volume_score')
            symbols = top_stocks['symbol'].tolist()
        
        correlations = []
        
        # Calculate pairwise correlations
        for i, symbol1 in enumerate(symbols):
            for symbol2 in symbols[i+1:]:
                
                corr_result = self._calculate_pair_correlation(symbol1, symbol2)
                if corr_result:
                    correlations.append(corr_result)
        
        return correlations
    
    def _calculate_pair_correlation(self, symbol1: str, symbol2: str) -> Optional[CorrelationResult]:
        """Calculate correlation between two specific stocks"""
        
        company1 = self.wig80_data[self.wig80_data['symbol'] == symbol1]
        company2 = self.wig80_data[self.wig80_data['symbol'] == symbol2]
        
        if company1.empty or company2.empty:
            return None
        
        company1 = company1.iloc[0]
        company2 = company2.iloc[0]
        
        # Simplified correlation calculation based on:
        # 1. Price momentum correlation
        # 2. Volume correlation
        # 3. Sector proxy correlation (same high/low ratio)
        
        price_corr = np.corrcoef([company1['change_percent']], [company2['change_percent']])[0, 1]
        volume_corr = np.corrcoef([company1['volume_score']], [company2['volume_score']])[0, 1]
        volatility_corr = np.corrcoef([company1['estimated_volatility']], [company2['estimated_volatility']])[0, 1]
        
        # Composite correlation
        composite_corr = (price_corr * 0.5 + volume_corr * 0.3 + volatility_corr * 0.2)
        
        # Determine relationship type
        if abs(composite_corr) > 0.7:
            relationship = "strong"
        elif abs(composite_corr) > 0.4:
            relationship = "moderate"
        else:
            relationship = "weak"
        
        if composite_corr > 0.3:
            lead_lag = "synchronized"
            relationship_type = "positive"
        elif composite_corr < -0.3:
            lead_lag = "inverse"
            relationship_type = "negative"
        else:
            lead_lag = "independent"
            relationship_type = "neutral"
        
        # Generate insights
        insights = []
        if abs(price_corr) > 0.5:
            insights.append(f"Price movements show {relationship} correlation")
        if abs(volume_corr) > 0.5:
            insights.append("Similar liquidity patterns detected")
        if abs(volatility_corr) > 0.5:
            insights.append("Comparable volatility characteristics")
        
        if not insights:
            insights.append("Limited correlation - independent price behavior")
        
        return CorrelationResult(
            stock1=symbol1,
            stock2=symbol2,
            correlation=composite_corr,
            relationship_type=relationship_type,
            significance=abs(composite_corr),
            lead_lag=lead_lag,
            insights=insights
        )
    
    def analyze_market_sentiment(self, symbol: str = None) -> Union[SentimentScore, Dict[str, SentimentScore]]:
        """
        Comprehensive market sentiment analysis
        
        Args:
            symbol: Specific stock symbol (analyzes all if None)
            
        Returns:
            Market sentiment analysis
        """
        
        if self.wig80_data is None:
            self.load_wig80_data()
        
        if symbol:
            return self._analyze_single_sentiment(symbol)
        else:
            return self._analyze_all_sentiment()
    
    def _analyze_single_sentiment(self, symbol: str) -> SentimentScore:
        """Analyze sentiment for a single stock"""
        
        company = self.wig80_data[self.wig80_data['symbol'] == symbol]
        if company.empty:
            raise ValueError(f"Symbol {symbol} not found")
        
        company = company.iloc[0]
        
        # Technical sentiment (price action)
        tech_sentiment = self._calculate_technical_sentiment(company)
        
        # Fundamental sentiment (financial health proxy)
        fund_sentiment = self._calculate_fundamental_sentiment(company)
        
        # News impact (simulated - would use real news feeds in production)
        news_impact = self._simulate_news_sentiment(company)
        
        # Overall sentiment calculation
        overall_score = (tech_sentiment * 0.4 + fund_sentiment * 0.35 + news_impact * 0.25)
        
        # Determine sentiment category
        if overall_score >= 60:
            sentiment = "bullish" if overall_score < 80 else "very_bullish"
        elif overall_score <= -60:
            sentiment = "bearish" if overall_score > -80 else "very_bearish"
        else:
            sentiment = "neutral"
        
        # Key factors
        key_factors = []
        if abs(company['change_percent']) > 5:
            key_factors.append(f"Strong price movement: {company['change_percent']:+.1f}%")
        if company['estimated_volatility'] > 6:
            key_factors.append("High volatility indicating uncertainty")
        if company['volume_score'] > 0.7:
            key_factors.append("High trading volume suggests interest")
        elif company['volume_score'] < 0.3:
            key_factors.append("Low volume may indicate limited interest")
        
        confidence = min(abs(overall_score) / 100 + 0.3, 0.95)
        
        return SentimentScore(
            overall_sentiment=sentiment,
            score=overall_score,
            confidence=confidence,
            key_factors=key_factors,
            news_impact=news_impact,
            technical_sentiment=tech_sentiment,
            fundamental_sentiment=fund_sentiment
        )
    
    def _calculate_technical_sentiment(self, company: pd.Series) -> float:
        """Calculate technical sentiment from price action"""
        score = 0
        
        # Price momentum
        if company['change_percent'] > 10:
            score += 30
        elif company['change_percent'] > 5:
            score += 20
        elif company['change_percent'] > 2:
            score += 10
        elif company['change_percent'] < -10:
            score -= 30
        elif company['change_percent'] < -5:
            score -= 20
        elif company['change_percent'] < -2:
            score -= 10
        
        # Volatility impact
        if company['estimated_volatility'] > 8:
            score -= 15  # High volatility often negative
        elif company['estimated_volatility'] < 2:
            score += 5   # Low volatility can be positive
        
        # Volume confirmation
        if company['volume_score'] > 0.6 and company['change_percent'] > 0:
            score += 10  # Volume confirming price move
        elif company['volume_score'] > 0.6 and company['change_percent'] < 0:
            score -= 10  # Volume confirming downward move
        elif company['volume_score'] < 0.3 and abs(company['change_percent']) > 5:
            score -= 5   # Low volume with big moves is concerning
        
        return max(-100, min(100, score))
    
    def _calculate_fundamental_sentiment(self, company: pd.Series) -> float:
        """Calculate fundamental sentiment (simplified proxy)"""
        score = 50  # Neutral baseline
        
        # Use available metrics as proxies
        # In production, would use real P/E, ROE, debt ratios, etc.
        
        # Price strength indicator
        if company['change_percent'] > 0:
            score += (company['change_percent'] * 0.5)
        
        # Liquidity score
        score += (company['volume_score'] - 0.5) * 20
        
        return max(-100, min(100, score))
    
    def _simulate_news_sentiment(self, company: pd.Series) -> float:
        """
        Simulate news sentiment (in production, would use real news feeds)
        For now, generate based on company characteristics
        """
        np.random.seed(hash(company['symbol']) % 2**32)  # Deterministic per symbol
        
        # Base sentiment on company performance
        base_sentiment = company['change_percent'] * 0.3
        
        # Add some randomness
        news_sentiment = base_sentiment + np.random.normal(0, 5)
        
        return max(-50, min(50, news_sentiment))
    
    def _analyze_all_sentiment(self) -> Dict[str, SentimentScore]:
        """Analyze sentiment for all WIG80 companies"""
        sentiment_results = {}
        
        for _, company in self.wig80_data.iterrows():
            try:
                sentiment = self._analyze_single_sentiment(company['symbol'])
                sentiment_results[company['symbol']] = sentiment
            except Exception as e:
                print(f"Error analyzing sentiment for {company['symbol']}: {e}")
        
        return sentiment_results
    
    def generate_market_overview(self) -> Dict:
        """
        Generate comprehensive market overview with AI insights
        
        Returns:
            Complete market analysis overview
        """
        
        if self.wig80_data is None:
            self.load_wig80_data()
        
        # Market statistics
        total_companies = len(self.wig80_data)
        gainers = len(self.wig80_data[self.wig80_data['change_percent'] > 0])
        losers = len(self.wig80_data[self.wig80_data['change_percent'] < 0])
        unchanged = total_companies - gainers - losers
        
        # Top performers
        top_gainers = self.wig80_data.nlargest(5, 'change_percent')[['symbol', 'company_name', 'change_percent']].to_dict('records')
        top_losers = self.wig80_data.nsmallest(5, 'change_percent')[['symbol', 'company_name', 'change_percent']].to_dict('records')
        
        # Volume analysis
        high_volume = self.wig80_data[self.wig80_data['volume_score'] > 0.7]
        low_volume = self.wig80_data[self.wig80_data['volume_score'] < 0.3]
        
        # Sentiment analysis
        all_sentiment = self.analyze_market_sentiment()
        sentiment_scores = [s.score for s in all_sentiment.values()]
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
        
        # Overvaluation analysis
        overvaluation_results = self.detect_overvaluation()
        overvalued_count = sum(1 for r in overvaluation_results if r.is_overvalued)
        
        # Correlation insights
        correlations = self.calculate_correlations()
        strong_correlations = [c for c in correlations if abs(c.correlation) > 0.5]
        
        overview = {
            "market_statistics": {
                "total_companies": total_companies,
                "gainers": gainers,
                "losers": losers,
                "unchanged": unchanged,
                "market_sentiment": "bullish" if avg_sentiment > 10 else "bearish" if avg_sentiment < -10 else "neutral",
                "average_sentiment_score": round(avg_sentiment, 2)
            },
            "top_performers": {
                "gainers": top_gainers,
                "losers": top_losers
            },
            "liquidity_analysis": {
                "high_volume_stocks": len(high_volume),
                "low_volume_stocks": len(low_volume),
                "high_volume_examples": high_volume[['symbol', 'company_name', 'volume_score']].head(3).to_dict('records')
            },
            "valuation_analysis": {
                "overvalued_companies": overvalued_count,
                "overvaluation_rate": round((overvalued_count / total_companies) * 100, 1),
                "high_risk_companies": [r for r in overvaluation_results if r.risk_level in ['high', 'critical']]
            },
            "correlation_insights": {
                "total_correlations_analyzed": len(correlations),
                "strong_correlations": len(strong_correlations),
                "correlation_examples": strong_correlations[:3] if strong_correlations else []
            },
            "risk_assessment": {
                "high_volatility_stocks": len(self.wig80_data[self.wig80_data['estimated_volatility'] > 6]),
                "low_liquidity_risk": len(low_volume),
                "overall_market_risk": "high" if avg_sentiment < -20 or overvalued_count > total_companies * 0.3 else "medium" if avg_sentiment < 0 else "low"
            },
            "ai_insights": self._generate_ai_insights(overvaluation_results, all_sentiment, correlations),
            "generated_at": datetime.now().isoformat()
        }
        
        return overview
    
    def _generate_ai_insights(self, overvaluation_results, sentiment_results, correlations) -> List[str]:
        """Generate AI-powered market insights"""
        insights = []
        
        # Sentiment insights
        bullish_count = sum(1 for s in sentiment_results.values() if 'bullish' in s.overall_sentiment)
        bearish_count = sum(1 for s in sentiment_results.values() if 'bearish' in s.overall_sentiment)
        
        if bullish_count > bearish_count * 1.5:
            insights.append("Market sentiment strongly favors bullish positions across WIG80")
        elif bearish_count > bullish_count * 1.5:
            insights.append("Bearish sentiment dominates - consider defensive positioning")
        else:
            insights.append("Mixed sentiment suggests tactical trading approach")
        
        # Overvaluation insights
        overvalued_high_risk = [r for r in overvaluation_results if r.risk_level in ['high', 'critical']]
        if len(overvalued_high_risk) > len(overvaluation_results) * 0.2:
            insights.append("Significant portion of WIG80 shows overvaluation - exercise caution")
        
        # Correlation insights
        strong_positive_corr = [c for c in correlations if c.correlation > 0.6]
        if len(strong_positive_corr) > len(correlations) * 0.1:
            insights.append("Strong sector correlations detected - portfolio diversification recommended")
        
        # Volatility insights
        high_vol_count = len([r for r in overvaluation_results if any('volatility' in ind.lower() for ind in r.key_indicators)])
        if high_vol_count > len(overvaluation_results) * 0.3:
            insights.append("Elevated volatility across multiple stocks - risk management crucial")
        
        return insights[:5]  # Return top 5 insights
    
    def export_analysis(self, output_path: str, analysis_type: str = "overview") -> bool:
        """
        Export analysis results to file
        
        Args:
            output_path: Output file path
            analysis_type: Type of analysis to export
            
        Returns:
            Success status
        """
        try:
            if analysis_type == "overview":
                data = self.generate_market_overview()
            elif analysis_type == "overvaluation":
                data = [asdict(r) for r in self.detect_overvaluation()]
            elif analysis_type == "sentiment":
                data = {k: asdict(v) for k, v in self.analyze_market_sentiment().items()}
            elif analysis_type == "correlations":
                data = [asdict(c) for c in self.calculate_correlations()]
            else:
                raise ValueError(f"Unknown analysis type: {analysis_type}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✓ Analysis exported to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting analysis: {e}")
            return False

def main():
    """Main execution function for testing"""
    
    # Initialize AI system
    ai = PolishMarketAI()
    
    # Load data
    ai.load_wig80_data()
    
    print("\n" + "="*60)
    print("POLISH MARKET AI INSIGHTS SYSTEM")
    print("="*60)
    
    # Generate comprehensive analysis
    overview = ai.generate_market_overview()
    
    print(f"\n📊 MARKET OVERVIEW:")
    print(f"Total Companies: {overview['market_statistics']['total_companies']}")
    print(f"Market Sentiment: {overview['market_statistics']['market_sentiment']} (Score: {overview['market_statistics']['average_sentiment_score']})")
    print(f"Gainers: {overview['market_statistics']['gainers']}, Losers: {overview['market_statistics']['losers']}")
    
    print(f"\n⚠️  VALUATION ANALYSIS:")
    print(f"Overvalued Companies: {overview['valuation_analysis']['overvalued_companies']} ({overview['valuation_analysis']['overvaluation_rate']}%)")
    
    print(f"\n🔗 CORRELATION INSIGHTS:")
    print(f"Strong Correlations Found: {overview['correlation_insights']['strong_correlations']}")
    
    print(f"\n🤖 AI INSIGHTS:")
    for insight in overview['ai_insights']:
        print(f"• {insight}")
    
    # Test individual components
    print(f"\n🎯 INDIVIDUAL ANALYSIS EXAMPLES:")
    
    # Test overvaluation detection
    overvaluation = ai.detect_overvaluation()
    overvalued = [r for r in overvaluation if r.is_overvalued][:3]
    if overvalued:
        print(f"\nMost Overvalued Stocks:")
        for result in overvalued:
            print(f"  {result.symbol}: {result.risk_level} risk, {result.overvaluation_score:.1f}% overvaluation score")
    
    # Test sentiment analysis
    sentiment = ai.analyze_market_sentiment()
    most_bullish = sorted(sentiment.items(), key=lambda x: x[1].score, reverse=True)[:3]
    print(f"\nMost Bullish Sentiment:")
    for symbol, score in most_bullish:
        print(f"  {symbol}: {score.score:.1f} ({score.overall_sentiment})")
    
    # Test pattern detection
    patterns = ai.detect_trend_patterns()
    print(f"\n📈 TREND PATTERNS DETECTED:")
    total_patterns = sum(len(p) for p in patterns.values())
    print(f"Total patterns found: {total_patterns}")
    
    return ai

if __name__ == "__main__":
    ai_system = main()