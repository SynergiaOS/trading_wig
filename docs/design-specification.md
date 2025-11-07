# Design Specification - Polish Financial Analysis Platform (Dark Mode First)

**Version:** 1.0 | **Date:** 2025-11-05 | **Style:** Dark Mode First (Financial Pro)

---

## 1. Direction & Rationale

### 1.1 Design Essence

Professional dark interface for Polish stock market traders and analysts, inspired by Bloomberg Terminal, TradingView, and modern fintech platforms. Pure black backgrounds (#0A0E27, #000000) minimize eye strain during extended trading sessions while vibrant emerald greens (#10B981) and crimson reds (#EF4444) create instant visual recognition for gains and losses. High-contrast data presentation with animated real-time tickers, glowing interactive elements, and dense information architecture optimized for power users monitoring WIG80 market movements.

**Target Audience:** Polish traders, financial analysts, and investors (20-45) using the platform for extended periods in low-light environments or during after-hours market analysis.

### 1.2 Real-World Examples

- **TradingView** (tradingview.com) - Professional charting with dark interface, vibrant accent colors
- **Bloomberg Terminal** - Dense data presentation, high contrast, terminal aesthetics
- **Robinhood Web** - Modern fintech dark UI with smooth animations
- **Binance** - Crypto trading platform with real-time tickers and color-coded metrics
- **Interactive Brokers Dashboard** - Professional table layouts with live data updates

### 1.3 Polish Financial Context

- **WIG80 Focus:** Top 80 liquid stocks on Warsaw Stock Exchange
- **Currency:** PLN (Polish Złoty) formatting with comma decimal separator (616,37 PLN)
- **Market Hours:** WSE trading 9:00-17:00 CET with visual status indicators
- **Local Companies:** Polish names (PKNORLEN, Erbud SA, Shoper) with proper character support (ł, ą, ę)
- **Professional Trust:** Dark interface signals serious trading tool, not consumer app

---

## 2. Design Tokens

### 2.1 Color Palette

#### Background Hierarchy (OLED Optimized)

| Token Name | Hex Value | Usage | Contrast |
|------------|-----------|-------|----------|
| `bg-pure-black` | `#000000` | OLED base, navigation bar, hero sections | - |
| `bg-near-black` | `#0A0E27` | Main page background (subtle blue tint) | - |
| `bg-surface-dark` | `#141824` | Elevated cards, table rows, modals | +5% lightness |
| `bg-surface-hover` | `#1E2433` | Hover states, active elements | +10% lightness |
| `bg-surface-modal` | `#282E3F` | Tooltip backgrounds, highest elevation | +15% lightness |

#### Text Colors (High Contrast)

| Token Name | Hex Value | WCAG Ratio | Usage |
|------------|-----------|------------|-------|
| `text-primary` | `#E4E4E7` | 15.2:1 (AAA) | Prices, company names, primary data |
| `text-secondary` | `#A1A1AA` | 8.9:1 (AAA) | Labels, secondary metrics, timestamps |
| `text-tertiary` | `#71717A` | 5.2:1 (AA) | Captions, footnotes, disabled states |
| `text-inverse` | `#0A0A0A` | - | Text on accent backgrounds (buttons) |

#### Accent Colors (Financial Semantics)

| Token Name | Hex Value | WCAG Ratio | Usage |
|------------|-----------|------------|-------|
| `accent-primary` | `#3B82F6` | 8.6:1 (AAA) | Primary CTAs, links, interactive icons |
| `accent-success` | `#10B981` | 9.1:1 (AAA) | Positive price changes, gains, buy signals |
| `accent-danger` | `#EF4444` | 8.2:1 (AAA) | Negative price changes, losses, sell signals |
| `accent-warning` | `#F59E0B` | 10.4:1 (AAA) | Alerts, pending actions, caution indicators |
| `accent-info` | `#06B6D4` | 8.8:1 (AAA) | Neutral information, chart annotations |

#### Chart & Visualization Colors

| Token Name | Hex Value | Usage |
|------------|-----------|-------|
| `chart-gain` | `#10B981` | Positive performance areas, uptrend lines |
| `chart-loss` | `#EF4444` | Negative performance areas, downtrend lines |
| `chart-grid` | `rgba(255,255,255,0.05)` | Background grid lines |
| `chart-axis` | `rgba(255,255,255,0.2)` | Axis lines and labels |

#### Borders & Dividers

| Token Name | Value | Usage |
|------------|-------|-------|
| `border-subtle` | `1px solid rgba(255,255,255,0.06)` | Card borders, table cell dividers |
| `border-moderate` | `1px solid rgba(255,255,255,0.12)` | Active borders, section separators |
| `border-strong` | `1px solid rgba(255,255,255,0.2)` | Focus states, emphasized boundaries |
| `border-accent` | `2px solid #3B82F6` | Selected items, active filters |

### 2.2 Typography

#### Font Families

| Token Name | Stack | Usage |
|------------|-------|-------|
| `font-display` | `'Inter', -apple-system, sans-serif` | Headlines, navigation, UI labels |
| `font-body` | `'Inter', -apple-system, sans-serif` | Body text, descriptions |
| `font-mono` | `'JetBrains Mono', 'Fira Code', monospace` | Prices, numbers, stock symbols, metrics |

**Rationale:** Inter for clean UI/UX readability, JetBrains Mono for terminal-like number precision (common in financial platforms).

#### Type Scale (Desktop)

| Token Name | Size | Weight | Line Height | Letter Spacing | Usage |
|------------|------|--------|-------------|----------------|-------|
| `text-hero` | 48px | 700 | 1.1 | -0.02em | Page title, major headlines |
| `text-h1` | 36px | 600 | 1.2 | -0.01em | Section headers |
| `text-h2` | 24px | 600 | 1.3 | 0 | Card titles, subsection headers |
| `text-h3` | 20px | 600 | 1.3 | 0 | Table headers, labels |
| `text-body-lg` | 18px | 400 | 1.6 | 0 | Intro paragraphs, descriptions |
| `text-body` | 16px | 400 | 1.5 | 0 | Standard UI text |
| `text-small` | 14px | 400 | 1.5 | 0.01em | Captions, timestamps |
| `text-price` | 32px | 600 | 1.2 | -0.01em | Large price displays |
| `text-metric` | 20px | 500 | 1.3 | 0 | Financial metrics (P/E, P/B) |

#### Responsive Type Scale (Mobile)

| Token | Desktop | Mobile |
|-------|---------|--------|
| `text-hero` | 48px | 32px |
| `text-h1` | 36px | 24px |
| `text-price` | 32px | 24px |
| Body/Small | Same | Same |

### 2.3 Spacing (8pt Grid)

| Token Name | Value | Usage |
|------------|-------|-------|
| `space-xs` | 4px | Icon padding, tight inline spacing |
| `space-sm` | 8px | Button padding vertical, inline gaps |
| `space-md` | 16px | Element gaps, card internal spacing |
| `space-lg` | 24px | Card padding (compact), table cell padding |
| `space-xl` | 32px | Card padding (standard), section margins |
| `space-2xl` | 48px | Large section spacing, hero padding |
| `space-3xl` | 64px | Major section gaps, page margins |
| `space-4xl` | 96px | Hero sections, visual breathing room |

### 2.4 Border Radius

| Token Name | Value | Usage |
|------------|-------|-------|
| `radius-sm` | 8px | Buttons, small badges, tags |
| `radius-md` | 12px | Cards, inputs, dropdowns |
| `radius-lg` | 16px | Modals, large panels |
| `radius-full` | 9999px | Pills, rounded buttons, status indicators |

### 2.5 Shadows & Glows

| Token Name | Value | Usage |
|------------|-------|-------|
| `shadow-card` | `0 0 0 1px rgba(255,255,255,0.06), 0 4px 12px rgba(0,0,0,0.5)` | Default card elevation |
| `shadow-card-hover` | `0 0 0 1px rgba(255,255,255,0.12), 0 8px 24px rgba(0,0,0,0.6)` | Card hover state |
| `shadow-modal` | `0 0 0 1px rgba(255,255,255,0.1), 0 12px 48px rgba(0,0,0,0.8)` | Modal/dropdown elevation |
| `glow-primary` | `0 0 20px rgba(59,130,246,0.5), 0 0 40px rgba(59,130,246,0.3)` | Primary button hover |
| `glow-success` | `0 0 16px rgba(16,185,129,0.4)` | Positive value flash |
| `glow-danger` | `0 0 16px rgba(239,68,68,0.4)` | Negative value flash |

### 2.6 Animation

| Token Name | Value | Usage |
|------------|-------|-------|
| `duration-fast` | 150ms | Button hover, icon changes |
| `duration-normal` | 250ms | Card elevation, transitions |
| `duration-slow` | 400ms | Modals, panels |
| `duration-ticker` | 30s | Scrolling ticker animation |
| `easing-default` | ease-out | Standard transitions |
| `easing-sharp` | cubic-bezier(0.4,0,0.2,1) | Snappy interactions |

---

## 3. Component Specifications

### 3.1 Navigation Bar

**Structure:**
```
Fixed top bar (64px height)
├── Logo/Brand (left, 180px width)
├── Market Status Badge (live indicator)
├── Global Search (center-left, 320px width)
├── Spacer (flex-grow)
├── Theme Toggle (icon button)
└── User Menu (right, dropdown trigger)
```

**Tokens:**
- Background: `bg-pure-black` with `border-bottom: border-subtle`
- Height: 64px
- Padding: `space-md` (16px) horizontal
- Logo text: `text-h3` (20px, 600 weight) in `text-primary`
- Search input: `bg-surface-dark`, `radius-md`, `text-body`
- Market status: `radius-full` pill, `accent-success` (open) or `text-tertiary` (closed)

**States:**
- Default: Sticky/fixed position
- Scroll: Add subtle `shadow-card` for depth
- Search focus: `border-accent` on input
- Dropdown open: `bg-surface-modal` overlay with `shadow-modal`

**Responsive:**
- Mobile: Collapse search to icon, show hamburger menu for user options
- Logo shrinks to icon-only (<640px)

### 3.2 Market Dashboard Cards (Stat Cards)

**Structure:**
```
Grid of 4 stat cards (responsive: 4 cols → 2 cols → 1 col)
Each card:
├── Icon (24px, accent color)
├── Label (text-small, text-secondary)
├── Value (text-price or text-h1, text-primary)
└── Change indicator (text-small, colored by positive/negative)
```

**Tokens:**
- Background: `bg-surface-dark`
- Padding: `space-xl` (32px)
- Radius: `radius-md` (12px)
- Border: `border-subtle`
- Gap between cards: `space-lg` (24px)

**States:**
- Default: Subtle border
- Hover: Background → `bg-surface-hover`, border → `border-moderate`
- Live update: Brief `glow-success` or `glow-danger` flash on value change (250ms)

**Special Treatment:**
- Top Gainer card: Left border `3px solid accent-success`
- Top Loser card: Left border `3px solid accent-danger`

**Numbers:**
- Use `font-mono` for prices and percentages
- Positive change: `accent-success` with ↑ symbol
- Negative change: `accent-danger` with ↓ symbol

### 3.3 Real-Time Ticker (Scrolling)

**Structure:**
```
Horizontal scrolling strip (40px height)
├── Company 1: [SYMBOL] [PRICE PLN] [±%]
├── Company 2: [SYMBOL] [PRICE PLN] [±%]
├── ... (repeating infinite loop)
```

**Tokens:**
- Background: `bg-surface-dark`
- Height: 40px
- Padding: `space-sm` (8px) vertical
- Border: Top & bottom `border-subtle`
- Text: `font-mono`, `text-small` (14px)
- Symbol: `text-primary`, bold
- Price: `text-secondary`
- Change: `accent-success` or `accent-danger`

**Animation:**
- Continuous scroll: `translateX` from 0% to -50% over `duration-ticker` (30s)
- Easing: linear (constant speed)
- Duplicate content for seamless loop
- Pause on hover (optional UX enhancement)

**Interaction:**
- Click on ticker item → Open company detail modal
- Hover: Slight brightness increase on hovered company

### 3.4 Stock Opportunity Cards

**Structure:**
```
Grid of 3-4 cards (responsive: 4 → 2 → 1)
Each card:
├── Company symbol badge (top-left)
├── Performance indicator (large ±% with icon)
├── Company name (text-h3)
├── Current price (text-price, font-mono)
├── Metric row: P/E | P/B
├── Mini line chart (40px height, sparkline)
└── Action buttons (Analyze, Alert)
```

**Tokens:**
- Background: `bg-surface-dark`
- Padding: `space-xl` (32px)
- Radius: `radius-md` (12px)
- Border: `border-subtle`
- Gap: `space-lg` (24px)
- Symbol badge: `bg-accent-primary`, `radius-sm`, `text-inverse`

**States:**
- Hover: Lift effect (`translateY(-4px)`), `shadow-card-hover`, `bg-surface-hover`
- Click: Scale down slightly (0.98) for 100ms, then open detail modal

**Chart Specification:**
- Type: Sparkline (area chart)
- Height: 40px
- Gradient fill: `chart-gain` or `chart-loss` with 50% opacity
- Line: 2px stroke, accent color
- No axes or labels (pure visual trend indicator)

**Visual Hierarchy:**
- Performance % is largest element (text-price, 32px)
- Price in `font-mono` for precision
- Metrics (P/E, P/B) in `text-metric` (20px)

### 3.5 Company Data Table

**Structure:**
```
Professional table with fixed header
Columns: Symbol | Company | Price (PLN) | Change | P/E | P/B | Score | Actions
Rows: Zebra striping, hover states, sortable columns
```

**Tokens:**
- Background: `bg-near-black` (table container)
- Header row: `bg-surface-dark`, `text-h3` (20px, 600 weight)
- Odd rows: `bg-surface-dark`
- Even rows: Transparent (zebra striping)
- Cell padding: `space-md` (16px) vertical, `space-lg` (24px) horizontal
- Border: `border-subtle` between cells
- Radius: `radius-md` on table container

**States:**
- Header hover: `text-primary` + sort icon appears
- Row hover: `bg-surface-hover`, slight `glow-primary` on left edge
- Active sort: Column header in `accent-primary` with arrow icon
- Selected row: Left border `3px solid accent-primary`

**Column Specifications:**
- **Symbol:** `font-mono`, `text-primary`, bold (600), 80px width
- **Company:** `text-body`, `text-primary`, 200px min-width (flexible)
- **Price (PLN):** `font-mono`, `text-price` (32px), right-aligned, 140px
- **Change:** `font-mono`, colored (`accent-success`/`accent-danger`), right-aligned, with ↑↓ arrow, 100px
- **P/E:** `font-mono`, `text-secondary`, right-aligned, 80px
- **P/B:** `font-mono`, `text-secondary`, right-aligned, 80px
- **Score:** Progress bar (0-100%), gradient from `accent-danger` to `accent-success`, 100px
- **Actions:** Icon buttons (View, Alert, Compare), 120px

**Sorting:**
- Click header to sort ascending/descending/default
- Visual indicator: ▲ (asc) or ▼ (desc) icon in header
- Default sort: Change % (descending, top gainers first)

**Responsive:**
- Desktop: Full 8-column table
- Tablet (768px): Hide P/B and Score columns
- Mobile (640px): Card-based layout (stack rows as cards)

### 3.6 Heat Map Visualization

**Structure:**
```
Grid of rectangles sized by market cap, colored by performance
Each cell:
├── Company symbol (centered)
├── Change % (centered below)
└── Background color intensity based on ±%
```

**Tokens:**
- Container: `bg-surface-dark`, `radius-md`, `space-xl` padding
- Cell radius: `radius-sm` (8px)
- Gap: 4px between cells
- Font: `font-mono`, `text-small` (14px) for symbol
- Change %: `text-small`, bold (600)

**Color Scale:**
- Strong positive (>10%): `#10B981` (full `accent-success`)
- Moderate positive (5-10%): `#10B981` at 60% opacity
- Slight positive (0-5%): `#10B981` at 30% opacity
- Neutral (0%): `bg-surface-hover`
- Slight negative (0 to -5%): `#EF4444` at 30% opacity
- Moderate negative (-5 to -10%): `#EF4444` at 60% opacity
- Strong negative (<-10%): `#EF4444` (full `accent-danger`)

**States:**
- Hover: Border `2px solid text-primary`, slight scale (1.05), tooltip with company name + price
- Click: Open company detail modal

**Size Logic:**
- Cell area proportional to market cap (largest company = largest cell)
- Algorithm: Square root of market cap for width/height to maintain readability

---

## 4. Layout & Responsive Strategy

### 4.1 Page Structure (SPA Layout)

**Reference:** `content-structure-plan.md` Section 3

**Visual Flow:**
```
[Navigation Bar - 64px fixed]
[Market Dashboard - 4 stat cards]
[Real-Time Ticker - 40px scrolling]
[Quick Profit Opportunities - 3-4 cards horizontal]
[Filter Bar - tabs + sort]
[Company Data Table OR Heat Map - toggle view]
[Footer - compact]
```

**Container:**
- Max-width: 1440px (financial platforms benefit from wider screens)
- Padding: `space-2xl` (48px) on desktop, `space-md` (16px) on mobile
- Background: `bg-near-black`

### 4.2 Section Spacing

| Section Transition | Gap (Desktop) | Gap (Mobile) |
|--------------------|---------------|--------------|
| Nav → Dashboard | 32px | 16px |
| Dashboard → Ticker | 24px | 16px |
| Ticker → Opportunities | 48px | 24px |
| Opportunities → Filter | 48px | 24px |
| Filter → Table | 16px | 12px |
| Table → Footer | 64px | 32px |

### 4.3 Grid Systems

**Market Dashboard (Stat Cards):**
- Desktop (≥1024px): 4 columns, `space-lg` (24px) gap
- Tablet (768-1023px): 2 columns, `space-lg` gap
- Mobile (<768px): 1 column, `space-md` (16px) gap

**Opportunity Cards:**
- Desktop: 4 columns (or 3 if limited opportunities)
- Tablet: 2 columns
- Mobile: 1 column

**Heat Map:**
- Flexbox grid with wrapping
- Min cell size: 80×80px (mobile), 120×120px (desktop)

### 4.4 Responsive Breakpoints

| Breakpoint | Min Width | Layout Changes |
|------------|-----------|----------------|
| `sm` | 640px | Stack cards, show hamburger menu |
| `md` | 768px | 2-column grids, hide some table columns |
| `lg` | 1024px | 4-column grids, full table |
| `xl` | 1280px | Wider containers (1280px max-width) |
| `2xl` | 1440px | Max content width (1440px) |

### 4.5 Mobile Adaptations

**Navigation:**
- Logo → Icon-only
- Search → Icon (expands on click)
- Menu → Hamburger drawer

**Dashboard Cards:**
- Stack vertically with `space-md` gaps
- Reduce padding to `space-lg` (24px)

**Table → Card List:**
- Each row becomes a card
- Symbol + Company at top
- Price + Change prominent (large size)
- Metrics in 2-column grid below
- Actions at bottom

**Ticker:**
- Maintain horizontal scroll
- Reduce text size to 12px for fit

---

## 5. Interaction & Animation

### 5.1 Micro-Animations

**Price Updates (Real-Time):**
- When price changes: Flash background `glow-success` (increase) or `glow-danger` (decrease) for 250ms
- Number count-up/down animation over 300ms (not instant jump)
- Easing: `cubic-bezier(0.4, 0.0, 0.2, 1)` for sharp snap

**Card Hover:**
- Transform: `translateY(-4px)` over 250ms `ease-out`
- Shadow: Transition from `shadow-card` to `shadow-card-hover`
- Background: Subtle lightening (`bg-surface-hover`)

**Button States:**
- Hover: Scale(1.02), glow effect (`glow-primary`), 150ms
- Active: Scale(0.98), brightness(90%), 100ms
- Focus: 2px `accent-primary` outline with 4px offset

**Ticker Scroll:**
- Linear infinite animation, no easing
- Pause on hover for usability
- Resume after 2s hover delay

### 5.2 Loading States

**Skeleton Screens:**
- Background: `bg-surface-dark`
- Shimmer: Linear gradient animation from left to right
- Shimmer colors: `rgba(255,255,255,0.0)` → `rgba(255,255,255,0.05)` → `rgba(255,255,255,0.0)`
- Duration: 1.5s, infinite loop

**Spinner (Modal/Button Loading):**
- Circular spinner with `accent-primary` color
- Size: 24px (inline), 48px (full-page)
- Animation: 360° rotation over 800ms, linear easing

**Progressive Enhancement:**
- Show skeletons immediately on page load
- Replace with real data smoothly (fade-in over 200ms)

### 5.3 Transitions

**Modal Open/Close:**
- Backdrop: Fade in `rgba(0,0,0,0.8)` over 250ms
- Content: Scale(0.95) → Scale(1.0) + fade-in over 300ms `ease-out`
- Close: Reverse animation, slightly faster (200ms)

**Tab Switching (Filters):**
- Active tab indicator: Slide `translateX` animation over 250ms
- Content: Cross-fade (old fades out while new fades in) over 200ms

**Table Sort:**
- Rows: Stagger fade (each row 30ms delay) for cascading effect
- Total duration: ≤500ms for perceived speed

### 5.4 Performance Rules

**CRITICAL - Animate Only:**
- ✅ `transform` (translateX, translateY, scale, rotate)
- ✅ `opacity`
- ❌ NEVER: width, height, margin, padding, left, top (causes layout reflow)

**Reduced Motion:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 5.5 Interaction Patterns

**Company Selection Flow:**
1. Click company (table row, card, heat map cell, ticker)
2. Modal slides up with scale animation (300ms)
3. Load company details with skeleton → real data fade-in
4. Chart animates drawing from left to right (800ms, one-time)

**Filter Application:**
1. Click filter tab
2. Active indicator slides to new position (250ms)
3. Table rows fade out (150ms)
4. New filtered rows fade in staggered (200ms, 30ms stagger)

**Real-Time Data:**
- WebSocket connection (when backend ready)
- On price change: Flash animation on affected cells/cards
- Update frequency: 1-5 seconds (configurable)
- Smooth number transitions (not jarring jumps)

---

## 6. Polish Market Specific Details

### 6.1 Currency Formatting

**PLN Display:**
- Format: `XXX,XX PLN` (comma as decimal separator, space before currency)
- Examples: `616,37 PLN`, `1 234,56 PLN`, `388,50 PLN`
- Large numbers: Use thin space as thousands separator (U+2009)
- Precision: Always 2 decimal places for prices

**Number Formatting Function:**
```
Input: 1234.56
Output: "1 234,56 PLN"
```

### 6.2 Market Status Indicator

**Trading Hours (Warsaw Stock Exchange):**
- Open: Monday-Friday, 9:00-17:00 CET
- Pre-market: 8:30-9:00 CET (auction phase)
- After-hours: 17:00-17:10 CET (closing auction)

**Status Display:**
- **Market Open:** Green pill badge with pulsing animation, "Rynek otwarty" (Polish) or "Market Open"
- **Market Closed:** Gray badge, "Rynek zamknięty" or "Market Closed"
- **Pre-market:** Amber badge, "Premarketowa" or "Pre-market"

### 6.3 Polish Character Support

**Ensure UTF-8 encoding for:**
- ł (LATIN SMALL LETTER L WITH STROKE)
- ą, ę, ć, ń, ó, ś, ź, ż

**Company Names:**
- PKNORLEN (PKN ORLEN SA)
- Erbud SA
- Shoper
- Kogeneracja SA
- Selena FM SA
- GreenX Metals

**Fonts:** Inter and JetBrains Mono both support full Latin Extended-A character set

### 6.4 Localization Options

**Bilingual Support (Future):**
- Toggle between Polish (pl-PL) and English (en-US)
- Date formats: DD.MM.YYYY (Polish) vs. MM/DD/YYYY (US)
- Number formats: Comma vs. period decimal separator
- Store preference in localStorage

---

## Quality Checklist

### Style Guide Compliance ✅
- Pure black (`#000000`) and near-black (`#0A0E27`) backgrounds
- Vibrant accents (80-100% saturation) for gains/losses
- Surface elevation via lightness, not shadows (with accent glows)
- High contrast text ≥7:1 (AAA compliant)
- Font weights: 400-500 for body on dark (avoid halation)
- Monospace fonts for financial precision

### Premium Financial Platform ✅
- Real-time animated ticker
- Color-coded data (green up, red down)
- Dense information architecture
- Professional table layouts
- Interactive charts and heat maps
- Generous spacing despite density (32-48px card padding)

### Performance ✅
- Animate only `transform` and `opacity`
- GPU-accelerated transitions
- Skeleton loading states
- Progressive enhancement
- Reduced motion support

### Polish Market Context ✅
- PLN currency formatting with comma decimal
- WIG80 index focus
- Market hours awareness
- Polish company names with proper characters
- Professional trader aesthetic

---

**Design Specification Complete**
**Word Count:** ~2,950 words
**Version:** 1.0 - Dark Mode First Financial Pro
**Next Steps:** Implement design tokens in CSS/Tailwind, build components per specifications
