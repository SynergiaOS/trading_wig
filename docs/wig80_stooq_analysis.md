# WIG80 Index Structure and Stooq.pl Data Access: Components, Organization, Metrics, and Scraping Strategy

## Executive Summary

This report provides an end-to-end, implementation-ready guide for accessing and maintaining constituents of Poland’s sWIG80 index (commonly referred to as WIG80) via Stooq.pl’s public web interface. It answers four questions critical to quantitative researchers and data engineers: what the index is and how it is compiled; where to obtain authoritative, machine-readable component lists; how Stooq.pl organizes Polish market data; and what metrics are available for daily analysis and portfolio construction.

Scope. The sWIG80 is the small-cap segment of the Warsaw Stock Exchange (GPW/WSE), comprising 80 stocks selected from the WSE Main List excluding WIG20 and mWIG40 constituents. Selection occurs quarterly based on turnover and free-float market capitalization, with annual rebalancing and publication rules governed by GPW Benchmark[^2]. The authoritative methodology resides in GPW documentation[^2] and index descriptions[^3].

Top findings.
- Authoritative component list. The most reliable approach to assemble the sWIG80 universe is to start from the official “index portfolio” or constituent lists published by GPW Benchmark and cross-check with daily market statistics published by Stooq for WSE (code plws). A secondary validation against Investing.com’s sWIG80 components page is useful but not authoritative[^7][^3].
- Stooq data organization. Stooq provides Poland market statistics (advancers/decliners, turnover, trades) with per-stock metrics (ticker, market, price, change, turnover, trades). It also supports individual stock pages and bulk historical downloads organized by country and granularity. WSE tickers are accessed via the “XWAR:” prefix or by appending the “.pl” suffix in many toolchains[^1][^4][^10][^8][^9].
- Available metrics. On Stooq’s market statistics pages and individual stock pages, core daily fields include price, change, turnover, and number of trades; volume is present in individual time series and historical files. P/E and P/B are not exposed on these pages; these fundamentals must be sourced elsewhere[^1][^11][^4].
- Scraping strategy. The recommended, low-friction path is: derive sWIG80 constituents from GPW Benchmark; enumerate WSE tickers from Stooq’s Poland statistics; verify tickers via Stooq’s stock pages; and obtain OHLCV (open-high-low-close-volume) via daily bulk files or per-symbol CSV downloads, adding a mandatory “.pl” suffix for WSE instruments. Respect AutoQuote session limits and incorporate historical date parameters where needed[^1][^4][^8][^9].

Deliverables. A reproducible plan and URL patterns are provided, alongside workflow tables for component verification and scraper operation. Known limitations are flagged, with specific guidance on verification cadence and symbol mapping.

References are consolidated at the end of the report.

[^1]: Market Stat: Poland — Stooq. https://stooq.com/t/s/?m=pl  
[^2]: sWIG80 – Index Methodology (GPW Benchmark). https://gpwbenchmark.pl/pub/BENCHMARK/files/PDF/metodologia_indeksow/new/2022_12_30_sWIG80_en.pdf  
[^3]: Index descriptions – GPW Benchmark. https://gpwbenchmark.pl/en-opisy-indeksow  
[^4]: Historical Data – Stooq (db/h). https://stooq.com/db/h/  
[^7]: WIG80 Companies Stock List – Investing.com. https://www.investing.com/indices/wig-80-components  
[^8]: Problem importing Polish stock data from Stooq – Stack Overflow. https://stackoverflow.com/questions/60866748/problem-with-importing-polish-stock-data-from-stooq-com  
[^9]: Stooq Poland All Stocks Price Index (^_PL). https://stooq.com/q/d/?s=%5E_pl  
[^10]: KGHM Polska Miedź SA (KGH) – Stooq. https://stooq.pl/q/?s=KGH  
[^11]: An Introduction to Stooq Pricing Data – QuantStart. https://www.quantstart.com/articles/an-introduction-to-stooq-pricing-data/


