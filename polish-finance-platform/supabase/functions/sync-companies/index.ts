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

        const { companies } = await req.json();

        if (!companies || !Array.isArray(companies)) {
            throw new Error('Companies array is required');
        }

        console.log(`Syncing ${companies.length} companies...`);

        // Sync each company
        const results = [];
        for (const company of companies) {
            try {
                // Upsert company data
                const upsertResponse = await fetch(`${supabaseUrl}/rest/v1/companies`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey,
                        'Content-Type': 'application/json',
                        'Prefer': 'resolution=merge-duplicates,return=representation'
                    },
                    body: JSON.stringify({
                        symbol: company.symbol,
                        company_name: company.company_name,
                        current_price: company.current_price,
                        change_percent: company.change_percent,
                        pe_ratio: company.pe_ratio,
                        pb_ratio: company.pb_ratio,
                        trading_volume: company.trading_volume,
                        trading_volume_numeric: company.trading_volume_numeric || null,
                        last_update: company.last_update,
                        sector: company.sector || null,
                        market_cap: company.market_cap || null,
                        category: company.category || null,
                        value_score: company.value_score || null,
                        growth_score: company.growth_score || null,
                        liquidity_score: company.liquidity_score || null,
                        overall_score: company.overall_score || null,
                        updated_at: new Date().toISOString()
                    })
                });

                if (!upsertResponse.ok) {
                    const errorText = await upsertResponse.text();
                    console.error(`Failed to sync ${company.symbol}: ${errorText}`);
                    results.push({ symbol: company.symbol, success: false, error: errorText });
                    continue;
                }

                const companyData = await upsertResponse.json();
                const companyId = companyData[0]?.id;

                // Add to price history
                if (companyId && company.current_price) {
                    await fetch(`${supabaseUrl}/rest/v1/price_history`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            company_id: companyId,
                            symbol: company.symbol,
                            price: company.current_price,
                            change_percent: company.change_percent,
                            volume: company.trading_volume_numeric || null,
                            timestamp: new Date().toISOString()
                        })
                    });
                }

                results.push({ symbol: company.symbol, success: true });
            } catch (error) {
                console.error(`Error processing ${company.symbol}:`, error);
                results.push({ symbol: company.symbol, success: false, error: error.message });
            }
        }

        const successCount = results.filter(r => r.success).length;
        const failCount = results.filter(r => !r.success).length;

        return new Response(JSON.stringify({
            data: {
                synced: successCount,
                failed: failCount,
                results: results
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Sync error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'SYNC_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
