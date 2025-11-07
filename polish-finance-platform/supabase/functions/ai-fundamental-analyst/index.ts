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

        // Fundamental analysis logic
        const analysis = performFundamentalAnalysis(company);

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
                analysis_type: 'fundamental',
                agent_name: 'Fundamental Analyst',
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

function performFundamentalAnalysis(company: any) {
    const keyPoints = [];
    let score = 50; // Start neutral

    // P/E Ratio Analysis
    if (company.pe_ratio) {
        if (company.pe_ratio < 10) {
            keyPoints.push(`Very attractive P/E ratio of ${company.pe_ratio} (below 10)`);
            score += 15;
        } else if (company.pe_ratio < 15) {
            keyPoints.push(`Good P/E ratio of ${company.pe_ratio} (below 15)`);
            score += 10;
        } else if (company.pe_ratio > 30) {
            keyPoints.push(`High P/E ratio of ${company.pe_ratio} indicates premium valuation`);
            score -= 10;
        }
    } else {
        keyPoints.push('P/E ratio not available - limited profitability data');
        score -= 5;
    }

    // P/B Ratio Analysis
    if (company.pb_ratio) {
        if (company.pb_ratio < 1.5) {
            keyPoints.push(`Excellent P/B ratio of ${company.pb_ratio} (below 1.5) - trading below book value`);
            score += 15;
        } else if (company.pb_ratio < 3) {
            keyPoints.push(`Good P/B ratio of ${company.pb_ratio} (below 3)`);
            score += 5;
        } else if (company.pb_ratio > 7) {
            keyPoints.push(`High P/B ratio of ${company.pb_ratio} - premium valuation`);
            score -= 10;
        }
    }

    // Value Score Analysis
    if (company.value_score && company.value_score > 0.6) {
        keyPoints.push(`Strong value score of ${(company.value_score * 100).toFixed(0)}%`);
        score += 10;
    }

    // Recent Performance
    if (company.change_percent) {
        if (company.change_percent > 5) {
            keyPoints.push(`Strong momentum with ${company.change_percent.toFixed(2)}% daily gain`);
            score += 5;
        } else if (company.change_percent < -5) {
            keyPoints.push(`Negative momentum with ${company.change_percent.toFixed(2)}% daily loss`);
            score -= 5;
        }
    }

    // Trading Volume (Liquidity)
    if (company.trading_volume_numeric) {
        if (company.trading_volume_numeric < 50000) {
            keyPoints.push('Low liquidity - be cautious with position sizing');
            score -= 10;
        } else if (company.trading_volume_numeric > 500000) {
            keyPoints.push('High liquidity - good for quick entry/exit');
            score += 5;
        }
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
Fundamental Analysis for ${company.company_name} (${company.symbol}):

Current Price: ${company.current_price} PLN (${company.change_percent > 0 ? '+' : ''}${company.change_percent?.toFixed(2)}%)

Valuation Metrics:
- P/E Ratio: ${company.pe_ratio || 'N/A'}
- P/B Ratio: ${company.pb_ratio || 'N/A'}
- Value Score: ${company.value_score ? (company.value_score * 100).toFixed(0) + '%' : 'N/A'}

Key Insights:
${keyPoints.map(point => `- ${point}`).join('\n')}

Overall Assessment (Score: ${score}/100):
${sentiment === 'bullish' 
    ? 'The company shows attractive fundamental characteristics for investment consideration.'
    : sentiment === 'bearish'
    ? 'The fundamental metrics suggest caution. Consider waiting for better entry points.'
    : 'Mixed fundamental signals. Requires additional analysis before making a decision.'
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
        score
    };
}
