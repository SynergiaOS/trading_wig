/**
 * Alpha Vantage API Integration for Enhanced Market Data
 * Provides company overview, fundamentals, and news sentiment
 * Rate limit: 25 requests/day (free tier) - use strategically
 */

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
        const alphaVantageKey = 'C8C4Q9GFD4FXKG3A';
        const { symbol, dataType = 'quote' } = await req.json();

        if (!symbol) {
            throw new Error('Symbol is required');
        }

        // Map Polish symbols to international symbols if needed
        // Alpha Vantage might have limited Polish stock coverage
        const internationalSymbol = mapToInternationalSymbol(symbol);

        let data;
        switch (dataType) {
            case 'quote':
                data = await fetchGlobalQuote(internationalSymbol, alphaVantageKey);
                break;
            case 'overview':
                data = await fetchCompanyOverview(internationalSymbol, alphaVantageKey);
                break;
            case 'news':
                data = await fetchNewsSentiment(internationalSymbol, alphaVantageKey);
                break;
            case 'technicals':
                data = await fetchTechnicalIndicators(internationalSymbol, alphaVantageKey);
                break;
            default:
                throw new Error(`Unknown data type: ${dataType}`);
        }

        return new Response(JSON.stringify({
            data: {
                symbol: symbol,
                international_symbol: internationalSymbol,
                data_type: dataType,
                result: data,
                timestamp: new Date().toISOString()
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Alpha Vantage API error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'ALPHA_VANTAGE_ERROR',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Fetch real-time quote from Alpha Vantage
 */
async function fetchGlobalQuote(symbol: string, apiKey: string) {
    const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${apiKey}`;
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Alpha Vantage API error: ${response.status}`);
    }

    const data = await response.json();
    
    if (data['Error Message']) {
        throw new Error(data['Error Message']);
    }

    if (data['Note']) {
        // Rate limit exceeded
        throw new Error('API rate limit exceeded. Please try again later.');
    }

    return data['Global Quote'] || {};
}

/**
 * Fetch company overview from Alpha Vantage
 */
async function fetchCompanyOverview(symbol: string, apiKey: string) {
    const url = `https://www.alphavantage.co/query?function=OVERVIEW&symbol=${symbol}&apikey=${apiKey}`;
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Alpha Vantage API error: ${response.status}`);
    }

    const data = await response.json();
    
    if (data['Error Message']) {
        throw new Error(data['Error Message']);
    }

    if (data['Note']) {
        throw new Error('API rate limit exceeded. Please try again later.');
    }

    return data;
}

/**
 * Fetch news sentiment from Alpha Vantage
 */
async function fetchNewsSentiment(symbol: string, apiKey: string) {
    const url = `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=${symbol}&apikey=${apiKey}`;
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Alpha Vantage API error: ${response.status}`);
    }

    const data = await response.json();
    
    if (data['Error Message']) {
        throw new Error(data['Error Message']);
    }

    if (data['Note']) {
        throw new Error('API rate limit exceeded. Please try again later.');
    }

    return data;
}

/**
 * Fetch technical indicators (RSI) from Alpha Vantage
 */
async function fetchTechnicalIndicators(symbol: string, apiKey: string) {
    const url = `https://www.alphavantage.co/query?function=RSI&symbol=${symbol}&interval=daily&time_period=14&series_type=close&apikey=${apiKey}`;
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Alpha Vantage API error: ${response.status}`);
    }

    const data = await response.json();
    
    if (data['Error Message']) {
        throw new Error(data['Error Message']);
    }

    if (data['Note']) {
        throw new Error('API rate limit exceeded. Please try again later.');
    }

    return data;
}

/**
 * Map Polish stock symbols to international symbols
 * Note: Alpha Vantage has limited coverage of Polish stocks
 * This function attempts to map to global symbols where available
 */
function mapToInternationalSymbol(polishSymbol: string): string {
    // Map known Polish companies with international presence
    const symbolMap: { [key: string]: string } = {
        'PKN': 'PKN.WSE',  // PKN Orlen
        'XTB': 'XTB.WSE',   // XTB
        'LVC': 'LVCHAT',    // LiveChat (may have US listing)
        'CDR': 'CDR.WSE',   // CD Projekt (if available)
        // Add more mappings as needed
    };

    // Try to use Warsaw Stock Exchange suffix
    return symbolMap[polishSymbol] || `${polishSymbol}.WSE`;
}
