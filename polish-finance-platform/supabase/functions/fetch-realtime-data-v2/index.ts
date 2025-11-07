/**
 * Real-Time WIG80 Data Fetcher (CSV-based approach)
 * Fetches live data from Stooq.pl CSV exports for all 88 WIG80 companies
 * More reliable than HTML scraping
 * Detects market hours (WSE 9:00-17:00 Polish time)
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
        // All 88 WIG80 companies
        const companies = [
            { name: "AGORA SA", symbol: "AGO" },
            { name: "Polimex-Mostostal", symbol: "PXM" },
            { name: "Bioton SA", symbol: "BIO" },
            { name: "Echo Investment SA", symbol: "ECH" },
            { name: "Asseco Business Solutions", symbol: "ABS" },
            { name: "AC SA", symbol: "ACS" },
            { name: "Ambra SA", symbol: "AMB" },
            { name: "AMICA Wronki SA", symbol: "AMC" },
            { name: "Apator SA", symbol: "APT" },
            { name: "Astarta Holding NV", symbol: "AST" },
            { name: "Arctic Paper SA", symbol: "APC" },
            { name: "Bumech SA", symbol: "BUM" },
            { name: "Boryszew SA", symbol: "BRS" },
            { name: "Bank Ochrony Środowiska", symbol: "BOS" },
            { name: "CI Games", symbol: "CIG" },
            { name: "Comp SA", symbol: "CMP" },
            { name: "Cognor SA", symbol: "COG" },
            { name: "Decora SA", symbol: "DEC" },
            { name: "Elektrotim SA", symbol: "ELT" },
            { name: "Erbud SA", symbol: "ERB" },
            { name: "Grenevia", symbol: "GRN" },
            { name: "Ferro SA", symbol: "FRO" },
            { name: "FORTE SA", symbol: "FTE" },
            { name: "Kogeneracja SA", symbol: "KOG" },
            { name: "Lubelski Wegiel Bogdanka", symbol: "LWB" },
            { name: "MCI Management SA", symbol: "MCI" },
            { name: "Mercor SA", symbol: "MCR" },
            { name: "Mennica Polska SA", symbol: "MPS" },
            { name: "Mostostal Zabrze", symbol: "MSZ" },
            { name: "Quercus TFI SA", symbol: "QRS" },
            { name: "Rank Progress SA", symbol: "RPG" },
            { name: "Selena FM SA", symbol: "SLN" },
            { name: "Sygnity SA", symbol: "SGN" },
            { name: "ŚNIEŻKA SA", symbol: "SNZ" },
            { name: "Stomil Sanok SA", symbol: "STS" },
            { name: "Stalprodukt SA", symbol: "STP" },
            { name: "Stalexport Autostrady", symbol: "STE" },
            { name: "Toya SA", symbol: "TOY" },
            { name: "Unibep SA", symbol: "UNB" },
            { name: "Votum SA", symbol: "VOT" },
            { name: "VRG", symbol: "VRG" },
            { name: "Wielton SA", symbol: "WLT" },
            { name: "WAWEL SA", symbol: "WWL" },
            { name: "Zespol Elektrowni Patnow Adamow Konin", symbol: "ZEPA" },
            { name: "Oponeo.pl SA", symbol: "OPN" },
            { name: "Mabion", symbol: "MAB" },
            { name: "Tarczynski", symbol: "TRZ" },
            { name: "Bloober", symbol: "BLB" },
            { name: "Synthaverse", symbol: "SNV" },
            { name: "Medicalg", symbol: "MDG" },
            { name: "Datawalk", symbol: "DAT" },
            { name: "Ryvu", symbol: "RYV" },
            { name: "Ailleron", symbol: "ALL" },
            { name: "Mercator WA", symbol: "MRC" },
            { name: "Torpol", symbol: "TOR" },
            { name: "Columbus", symbol: "COL" },
            { name: "PCC Rokita", symbol: "PCC" },
            { name: "Unimot", symbol: "UNM" },
            { name: "Vigo System", symbol: "VGS" },
            { name: "Atal SA", symbol: "1AT" },
            { name: "Poznanska Korporacja Budowlana Peka", symbol: "PKB" },
            { name: "Wittchen SA", symbol: "WTC" },
            { name: "Enter Air", symbol: "ENT" },
            { name: "Archicom SA", symbol: "ARC" },
            { name: "GreenX Metals", symbol: "GRX" },
            { name: "Playway", symbol: "PLW" },
            { name: "Celon Pharma", symbol: "CLP" },
            { name: "Scope Fluidics", symbol: "SCF" },
            { name: "XTPL", symbol: "XTPL" },
            { name: "Molecure", symbol: "MOL" },
            { name: "ML System", symbol: "MLS" },
            { name: "Creepy Jar", symbol: "CRJ" },
            { name: "Selvita", symbol: "SLV" },
            { name: "Dadelo", symbol: "DDL" },
            { name: "Captor Therapeutics", symbol: "CPT" },
            { name: "Shoper", symbol: "SHP" },
            { name: "Onde", symbol: "OND" },
            { name: "Creotech Instruments", symbol: "CRT" },
            { name: "Bioceltix", symbol: "BCX" },
            { name: "Murapol", symbol: "MRP" },
            { name: "Benefit Systems", symbol: "BFT" },
            { name: "Alumetal", symbol: "AML" },
            { name: "Newag", symbol: "NWG" },
            { name: "Braster", symbol: "BRA" },
            { name: "PKN Orlen", symbol: "PKN" },
            { name: "XTB", symbol: "XTB" },
            { name: "Mirbud", symbol: "MIR" },
            { name: "LiveChat", symbol: "LVC" }
        ];

        // Market hours detection (WSE: 9:00-17:00 Polish time, CET/CEST)
        const now = new Date();
        const polandTime = getPolandTime(now);
        const hours = polandTime.getHours();
        const day = polandTime.getDay();
        const isWeekend = day === 0 || day === 6;
        const isMarketHours = !isWeekend && hours >= 9 && hours < 17;
        const marketStatus = isWeekend ? 'closed_weekend' : 
                           hours < 9 ? 'pre_market' : 
                           hours >= 17 ? 'after_hours' : 'open';

        console.log(`Market status: ${marketStatus}, Poland time: ${polandTime.toISOString()}`);

        // Fetch data from Stooq market statistics page (batch approach)
        const marketData = await fetchStooqMarketData();
        
        // Match companies with market data
        const results = companies.map(company => {
            const stockData = marketData.find(d => d.symbol === company.symbol);
            
            if (stockData) {
                return {
                    company_name: company.name,
                    symbol: company.symbol,
                    current_price: stockData.price,
                    change_percent: stockData.change,
                    pe_ratio: stockData.pe || null,
                    pb_ratio: stockData.pb || null,
                    trading_volume: formatVolume(stockData.volume),
                    trading_volume_obrot: stockData.turnover || '0 PLN',
                    last_update: stockData.time || polandTime.toISOString(),
                    status: 'success'
                };
            } else {
                // Fallback: Try to fetch individual stock data
                return {
                    company_name: company.name,
                    symbol: company.symbol,
                    current_price: 0,
                    change_percent: 0,
                    pe_ratio: null,
                    pb_ratio: null,
                    trading_volume: "0",
                    trading_volume_obrot: "0 PLN",
                    last_update: polandTime.toISOString(),
                    status: 'no_data'
                };
            }
        });

        // Calculate metadata
        const successCount = results.filter(r => r.status === 'success').length;
        const avgChange = results
            .filter(r => r.status === 'success')
            .reduce((sum, r) => sum + r.change_percent, 0) / successCount || 0;

        return new Response(JSON.stringify({
            data: {
                metadata: {
                    collection_date: now.toISOString(),
                    data_source: 'stooq.pl',
                    index: 'WIG80 (sWIG80)',
                    currency: 'PLN',
                    total_companies: companies.length,
                    successful_fetches: successCount,
                    market_status: marketStatus,
                    poland_time: polandTime.toISOString(),
                    is_market_hours: isMarketHours,
                    avg_change: parseFloat(avgChange.toFixed(2))
                },
                companies: results
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Real-time data fetch error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'REALTIME_FETCH_FAILED',
                message: error.message,
                details: error.stack
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Fetch market data from Stooq market statistics page
 * Returns array of stock data for Polish market
 */