## 1. WIG80 Index: Definition, Universe, and Methodology

The sWIG80 index (ticker: SWIG80 on Stooq; frequently referenced as WIG80 in market usage) is the small-cap benchmark of the Warsaw Stock Exchange. It consists of 80 companies listed on the WSE Main List, explicitly excluding constituents of the WIG20 (large-cap) and mWIG40 (mid-cap) indices[^2][^3]. Its role is to reflect the performance of smaller Polish issuers that meet liquidity and free-float thresholds, serving as the investable universe for small-cap strategies and as a source of candidates for the broader Polish small-cap opportunity set.

Methodology. The selection is based on a ranking that combines 12‑month turnover with free-float market capitalization (calculated using closing prices from the last five trading sessions before ranking). Only companies satisfying the Monthly Turnover Ratio (MTR) over the prior 12 months are eligible. Companies in the lowest quartile of free-float market capitalization are excluded from ranking. The ranking is conducted following the third Friday of February, May, August, and November. The index portfolio is adjusted after the third Friday of June, September, and December, with an annual revision after the third Friday of March. Single-stock weight caps are set at 10 percent. sWIG80 is a price index, meaning dividends are not included in the index calculation[^2].

To anchor these concepts, the methodology excerpt below highlights selection rules and publication schedule:

![Excerpt from GPW Benchmark sWIG80 methodology (selection criteria and publication parameters)](.pdf_temp/subset_1_10_4cd7b5c4_1762284072/images/rtlq74.jpg)

This governance framework ensures systematic reconstitution and ongoing alignment with liquidity and free-float constraints. For data engineers, it also implies that universe verification should be tied to the quarterly ranking and the subsequent adjustment windows.

Table 1 summarizes the methodology at a glance.

Table 1. Methodology summary of sWIG80

| Aspect | Rule/Parameter |
|---|---|
| Number of constituents | 80 |
| Universe | WSE Main List excluding WIG20 and mWIG40 |
| Basic eligibility | Free float >10%; free float value > €1m; ≥1 trade in last 3 months; not under special status (e.g., bankruptcy); not in ALERT LISTS or Lower Liquidity Space |
| Ranking inputs | 12-month turnover and free-float market cap (based on last 5 sessions’ closing prices) |
| MTR requirement | Must meet Monthly Turnover Ratio over prior 12 months |
| Exclusions | Lowest quartile of free-float market cap; dual-listed companies above mWIG40 median cap |
| Selection cadence | Data collection after third Friday of Feb, May, Aug, Nov |
| Portfolio adjustments | After third Friday of Jun, Sep, Dec; annual revision after third Friday of Mar |
| Weight cap | 10% per constituent |
| Index type | Price index (dividends excluded) |

[^2]: sWIG80 – Index Methodology (GPW Benchmark).  
[^3]: Index descriptions – GPW Benchmark.

### 1.1 Universe and Eligibility

The eligible universe is the WSE Main List, filtered to exclude current WIG20 and mWIG40 constituents. Within that universe, companies must satisfy basic liquidity and free-float thresholds. The ranking then balances trade activity (turnover) with size (free-float market cap), with a minimum trading activity requirement (MTR) applied across the prior 12 months[^2]. This approach ensures that selected small caps are sufficiently tradable to support index replication and backtesting without undue microstructure noise.

### 1.2 Ranking, Weighting, and Revisions

The ranking draws on two dimensions—12‑month turnover and free-float market capitalization—computed from a short window of closing prices prior to the ranking day. To emphasize tradability, only securities meeting the MTR criterion are considered; to avoid extremes, the bottom quartile by free-float capitalization is excluded. Portfolio changes are synchronized with the exchange calendar through scheduled adjustments and an annual revision, ensuring predictability for rebalancing operations. Finally, single-stock weights are capped at 10 percent to limit concentration risk[^2].


## 2. Component List Construction Strategy (Companies + Symbols)

