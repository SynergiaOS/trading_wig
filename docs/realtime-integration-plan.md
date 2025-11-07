# Real-Time Data Integration Implementation Plan

## Overview
Transform the Polish Finance Platform from static data to real-time trading tool with live updates from Stooq.pl and Alpha Vantage API.

## Current Status
- **Platform URL**: https://fslfzvzhls4e.space.minimax.io
- **Current State**: Static data with 30-second refresh (reloads same JSON)
- **Target**: Real-time data updates from live sources

## Implementation Strategy

### Phase 1: Backend - Real-Time Data Fetching

#### Edge Functions Created:
1. **fetch-realtime-data** (`/supabase/functions/fetch-realtime-data/index.ts`)
   - Fetches real-time data for all 88 WIG80 companies from Stooq.pl
   - Uses HTML scraping with multiple fallback patterns
   - Market hours detection (WSE 9:00-17:00 Polish time)
   - Batch processing to avoid rate limits
   - Returns formatted JSON with company data

2. **fetch-realtime-data-v2** (`/supabase/functions/fetch-realtime-data-v2/index.ts`)
   - Alternative approach using Stooq market statistics page
   - Batch fetches all Polish stocks in one request
   - More efficient than individual requests
   - Parses market table for stock data

3. **fetch-alpha-vantage-data** (`/supabase/functions/fetch-alpha-vantage-data/index.ts`)
   - Provides enhanced data from Alpha Vantage API
   - Supports: quote, overview, news, technical indicators
   - Rate limited (25 requests/day) - use strategically
   - Maps Polish symbols to international format

#### Deployment Requirements:
- **Supabase URL**: Required
- **Supabase Anon Key**: Required
- **Alpha Vantage API Key**: C8C4Q9GFD4FXKG3A (already embedded in functions)

### Phase 2: Frontend - Real-Time UI Updates

#### Changes Required in Dashboard.tsx:
1. **Data Source**: Change from static JSON to Supabase edge function
2. **Real-Time Indicators**: 
   - Live price change animations
   - Market status badge (Open/Closed/Pre-market/After-hours)
   - Last update timestamp
   - Connection status indicator
3. **Error Handling**:
   - Fallback to cached data on error
   - Display connection errors gracefully
   - Retry mechanism for failed requests

#### New Components to Add:
1. **MarketStatusBadge**: Shows live market status
2. **PriceChangeAnimation**: Animates price changes
3. **ConnectionIndicator**: Shows data freshness
4. **VolumeAlert**: Highlights volume spikes

### Phase 3: Optimization & Polish

#### Performance:
- Implement caching layer (edge function caches for 30 seconds)
- Progressive loading for large datasets
- Debounce rapid updates

#### Error Handling:
- Graceful degradation when sources fail
- Multiple fallback data sources
- User-friendly error messages in Polish

#### Real-Time Features:
- Price change flash animations (green for gains, red for losses)
- Volume spike alerts
- Real-time trend analysis updates
- Live countdown to next refresh

## Market Hours Detection

### WSE Trading Hours (Polish Time):
- **Regular Hours**: Monday-Friday, 9:00-17:00 CET/CEST
- **Pre-market**: Before 9:00
- **After-hours**: After 17:00
- **Closed**: Weekends and holidays

### Time Zone Handling:
- Poland uses CET (UTC+1) in winter
- Poland uses CEST (UTC+2) in summer (DST)
- DST: Last Sunday of March to last Sunday of October
- Edge functions calculate Poland time from UTC

## Data Flow

### Current (Static):
```
Frontend → Static JSON file → Display
```

### New (Real-Time):
```
Frontend → Supabase Edge Function → Stooq.pl Scraping → Format Data → Return JSON → Display
                                  ↓
                            Alpha Vantage API (enhanced data)
```

### Caching Strategy:
```
Request → Check Cache (30s TTL) → If Fresh: Return Cached
                                → If Stale: Fetch New → Update Cache → Return
```

## API Endpoints

### Primary Endpoint:
- **URL**: `https://[SUPABASE_URL]/functions/v1/fetch-realtime-data`
- **Method**: GET/POST
- **Response**: JSON with all 88 companies + metadata
- **Cache**: 30 seconds
- **Rate Limit**: None (self-hosted)

### Enhanced Data Endpoint:
- **URL**: `https://[SUPABASE_URL]/functions/v1/fetch-alpha-vantage-data`
- **Method**: POST
- **Body**: `{ symbol: "PKN", dataType: "quote" }`
- **Response**: Alpha Vantage data for specific symbol
- **Rate Limit**: 25 requests/day (API limitation)

## Testing Plan

1. **Edge Function Testing**:
   - Test data fetching for all companies
   - Verify market hours detection
   - Check error handling
   - Validate data format

2. **Frontend Integration**:
   - Test auto-refresh mechanism
   - Verify real-time indicators
   - Check animations and transitions
   - Test error states

3. **Performance Testing**:
   - Measure response times
   - Check cache effectiveness
   - Monitor memory usage
   - Test with multiple concurrent users

## Rollout Strategy

### Step 1: Deploy Edge Functions
- Deploy to Supabase
- Test with sample requests
- Verify data accuracy

### Step 2: Update Frontend
- Integrate edge function calls
- Add real-time indicators
- Implement error handling

### Step 3: Testing
- Comprehensive QA testing
- Performance validation
- User acceptance testing

### Step 4: Deployment
- Build production bundle
- Deploy to hosting
- Monitor for issues

## Success Criteria

- [ ] All 88 companies show real-time data
- [ ] Updates every 30 seconds during market hours
- [ ] Market status correctly shows Open/Closed/Pre-market/After-hours
- [ ] Price changes animate smoothly
- [ ] Volume spikes trigger alerts
- [ ] Error handling works gracefully
- [ ] Performance remains smooth
- [ ] Polish language maintained throughout
- [ ] Bloomberg Terminal aesthetic preserved

## Known Limitations

1. **Stooq.pl Scraping**:
   - May be blocked if too many requests
   - HTML structure changes could break parser
   - Solution: Multiple fallback patterns, error recovery

2. **Alpha Vantage Rate Limits**:
   - Free tier: 25 requests/day
   - Solution: Use strategically for top gainers/losers only

3. **Edge Function Timeouts**:
   - Deno Deploy has execution time limits
   - Solution: Batch processing, parallel requests

4. **Market Holidays**:
   - No automatic holiday detection
   - Solution: Will show last available data

## Next Steps

1. **Wait for Supabase credentials** to deploy edge functions
2. Test edge functions with sample data
3. Update frontend Dashboard component
4. Deploy and test complete system
5. Monitor performance and optimize
