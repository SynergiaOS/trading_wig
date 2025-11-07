# WIG80 Current Data Collection from Stooq: Methodology, Findings, and Dataset Blueprint

## Executive Summary

This report documents the design, implementation, and validation of a repeatable process to build a current dataset for all companies in the WIG80 index (also known as sWIG80) using publicly accessible pages on Stooq. The deliverable is a consolidated JSON file containing core fields required by quantitative analysts and data engineers: current price, price-to-earnings ratio (P/E; labelled C/Z on Stooq), price-to-book ratio (P/B; labelled C/WZ on Stooq), daily trading volume (Wolumen), turnover (Obrót), company symbol, company name, and a last-updated timestamp.

The scope is explicitly point-in-time and centered on Warsaw Stock Exchange (GPW) listings. Stooq offers wide coverage of Polish equities, including component lists for sWIG80 and symbol pages for individual equities and ratio pages, and also supports a regional index view and market statistics for Poland that are valuable for context and cross-checks. The main findings are threefold. First, Stooq’s component lists and symbol pages make it feasible to assemble a comprehensive snapshot of WIG80 constituents with intraday timestamps. Second, P/E and P/B for individual stocks are available on Stooq via metric-specific suffix conventions (e.g., _PE and _PB), though coverage varies by issue. Third, while Stooq provides daily historical files through its historical database portal, a direct single-url CSV for current cross-sectional snapshots is not explicitly documented; as a result, the production approach relies on enumerating the component list and resolving each symbol’s pages.

The dataset is designed to be saved as data/wig80_current_data.json. Because index membership can change and Stooq pages can be updated intraday, periodic refreshes and reconciliation against authoritative index membership publications are recommended to maintain dataset integrity. The report closes with a quality assurance framework and an implementation checklist.

Key references include Stooq’s Polish-language portal (for equity navigation and market statistics), the sWIG80 component page, and Stooq’s historical data portal that informs retrieval best practices.[^1][^3][^5]


## Scope, Definitions, and Data Dictionary

The scope is the current cross-section of sWIG80 constituents as listed by Stooq, with all figures captured at a single point in time. All amounts are in Polish złoty (PLN). The dataset follows the field structure produced by Stooq’s sWIG80 component listings and symbol-level pages:

- Symbol: the issue identifier used by Stooq (e.g., three-letter codes).
- Company name: the listing name as displayed on Stooq.
- Current price (Kurs): the latest displayed price, typically timestamped to the session.
- Change (Zmiana): intraday or session change as displayed.
- P/E (C/Z): price-to-earnings ratio page for the symbol (suffix _PE), if available.
- P/B (C/WZ): price-to-book ratio page for the symbol (suffix _PB), if available.
- Volume (Wolumen): the traded volume in units, commonly abbreviated with k (thousands) or m (millions).
- Turnover (Obrót): turnover as displayed, with PLN context provided via Stooq market statistics.
- Last update: the timestamp shown on the page (CET/CEST).

To illustrate the dataset fields, the following table provides the canonical data dictionary. Field names are chosen to reflect Stooq labels while maintaining clarity for downstream consumers.

Table 1. Data dictionary for WIG80 current snapshot

| Field name                 | Type     | Example           | Source/location on Stooq                        |
|---------------------------|----------|-------------------|-------------------------------------------------|
| symbol                    | string   | AGO               | sWIG80 components table (Symbol column)[^3]     |
| company_name              | string   | AGORA SA          | sWIG80 components table (Nazwa column)[^3]      |
| current_price             | float    | 9.2               | Symbol page; last price display[^1][^15]        |
| change_percent            | float    | -1.50             | Symbol page; change display[^1][^15]            |
| pe_ratio                  | float    | 15.5              | Symbol page ending with _PE[^6]                 |
| pb_ratio                  | float    | 1.2               | Symbol page ending with _PB[^6]                 |
| volume                    | integer  | 1365              | Components table; “Wolumen” normalized[^3]      |
| volume_abbrev             | string   | 1.37k             | Components table display[^3]                    |
| obrot_value               | string   | 220.77M PLN       | Symbol page or derived; PLN context[^1][^4]     |
| last_update               | string   | 17:10:00          | Components table “Data” or symbol page[^3][^15] |

Interpretation notes:
- Volume normalization: Stooq often abbreviates with k/m. Normalize to units for analysis (e.g., 1.37k → 1,370).
- Obrót: The PLN currency context is validated using Stooq’s Poland market statistics.[^4]
- P/E and P/B: Availability varies by issue and timing; capture null when not available.
- Timestamps: Use CET/CEST as displayed; daylight-saving transitions may apply.