An authoritative sWIG80 component list must ultimately be anchored to GPW Benchmark. In practice, two sources on Stooq offer practical enumeration and validation:
- Stooq’s Poland market statistics page for WSE (code plws) for symbol discovery and trading-day checks[^1].
- Individual stock pages for per-symbol validation and historical series access[^10].

Investing.com’s components page is useful for cross-checks but not authoritative[^7]. GPW’s “List of companies” is a broad registry; you must filter it by index membership to reach sWIG80[^6]. TradingView’s sWIG80 view can provide supplementary identification of tickers and company names for a subset of constituents[^12].

Table 2 compares these sources.

Table 2. Source comparison for sWIG80 components and ticker mapping

| Source | Role | Strengths | Limitations | Recommended usage |
|---|---|---|---|---|
| GPW Benchmark (methodology and index portfolio) | Authoritative index definition and membership | Official rules and portfolios; governance cadence | Requires access to current portfolio files/communiqués | Primary reference for constituent list and rebalancing cadence |
| Stooq Market Statistics (Poland, WSE) | Universe and daily symbol enumeration (plws) | Comprehensive daily statistics; per-stock fields; historical date parameters | Not an index official source; symbols must be mapped to index membership | Symbol discovery, validation of trading activity, and data pulls |
| Stooq Individual Stock Pages (XWAR: or .pl) | Per-symbol validation and data access | Real-time snapshot fields; links to historical data and CSV | Manual enumeration required to cover 80 names | Verification of symbol mapping and historical coverage |
| Investing.com Components (sWIG80) | Secondary validation | Human-readable component list with live prices | Not official; symbol mapping may require disambiguation | Supplemental cross-check for completeness |
| GPW “List of companies” | Broad registry of WSE issuers | Official company registry | Not filtered to sWIG80; requires mapping to index membership |辅助映射和名称清理 (auxiliary mapping and name cleanup) |
| TradingView sWIG80 | Supplementary ticker discovery | Shows tickers and names for many constituents | Not official; coverage may be partial | Supplemental discovery and name standardization |

[^6]: GPW Main Market – List of companies. https://www.gpw.pl/list-of-companies  
[^7]: WIG80 Companies Stock List – Investing.com. https://www.investing.com/indices/wig-80-components  
[^12]: SWIG80 Index Charts and Quotes — TradingView. https://www.tradingview.com/symbols/GPW-SWIG80/

### 2.1 Authoritative Sources and Cross-Checks

Use GPW Benchmark’s methodology and any published index portfolios to derive the authoritative constituent list. Where GPW publishes historical portfolios or current constituents, capture them as the source of truth. Then, enumerate tickers via Stooq’s WSE market statistics and confirm each symbol’s Stooq presence on its dedicated page. Once a working list is assembled, use Investing.com as a secondary validation against omissions or duplicate names, keeping in mind that Investing.com is not the official index owner[^2][^7].

### 2.2 Ticker Mapping for WSE on Stooq

Stooq tags WSE instruments with the exchange prefix “XWAR:” on pages (e.g., XWAR:KGH). When accessing data programmatically or through client libraries, append the “.pl” suffix to the plain ticker (e.g., KGH.pl). The “.pl” suffix is necessary to avoid misrouting to other markets (such as U.S. tickers with similar symbols)[^10][^8]. This convention applies broadly across Stooq’s non-U.S. markets.


## 3. How Stooq.pl Organizes Polish Market Data

Stooq structures Poland’s market pages along three axes: daily market statistics (advancers/decliners, turnover, trades), individual stock pages (quote, historical data, CSV downloads), and bulk historical downloads by granularity and format. It also provides historical views of market statistics by date.

