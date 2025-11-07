/**
 * Historical price data generator and technical indicators
 * VERSION 2.0: Supports both real data (Stooq.pl) and simulated fallback
 * 
 * CONFIGURATION:
 * - Set USE_REAL_DATA = true to attempt fetching from Stooq.pl
 * - Set USE_REAL_DATA = false to use simulated data only
 * 
 * DATA SOURCES:
 * 1. Stooq.pl (Primary): https://stooq.com/q/d/l/?s=[TICKER].pl&i=d
 * 2. Fallback: Algorithmic simulation based on current price
 */

// ==================== CONFIGURATION ====================
const USE_REAL_DATA = true; // Toggle real data fetching
const STOOQ_BASE_URL = 'https://stooq.com/q/d/l/';
const CACHE_DURATION_MS = 24 * 60 * 60 * 1000; // 24 hours

// ==================== INTERFACES ====================

interface CandlestickData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TechnicalIndicators {
  sma20: number[];
  sma50: number[];
  ema12: number[];
  ema26: number[];
  macd: number[];
  signal: number[];
  histogram: number[];
  rsi: number[];
  bollingerUpper: number[];
  bollingerMiddle: number[];
  bollingerLower: number[];
  supportLevels: number[];
  resistanceLevels: number[];
}

interface DataSourceInfo {
  source: 'stooq.pl' | 'yahoo-finance' | 'simulated';
  dataPoints: number;
  fetchedAt: number;
}

// ==================== CACHING ====================

function getCachedData(symbol: string): { data: CandlestickData[], sourceInfo: DataSourceInfo } | null {
  if (typeof localStorage === 'undefined') return null;
  
  try {
    const cached = localStorage.getItem(`historical_${symbol.toUpperCase()}`);
    if (!cached) return null;
    
    const parsed = JSON.parse(cached);
    const age = Date.now() - parsed.sourceInfo.fetchedAt;
    
    if (age > CACHE_DURATION_MS) {
      localStorage.removeItem(`historical_${symbol.toUpperCase()}`);
      return null;
    }
    
    return { data: parsed.data, sourceInfo: parsed.sourceInfo };
  } catch (error) {
    console.error('Cache read error:', error);
    return null;
  }
}

function cacheData(symbol: string, data: CandlestickData[], sourceInfo: DataSourceInfo): void {
  if (typeof localStorage === 'undefined') return;
  
  try {
    localStorage.setItem(`historical_${symbol.toUpperCase()}`, JSON.stringify({
      data,
      sourceInfo: {
        ...sourceInfo,
        fetchedAt: Date.now()
      }
    }));
  } catch (error) {
    console.error('Cache write error:', error);
  }
}

// ==================== REAL DATA FETCHING ====================

/**
 * Fetch real historical data from Stooq.pl
 * URL Pattern: https://stooq.com/q/d/l/?s=[TICKER].pl&i=d
 * CSV Format: Date,Open,High,Low,Close,Volume
 */
async function fetchStooqData(symbol: string): Promise<CandlestickData[]> {
  try {
    const ticker = symbol.toLowerCase();
    const url = `${STOOQ_BASE_URL}?s=${ticker}.pl&i=d`;
    
    console.log(`📡 Fetching from Stooq.pl: ${symbol.toUpperCase()}`);
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/csv'
      },
      mode: 'cors'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const csvText = await response.text();
    const lines = csvText.trim().split('\n');
    
    if (lines.length < 2) {
      throw new Error('Empty or invalid CSV response');
    }
    
    // Skip header row
    const dataLines = lines.slice(1);
    const historicalData: CandlestickData[] = [];
    
    for (const line of dataLines) {
      const [date, open, high, low, close, volume] = line.split(',');
      
      // Validate data
      if (!date || !open || !high || !low || !close) continue;
      
      const parsedOpen = parseFloat(open);
      const parsedHigh = parseFloat(high);
      const parsedLow = parseFloat(low);
      const parsedClose = parseFloat(close);
      const parsedVolume = volume ? parseFloat(volume) : 0;
      
      // Skip invalid rows
      if (isNaN(parsedOpen) || isNaN(parsedHigh) || isNaN(parsedLow) || isNaN(parsedClose)) {
        continue;
      }
      
      historicalData.push({
        time: date,
        open: parsedOpen,
        high: parsedHigh,
        low: parsedLow,
        close: parsedClose,
        volume: parsedVolume
      });
    }
    
    if (historicalData.length === 0) {
      throw new Error('No valid data points parsed');
    }
    
    console.log(`✅ Stooq.pl: Loaded ${historicalData.length} days for ${symbol.toUpperCase()}`);
    return historicalData;
    
  } catch (error) {
    console.error(`❌ Stooq.pl fetch failed for ${symbol}:`, error);
    return [];
  }
}

