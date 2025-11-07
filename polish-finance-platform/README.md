# Polish Financial Analysis Platform

An integrated financial analysis platform for the Polish stock market (WIG80) combining real-time market data, AI-powered multi-agent analysis, and automated trading insights.

## Features

### Real-Time Market Dashboard
- Live WIG80 company data (88 companies)
- Top gainers and losers tracking
- Quick profit opportunities showcase
- Advanced search and filtering
- Polish market metrics (PLN currency, P/E, P/B ratios)

### AI Multi-Agent Analysis System
Three specialized AI agents analyze each stock:

1. **Fundamental Analyst**
   - P/E and P/B ratio analysis
   - Value score calculations
   - Profitability metrics
   - Growth potential assessment

2. **Technical Analyst**
   - Moving averages (SMA 5, 10, 20)
   - Volatility analysis
   - Support and resistance levels
   - Volume trend analysis
   - Momentum indicators

3. **Sentiment Analyst**
   - Market consensus evaluation
   - Multi-agent opinion aggregation
   - Confidence scoring
   - Risk assessment

### Trading Capabilities
- Quick profit opportunity identification
- Position sizing recommendations (1.5-4% per trade)
- Stop-loss and take-profit calculations
- Portfolio tracking
- Risk management tools

### Alert System
- Automated price monitoring
- User-specific alerts (above/below/equals)
- Cron-based checking system
- Real-time notifications

## Technology Stack

### Backend
- **Supabase**: Database, authentication, edge functions
- **PostgreSQL**: Relational database with RLS
- **Deno**: Edge function runtime
- **TypeScript**: Type-safe server code

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Vite**: Fast build tool
- **Lucide Icons**: Clean, modern icons
- **ECharts**: Data visualization

## Project Structure

```
polish-finance-platform/
├── schema.sql                    # Database schema with RLS
├── supabase/
│   └── functions/               # Edge functions
│       ├── sync-companies/      # Data synchronization
│       ├── ai-fundamental-analyst/
│       ├── ai-technical-analyst/
│       ├── ai-sentiment-analyst/
│       └── check-alerts/        # Cron job for alerts
├── polish-finance-app/          # React frontend
│   ├── src/
│   │   ├── pages/              # Page components
│   │   ├── components/         # Reusable components
│   │   ├── types/              # TypeScript definitions
│   │   ├── lib/                # Utilities & config
│   │   └── App.tsx
│   └── public/                 # Static assets & data
│       ├── wig80_current_data.json
│       ├── filtered_companies.json
│       └── quick_profit_strategy.md
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
└── PROJECT_SUMMARY.md          # Project overview
```

## Quick Start

### Prerequisites
- Node.js 18+
- pnpm package manager
- Supabase account

### Installation

1. **Clone and navigate**
   ```bash
   cd polish-finance-platform/polish-finance-app
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Run development server**
   ```bash
   pnpm run dev
   ```

5. **Build for production**
   ```bash
   pnpm run build
   ```

### Backend Setup

1. **Apply database schema**
   - Open Supabase SQL Editor
   - Run `schema.sql`

2. **Deploy edge functions**
   - Use Supabase CLI or deployment tool
   - Deploy all 5 functions from `supabase/functions/`

3. **Initial data sync**
   - Call `sync-companies` edge function
   - Pass WIG80 data from JSON file

4. **Setup cron job**
   - Create cron job for `check-alerts`
   - Schedule: Every 5 minutes

## Top Trading Opportunities

Based on current WIG80 analysis (November 5, 2025):

| Symbol | Company | Price (PLN) | Change | P/E | Strategy |
|--------|---------|-------------|--------|-----|----------|
| ERB | Erbud SA | 616.37 | +14.94% | 35.81 | Strong Buy |
| PKN | PKNORLEN | 388.50 | +13.76% | 29.75 | Buy |
| SHP | Shoper | 469.71 | +12.82% | 27.84 | Buy |
| DGE | DRAGOENT | 472.41 | +11.68% | 38.54 | Buy |
| SLN | Selena FM | 177.97 | +10.59% | 5.57 | Strong Buy |

## Risk Management

### Position Sizing
- Conservative: 1.5-2% per trade
- Moderate: 2-3% per trade
- Aggressive: 3-4% per trade
- Maximum total exposure: 10-12%

### Stop-Loss Strategy
- Strict stops: -2.5% to -4%
- Based on volatility and liquidity
- Automatic calculations provided

### Holding Periods
- Intraday: Same day trades
- Short-term: 1-3 day holds
- Swing: Up to 1 week

## Database Schema

### Companies Table
Stores WIG80 company information with metrics:
- Basic info: symbol, name, price
- Valuation: P/E, P/B ratios
- Scores: value, growth, liquidity, overall
- Volume and market cap

### Price History
Historical price data for technical analysis:
- Price, volume, timestamp
- Daily change percentages
- Linked to companies

### User Alerts
User-configured price alerts:
- Target price and condition
- Active/triggered status
- Alert types

### User Portfolios
Track user positions and trades:
- Entry/exit prices and dates
- Stop-loss and take-profit levels
- Position sizing and P&L

### AI Analysis
Multi-agent analysis results:
- Agent name and type
- Sentiment and recommendation
- Confidence scores
- Detailed analysis text

## API Endpoints (Edge Functions)

### POST /functions/v1/sync-companies
Sync company data to database
```json
{
  "companies": [...]
}
```

### POST /functions/v1/ai-fundamental-analyst
Get fundamental analysis for a symbol
```json
{
  "symbol": "ERB"
}
```

### POST /functions/v1/ai-technical-analyst
Get technical analysis for a symbol
```json
{
  "symbol": "SHP"
}
```

### POST /functions/v1/ai-sentiment-analyst
Get sentiment analysis for a symbol
```json
{
  "symbol": "PKN"
}
```

### POST /functions/v1/check-alerts (Cron)
Automatic alert checking (no parameters)

## Development

### Code Style
- TypeScript strict mode enabled
- ESLint for code quality
- Prettier for formatting (via Tailwind)

### Testing
- Component testing: TBD
- Integration testing: TBD
- E2E testing: TBD

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Deployment

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete deployment instructions.

**Quick Deployment:**
1. Get Supabase credentials
2. Apply database schema
3. Deploy edge functions
4. Configure frontend environment
5. Build and deploy frontend
6. Setup cron job

Estimated deployment time: 20 minutes

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- Check DEPLOYMENT_GUIDE.md
- Review PROJECT_SUMMARY.md
- Open an issue on GitHub

## Acknowledgments

- WIG80 data from stooq.pl
- Polish Stock Exchange (GPW)
- Supabase for backend infrastructure
- React and Tailwind communities

---

**Status**: Production-ready, awaiting Supabase credentials for deployment

**Last Updated**: November 5, 2025