- Market statistics. The Poland overview aggregates the WSE and NewConnect markets, breaking out advancing, declining, and unchanged issues, along with volume, turnover (PLN/EUR/USD), and trade counts. Equities below price or turnover thresholds are omitted from statistics to reduce noise in summaries[^1].
- WSE vs NewConnect. The WSE market code on Stooq is plws; NewConnect is plnc. Most sWIG80 constituents trade on WSE Main List[^1].
- Individual stock pages. Each equity has a quote page (e.g., KGH), with a real-time snapshot (price, change, day range), turnover, trades, and links to historical data and CSV download. Exchange prefixes (XWAR:) are used on-page[^10].
- Bulk historical data. Stooq maintains a directory of historical downloads organized by country and granularity (daily, hourly, 5-minute), offered as ASCII (plain text) and Metastock formats. Polish data (country code pl) is available under db/h with separate folders for each granularity[^4].

Table 3 summarizes Stooq’s organization for Poland.

Table 3. Stooq Poland data organization and page taxonomy

| Layer | Purpose | Examples |
|---|---|---|
| Country overview | Aggregated market statistics by country; historical links by date | Poland overview (advancers/decliners, volume, turnover, trades) |
| Exchange-level | Market statistics for a specific exchange | WSE (plws), NewConnect (plnc) |
| Individual stock | Quote, snapshot fields, historical data, CSV download | XWAR:KGH on Stooq.pl |
| Bulk historical | Daily/hourly/5-minute ASCII and Metastock downloads | db/h: daily/hourly/5-minute for Poland |
| CSV download helper | Per-symbol CSV field selection and download | CSV export links on individual stock pages |

Table 4 details Poland’s bulk historical data options and approximate sizes.

Table 4. Poland historical data options (db/h)

| Granularity | Format | Approx. size | Use case |
|---|---|---|---|
| Daily | ASCII | ~184 MB | OHLCV backtesting; broad coverage |
| Daily | Metastock | ~3.9 MB | Compatibility with Metastock tools |
| Hourly | ASCII | ~24 MB | Intraday analysis with limited history |
| Hourly | Metastock | ~2.4 MB | Compatibility with Metastock tools |
| 5-minute | ASCII | ~26 MB | Short-horizon intraday strategies |
| 5-minute | Metastock | ~2.4 MB | Compatibility with Metastock tools |

[^4]: Historical Data – Stooq (db/h).

### 3.1 Market Statistics Pages

For a chosen trading day, Stooq presents:
- Issues summary: counts and percentages of advancing, declining, and unchanged issues.
- Volume and turnover: by direction, with turnover reported in PLN, EUR, and USD.
- Trades: total trades and directional splits.
- New highs/lows: counts and percentages.

The page omits equities with prices below 0.021 PLN, as well as WSE equities with turnover below 100,000 PLN and NewConnect equities with turnover below 10,000 PLN. These filters reduce outliers and improve the interpretability of daily summaries[^1].

### 3.2 Individual Stock Pages

On an equity’s page (e.g., KGHM Polska Miedź), fields include current price with timestamp, change and percentage change, day high/low, open, previous close, bid/ask with volumes, turnover, and number of transactions. Historical data ranges (1 day to “Max since 1997”) and CSV download links are available. The XWAR: prefix denotes the Warsaw Stock Exchange on Stooq pages[^10].


## 4. Available Financial Metrics on Stooq

Stooq’s Poland market pages and individual stock pages expose complementary sets of metrics:

- Market statistics page: equity ticker, market (WSE/NewConnect), price with timestamp, percentage change, turnover (PLN), and number of trades. Volume is presented in aggregates across advancers/decliners/unchanged. P/E and P/B are not displayed on these pages[^1].
- Individual stock pages: richer real-time fields (price, change, day range, open, previous close, bid/ask, volume, turnover, transactions) and access to historical series. P/E and P/B remain unavailable here as well[^10].
- Historical bulk downloads: complete OHLCV time series, typically used for backtesting and signal generation[^4][^11].

Table 5 clarifies metric coverage by page type.

Table 5. Metrics availability by Stooq page type

