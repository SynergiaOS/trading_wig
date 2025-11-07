/**
 * Real-Time Data Service
 * Handles fetching live WIG80 data from various sources
 */

// Configuration
const DATA_SOURCE_CONFIG = {
  // Static JSON data source
  staticDataUrl: '/wig80_current_data.json',
  
  // Backend Python API - uses environment variable or defaults to localhost
  apiUrl: import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/data`
    : 'http://localhost:8000/data',
  
  // Refresh interval (milliseconds) - from env or default
  refreshInterval: import.meta.env.VITE_REFRESH_INTERVAL 
    ? parseInt(import.meta.env.VITE_REFRESH_INTERVAL, 10)
    : 30000, // 30 seconds default
};

export interface Company {
  company_name: string;
  symbol: string;
  current_price: number;
  change_percent: number;
  pe_ratio: number | null;
  pb_ratio: number | null;
  trading_volume: string;
  trading_volume_obrot?: string;
  last_update?: string;
  status?: string;
  score?: number;
}

export interface MarketData {
  metadata: {
    collection_date: string;
    data_source: string;
    index: string;
    currency: string;
    total_companies: number;
    successful_fetches?: number;
    market_status?: string;
    poland_time?: string;
    is_market_hours?: boolean;
    avg_change?: number;
  };
  companies: Company[];
}

/**
 * Fetch real-time data for specified index
 */
export async function fetchRealTimeData(index: 'WIG80' | 'WIG30' = 'WIG80'): Promise<MarketData> {
  try {
    // Try backend API first, fallback to static JSON
    try {
      return await fetchFromAPI(index);
    } catch (apiError) {
      console.warn('API fetch failed, using static JSON:', apiError);
      return await fetchFromStaticJSON(index);
    }
  } catch (error) {
    console.error('Error fetching real-time data:', error);
    // Fallback to static JSON on error
    return await fetchFromStaticJSON(index);
  }
}

/**
 * Fetch WIG30 data (top 30 companies)
 */
export async function fetchWIG30Data(): Promise<MarketData> {
  return fetchRealTimeData('WIG30');
}

/**
 * Fetch WIG80 data (all 88 companies)
 */
export async function fetchWIG80Data(): Promise<MarketData> {
  return fetchRealTimeData('WIG80');
}

/**
 * Fetch data from Backend Python API
 */
async function fetchFromAPI(index: 'WIG80' | 'WIG30' = 'WIG80'): Promise<MarketData> {
  const endpoint = index === 'WIG30' ? '/wig30' : '/data';
  const apiUrl = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}${endpoint}`
    : `http://localhost:8000${endpoint}`;
  
  const response = await fetch(apiUrl, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`API fetch failed: ${response.status}`);
  }

  return await response.json();
}

/**
 * Fetch data from static JSON file
 */
async function fetchFromStaticJSON(index: 'WIG80' | 'WIG30' = 'WIG80'): Promise<MarketData> {
  const response = await fetch(DATA_SOURCE_CONFIG.staticDataUrl);
  
  if (!response.ok) {
    throw new Error(`Static JSON fetch failed: ${response.status}`);
  }

  const data = await response.json();
  
  // If WIG30, filter to top 30 by volume
  if (index === 'WIG30') {
    const companies = [...data.companies];
    
    const getVolumeNum = (volStr: string): number => {
      try {
        const vol = volStr.replace(/[KM, ]/g, '');
        let num = parseFloat(vol);
        if (volStr.includes('M')) num *= 1000;
        return num;
      } catch {
        return 0;
      }
    };
    
    companies.sort((a, b) => getVolumeNum(b.trading_volume || '0') - getVolumeNum(a.trading_volume || '0'));
    const top30 = companies.slice(0, 30);
    
    return {
      ...data,
      metadata: {
        ...data.metadata,
        index: 'WIG30',
        total_companies: 30
      },
      companies: top30
    };
  }
  
  return data;
}

/**
 * Get current data source
 */
export function getDataSource(): string {
  const apiUrl = DATA_SOURCE_CONFIG.apiUrl.replace('/data', '');
  return `Backend Python API (${apiUrl})`;
}

export interface TechnicalPattern {
  pattern_name: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  strength: number;
  confidence: number;
  duration: string;
  key_levels: Record<string, number>;
  probability: number;
}

export interface CompanyWithPatterns extends Company {
  patterns?: TechnicalPattern[];
  analysis?: {
    value_score: number;
    growth_score: number;
    momentum_score: number;
    overall_score: number;
    recommendation: string;
    sentiment: string;
    risk_level: string;
    confidence: number;
  };
}

export interface PatternsData {
  timestamp: string;
  total_with_patterns: number;
  companies: CompanyWithPatterns[];
}

export async function fetchPatternsData(): Promise<PatternsData> {
  try {
    const analysisUrl = import.meta.env.VITE_ANALYSIS_API_URL 
      ? `${import.meta.env.VITE_ANALYSIS_API_URL}/api/analysis/patterns`
      : 'http://localhost:8001/api/analysis/patterns';
    
    const response = await fetch(analysisUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Patterns API fetch failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching patterns data:', error);
    return {
      timestamp: new Date().toISOString(),
      total_with_patterns: 0,
      companies: []
    };
  }
}

export { DATA_SOURCE_CONFIG };