/**
 * Alternative: Fetch from Yahoo Finance
 * Used as backup if Stooq.pl fails
 */
async function fetchYahooFinanceData(symbol: string): Promise<CandlestickData[]> {
  try {
    const ticker = `${symbol.toUpperCase()}.WA`; // Warsaw Stock Exchange suffix
    const endDate = Math.floor(Date.now() / 1000);
    const startDate = endDate - (365 * 24 * 60 * 60); // 1 year ago
    
    const url = `https://query1.finance.yahoo.com/v7/finance/download/${ticker}?period1=${startDate}&period2=${endDate}&interval=1d&events=history`;
    
    console.log(`📡 Fetching from Yahoo Finance: ${symbol.toUpperCase()}`);
    
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const csvText = await response.text();
    const lines = csvText.trim().split('\n').slice(1); // Skip header
    
    const historicalData: CandlestickData[] = [];
    
    for (const line of lines) {
      const [date, open, high, low, close, , volume] = line.split(',');
      
      if (date && open !== 'null' && high !== 'null') {
        historicalData.push({
          time: date,
          open: parseFloat(open),
          high: parseFloat(high),
          low: parseFloat(low),
          close: parseFloat(close),
          volume: volume ? parseFloat(volume) : 0
        });
      }
    }
    
    console.log(`✅ Yahoo Finance: Loaded ${historicalData.length} days for ${symbol.toUpperCase()}`);
    return historicalData;
    
  } catch (error) {
    console.error(`❌ Yahoo Finance fetch failed for ${symbol}:`, error);
    return [];
  }
}

// ==================== SIMULATED DATA GENERATION ====================

/**
 * Generate realistic historical price data (fallback when real data unavailable)
 */
function generateSimulatedData(
  currentPrice: number,
  changePercent: number,
  symbol: string,
  days: number = 365
): CandlestickData[] {
  const data: CandlestickData[] = [];
  const today = new Date();
  
  // Calculate starting price based on current change
  const dailyChange = changePercent / 100;
  let price = currentPrice / (1 + dailyChange);
  
  // Add some randomness but maintain trend
  const trendStrength = Math.abs(changePercent) / 100;
  const volatility = 0.02 + (trendStrength * 0.01); // 2-3% daily volatility
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    // Skip weekends
    if (date.getDay() === 0 || date.getDay() === 6) continue;
    
    // Calculate daily movement with trend bias
    const trendBias = changePercent > 0 ? 0.002 : -0.002; // Slight trend bias
    const randomMove = (Math.random() - 0.5) * volatility;
    const movement = trendBias + randomMove;
    
    const open = price;
    const high = price * (1 + Math.abs(movement) * 1.5);
    const low = price * (1 - Math.abs(movement) * 1.5);
    const close = price * (1 + movement);
    
    // Volume varies with price movement
    const baseVolume = 100000 + Math.random() * 500000;
    const volume = baseVolume * (1 + Math.abs(movement) * 10);
    
    data.push({
      time: date.toISOString().split('T')[0],
      open: Math.max(0.01, open),
      high: Math.max(0.01, high),
      low: Math.max(0.01, low),
      close: Math.max(0.01, close),
      volume: Math.floor(volume)
    });
    
    price = close;
  }
  
  // Adjust final price to match current price
  const lastCandle = data[data.length - 1];
  if (lastCandle) {
    const adjustment = currentPrice / lastCandle.close;
    data.forEach(candle => {
      candle.open *= adjustment;
      candle.high *= adjustment;
      candle.low *= adjustment;
      candle.close *= adjustment;
    });
  }
  
  return data;
}