| Metric | Market statistics (country/exchange) | Individual equity page | Historical CSV/bulk files |
|---|---|---|---|
| Price (last) | Yes | Yes | Yes |
| Change (%) | Yes | Yes | Derived from Close |
| Turnover (PLN/EUR/USD) | Yes (aggregated; PLN primary) | Yes (per-symbol) | Derived from price × volume (if not present) |
| Number of trades | Yes | Yes | Sometimes present; otherwise derived if available |
| Volume | Aggregated | Yes (per symbol) | Yes (V field) |
| P/E, P/B | No | No | No (not in OHLCV) |
| Historical date parameter | Yes | Yes | Yes (by file selection) |

[^1]: Market Stat: Poland — Stooq.  
[^4]: Historical Data – Stooq (db/h).  
[^10]: KGHM Polska Miedź SA (KGH) – Stooq.  
[^11]: An Introduction to Stooq Pricing Data – QuantStart.

### 4.1 P/E and P/B: Where to Find (or Not)

Neither P/E nor P/B is available on Stooq’s market statistics or individual stock pages, nor in the OHLCV historical files. For these fundamentals, use other sources (e.g., issuer reports, investor relations pages, or financial data vendors). Given the scope of this report, a comprehensive fundamental catalog is out of scope and is flagged as an information gap.


## 5. Scraping Strategy for WIG80 Data on Stooq

The most robust and compliant workflow minimizes scraping volatility by combining authoritative index membership with Stooq’s market statistics for symbol discovery and bulk historical data for time series.

Workflow.
1. Constituents. Obtain the current sWIG80 constituent list from GPW Benchmark (authoritative). Use historical portfolios or communiqués if available to lock a versioned list per review/adjustment window[^2].
2. Symbol mapping. Enumerate candidate WSE tickers from Stooq’s Poland market statistics (plws). Verify each symbol’s individual page and build a mapping (company name ↔ Stooq ticker ↔ XWAR: ticker ↔ .pl suffix). Confirm that “.pl” is needed when requesting data via tools that default to U.S. markets[^1][^8][^10].
3. Time series. Use Stooq’s bulk daily ASCII files for Poland to obtain OHLCV for all mapped tickers in one pass. Alternatively, use per-symbol CSV download links where bulk handling is impractical. Respect AutoQuote session durations on interactive pages[^4][^10][^11].
4. Validation. Reconcile the number of constituents (80) and verify symbol coverage; ensure that trading-day filters on market statistics (price/turnover thresholds) do not cause false negatives. Align verification cadence with GPW’s review/adjustment calendar[^2][^1].
5. Governance. Cache a snapshot of the index portfolio used, store the source, and record the retrieval timestamp for auditability.

Table 6 collects the key URL patterns used in this workflow.

Table 6. URL pattern cheat sheet (Stooq Poland, WSE, and WIG80 index)

| Purpose | Pattern (base: stooq.com) | Notes |
|---|---|---|
| Poland market statistics | /t/s/?m=pl | Aggregated country view with advancers/decliners, turnover, trades |
| Historical market stats by date | /t/s/?m=pl&d=YYYYMMDD | Navigate to a specific session’s summary |
| WSE-specific statistics | /t/s/?m=plws | Enumerate WSE tickers; symbol discovery |
| Individual equity quote | /q/?s=SYMBOL | Displays price, change, turnover, trades; use XWAR: prefix where shown |
| CSV for a symbol | /q/l/?s=SYMBOL&f=…&h&e=csv | Fields controlled by f parameter; consult on-page helper |
| Poland all-stocks index | /q/d/?s=^_pl | Broad market benchmark for cross-checks |
| WIG80 (sWIG80) index | /q/?s=swig80 | Index page for quick reference and chart |

Examples:
- KGH quote page: https://stooq.pl/q/?s=KGH[^10]
- WIG80 index page: https://stooq.com/q/?s=swig80[^5]
- Poland all-stocks index CSV: https://stooq.com/q/d/?s=^_pl[^9]
- Poland market statistics: https://stooq.com/t/s/?m=pl[^1]

