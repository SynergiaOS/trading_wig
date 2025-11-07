#!/usr/bin/env python3
"""
Polish Market AI Demo Script
Demonstrates the capabilities of the AI insights and trading signals system.
"""

import sys
import os
sys.path.append('/workspace/code')

from polish_market_ai import PolishMarketAI
from ai_trading_signals import AITradingSignals

def main():
    print("🚀 POLISH MARKET AI SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize systems
    ai = PolishMarketAI()
    signals_system = AITradingSignals()
    
    # Load data
    print("📊 Loading WIG80 data...")
    ai.load_wig80_data()
    print(f"✓ Loaded {len(ai.wig80_data)} companies")
    
    # 1. Market Overview Analysis
    print("\n1️⃣ MARKET OVERVIEW ANALYSIS")
    print("-" * 30)
    overview = ai.generate_market_overview()
    
    print(f"Market Sentiment: {overview['market_statistics']['market_sentiment']}")
    print(f"Total Companies: {overview['market_statistics']['total_companies']}")
    print(f"Gainers vs Losers: {overview['market_statistics']['gainers']} vs {overview['market_statistics']['losers']}")
    print(f"AI Insights: {len(overview['ai_insights'])} key insights generated")
    
    # 2. Overvaluation Detection
    print("\n2️⃣ OVERVALUATION DETECTION")
    print("-" * 30)
    overvaluation_results = ai.detect_overvaluation()
    overvalued = [r for r in overvaluation_results if r.is_overvalued]
    
    if overvalued:
        print(f"⚠️ Found {len(overvalued)} overvalued companies:")
        for result in overvalued[:3]:
            print(f"  • {result.symbol}: {result.risk_level} risk ({result.overvaluation_score:.1f}% score)")
    else:
        print("✅ No significantly overvalued companies detected")
    
    # 3. Sentiment Analysis
    print("\n3️⃣ MARKET SENTIMENT ANALYSIS")
    print("-" * 30)
    sentiment_results = ai.analyze_market_sentiment()
    
    # Top bullish and bearish
    bullish = [(s, data) for s, data in sentiment_results.items() if 'bullish' in data.overall_sentiment]
    bearish = [(s, data) for s, data in sentiment_results.items() if 'bearish' in data.overall_sentiment]
    
    print(f"Bullish sentiment: {len(bullish)} companies")
    print(f"Bearish sentiment: {len(bearish)} companies")
    
    if bullish:
        top_bullish = sorted(bullish, key=lambda x: x[1].score, reverse=True)[:2]
        print("Most bullish:", ", ".join([s for s, _ in top_bullish]))
    
    # 4. Trading Signals Generation
    print("\n4️⃣ AI TRADING SIGNALS")
    print("-" * 30)
    signals = signals_system.generate_trading_signals(min_confidence=0.6)
    
    buy_signals = [s for s in signals if s.signal_type.value in ['buy', 'strong_buy']]
    sell_signals = [s for s in signals if s.signal_type.value in ['sell', 'strong_sell']]
    
    print(f"Generated {len(signals)} signals total")
    print(f"Buy signals: {len(buy_signals)}")
    print(f"Sell signals: {len(sell_signals)}")
    
    if buy_signals:
        print("\n🎯 Top Buy Signals:")
        for i, signal in enumerate(buy_signals[:3], 1):
            print(f"{i}. {signal.symbol}")
            print(f"   Confidence: {signal.confidence:.1%}")
            print(f"   Target: {signal.target_price:.2f} PLN")
            print(f"   Expected Return: {signal.expected_return:+.1f}%")
            print(f"   Risk Level: {signal.risk_level.value}")
            print()
    
    # 5. Portfolio Recommendations
    print("5️⃣ PORTFOLIO RECOMMENDATIONS")
    print("-" * 30)
    portfolio_signal = signals_system.generate_portfolio_signals(signals)
    
    print(f"Overall Portfolio Sentiment: {portfolio_signal.overall_sentiment}")
    print(f"Expected Portfolio Return: {portfolio_signal.expected_portfolio_return:+.1f}%")
    print(f"Portfolio Risk Score: {portfolio_signal.risk_score:.1f}/100")
    print(f"Market Timing: {portfolio_signal.market_timing}")
    
    if portfolio_signal.recommended_allocation:
        print("\nRecommended Allocation:")
        for symbol, allocation in list(portfolio_signal.recommended_allocation.items())[:3]:
            print(f"  {symbol}: {allocation:.1%}")
    
    # 6. Quick Stock Analysis Example
    print("\n6️⃣ INDIVIDUAL STOCK ANALYSIS EXAMPLE")
    print("-" * 30)
    example_symbol = "bumech"  # Use a stock that showed good signals
    
    try:
        # Overvaluation analysis
        overval = ai.detect_overvaluation(example_symbol)
        sentiment = ai.analyze_market_sentiment(example_symbol)
        patterns = ai.detect_trend_patterns(example_symbol)
        
        print(f"Analysis for {example_symbol}:")
        print(f"  Overvaluation Risk: {overval.risk_level} ({overval.overvaluation_score:.1f}% score)")
        print(f"  Market Sentiment: {sentiment.overall_sentiment} ({sentiment.score:.1f})")
        print(f"  Trend Patterns Found: {len(patterns)}")
        
        if patterns:
            print(f"  Main Pattern: {patterns[0].pattern_name} (strength: {patterns[0].strength:.2f})")
            
    except Exception as e:
        print(f"Could not analyze {example_symbol}: {e}")
    
    # 7. System Export Demo
    print("\n7️⃣ DATA EXPORT DEMO")
    print("-" * 30)
    
    # Export market overview
    overview_path = "/workspace/polish_market_analysis.json"
    if ai.export_analysis(overview_path, "overview"):
        print(f"✓ Market overview exported to {overview_path}")
    
    # Export trading signals
    signals_path = "/workspace/trading_signals.json"
    if signals_system.export_signals(signals[:5], signals_path, portfolio_signal):  # Export top 5 signals
        print(f"✓ Top trading signals exported to {signals_path}")
    
    print("\n" + "=" * 50)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("\nNext Steps:")
    print("• Review exported analysis files")
    print("• Experiment with different confidence thresholds")
    print("• Analyze specific stocks of interest")
    print("• Implement paper trading with generated signals")
    print("• Monitor performance and refine parameters")
    
    return True

if __name__ == "__main__":
    main()