// ==================== MAIN DATA GENERATION ====================

/**
 * Generate historical data with intelligent fallback
 * Tries real data sources first, falls back to simulation
 */
export async function generateHistoricalData(
  currentPrice: number,
  changePercent: number,
  symbol: string,
  days: number = 365
): Promise<{ data: CandlestickData[], sourceInfo: DataSourceInfo }> {
  // Check cache first
  const cached = getCachedData(symbol);
  if (cached) {
    console.log(`💾 Using cached data for ${symbol.toUpperCase()} (${cached.sourceInfo.source})`);
    return cached;
  }
  
  let historicalData: CandlestickData[] = [];
  let sourceInfo: DataSourceInfo = {
    source: 'simulated',
    dataPoints: 0,
    fetchedAt: Date.now()
  };
  
  // Try to fetch real data if enabled
  if (USE_REAL_DATA) {
    // Try Stooq.pl first (best for Polish stocks)
    historicalData = await fetchStooqData(symbol);
    
    if (historicalData.length > 0) {
      sourceInfo = {
        source: 'stooq.pl',
        dataPoints: historicalData.length,
        fetchedAt: Date.now()
      };
    } else {
      // Try Yahoo Finance as backup
      historicalData = await fetchYahooFinanceData(symbol);
      
      if (historicalData.length > 0) {
        sourceInfo = {
          source: 'yahoo-finance',
          dataPoints: historicalData.length,
          fetchedAt: Date.now()
        };
      }
    }
  }
  
  // Fallback to simulated data if real data unavailable
  if (historicalData.length === 0) {
    console.warn(`⚠️  Using simulated data for ${symbol.toUpperCase()}`);
    historicalData = generateSimulatedData(currentPrice, changePercent, symbol, days);
    sourceInfo = {
      source: 'simulated',
      dataPoints: historicalData.length,
      fetchedAt: Date.now()
    };
  }
  
  // Cache the result
  cacheData(symbol, historicalData, sourceInfo);
  
  return { data: historicalData, sourceInfo };
}

// ==================== TECHNICAL INDICATORS ====================

/**
 * Calculate Simple Moving Average
 */
function calculateSMA(prices: number[], period: number): number[] {
  const sma: number[] = [];
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      sma.push(NaN);
      continue;
    }
    const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
    sma.push(sum / period);
  }
  return sma;
}

/**
 * Calculate Exponential Moving Average
 */
function calculateEMA(prices: number[], period: number): number[] {
  const ema: number[] = [];
  const multiplier = 2 / (period + 1);
  
  // First EMA is SMA
  let sum = 0;
  for (let i = 0; i < period; i++) {
    if (i < prices.length) {
      sum += prices[i];
    }
  }
  ema.push(sum / period);
  
  // Calculate remaining EMAs
  for (let i = period; i < prices.length; i++) {
    const value = (prices[i] - ema[i - period]) * multiplier + ema[i - period];
    ema.push(value);
  }
  
  // Pad beginning with NaN
  const result = new Array(period - 1).fill(NaN).concat(ema);
  return result;
}

/**
 * Calculate RSI (Relative Strength Index)
 */
