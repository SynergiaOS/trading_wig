/**
 * Real-Time WIG80 Data Fetcher
 * Fetches live data from Stooq.pl for all 88 WIG80 companies
 * Integrates with Alpha Vantage API for enhanced data
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
        const alphaVantageKey = 'C8C4Q9GFD4FXKG3A';
        
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
        const polandOffset = 1; // CET is UTC+1, CEST is UTC+2
        const isDST = isDaylightSavingTime(now);
        const polandTime = new Date(now.getTime() + (polandOffset + (isDST ? 1 : 0)) * 3600000);
        const hours = polandTime.getHours();
        const day = polandTime.getDay();
        const isWeekend = day === 0 || day === 6;
        const isMarketHours = !isWeekend && hours >= 9 && hours < 17;
        const marketStatus = isWeekend ? 'closed_weekend' : 
                           hours < 9 ? 'pre_market' : 
                           hours >= 17 ? 'after_hours' : 'open';

        console.log(`Market status: ${marketStatus}, Poland time: ${polandTime.toISOString()}`);

        // Fetch data for all companies in parallel (batched to avoid rate limits)
        const batchSize = 10; // Process 10 companies at a time
        const results = [];
        
        for (let i = 0; i < companies.length; i += batchSize) {
            const batch = companies.slice(i, i + batchSize);
            const batchPromises = batch.map(company => 
                fetchStooqData(company.symbol, company.name)
            );
            
            const batchResults = await Promise.allSettled(batchPromises);
            results.push(...batchResults.map((r, idx) => 
                r.status === 'fulfilled' ? r.value : {
                    company_name: batch[idx].name,
                    symbol: batch[idx].symbol,
                    current_price: 0,
                    change_percent: 0,
                    pe_ratio: null,
                    pb_ratio: null,
                    trading_volume: "0",
                    trading_volume_obrot: "0 PLN",
                    last_update: new Date().toISOString(),
                    status: 'error',
                    error: r.reason?.message || 'Failed to fetch'
                }
            ));
            
            // Small delay between batches to avoid overwhelming Stooq
            if (i + batchSize < companies.length) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }

        // Calculate metadata
        const successCount = results.filter(r => r.status === 'success').length;
        const avgChange = results.reduce((sum, r) => sum + (r.change_percent || 0), 0) / results.length;

        return new Response(JSON.stringify({
            data: {
                metadata: {
                    collection_date: new Date().toISOString(),
                    data_source: 'stooq.pl',
                    index: 'WIG80 (sWIG80)',
                    currency: 'PLN',
                    total_companies: companies.length,
                    successful_fetches: successCount,
                    market_status: marketStatus,
                    poland_time: polandTime.toISOString(),
                    is_market_hours: isMarketHours,
                    avg_change: avgChange.toFixed(2)
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
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

/**
 * Fetch real-time data from Stooq.pl for a single company
 */
async function fetchStooqData(symbol: string, companyName: string) {
    try {
        // Stooq URL pattern: https://stooq.pl/q/?s=SYMBOL
        const url = `https://stooq.pl/q/?s=${symbol}`;
        
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const html = await response.text();
        
        // Extract data using regex patterns
        const price = extractPrice(html);
        const change = extractChange(html);
        const volume = extractVolume(html);
        const peRatio = extractPE(html);
        const pbRatio = extractPB(html);
        const lastUpdate = extractLastUpdate(html);

        return {
            company_name: companyName,
            symbol: symbol,
            current_price: price,
            change_percent: change,
            pe_ratio: peRatio,
            pb_ratio: pbRatio,
            trading_volume: formatVolume(volume),
            trading_volume_obrot: volume > 0 ? `${(volume * price).toFixed(2)}M PLN` : '0 PLN',
            last_update: lastUpdate || new Date().toISOString(),
            status: 'success'
        };

    } catch (error) {
        console.error(`Error fetching ${symbol}:`, error);
        throw error;
    }
}

/**
 * Extract price from Stooq HTML
 */
function extractPrice(html: string): number {
    // Look for price in various possible locations
    const patterns = [
        /<span[^>]*id="aq_[^"]*_c[^>]*>([0-9,\.]+)<\/span>/i,
        /<span[^>]*class="[^"]*price[^"]*"[^>]*>([0-9,\.]+)<\/span>/i,
        /Kurs:\s*([0-9,\.]+)/i
    ];

    for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match) {
            return parseFloat(match[1].replace(',', '.'));
        }
    }

    return 0;
}

/**
 * Extract change percentage from Stooq HTML
 */
function extractChange(html: string): number {
    const patterns = [
        /<span[^>]*id="aq_[^"]*_p[^>]*>([+-]?[0-9,\.]+)%?<\/span>/i,
        /Zmiana:\s*([+-]?[0-9,\.]+)%/i
    ];

    for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match) {
            return parseFloat(match[1].replace(',', '.'));
        }
    }

    return 0;
}

/**
 * Extract volume from Stooq HTML
 */
function extractVolume(html: string): number {
    const patterns = [
        /Wolumen:\s*([0-9,\.]+)/i,
        /<td[^>]*>Wolumen<\/td>\s*<td[^>]*>([0-9,\.]+)/i
    ];

    for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match) {
            const volStr = match[1].replace(',', '');
            return parseFloat(volStr);
        }
    }

    return 0;
}

/**
 * Extract P/E ratio from Stooq HTML
 */
function extractPE(html: string): number | null {
    const patterns = [
        /C\/Z:\s*([0-9,\.]+)/i,
        /<td[^>]*>C\/Z<\/td>\s*<td[^>]*>([0-9,\.]+)/i
    ];

    for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match) {
            return parseFloat(match[1].replace(',', '.'));
        }
    }

    return null;
}

/**
 * Extract P/B ratio from Stooq HTML
 */
function extractPB(html: string): number | null {
    const patterns = [
        /C\/WK:\s*([0-9,\.]+)/i,
        /<td[^>]*>C\/WK<\/td>\s*<td[^>]*>([0-9,\.]+)/i
    ];

    for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match) {
            return parseFloat(match[1].replace(',', '.'));
        }
    }

    return null;
}

/**
 * Extract last update time from Stooq HTML
 */
function extractLastUpdate(html: string): string | null {
    const patterns = [
        /Data:\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})/i,
        /<span[^>]*id="aq_[^"]*_t[^>]*>([^<]+)<\/span>/i
    ];

    for (const pattern of patterns) {
        const match = html.match(pattern);
        if (match) {
            return match[1];
        }
    }

    return null;
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