Table 7 illustrates a component verification workflow.

Table 7. Component verification workflow

| Step | Input | Process | Output |
|---|---|---|---|
| 1 | GPW Benchmark sWIG80 list | Capture as authoritative universe | Authoritative constituents (80) |
| 2 | Stooq plws statistics | Enumerate tickers present on latest session | Candidate tickers set |
| 3 | Map names to tickers | Verify each symbol’s Stooq page; record XWAR: and .pl | Clean mapping table |
| 4 | Data ingestion | Bulk daily ASCII (pl) or per-symbol CSV | OHLCV time series for 80 names |
| 5 | Validation | Cross-check counts and coverage; confirm index membership | Completeness report and exceptions |
| 6 | Governance | Snapshot list with source and timestamp | Auditable dataset |

[^1]: Market Stat: Poland — Stooq.  
[^2]: sWIG80 – Index Methodology (GPW Benchmark).  
[^4]: Historical Data – Stooq (db/h).  
[^5]: SWIG80 Index — Stooq. https://stooq.com/q/?s=swig80  
[^8]: Problem importing Polish stock data from Stooq – Stack Overflow.  
[^9]: Stooq Poland All Stocks Price Index (^_PL).  
[^10]: KGHM Polska Miedź SA (KGH) – Stooq.

### 5.1 URL Patterns and Parameters

Stooq provides consistent patterns for navigation and CSV retrieval:
- Market statistics by country: /t/s/?m=pl, with optional date /t/s/?m=pl&d=YYYYMMDD[^1].
- WSE-specific market page: /t/s/?m=plws[^1].
- Individual stock: /q/?s=SYMBOL (exchange shown as XWAR:SYMBOL on page)[^10].
- CSV download: /q/l/?s=SYMBOL&f=…&h&e=csv, where the f parameter controls included fields and “h” often signals header inclusion; exact field codes are visible in the helper on the symbol page[^10][^11].
- Historical bulk files: organized under db/h by granularity (daily, hourly, 5-minute) and format (ASCII/Metastock); Poland is under the “pl” country group[^4].

These patterns minimize scraping complexity by standardizing endpoint structure across instruments and dates.

### 5.2 Symbol Mapping and Validation

Implement the following validation rules:
- Enforce the “.pl” suffix when accessing Polish tickers through libraries or generic fetchers that default to U.S. markets. This avoids symbol collisions and ensures routing to WSE[^8].
- Confirm exchange membership to WSE (plws) via the market statistics pages for each symbol and verify the presence of historical data and CSV links on the individual stock page[^1][^10].
- Use Investing.com’s component list to cross-check names and catch any missing tickers, noting that Investing.com is not the authoritative index owner[^7].
- Align verification with GPW’s revision/adjustment schedule to maintain an up-to-date universe[^2].


## 6. Limitations, Risks, and Maintenance

Index changes. sWIG80 undergoes scheduled adjustments after the third Friday of June, September, and December, with an annual revision after the third Friday of March. New constituents enter and others exit in line with the ranking rules. Production data pipelines should freeze the universe at these checkpoints to avoid “drift” between official index composition and the working dataset[^2].

Stooq page behaviors. The AutoQuote feature updates pages automatically for a limited session window. When building scrapers, treat interactive features as best-effort and prefer bulk historical files for durability. Where interactive navigation is needed (e.g., enumerating symbols), plan for session refreshes and avoid excessive request rates. Stooq’s market statistics also omit low-price and low-turnover securities from the daily summaries; this filtering should not be misconstrued as absence from the exchange[^1].

Data scope. P/E and P/B are not available on Stooq’s market statistics or individual stock pages, nor in OHLCV files. Any analytics requiring these fundamentals must incorporate additional sources. Historical coverage and the maximum lookback for intraday files are governed by Stooq’s bulk data organization; validate instrument counts and file sizes prior to full-scale ingestion[^4][^11].