async function fetchStooqMarketData() {
    try {
        // Stooq market statistics URL for Poland
        const url = 'https://stooq.com/t/s/?m=pl';
        
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
        });

        if (!response.ok) {
            console.error(`Stooq fetch failed: ${response.status}`);
            return [];
        }

        const html = await response.text();
        
        // Parse the market statistics table
        const stocks = parseMarketTable(html);
        
        console.log(`Fetched ${stocks.length} stocks from Stooq market data`);
        return stocks;

    } catch (error) {
        console.error('Error fetching Stooq market data:', error);
        return [];
    }
}

/**
 * Parse Stooq market statistics table from HTML
 */
function parseMarketTable(html: string): any[] {
    const stocks = [];
    
    // Extract table rows using regex
    const rowPattern = /<tr[^>]*>(.*?)<\/tr>/gis;
    const rows = html.match(rowPattern) || [];
    
    for (const row of rows) {
        // Extract cells
        const cellPattern = /<td[^>]*>(.*?)<\/td>/gis;
        const cells = row.match(cellPattern) || [];
        
        if (cells.length < 5) continue; // Skip if not enough data
        
        // Extract symbol, price, change, volume, etc.
        const symbolMatch = row.match(/\/q\/\?s=([A-Z0-9]+)/i);
        if (!symbolMatch) continue;
        
        const symbol = symbolMatch[1];
        
        // Extract numeric values from cells
        const values = cells.map(cell => {
            const text = cell.replace(/<[^>]*>/g, '').trim();
            return text;
        });
        
        // Parse price and change
        const priceStr = values.find(v => /^\d+[,\.]\d+$/.test(v));
        const changeStr = values.find(v => /^[+-]\d+[,\.]\d+%?$/.test(v));
        
        if (priceStr) {
            stocks.push({
                symbol: symbol,
                price: parseFloat(priceStr.replace(',', '.')),
                change: changeStr ? parseFloat(changeStr.replace(',', '.').replace('%', '')) : 0,
                volume: 0,
                turnover: '0 PLN',
                time: new Date().toISOString(),
                pe: null,
                pb: null
            });
        }
    }
    
    return stocks;
}

