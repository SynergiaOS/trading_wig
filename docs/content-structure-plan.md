# Content Structure Plan - Polish Financial Analysis Platform (WIG80)

## 1. Material Inventory

**Existing Platform URL:** https://g3plhagtpd01.space.minimax.io

**Current Features:**
- Market dashboard with WIG80 statistics
- Quick profit opportunities showcase (top 4 gainers)
- Company filtering system (All Categories, Small Cap, Value, Growth Potential)
- Detailed company data table (Symbol, Company, Price, Change, P/E, P/B, Score)

**Data Assets:**
- `wig80_current_data.json` (23 companies with real-time market data)
- `filtered_companies.json` (8 small-cap value + 15 growth stocks)
- `quick_profit_strategy.md` (Trading strategy with opportunities)

**Visual Assets:**
- Company logos (if available)
- Polish market branding elements
- Chart placeholder areas

## 2. Website Structure

**Type:** SPA (Single-Page Application)

**Reasoning:** 
- Focused single purpose: Polish stock market analysis dashboard
- Real-time data updates require SPA architecture for live tickers
- All features belong to one cohesive trading dashboard experience
- Content volume: ~23 companies, 5-6 main sections
- User goal: Monitor market, identify opportunities, analyze companies (single session workflow)
- Financial dashboards benefit from instant section switching without page reloads

## 3. Section Breakdown

### Section 1: Navigation Bar (`nav-bar`)
**Purpose:** Primary navigation and quick access controls
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Logo/Branding | Logo + App Name | Static | "Polish Financial Analysis Platform" | Logo (if available) or text |
| Market Status | Status Badge | Real-time | "Market Open/Closed" + current time | - |
| Theme Toggle | Toggle Button | UI State | Dark/Light mode switch | - |
| Search | Search Input | Interactive | Global company search | - |
| User Menu | Dropdown | UI | Settings, Alerts, Profile | - |

### Section 2: Market Dashboard (`market-overview`)
**Purpose:** High-level market statistics and key metrics
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Market Summary Cards | Stat Card Grid (4 cards) | `wig80_current_data.json` | Total companies count, avg change, market cap, volume | - |
| Top Gainer Badge | Highlight Card | Computed from JSON | ERB +14.94% | - |
| Top Loser Badge | Highlight Card | Computed from JSON | AMB -13.89% | - |
| Real-time Ticker | Scrolling Ticker | `wig80_current_data.json` | All company symbols + prices + changes | - |
| Market Heat Map | Grid Visualization | `wig80_current_data.json` | All 23 companies sized by market cap, colored by change % | - |

**FORBIDDEN:** Design decisions (these go in Design Specification)

### Section 3: Quick Profit Opportunities (`opportunities-showcase`)
**Purpose:** Highlight top performing stocks for quick trading decisions
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Opportunity Cards | Stock Card Grid (3-4 cards) | `quick_profit_strategy.md` or computed | Top 4 gainers: ERB, PKN, SHP, DGE | - |
| Performance Chart | Mini Line Chart | Time-series data (if available) | 7-day or 30-day price trend | Chart visualization |
| Quick Action CTAs | Button Group | Interactive | "Analyze", "Add Alert", "Compare" | - |

**Note:** Charts are decorative data visualizations, NOT content images

### Section 4: Category Filters (`filter-bar`)
**Purpose:** Dynamic filtering of company data
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Filter Tabs | Horizontal Tab Bar | Static categories | "All Categories", "Small Cap", "Value", "Growth Potential" | - |
| Active Count Badge | Number Badge | Computed | Count of companies in each category | - |
| Sort Dropdown | Dropdown Menu | UI State | Sort by: Change %, P/E, P/B, Score | - |

### Section 5: Company Data Table (`companies-table`)
**Purpose:** Comprehensive data table for all WIG80 companies
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Data Table | Professional Table | `wig80_current_data.json` | All 23 companies | Company logos (optional) |
| Table Columns | - | - | Symbol, Company, Price (PLN), Change %, P/E, P/B, Score | - |
| Row Actions | Action Buttons | Interactive | "View Details", "Add to Watchlist" | - |
| Pagination | Pagination Controls | Computed | Page numbers, items per page | - |

**Table Data Extraction Rules:**
- Symbol: `company.symbol`
- Company: `company.name`
- Price: `company.price` (format as PLN with 2 decimals)
- Change: `company.change_percent` (positive = green, negative = red)
- P/E: `company.pe_ratio`
- P/B: `company.pb_ratio`
- Score: Computed composite score (0-100%)

### Section 6: Company Detail Modal (`detail-modal`)
**Purpose:** Deep-dive analysis when user clicks a company
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Company Header | Modal Header | Selected company data | Company name, symbol, current price | Company logo |
| Price Chart | Full-size Chart | Historical data | Price movement over selected timeframe | Interactive chart |
| Financial Metrics | Metrics Grid | Selected company data | P/E, P/B, Volume, Market Cap, 52W High/Low | - |
| AI Analysis | Analysis Cards | Edge functions (future) | Fundamental, Technical, Sentiment analysis | - |
| Action Bar | Button Group | Interactive | "Add Alert", "Compare", "View Full Report" | - |

**Note:** AI analysis cards prepared for future backend integration

### Section 7: Footer (`footer`)
**Purpose:** Platform information and links
**Content Mapping:**

| Section | Component Pattern | Data File Path | Content to Extract | Visual Asset |
|---------|------------------|----------------|-------------------|--------------|
| Platform Info | Text Block | Static | "Polish Financial Analysis Platform - WIG80 Real-time Data" | - |
| Data Disclaimer | Small Text | Static | Market data disclaimer, update frequency | - |
| Links | Link Group | Static | About, Privacy, Terms, Contact | - |
| Timestamp | Live Clock | Real-time | Last updated timestamp | - |

## 4. Content Analysis

**Information Density:** High
- 23 companies with 7 data points each = 161+ data points
- Real-time updates every second (ticker)
- Multiple visualization types (cards, tables, charts, heat maps)
- Financial metrics require precision and clarity

**Content Balance:**
- Data/Numbers: 70% (price, metrics, percentages)
- Text: 20% (company names, labels, descriptions)
- Charts/Visualizations: 10% (heat maps, line charts, performance indicators)

**Content Type:** Data-driven financial dashboard
- Heavy numerical data presentation
- Real-time updates critical
- Color-coded information (green/red for gains/losses)
- Interactive filtering and sorting
- Professional trading tool aesthetic

**Polish Market Specifics:**
- Currency: PLN (Polish Złoty) with proper formatting (e.g., "616,37 PLN")
- Market index: WIG80 (top 80 companies by liquidity on Warsaw Stock Exchange)
- Company names: Polish companies (PKNORLEN, Erbud SA, Shoper, etc.)
- Trading hours: Warsaw Stock Exchange 9:00-17:00 CET
- Decimal separator: Comma (,) in Polish format vs. period (.) in international

**Design Implications:**
- Dark theme reduces eye strain for extended monitoring sessions
- High contrast needed for quick number scanning
- Animation on price changes draws attention to movement
- Color coding must be instantly recognizable (green up, red down)
- Dense data requires generous spacing to prevent overwhelming users
- Professional aesthetic builds trust for financial decisions