To avoid ambiguity, the next table clarifies the abbreviations encountered in the raw pages.

Table 2. Polish-to-English abbreviations and units

| Abbreviation | Polish term      | English meaning                 | Notes                                                                 |
|--------------|-------------------|---------------------------------|-----------------------------------------------------------------------|
| C/Z          | Cena/Zysk         | Price/Earnings (P/E)            | Metric suffix _PE on Stooq[^6]                                       |
| C/WZ         | Cena/Wartość Księgi| Price/Book (P/B)               | Metric suffix _PB on Stooq[^6]                                       |
| Wolumen      | Wolumen           | Volume                          | Often abbreviated with k/m[^3]                                       |
| Obrót        | Obrót             | Turnover                        | Displayed with PLN context in market stat[^4]                        |
| Zmiana       | Zmiana            | Change                          | Intraday or session change on the page[^1]                           |


## Data Sources and Retrieval Architecture

Stooq’s Polish-language portal organizes equity data by market and index categories. For this project, three resource types are pivotal:

- sWIG80 components list: a tabular view of constituents with symbols, names, prices, changes, volumes, and last update times.[^3]
- Symbol pages: per-issue pages with current quotes and links to metric-specific subpages for P/E and P/B, accessed by appending _PE or _PB to the symbol.[^1][^6]
- Historical database portal: the documented path for bulk/daily data retrieval in CSV format (used here as context and for validation of Stooq’s conventions).[^5]

The retrieval workflow is designed to be deterministic and resilient to minor page variations:

1. Start from the sWIG80 components page to obtain the authoritative list of symbols and names.[^3]
2. For each symbol, fetch the core quote page to capture current price, change, last update, and any displayed turnover.[^1][^15]
3. Attempt to fetch the symbol’s P/E page (_PE) and P/B page (_PB). Where these pages exist and return a numeric metric, record the value; otherwise, record null.[^6]
4. Normalize displayed units and validate currency context using Stooq’s Poland market statistics.[^4]

Table 3. Endpoint-to-field mapping

| Endpoint type            | Example URL pattern          | Fields extracted                                      | Notes                                                     |
|--------------------------|------------------------------|-------------------------------------------------------|-----------------------------------------------------------|
| sWIG80 components list   | /t/?i=588                    | symbol, company_name, current_price, change_percent, volume_abbrev, last_update | Canonical constituents list[^3]                          |
| Symbol quote page        | /q/?s=SYMBOL                 | current_price, change_percent, last_update, obrot_value | Core quote view; AutoQuote may be active[^1][^15]        |
| P/E metric page          | /q/?s=SYMBOL_PE              | pe_ratio                                              | Metrics availability varies[^6]                           |
| P/B metric page          | /q/?s=SYMBOL_PB              | pb_ratio                                              | Metrics availability varies[^6]                           |
| Market statistics (PL)   | /t/s/?m=pl                   | Currency/turnover context                             | Validates PLN usage[^4]                                   |
| Historical portal        | /db/h/                       | Daily file conventions (CSV)                          | Used for context on Stooq data structure[^5]              |

### Components List and Symbol Set

The sWIG80 components page is the system of record for enumerating symbols and names and for obtaining the current snapshot fields (price, change, volume, last update) in one pass. It uses sortable columns and displays abbreviated volumes in k/m format. The page also indicates the update window and session context, which is important for interpreting timestamps.[^3]

### Quote and Metrics Endpoints

Core quotes for each symbol are retrieved via the /q/?s=SYMBOL pattern. Stooq convention extends this pattern for fundamentals: appending _PE or _PB yields a metric-specific page. The presence of a metric page does not guarantee a current numeric value; some symbols may not publish P/E or P/B at all times. Consequently, the pipeline must be tolerant to missing metrics and record nulls rather than failing.[^1][^6]

### Currency, Volume, and Turnover

All amounts in this dataset are in PLN. Stooq’s Poland market statistics page provides currency context and session-level turnover aggregates, which are useful for sanity checks on Obrót figures. Volumes displayed on component lists are commonly abbreviated with k (thousands) and m (millions). The extraction logic should parse these abbreviations, convert to full units, and preserve both normalized numeric volumes and the original abbreviated strings for transparency.[^4][^3]


## Methodology: Extraction, Normalization, and Validation

The methodology is designed to be robust to minor layout variations and tolerant of partial metric availability:

- Extraction: Enumerate the sWIG80 components table row-by-row to build the symbol set and capture current_price, change_percent, volume_abbrev, and last_update. For each symbol, fetch the quote page and metric pages (_PE and _PB).[^3][^1][^6]
- Normalization: Convert k/m abbreviations into full integer units (e.g., 1.37k → 1,370; 1.59m → 1,590,000). Preserve the original abbreviation in a separate field.
- Validation: Use Poland market statistics to confirm currency context for turnover (PLN). Cross-check that any turnover displayed on symbol pages is consistent with session aggregates when available.[^4]
- Timestamps: Capture last_update exactly as displayed on the component list or symbol page. Session times are shown in CET/CEST; no additional conversion is performed unless explicitly required by downstream consumers.[^3]

Table 4. Validation checks

| Check                                   | Purpose                                         | Rule/criterion                                    | Action on failure                      |
|-----------------------------------------|-------------------------------------------------|---------------------------------------------------|----------------------------------------|
| Currency sanity check                   | Confirm PLN context                             | Use market statistics to corroborate PLN usage[^4]| Flag for review; retain with note      |
| Volume unit normalization               | Ensure analysis-ready units                     | Parse k/m; convert to integers                    | Keep both normalized and raw strings   |
| Timestamp presence                      | Ensure time context                             | last_update must be non-empty                     | Re-fetch page; else mark with null     |
| Metric page availability                | Track ratio coverage                            | _PE/_PB pages may be absent or lack values        | Record null for missing metrics        |
| Price/change consistency                | Detect parsing anomalies                        | Non-negative volumes; plausible price ranges      | Log and re-parse; alert if outlier     |


## Findings: Data Availability and Coverage

Component-level data for sWIG80 is consistently available on Stooq’s components page, including symbols, names, prices, changes, volumes, and last update times. This page is the primary and most efficient source for a cross-sectional snapshot. At the issue level, Stooq exposes both quote pages and, by suffix, P/E and P/B pages.

A practical caveat is that Investing.com’s sWIG80 component page occasionally presents a truncated sample in free views, which underscores the importance of relying on Stooq’s own components listing for completeness. As an illustration of metric-specific pages, Stooq hosts LPP’s P/B page (LPP_PB), demonstrating the suffix convention used across issues for both P/B and P/E ratios. The Poland-wide market statistics page further confirms that session aggregates are presented in PLN, reinforcing currency normalization. Finally, Stooq’s historical database portal clarifies CSV conventions, even though current cross-sectional snapshots are best assembled from the components table and per-symbol pages.[^3][^6][^4][^5][^8]

Table 5. Coverage summary (current snapshot)

| Field              | Availability on components list | Availability via symbol pages | Notes                                                       |
|--------------------|----------------------------------|-------------------------------|-------------------------------------------------------------|
| symbol             | Yes                              | Yes                           | Single identifier across views[^3]                          |
| company_name       | Yes                              | Yes                           | Consistent naming across pages[^3]                          |
| current_price      | Yes                              | Yes                           | Price is timestamped on symbol pages[^1][^15]               |
| change_percent     | Yes                              | Yes                           | Intraday/session change display[^1][^15]                    |
| volume (Wolumen)   | Yes                              | Often                         | Abbreviated k/m on components; normalized for analysis[^3]  |
| turnover (Obrót)   | Sometimes                        | Sometimes                     | Currency context validated via Poland stats[^4]             |
| P/E (C/Z)          | N/A                              | Sometimes                     | Page suffix _PE; coverage varies by issue[^6]               |
| P/B (C/WZ)         | N/A                              | Sometimes                     | Page suffix _PB; coverage varies by issue[^6]               |
| last_update        | Yes                              | Yes                           | CET/CEST as displayed[^3][^15]                              |


## Dataset Specifications and Output

The output dataset is a UTF-8 encoded JSON file with a metadata block and a companies array. The metadata captures collection timestamp, data source, currency, and index context. Each company record includes both normalized fields and original display strings for transparency.

- File path: data/wig80_current_data.json
- Structure: JSON with metadata and companies array
- Currency: PLN
- Point-in-time semantics: all fields reflect the last displayed values at the time of capture

Table 6. Field mapping and units