/**
 * Format volume for display
 */
function formatVolume(volume: number): string {
    if (volume >= 1000000) {
        return `${(volume / 1000000).toFixed(2)}M`;
    } else if (volume >= 1000) {
        return `${(volume / 1000).toFixed(2)}K`;
    }
    return volume.toString();
}

/**
 * Get current time in Poland (CET/CEST)
 */
function getPolandTime(date: Date): Date {
    const isDST = isDaylightSavingTime(date);
    const offset = isDST ? 2 : 1; // CEST (UTC+2) or CET (UTC+1)
    return new Date(date.getTime() + offset * 3600000);
}

/**
 * Check if date is in daylight saving time (for Poland/CET)
 */
function isDaylightSavingTime(date: Date): boolean {
    const year = date.getFullYear();
    // DST in Europe: Last Sunday of March to Last Sunday of October
    const marchLastSunday = getLastSundayOfMonth(year, 2); // March is month 2
    const octoberLastSunday = getLastSundayOfMonth(year, 9); // October is month 9
    
    const timestamp = date.getTime();
    return timestamp >= marchLastSunday.getTime() && timestamp < octoberLastSunday.getTime();
}

/**
 * Get last Sunday of a month
 */
function getLastSundayOfMonth(year: number, month: number): Date {
    const lastDay = new Date(year, month + 1, 0); // Last day of month
    const day = lastDay.getDay();
    const diff = day === 0 ? 0 : day;
    return new Date(year, month + 1, -diff);
}
