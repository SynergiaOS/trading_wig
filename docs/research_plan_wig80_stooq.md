# WIG80 Index and Stooq.pl Data Research Plan

## Research Objectives
1. Complete list of WIG80 companies with symbols ✓
2. How stooq.pl organizes Polish stock data ✓
3. Available financial metrics (P/E, P/B, volume) ✓
4. Best approach for scraping stooq.pl for WIG80 data ✓

## Research Tasks

### Phase 1: WIG80 Index Research
- [x] 1.1 Research WIG80 index definition and structure
- [x] 1.2 Find official WIG80 component list
- [x] 1.3 Identify stock symbols for all WIG80 companies
- [x] 1.4 Document index methodology and selection criteria

### Phase 2: Stooq.pl Data Organization Analysis
- [x] 2.1 Explore stooq.pl website structure
- [x] 2.2 Analyze Polish stock data organization
- [x] 2.3 Identify URL patterns for Polish stocks
- [x] 2.4 Document data endpoints and APIs

### Phase 3: Financial Metrics Investigation
- [x] 3.1 Check available financial metrics on stooq.pl
- [x] 3.2 Document P/E, P/B, and volume data availability
- [x] 3.3 Analyze data formats and update frequencies
- [x] 3.4 Identify other relevant financial indicators

### Phase 4: Scraping Strategy Development
- [x] 4.1 Analyze stooq.pl HTML structure
- [x] 4.2 Test data extraction methods
- [x] 4.3 Identify rate limits and access patterns
- [x] 4.4 Develop optimal scraping approach

### Phase 5: Report Generation
- [x] 5.1 Synthesize all findings
- [x] 5.2 Create comprehensive analysis document
- [x] 5.3 Include practical implementation guidance

## Key Findings Summary

### WIG80 Index Structure
- **Size**: 80 small-cap companies from WSE Main List
- **Exclusions**: Companies already in WIG20 and mWIG40
- **Selection**: Based on 12-month turnover and free float market cap
- **Current Value**: ~29,800 points (November 2024)

### Stooq.pl Data Organization
- **418 WSE stocks** organized by granularity (daily, hourly, 5-minute)
- **Polish symbol format**: Requires ".pl" suffix (e.g., KGH.pl, PGE.pl)
- **Data formats**: CSV download with OHLCV fields
- **No API**: Direct web download required

### Financial Metrics Available
- **Price data**: Open, High, Low, Close (adjusted)
- **Volume**: Daily trading volume
- **Turnover**: Trading value in PLN, EUR, USD
- **Performance**: Percentage changes, 52-week ranges
- **Trades count**: Number of transactions
- **Missing**: P/E, P/B ratios not directly available

### Sample WIG80 Companies/Symbols Found
- **MNC**: Mennica Polska S.A.
- **MCI**: MCI Capital Alternatywna Spolka Inwestycyjna S.A.
- **SHO**: Shoper Spolka Akcyjna
- **Additional symbols**: VVD, MGT, SLV, CLC, ECH, GRX, WTN, UNI, etc.

## Timeline
✅ **Completed**: All tasks completed successfully within current session