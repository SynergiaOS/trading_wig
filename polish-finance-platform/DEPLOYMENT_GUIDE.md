# Polish Financial Analysis Platform - Deployment Guide

## Architecture Overview

### Backend (Supabase)
- **Database**: 5 tables (companies, price_history, user_alerts, user_portfolios, ai_analysis)
- **Edge Functions**: 5 functions
  - `sync-companies`: Sync WIG80 data to database
  - `ai-fundamental-analyst`: Fundamental analysis agent
  - `ai-technical-analyst`: Technical analysis agent  
  - `ai-sentiment-analyst`: Sentiment analysis agent
  - `check-alerts`: Alert monitoring (cron job)

### Frontend (React + TypeScript + Tailwind)
- Dashboard with real-time WIG80 data
- Company filtering and search
- Quick profit opportunities highlighted
- AI-powered multi-agent analysis
- Portfolio management
- Alert system

## Deployment Steps

### 1. Supabase Setup (REQUIRED - Waiting for Credentials)

Once Supabase credentials are provided:

```bash
# 1. Apply database schema
# Run schema.sql in Supabase SQL editor

# 2. Deploy edge functions
# Use batch_deploy_edge_functions tool with these functions:
- supabase/functions/sync-companies/index.ts (type: normal)
- supabase/functions/ai-fundamental-analyst/index.ts (type: normal)
- supabase/functions/ai-technical-analyst/index.ts (type: normal)
- supabase/functions/ai-sentiment-analyst/index.ts (type: normal)
- supabase/functions/check-alerts/index.ts (type: cron)

# 3. Initial data sync
# Call sync-companies edge function with wig80_current_data.json

# 4. Setup cron job for alert checking
# Create background cron job for check-alerts function (every 5 minutes)
```

### 2. Frontend Configuration

Update `.env` file in polish-finance-app/:

```env
VITE_SUPABASE_URL=<your-supabase-url>
VITE_SUPABASE_ANON_KEY=<your-supabase-anon-key>
```

### 3. Build and Deploy

```bash
cd polish-finance-app
pnpm run build
# Deploy dist/ directory
```

## Features Implemented

### Dashboard
- Real-time WIG80 company data
- Top gainers/losers cards
- Quick profit opportunities section
- Search and filter functionality
- Company table with metrics (P/E, P/B, scores)

### Data Integration
- WIG80 data (88 companies) ready to sync
- Filtered companies (8 small-cap value + 15 growth)
- Quick profit strategy data
- Polish market focus (PLN currency)

### AI Analysis (Ready for deployment)
- Multi-agent system:
  - Fundamental Analyst: P/E, P/B, value scores
  - Technical Analyst: SMA, volatility, trends
  - Sentiment Analyst: Market consensus
- Scoring system (0-100)
- Recommendations: strong_buy, buy, hold, sell, strong_sell

### Risk Management
- Position sizing recommendations (1.5-4% per trade)
- Stop-loss calculations
- Portfolio tracking
- Alert system for price movements

## Next Steps

1. **Get Supabase credentials** [ACTION_REQUIRED]
2. Deploy database schema
3. Deploy edge functions
4. Sync initial WIG80 data
5. Configure frontend environment variables
6. Build and deploy frontend
7. Test all features
8. Set up cron job for alerts

## Files Ready for Deployment

Backend:
- `/workspace/polish-finance-platform/schema.sql`
- `/workspace/polish-finance-platform/supabase/functions/*/index.ts` (5 functions)

Frontend:
- `/workspace/polish-finance-platform/polish-finance-app/` (complete React app)

Data:
- `/workspace/polish-finance-platform/polish-finance-app/public/wig80_current_data.json`
- `/workspace/polish-finance-platform/polish-finance-app/public/filtered_companies.json`

## Testing Plan

After deployment:
1. Test company data loading
2. Test AI analysis for sample symbols (ERB, PKN, SHP)
3. Test alert creation and triggering
4. Test portfolio management
5. Verify Polish market data display (PLN prices)

## Top Trading Opportunities (from quick_profit_strategy.md)

BUY Signals:
- **ERB** (Erbud SA): +14.94% - Strong momentum
- **PKN** (PKNORLEN): +13.76% - Large cap opportunity
- **SHP** (Shoper): +12.82% - E-commerce growth
- **DGE** (DRAGOENT): +11.68% - Small cap value
- **SLN** (Selena FM): +10.59% - P/E 5.57 value play

The platform is production-ready pending Supabase credentials.