| JSON field            | Type     | Description                                           | Units/format                         | Source location                          |
|-----------------------|----------|-------------------------------------------------------|--------------------------------------|------------------------------------------|
| metadata              | object   | Collection metadata                                   | —                                    | —                                        |
| data_source           | string   | Source website                                        | Stooq domain                         | Page header/site context[^1]             |
| collection_timestamp  | string   | UTC timestamp of collection                           | ISO 8601                             | System time at extraction                |
| index_name            | string   | Index name                                            | sWIG80 (WIG80)                       | Components page context[^3]              |
| currency              | string   | Currency of amounts                                   | PLN                                  | Market statistics context[^4]            |
| companies             | array    | List of company records                               | —                                    | —                                        |
| symbol                | string   | Issue symbol                                          | Text                                 | Components table, symbol page[^3][^15]   |
| company_name          | string   | Company name                                          | Text                                 | Components table, symbol page[^3][^15]   |
| current_price         | number   | Latest price                                          | PLN                                  | Components/symbol page[^1][^3][^15]      |
| change_percent        | number   | Session/intraday change                               | Percent                              | Components/symbol page[^1][^3][^15]      |
| pe_ratio              | number   | Price-to-earnings ratio                               | Ratio                                | Symbol _PE page[^6]                      |
| pb_ratio              | number   | Price-to-book ratio                                   | Ratio                                | Symbol _PB page[^6]                      |
| volume                | integer  | Traded volume (normalized)                            | Units                                | Components “Wolumen” normalized[^3]      |
| volume_abbrev         | string   | Volume as displayed                                   | e.g., 1.37k                          | Components “Wolumen” display[^3]         |
| obrot_value           | string   | Turnover (if displayed)                               | e.g., 220.77M PLN                    | Symbol page or derived; PLN context[^1][^4] |
| last_update           | string   | Timestamp on page                                     | CET/CEST                             | Components “Data” or symbol page[^3][^15]|


## Quality Assurance and Reproducibility

A disciplined QA framework ensures reproducibility and consistent coverage over time:

- Symbol set verification: validate that the symbol set matches the current sWIG80 components list at the time of extraction. Re-run if index changes are suspected or announced.[^3]
- Field-level completeness: ensure that every record contains symbol, company name, current price, change, last update, and volume. P/E and P/B may be null; do not impute.
- Currency checks: verify PLN context against Poland market statistics; treat any deviation as a controlled exception.[^4]
- Timestamp checks: capture the displayed timestamp and record CET/CEST explicitly; if a page lacks a timestamp, flag and re-fetch.
- Change detection: maintain per-run logs recording the number of symbols processed, success/failure counts, and any missing metrics to detect drifts in coverage over time.

Table 7. QA checklist

| Check                                  | Rule                                                  | Pass/fail criteria                      | Remediation                                      |
|----------------------------------------|-------------------------------------------------------|-----------------------------------------|--------------------------------------------------|
| Component set completeness              | All symbols from current list present                 | 100% of listed symbols                  | Re-enumerate from components page[^3]            |
| Required fields present                 | symbol, name, price, change, last_update, volume      | No nulls in required fields             | Re-fetch missing fields                          |
| Volume normalization                   | k/m parsed to integers                                | Integer ≥ 0                             | Re-parse abbreviations                           |
| Currency context                        | PLN confirmed via market statistics                   | PLN indicated[^4]                       | Review source pages; annotate discrepancy        |
| Metrics coverage                        | P/E and P/B captured when available                   | Non-null when page has value            | Record nulls; no imputation                      |
| Timestamp capture                       | last_update present and plausible                     | Non-empty; reasonable time range        | Re-fetch page or mark as null with note          |
| Run logging                             | Success/failure counts logged                         | Counts match expected totals            | Investigate failures; re-run affected symbols    |


## Limitations and Risk Management

Three structural limitations merit attention:

- Metric availability: Not all symbols publish P/E or P/B on Stooq at all times. The pipeline records nulls when metric pages are unavailable or lack a current value. No inference or imputation is performed.[^6]
- Membership changes: The WIG80 index is periodically rebalanced. Always reconcile the symbol set against the latest components list before each run and after known index events.[^3][^9]
- Volatility of turnover reporting: Turnover (Obrót) may be displayed differently across pages or omitted for certain instruments. Use Poland market statistics to confirm currency context (PLN) and avoid false precision when reconciling across sources.[^4]

Operational safeguards include conservative retry logic for network hiccups, clear logging of missing metric pages per symbol, and strict avoidance of inferred values in place of nulls. For regulatory and branding considerations, Stooq acknowledges content and data integrations from third parties; the dataset should be used in line with these terms and the site’s usage guidelines.[^1]


## Actionable Insights and Use Cases

The dataset supports several immediate analytical workflows:

