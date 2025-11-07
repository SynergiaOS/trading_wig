Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');

        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        const { symbol } = await req.json();

        if (!symbol) {
            throw new Error('Symbol is required');
        }

        // Fetch price history (last 30 records)
        const historyResponse = await fetch(
            `${supabaseUrl}/rest/v1/price_history?symbol=eq.${symbol}&order=timestamp.desc&limit=30`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        if (!historyResponse.ok) {
            throw new Error('Failed to fetch price history');
        }

        const priceHistory = await historyResponse.json();

        if (!priceHistory || priceHistory.length === 0) {
            throw new Error(`No price history found for ${symbol}`);
        }

        // Technical analysis logic
        const analysis = performTechnicalAnalysis(priceHistory, symbol);

        // Store analysis in database
        await fetch(`${supabaseUrl}/rest/v1/ai_analysis`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symbol: symbol,
                analysis_type: 'technical',
                agent_name: 'Technical Analyst',
                sentiment: analysis.sentiment,
                recommendation: analysis.recommendation,
                confidence_score: analysis.confidence,
                key_points: JSON.stringify(analysis.key_points),
                detailed_analysis: analysis.detailed_analysis
            })
        });

        return new Response(JSON.stringify({
            data: analysis
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Analysis error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'ANALYSIS_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

function performTechnicalAnalysis(priceHistory: any[], symbol: string) {
    const keyPoints = [];
    let score = 50; // Start neutral

    // Sort by timestamp ascending for calculations
    const sortedHistory = [...priceHistory].reverse();
    const latestPrice = sortedHistory[sortedHistory.length - 1];
    const prices = sortedHistory.map(h => parseFloat(h.price));

    // Calculate moving averages
    const sma5 = calculateSMA(prices, 5);
    const sma10 = calculateSMA(prices, 10);
    const sma20 = calculateSMA(prices, 20);

    // Trend Analysis
    if (sma5 && sma10 && sma20) {
        if (sma5 > sma10 && sma10 > sma20) {
            keyPoints.push('Strong uptrend: SMA(5) > SMA(10) > SMA(20)');
            score += 20;
        } else if (sma5 < sma10 && sma10 < sma20) {
            keyPoints.push('Strong downtrend: SMA(5) < SMA(10) < SMA(20)');
            score -= 20;
        } else if (sma5 > sma10) {
            keyPoints.push('Short-term uptrend: SMA(5) > SMA(10)');
            score += 10;
        } else if (sma5 < sma10) {
            keyPoints.push('Short-term downtrend: SMA(5) < SMA(10)');
            score -= 10;
        }
    }

    // Recent momentum (last price change)
    const recentChange = parseFloat(latestPrice.change_percent || 0);
    if (recentChange > 5) {
        keyPoints.push(`Strong bullish momentum: +${recentChange.toFixed(2)}% today`);
        score += 15;
    } else if (recentChange > 2) {
        keyPoints.push(`Positive momentum: +${recentChange.toFixed(2)}% today`);
        score += 5;
    } else if (recentChange < -5) {
        keyPoints.push(`Strong bearish momentum: ${recentChange.toFixed(2)}% today`);
        score -= 15;
    } else if (recentChange < -2) {
        keyPoints.push(`Negative momentum: ${recentChange.toFixed(2)}% today`);
        score -= 5;
    }

    // Volatility Analysis
    const volatility = calculateVolatility(prices);
    if (volatility > 10) {
        keyPoints.push(`High volatility detected (${volatility.toFixed(2)}%) - suitable for short-term trading`);
        score += 5;
    } else if (volatility < 3) {
        keyPoints.push(`Low volatility (${volatility.toFixed(2)}%) - stable price action`);
        score += 2;
    }

    // Support/Resistance levels
    const recentHigh = Math.max(...prices.slice(-10));
    const recentLow = Math.min(...prices.slice(-10));
    const currentPrice = prices[prices.length - 1];
    
    if (currentPrice >= recentHigh * 0.98) {
        keyPoints.push('Price near recent resistance - potential breakout or reversal');
        score += 5;
    } else if (currentPrice <= recentLow * 1.02) {
        keyPoints.push('Price near recent support - potential bounce opportunity');
        score += 5;
    }

    // Volume trend analysis
    const volumeTrend = analyzeVolumeTrend(sortedHistory);
    if (volumeTrend === 'increasing') {
        keyPoints.push('Increasing volume confirms trend strength');
        score += 10;
    } else if (volumeTrend === 'decreasing') {
        keyPoints.push('Decreasing volume suggests weakening trend');
        score -= 5;
    }

    // Determine sentiment and recommendation
    let sentiment = 'neutral';
    let recommendation = 'hold';
    
    if (score >= 70) {
        sentiment = 'bullish';
        recommendation = 'strong_buy';
    } else if (score >= 60) {
        sentiment = 'bullish';
        recommendation = 'buy';
    } else if (score <= 40) {
        sentiment = 'bearish';
        recommendation = 'sell';
    } else if (score <= 30) {
        sentiment = 'bearish';
        recommendation = 'strong_sell';
    }

    const confidence = Math.min(Math.max(score / 100, 0), 1);

    const detailed_analysis = `
Technical Analysis for ${symbol}:

Current Price: ${latestPrice.price} PLN (${recentChange > 0 ? '+' : ''}${recentChange.toFixed(2)}%)

Technical Indicators:
- SMA(5): ${sma5?.toFixed(2) || 'N/A'}
- SMA(10): ${sma10?.toFixed(2) || 'N/A'}
- SMA(20): ${sma20?.toFixed(2) || 'N/A'}
- Volatility: ${volatility.toFixed(2)}%
- Support Level: ${recentLow.toFixed(2)} PLN
- Resistance Level: ${recentHigh.toFixed(2)} PLN

Key Technical Insights:
${keyPoints.map(point => `- ${point}`).join('\n')}

Trading Signal (Score: ${score}/100):
${sentiment === 'bullish' 
    ? 'Technical indicators suggest upward momentum. Consider entry positions with tight stop-loss.'
    : sentiment === 'bearish'
    ? 'Technical indicators show weakness. Consider taking profits or avoiding new positions.'
    : 'Mixed technical signals. Wait for clearer trend confirmation.'
}

Recommendation: ${recommendation.toUpperCase().replace('_', ' ')}
Confidence Level: ${(confidence * 100).toFixed(0)}%
    `.trim();

    return {
        sentiment,
        recommendation,
        confidence,
        key_points: keyPoints,
        detailed_analysis,
        score,
        indicators: {
            sma5,
            sma10,
            sma20,
            volatility,
            support: recentLow,
            resistance: recentHigh,
            currentPrice
        }
    };
}

function calculateSMA(prices: number[], period: number): number | null {
    if (prices.length < period) return null;
    const relevantPrices = prices.slice(-period);
    return relevantPrices.reduce((sum, price) => sum + price, 0) / period;
}

function calculateVolatility(prices: number[]): number {
    if (prices.length < 2) return 0;
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
    }
    const mean = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
    const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - mean, 2), 0) / returns.length;
    return Math.sqrt(variance) * 100;
}

function analyzeVolumeTrend(history: any[]): string {
    if (history.length < 5) return 'unknown';
    
    const recentVolumes = history.slice(-5).map(h => h.volume || 0);
    const previousVolumes = history.slice(-10, -5).map(h => h.volume || 0);
    
    const recentAvg = recentVolumes.reduce((a, b) => a + b, 0) / recentVolumes.length;
    const previousAvg = previousVolumes.reduce((a, b) => a + b, 0) / previousVolumes.length;
    
    if (recentAvg > previousAvg * 1.2) return 'increasing';
    if (recentAvg < previousAvg * 0.8) return 'decreasing';
    return 'stable';
}
