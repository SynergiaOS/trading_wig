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

        console.log('Checking alerts...');

        // Fetch all active alerts
        const alertsResponse = await fetch(
            `${supabaseUrl}/rest/v1/user_alerts?is_active=eq.true&select=*`,
            {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            }
        );

        if (!alertsResponse.ok) {
            throw new Error('Failed to fetch alerts');
        }

        const alerts = await alertsResponse.json();
        console.log(`Found ${alerts.length} active alerts`);

        const triggeredAlerts = [];

        // Check each alert
        for (const alert of alerts) {
            try {
                // Fetch current company price
                const companyResponse = await fetch(
                    `${supabaseUrl}/rest/v1/companies?symbol=eq.${alert.symbol}&select=current_price,company_name`,
                    {
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );

                if (!companyResponse.ok) {
                    console.error(`Failed to fetch company data for ${alert.symbol}`);
                    continue;
                }

                const companies = await companyResponse.json();
                if (!companies || companies.length === 0) {
                    console.error(`Company ${alert.symbol} not found`);
                    continue;
                }

                const currentPrice = parseFloat(companies[0].current_price);
                const targetValue = parseFloat(alert.target_value);

                // Check if alert condition is met
                let shouldTrigger = false;

                switch (alert.condition) {
                    case 'above':
                        shouldTrigger = currentPrice > targetValue;
                        break;
                    case 'below':
                        shouldTrigger = currentPrice < targetValue;
                        break;
                    case 'equals':
                        shouldTrigger = Math.abs(currentPrice - targetValue) < 0.01;
                        break;
                    default:
                        console.error(`Unknown condition: ${alert.condition}`);
                }

                if (shouldTrigger) {
                    console.log(`Alert triggered for ${alert.symbol}: ${currentPrice} ${alert.condition} ${targetValue}`);

                    // Update alert as triggered
                    await fetch(`${supabaseUrl}/rest/v1/user_alerts?id=eq.${alert.id}`, {
                        method: 'PATCH',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            is_active: false,
                            triggered_at: new Date().toISOString()
                        })
                    });

                    triggeredAlerts.push({
                        alert_id: alert.id,
                        symbol: alert.symbol,
                        company_name: companies[0].company_name,
                        current_price: currentPrice,
                        target_value: targetValue,
                        condition: alert.condition,
                        user_id: alert.user_id
                    });
                }
            } catch (error) {
                console.error(`Error processing alert ${alert.id}:`, error);
            }
        }

        return new Response(JSON.stringify({
            data: {
                checked: alerts.length,
                triggered: triggeredAlerts.length,
                alerts: triggeredAlerts
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Alert check error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'ALERT_CHECK_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});
