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

        // Fetch company data
        const companyResponse = await fetch(
            `${supabaseUrl}/rest/v1/companies?symbol=eq.${symbol}&select=*`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        if (!companyResponse.ok) {
            throw new Error('Failed to fetch company data');
        }

        const companies = await companyResponse.json();
        if (!companies || companies.length === 0) {
            throw new Error(`Company ${symbol} not found`);
        }

        const company = companies[0];

        // Fetch recent AI analyses
        const analysesResponse = await fetch(
            `${supabaseUrl}/rest/v1/ai_analysis?symbol=eq.${symbol}&order=created_at.desc&limit=10`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        let recentAnalyses = [];
        if (analysesResponse.ok) {
            recentAnalyses = await analysesResponse.json();
        }

        // Sentiment analysis logic
        const analysis = performSentimentAnalysis(company, recentAnalyses);

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
                analysis_type: 'sentiment',
                agent_name: 'Sentiment Analyst',
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

function performSentimentAnalysis(company: any, recentAnalyses: any[]) {
    const keyPoints = [];
    let score = 50; // Start neutral

    // Current price action sentiment
    const changePercent = parseFloat(company.change_percent || 0);
    if (changePercent > 10) {
        keyPoints.push('Market showing very strong bullish sentiment with double-digit gains');
        score += 20;
    } else if (changePercent > 5) {
        keyPoints.push('Strong positive market sentiment with significant daily gains');
        score += 15;
    } else if (changePercent > 2) {
        keyPoints.push('Positive market sentiment with moderate gains');
        score += 10;
    } else if (changePercent < -10) {
        keyPoints.push('Very negative market sentiment with significant selloff');
        score -= 20;
    } else if (changePercent < -5) {
        keyPoints.push('Bearish market sentiment with notable losses');
        score -= 15;
    } else if (changePercent < -2) {
        keyPoints.push('Negative market sentiment with moderate losses');
        score -= 10;
    }

    // Analyze consensus from other AI agents
    const fundamentalAnalyses = recentAnalyses.filter(a => a.analysis_type === 'fundamental');
    const technicalAnalyses = recentAnalyses.filter(a => a.analysis_type === 'technical');

    if (fundamentalAnalyses.length > 0) {
        const latestFundamental = fundamentalAnalyses[0];
        if (latestFundamental.sentiment === 'bullish') {
            keyPoints.push('Fundamental analysis shows positive valuation metrics');
            score += 10;
        } else if (latestFundamental.sentiment === 'bearish') {
            keyPoints.push('Fundamental analysis raises valuation concerns');
            score -= 10;
        }
    }

    if (technicalAnalyses.length > 0) {
        const latestTechnical = technicalAnalyses[0];
        if (latestTechnical.sentiment === 'bullish') {
            keyPoints.push('Technical indicators confirm bullish momentum');
            score += 10;
        } else if (latestTechnical.sentiment === 'bearish') {
            keyPoints.push('Technical indicators suggest bearish pressure');
            score -= 10;
        }
    }

    // Market positioning analysis
    if (company.category) {
        if (company.category === 'growth_potential') {
            keyPoints.push('Identified as growth opportunity by market filters');
            score += 5;
        } else if (company.category === 'small_cap_value') {
            keyPoints.push('Classified as small-cap value play - attractive for contrarian investors');
            score += 5;
        }
    }

    // Overall score consideration
    if (company.overall_score && company.overall_score > 0.6) {
        keyPoints.push(`Strong composite score (${(company.overall_score * 100).toFixed(0)}%) indicates market confidence`);
        score += 10;
    } else if (company.overall_score && company.overall_score < 0.4) {
        keyPoints.push('Lower composite score suggests market uncertainty');
        score -= 5;
    }

    // Liquidity sentiment
    if (company.liquidity_score) {
        if (company.liquidity_score >= 0.8) {
            keyPoints.push('High liquidity provides confidence for position building');
            score += 5;
        } else if (company.liquidity_score < 0.3) {
            keyPoints.push('Low liquidity may indicate limited market interest');
            score -= 5;
        }
    }

    // Determine overall sentiment
    let sentiment = 'neutral';
    let recommendation = 'hold';
    
    if (score >= 75) {
        sentiment = 'very_bullish';
        recommendation = 'strong_buy';
    } else if (score >= 60) {
        sentiment = 'bullish';
        recommendation = 'buy';
    } else if (score <= 25) {
        sentiment = 'very_bearish';
        recommendation = 'strong_sell';
    } else if (score <= 40) {
        sentiment = 'bearish';
        recommendation = 'sell';
    }

    const confidence = Math.min(Math.max(score / 100, 0), 1);

    const detailed_analysis = `
Market Sentiment Analysis for ${company.company_name} (${company.symbol}):

Current Market Status:
- Price: ${company.current_price} PLN
- Daily Change: ${changePercent > 0 ? '+' : ''}${changePercent.toFixed(2)}%
- Trading Volume: ${company.trading_volume}

Sentiment Indicators:
${keyPoints.map(point => `- ${point}`).join('\n')}

Multi-Agent Consensus:
${fundamentalAnalyses.length > 0 ? `- Fundamental Outlook: ${fundamentalAnalyses[0].sentiment}` : '- No recent fundamental analysis'}
${technicalAnalyses.length > 0 ? `- Technical Outlook: ${technicalAnalyses[0].sentiment}` : '- No recent technical analysis'}

Overall Market Sentiment (Score: ${score}/100):
${sentiment === 'very_bullish' || sentiment === 'bullish'
    ? 'Strong positive market sentiment across multiple indicators. Market participants are showing confidence in this stock.'
    : sentiment === 'very_bearish' || sentiment === 'bearish'
    ? 'Negative market sentiment prevails. Consider defensive positioning or await better sentiment indicators.'
    : 'Mixed market signals. No clear directional bias from market participants at this time.'
}

Recommendation: ${recommendation.toUpperCase().replace('_', ' ')}
Confidence Level: ${(confidence * 100).toFixed(0)}%

Risk Assessment:
${company.liquidity_score && company.liquidity_score < 0.5 
    ? 'CAUTION: Lower liquidity may amplify price volatility and impact execution.'
    : 'Good liquidity supports confident position management.'
}
    `.trim();

    return {
        sentiment,
        recommendation,
        confidence,
        key_points: keyPoints,
        detailed_analysis,
        score
    };
}