function calculateRSI(prices: number[], period: number = 14): number[] {
  const rsi: number[] = new Array(period).fill(NaN);
  
  const changes: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    changes.push(prices[i] - prices[i - 1]);
  }
  
  let avgGain = 0;
  let avgLoss = 0;
  
  // Initial average
  for (let i = 0; i < period; i++) {
    if (changes[i] > 0) avgGain += changes[i];
    else avgLoss += Math.abs(changes[i]);
  }
  avgGain /= period;
  avgLoss /= period;
  
  let rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
  rsi.push(100 - (100 / (1 + rs)));
  
  // Calculate remaining RSI values
  for (let i = period; i < changes.length; i++) {
    const gain = changes[i] > 0 ? changes[i] : 0;
    const loss = changes[i] < 0 ? Math.abs(changes[i]) : 0;
    
    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;
    
    rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    rsi.push(100 - (100 / (1 + rs)));
  }
  
  return rsi;
}

/**
 * Calculate MACD (Moving Average Convergence Divergence)
 */
function calculateMACD(prices: number[]): { macd: number[], signal: number[], histogram: number[] } {
  const ema12 = calculateEMA(prices, 12);
  const ema26 = calculateEMA(prices, 26);
  
  const macd: number[] = [];
  for (let i = 0; i < prices.length; i++) {
    if (isNaN(ema12[i]) || isNaN(ema26[i])) {
      macd.push(NaN);
    } else {
      macd.push(ema12[i] - ema26[i]);
    }
  }
  
  // Signal line is 9-period EMA of MACD
  const validMACD = macd.filter(v => !isNaN(v));
  const signalEMA = calculateEMA(validMACD, 9);
  
  // Pad signal to match MACD length
  const signal = new Array(macd.length - validMACD.length + 8).fill(NaN).concat(signalEMA);
  
  // Histogram is MACD - Signal
  const histogram: number[] = [];
  for (let i = 0; i < macd.length; i++) {
    if (isNaN(macd[i]) || isNaN(signal[i])) {
      histogram.push(NaN);
    } else {
      histogram.push(macd[i] - signal[i]);
    }
  }
  
  return { macd, signal, histogram };
}

/**
 * Calculate Bollinger Bands
 */
function calculateBollingerBands(prices: number[], period: number = 20, stdDev: number = 2): {
  upper: number[], middle: number[], lower: number[]
} {
  const middle = calculateSMA(prices, period);
  const upper: number[] = [];
  const lower: number[] = [];
  
  for (let i = 0; i < prices.length; i++) {
    if (i < period - 1) {
      upper.push(NaN);
      lower.push(NaN);
      continue;
    }
    
    const slice = prices.slice(i - period + 1, i + 1);
    const mean = middle[i];
    const variance = slice.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / period;
    const sd = Math.sqrt(variance);
    
    upper.push(mean + (stdDev * sd));
    lower.push(mean - (stdDev * sd));
  }
  
  return { upper, middle, lower };
}

/**
 * Detect support and resistance levels
 */
function detectSupportResistance(data: CandlestickData[]): { support: number[], resistance: number[] } {
  const prices = data.map(d => d.close);
  const support: number[] = [];
  const resistance: number[] = [];
  
  // Find local minima and maxima
  for (let i = 2; i < prices.length - 2; i++) {
    const current = prices[i];
    const prev2 = prices[i - 2];
    const prev1 = prices[i - 1];
    const next1 = prices[i + 1];
    const next2 = prices[i + 2];
    
    // Local minimum (support)
    if (current < prev2 && current < prev1 && current < next1 && current < next2) {
      if (support.length === 0 || Math.abs(current - support[support.length - 1]) / current > 0.02) {
        support.push(current);
      }
    }
    
    // Local maximum (resistance)
    if (current > prev2 && current > prev1 && current > next1 && current > next2) {
      if (resistance.length === 0 || Math.abs(current - resistance[resistance.length - 1]) / current > 0.02) {
        resistance.push(current);
      }
    }
  }
  
  // Keep only the 3 most significant levels
  support.sort((a, b) => b - a);
  resistance.sort((a, b) => a - b);
  
  return {
    support: support.slice(0, 3),
    resistance: resistance.slice(0, 3)
  };
}

