# Stooq Polish Market Research Summary

## Overview
Research conducted on November 5, 2025, examining the Polish market statistics page on Stooq.com (https://stooq.com/t/s/?m=pl) and its sister site Stooq.pl to identify ways to access individual stock listings and download data for Polish stocks.

## Key Findings

### 1. Page Structure and Navigation

#### Main Polish Market Statistics Page
- **URL**: https://stooq.com/t/s/?m=pl
- **Content**: General Polish market statistics with links to specific exchanges
- **Navigation Options**: Access to WSE, NewConnect, and other international markets

#### Warsaw Stock Exchange (WSE) Specific Page
- **URL**: https://stooq.com/t/s/?m=plws
- **Alternative URL**: https://stooq.pl/t/s/?m=plws (Polish version)
- **Content**: Detailed WSE session statistics with individual stock listings

### 2. Individual Stock Access Methods

#### Method 1: Direct Symbol Search
- **Location**: Top navigation bar on all pages
- **Functionality**: Input field with "Kwotuj" (Quote) button
- **URL Pattern**: `https://stooq.com/q/?s=[SYMBOL]` or `https://stooq.pl/q/?s=[SYMBOL]`
- **Example**: https://stooq.com/q/?s=kgh (for KGH stock)

#### Method 2: Clickable Stock Links
- **Content**: Individual stock symbols displayed as clickable links
- **URL Pattern**: `https://stooq.com/q/?s=[SYMBOL]&d=YYYYMMDD`
- **Access**: Available on WSE statistics page showing top 25 advancing/declining stocks

### 3. Complete List of WSE Stock Symbols Found

#### Top 25 Advancing Stocks (as of 2025-11-04)
```
VVD, MGT, SLV, CLC, ECH, GRX, WTN, UNI, TOA, ENA, NEU, XTB, LBW, KER, TAR, CIG, BNP, TPE, VGO, DIG, ARL, ZRE, MIL, CBF, CMP
```

#### Top 25 Declining Stocks (as of 2025-11-04)
```
DGE, MDG, MCR, IZS, QRS, ICE, GTN, DAT, MOC, SPR, ELT, SVRS, PEN, CCC, APT, SGN, ACP, SNX, EAT, ATR, KTY, UNT, LPP, KGH, OPN
```

#### Additional Notable Symbols
- **WSE Indices**: WIG, WIG20
- **Stock Exchange Indices**: NCINDEX (NewConnect)

### 4. Data Download Options

#### Primary Download Option
- **Type**: CSV format
- **Content**: Combined quotes of most rising and falling stocks
- **URL**: 
  - English: `https://stooq.com/q/l/?s=_stat_plws_up_+_stat_plws_dw_&f=sd2t2ohlcm2vr&h&e=csv`
  - Polish: `https://stooq.pl/q/l/?s=_stat_plws_up_+_stat_plws_dw_&f=sd2t2ohlcm2vr&h&e=csv`
- **Data Included**: Symbol, date, open, high, low, close, volume, turnover

#### Filtered Data Options
- **Most Active**: `https://stooq.com/t/s/?m=plws&d=20251104&t=1`
- **New Highs**: `https://stooq.com/t/s/?m=plws&d=20251104&t=2`
- **New Lows**: `https://stooq.com/t/s/?m=plws&d=20251104&t=3`

### 5. Historical Data Access

#### Date-Specific URLs
- **Pattern**: `https://stooq.com/t/s/?m=plws&d=YYYYMMDD`
- **Available Dates**: Links provided for recent trading days (2025-11-03, 2025-10-31, 2025-10-30, 2025-10-29)
- **Coverage**: Daily session statistics for each date

#### URL Parameters Explained
- `m=plws`: Market code for Warsaw Stock Exchange
- `d=YYYYMMDD`: Date parameter
- `t=1,2,3`: Filter type (Most Active, New Highs, New Lows)

### 6. Additional Features and Options

#### Market Filters
- **ON/OFF Toggles**: Available for "AQ" (likely "AutoQuote") functionality
- **Market Categories**: Access to different exchanges via left sidebar navigation
- **Polish Localization**: Full Polish language interface available at stooq.pl

#### Search and Navigation Tools
- **Ticker Rank**: Link to ranking system (https://stooq.com/t/tr/)
- **Global Market Access**: Links to US, European, and Asian markets
- **Index Tracking**: Direct links to WIG and WIG20 indices

### 7. Technical Implementation Notes

#### Website Structure
- **Main Site**: stooq.com (English)
- **Polish Site**: stooq.pl (Polish localization)
- **URL Consistency**: Predictable URL patterns for programmatic access
- **Data Format**: CSV downloads available for bulk data

#### Data Access Patterns
- **Real-time Data**: Current session statistics updated daily
- **Historical Access**: URL-based date navigation
- **Symbol Lookup**: Direct symbol-based page access
- **Bulk Downloads**: CSV format for automated data collection

## Recommendations for Data Access

### For Individual Stock Data
1. Use direct symbol search in the top navigation
2. Click on stock symbols from the WSE statistics tables
3. Access individual stock pages via URL pattern: `https://stooq.com/q/?s=[SYMBOL]`

### For Complete Stock Lists
1. Start with the WSE statistics page showing top 25 advancers/decliners
2. Use historical date URLs to build comprehensive lists over time
3. Download CSV data for bulk processing
4. Consider web scraping for complete daily listings

### For Data Downloads
1. Use the primary CSV download link for top performers data
2. Utilize date-specific URLs for historical analysis
3. Implement automation using the predictable URL patterns

## Screenshots Captured
1. `polish_market_stooq_initial.png` - Initial Polish market page
2. `wse_stooq_page.png` - WSE statistics page
3. `wse_page_with_stocks.png` - WSE page with stock listings
4. `polish_site_version.png` - Polish version (stooq.pl)
5. `polish_site_scrolled.png` - Scrolled Polish site view

## Limitations and Considerations
- Only top 25 advancing and declining stocks visible per session
- Some navigation elements may be dynamically loaded
- Complete WSE stock list requires multiple date access or web scraping
- Polish and English versions may have slightly different features

## Conclusion
Stooq provides robust access to Polish stock market data through multiple channels:
- Direct symbol search
- Clickable stock links on statistics pages
- CSV downloads for bulk data
- Historical data via date-specific URLs
- Both English and Polish interfaces

The most effective approach for accessing complete WSE stock listings would be to combine multiple methods: start with the visible top performers, then use historical data and potential web scraping to build comprehensive lists over time.