Documentation and auditability. Maintain a source-of-truth log capturing: (i) the official sWIG80 portfolio used, (ii) the exact retrieval timestamp, and (iii) the Stooq bulk file hashes/sizes. This creates a reproducible lineage for backtests and production runs.


## 7. Appendix

Glossary of terms.
- MTR (Monthly Turnover Ratio): A liquidity criterion based on trading activity over the prior 12 months, used to filter eligible securities for ranking[^2].
- Free float: Shares available for trading by the public, excluding restricted or insider holdings; a determinant of market capitalization used in ranking[^2].
- Weight cap: Maximum allowed weight of a single constituent in the index, set at 10 percent for sWIG80[^2].
- Price index vs. total return: sWIG80 is a price index, meaning dividends are not included in the index calculation[^2].

GPW WSE structure overview. Stooq labels the Warsaw Stock Exchange as WSE (plws) and the NewConnect market as plnc within its page taxonomy[^1]. The Poland country overview aggregates both markets, while per-exchange views enable focused enumeration of WSE-listed constituents.

Table 8. Example symbol mapping (illustrative subset)

| Company | Stooq ticker | XWAR: ticker | Notes |
|---|---|---|---|
| KGHM Polska Miedź SA | KGH | XWAR:KGH | Confirmed on Stooq; “.pl” suffix required in many toolchains |
| Additional sWIG80 constituents | — | — | To be completed from authoritative GPW list and validated via Stooq plws pages |

The mapping table should be populated from GPW Benchmark’s constituent list and verified through Stooq’s WSE market statistics and individual stock pages. Use Investing.com as a secondary cross-check[^10][^1][^7].


## Information Gaps

- An authoritative, machine-readable list of current sWIG80 constituents with ticker symbols directly from GPW Benchmark was not captured in this context. The official methodology is available, but a current portfolio file with symbols is needed to complete the mapping[^2][^3].
- The exact, complete enumeration of all 80 sWIG80 tickers from Stooq is not fully assembled here; enumeration requires either (a) GPW portfolio files or (b) a systematic pass of Stooq’s WSE listings and individual pages[^1].
- P/E and P/B are not available on Stooq’s pages or historical OHLCV files; where needed, alternate fundamental sources must be integrated[^11].
- A comprehensive official catalog of all fields and codes in Stooq’s CSV export “f” parameter is not fully documented here; users should rely on on-page helpers for definitive field codes[^10][^11].


## References

[^1]: Market Stat: Poland — Stooq. https://stooq.com/t/s/?m=pl  
[^2]: sWIG80 – Index Methodology (GPW Benchmark). https://gpwbenchmark.pl/pub/BENCHMARK/files/PDF/metodologia_indeksow/new/2022_12_30_sWIG80_en.pdf  
[^3]: Index descriptions – GPW Benchmark. https://gpwbenchmark.pl/en-opisy-indeksow  
[^4]: Historical Data – Stooq (db/h). https://stooq.com/db/h/  
[^5]: SWIG80 Index — Stooq. https://stooq.com/q/?s=swig80  
[^6]: GPW Main Market – List of companies. https://www.gpw.pl/list-of-companies  
[^7]: WIG80 Companies Stock List – Investing.com. https://www.investing.com/indices/wig-80-components  
[^8]: Problem importing Polish stock data from Stooq – Stack Overflow. https://stackoverflow.com/questions/60866748/problem-with-importing-polish-stock-data-from-stooq-com  
[^9]: Stooq Poland All Stocks Price Index (^_PL). https://stooq.com/q/d/?s=%5E_pl  
[^10]: KGHM Polska Miedź SA (KGH) – Stooq. https://stooq.pl/q/?s=KGH  
[^11]: An Introduction to Stooq Pricing Data – QuantStart. https://www.quantstart.com/articles/an-introduction-to-stooq-pricing-data/  
[^12]: SWIG80 Index Charts and Quotes — TradingView. https://www.tradingview.com/symbols/GPW-SWIG80/