/**
 * Calculate all technical indicators
 */
export function calculateTechnicalIndicators(data: CandlestickData[]): TechnicalIndicators {
  const closePrices = data.map(d => d.close);
  
  const sma20 = calculateSMA(closePrices, 20);
  const sma50 = calculateSMA(closePrices, 50);
  const ema12 = calculateEMA(closePrices, 12);
  const ema26 = calculateEMA(closePrices, 26);
  
  const { macd, signal, histogram } = calculateMACD(closePrices);
  const rsi = calculateRSI(closePrices, 14);
  const { upper, middle, lower } = calculateBollingerBands(closePrices, 20, 2);
  const { support, resistance } = detectSupportResistance(data);
  
  return {
    sma20,
    sma50,
    ema12,
    ema26,
    macd,
    signal,
    histogram,
    rsi,
    bollingerUpper: upper,
    bollingerMiddle: middle,
    bollingerLower: lower,
    supportLevels: support,
    resistanceLevels: resistance
  };
}

/**
 * Filter data by timeframe
 */
export function filterByTimeframe(data: CandlestickData[], timeframe: '1D' | '1W' | '1M' | '3M' | '1Y'): CandlestickData[] {
  const today = new Date();
  const cutoffDate = new Date(today);
  
  switch (timeframe) {
    case '1D':
      cutoffDate.setDate(today.getDate() - 1);
      break;
    case '1W':
      cutoffDate.setDate(today.getDate() - 7);
      break;
    case '1M':
      cutoffDate.setMonth(today.getMonth() - 1);
      break;
    case '3M':
      cutoffDate.setMonth(today.getMonth() - 3);
      break;
    case '1Y':
      cutoffDate.setFullYear(today.getFullYear() - 1);
      break;
  }
  
  return data.filter(d => new Date(d.time) >= cutoffDate);
}

/**
 * Calculate price target based on technical analysis
 */
export function calculatePriceTarget(data: CandlestickData[], indicators: TechnicalIndicators): {
  target: number;
  confidence: 'high' | 'medium' | 'low';
  reasoning: string;
  reasoningPL: string;
} {
  const currentPrice = data[data.length - 1].close;
  const sma20Current = indicators.sma20[indicators.sma20.length - 1];
  const sma50Current = indicators.sma50[indicators.sma50.length - 1];
  const rsiCurrent = indicators.rsi[indicators.rsi.length - 1];
  
  let target = currentPrice;
  let confidence: 'high' | 'medium' | 'low' = 'medium';
  let reasoning = '';
  let reasoningPL = '';
  
  // Bullish scenario
  if (currentPrice > sma20Current && currentPrice > sma50Current && rsiCurrent < 70) {
    const resistance = indicators.resistanceLevels[0] || currentPrice * 1.1;
    target = Math.min(resistance, currentPrice * 1.15);
    confidence = 'high';
    reasoning = 'Strong uptrend with room to grow';
    reasoningPL = 'Silny trend wzrostowy z przestrzenią do wzrostu';
  }
  // Bearish scenario
  else if (currentPrice < sma20Current && currentPrice < sma50Current && rsiCurrent > 30) {
    const support = indicators.supportLevels[0] || currentPrice * 0.9;
    target = Math.max(support, currentPrice * 0.85);
    confidence = 'high';
    reasoning = 'Downtrend likely to continue';
    reasoningPL = 'Trend spadkowy prawdopodobnie będzie kontynuowany';
  }
  // Neutral/consolidation
  else {
    target = sma20Current;
    confidence = 'low';
    reasoning = 'Consolidation phase - unclear direction';
    reasoningPL = 'Faza konsolidacji - niejasny kierunek';
  }
  
  return { target, confidence, reasoning, reasoningPL };
}

// ==================== EXPORTS ====================

export type { CandlestickData, TechnicalIndicators, DataSourceInfo };
