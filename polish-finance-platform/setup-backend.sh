#!/bin/bash
# Supabase Backend Setup Script
# Run this script after obtaining Supabase credentials

set -e

echo "================================================"
echo "Polish Financial Analysis Platform"
echo "Supabase Backend Setup Script"
echo "================================================"
echo ""

# Check if credentials are provided
if [ -z "$SUPABASE_PROJECT_ID" ] || [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
    echo "ERROR: Missing Supabase credentials"
    echo ""
    echo "Please set the following environment variables:"
    echo "  export SUPABASE_PROJECT_ID='your-project-id'"
    echo "  export SUPABASE_ACCESS_TOKEN='your-access-token'"
    echo ""
    exit 1
fi

echo "✓ Credentials detected"
echo "  Project ID: ${SUPABASE_PROJECT_ID:0:8}..."
echo ""

# Step 1: Apply Database Schema
echo "Step 1: Applying database schema..."
echo "  → Please manually apply schema.sql in Supabase SQL Editor"
echo "  → Navigate to: Supabase Dashboard → SQL Editor → New Query"
echo "  → Copy contents of schema.sql and execute"
echo ""
read -p "Press Enter after applying schema.sql..."
echo "✓ Schema applied"
echo ""

# Step 2: Deploy Edge Functions
echo "Step 2: Deploying edge functions..."
echo "  → Use batch_deploy_edge_functions tool with these functions:"
echo ""
echo "  functions = ["
echo "    {"
echo "      \"slug\": \"sync-companies\","
echo "      \"file_path\": \"supabase/functions/sync-companies/index.ts\","
echo "      \"type\": \"normal\","
echo "      \"description\": \"Sync WIG80 company data to database\""
echo "    },"
echo "    {"
echo "      \"slug\": \"ai-fundamental-analyst\","
echo "      \"file_path\": \"supabase/functions/ai-fundamental-analyst/index.ts\","
echo "      \"type\": \"normal\","
echo "      \"description\": \"Fundamental analysis agent\""
echo "    },"
echo "    {"
echo "      \"slug\": \"ai-technical-analyst\","
echo "      \"file_path\": \"supabase/functions/ai-technical-analyst/index.ts\","
echo "      \"type\": \"normal\","
echo "      \"description\": \"Technical analysis agent\""
echo "    },"
echo "    {"
echo "      \"slug\": \"ai-sentiment-analyst\","
echo "      \"file_path\": \"supabase/functions/ai-sentiment-analyst/index.ts\","
echo "      \"type\": \"normal\","
echo "      \"description\": \"Sentiment analysis agent\""
echo "    },"
echo "    {"
echo "      \"slug\": \"check-alerts\","
echo "      \"file_path\": \"supabase/functions/check-alerts/index.ts\","
echo "      \"type\": \"cron\","
echo "      \"description\": \"Alert monitoring cron job\""
echo "    }"
echo "  ]"
echo ""
read -p "Press Enter after deploying edge functions..."
echo "✓ Edge functions deployed"
echo ""

# Step 3: Sync Initial Data
echo "Step 3: Syncing WIG80 data..."
echo "  → Call sync-companies edge function with:"
echo "  → curl -X POST https://YOUR-PROJECT.supabase.co/functions/v1/sync-companies \\"
echo "       -H \"Authorization: Bearer YOUR-ANON-KEY\" \\"
echo "       -H \"Content-Type: application/json\" \\"
echo "       -d @polish-finance-app/public/wig80_current_data.json"
echo ""
read -p "Press Enter after syncing data..."
echo "✓ Data synced"
echo ""

# Step 4: Setup Cron Job
echo "Step 4: Setting up cron job for alerts..."
echo "  → Use create_background_cron_job tool:"
echo "  → edge_function_name: \"check-alerts\""
echo "  → cron_expression: \"*/5 * * * *\"  (every 5 minutes)"
echo ""
read -p "Press Enter after setting up cron job..."
echo "✓ Cron job configured"
echo ""

# Step 5: Configure Frontend
echo "Step 5: Configuring frontend..."
echo "  → Get Supabase URL and Anon Key from dashboard"
echo "  → Update polish-finance-app/.env:"
echo ""
echo "    VITE_SUPABASE_URL=https://YOUR-PROJECT.supabase.co"
echo "    VITE_SUPABASE_ANON_KEY=your-anon-key-here"
echo ""
read -p "Press Enter after updating .env..."
echo "✓ Frontend configured"
echo ""

# Step 6: Rebuild and Redeploy Frontend
echo "Step 6: Rebuilding frontend..."
cd polish-finance-app
pnpm run build
echo "✓ Frontend built"
echo ""
echo "  → Deploy dist/ folder to production"
read -p "Press Enter after deploying..."
echo "✓ Frontend deployed"
echo ""

# Summary
echo "================================================"
echo "✓ SETUP COMPLETE!"
echo "================================================"
echo ""
echo "Your Polish Financial Analysis Platform is now live with:"
echo "  - Database with 5 tables"
echo "  - 5 Edge functions (4 analysis agents + 1 cron)"
echo "  - WIG80 data synchronized"
echo "  - Alert monitoring active"
echo "  - Frontend connected to backend"
echo ""
echo "Next steps:"
echo "  1. Test AI analysis: Call fundamental/technical/sentiment analysts"
echo "  2. Create test alerts to verify monitoring"
echo "  3. Monitor edge function logs in Supabase dashboard"
echo ""
echo "Platform ready for use!"