- Valuation screening: filter issues by P/B or P/E thresholds to identify candidates for fundamental review. This is straightforward where ratio pages are available; otherwise, records naturally fall out of ratio-specific screens.[^6]
- Liquidity analysis: combine volume (Wolumen) with turnover (Obrót) to gauge market activity and execution feasibility, using PLN context from market statistics to normalize expectations across sessions.[^3][^4]
- Market monitoring: track price changes and last update times to identify delayed quotes, outliers, or symbols with anomalous volume spikes relative to typical sessions.
- Index-aware analytics: evaluate sector exposure and size positioning within sWIG80 by joining the snapshot with external sector and size metadata, mindful of the index’s mid/small-cap orientation and periodic rebalances.[^9]

For backtesting, the current snapshot can serve as a calibration point; Stooq’s historical database provides the daily CSV context needed for time-series reconstruction.[^5]


## Appendices

### A. Sample URL patterns (no full URLs)

- Components list: /t/?i=588
- Index overview (intraday index panel): /q/i/?s=swig80
- Index summary page: /q/?s=swig80
- Symbol page: /q/?s=SYMBOL
- P/E page: /q/?s=SYMBOL_PE
- P/B page: /q/?s=SYMBOL_PB
- Market statistics (Poland): /t/s/?m=pl
- Historical data portal: /db/h/

Example issue-level metric pages include LPP_PB and WIG_PE, illustrating metric suffix conventions and their interpretation.[^6][^7]

### B. Glossary

Table 8. Polish terms and English equivalents

| Term (PL)  | English equivalent        | Notes                                      |
|------------|----------------------------|--------------------------------------------|
| Cena       | Price                      | Current last trade price                   |
| Zmiana     | Change                     | Intraday/session change                    |
| Wolumen    | Volume                     | Number of shares traded                    |
| Obrót      | Turnover                   | Value traded (PLN context)                 |
| Cena/Zysk  | Price/Earnings (P/E)       | C/Z; _PE suffix page                       |
| Cena/Wartość Księgi | Price/Book (P/B) | C/WZ; _PB suffix page                      |

### C. Implementation checklist (from components list to JSON)

1. Fetch the sWIG80 components list and extract symbol, name, price, change, volume, last_update.[^3]
2. For each symbol, fetch the symbol page to confirm price/change and collect turnover if displayed; record timestamp.[^1][^15]
3. Fetch P/E (_PE) and P/B (_PB) pages; record numeric ratio if available, else null.[^6]
4. Normalize volume: parse k/m abbreviations to integer units; retain abbreviated string as volume_abbrev.[^3]
5. Validate currency context (PLN) using market statistics; annotate any discrepancies.[^4]
6. Assemble JSON with metadata (timestamp, source, currency, index) and company records with normalized fields.
7. Run QA checks (completeness, normalization, currency sanity, timestamp presence, metrics coverage).
8. Save to data/wig80_current_data.json.

### D. Information gaps (to be addressed during operations)

- A single, authoritative list of Polish ticker suffixes and any special cases beyond the general Stooq conventions is not consolidated in one place; the pipeline must therefore validate suffixes issue-by-issue.
- A dedicated Stooq page documenting current cross-sectional CSV downloads is not explicitly provided; the methodology derives such snapshots from component tables and per-symbol pages.
- Coverage and refresh cadence of _PE and _PB pages vary by issue; some entries may legitimately lack a current ratio.
- Turnover (Obrót) reporting conventions can differ across instrument types; confirm units via market statistics and symbol pages.
- Time zone normalization is not explicitly documented beyond CET/CEST displays; record timestamps as shown unless a standard is mandated downstream.


## References

[^1]: Stooq.pl (Polish) – Market Data Portal. https://stooq.pl/
[^2]: Stooq – Main Site (English Mirror). https://stooq.com/
[^3]: Akcje sWIG80 – Stooq Components List. https://stooq.pl/t/?i=588
[^4]: Poland – Market Statistics – Stooq. https://stooq.com/t/s/?m=pl
[^5]: Stooq – Historical Data Download Portal. https://stooq.com/db/h/
[^6]: LPP_PB – LPP Price/Book Ratio – Stooq. https://stooq.pl/q/?s=lpp_pb
[^7]: WIG_PE – WIG Price/Earnings Ratio – Stooq. https://stooq.pl/q/?s=wig_pe
[^8]: WIG80 Components – Investing.com. https://www.investing.com/indices/wig-80-components
[^9]: GPW Benchmark – Index Descriptions (WIG80/sWIG80). https://gpwbenchmark.pl/en-opisy-indeksow
[^15]: Stooq – Quote Lookup (General Symbol Page Pattern). https://stooq.com/q/?s=

Note: Reference [^15] illustrates Stooq’s general symbol query pattern and quote pages; individual symbol paths follow /q/?s=SYMBOL on the stooq.pl domain as described in the methodology.