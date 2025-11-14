/**
 * Real-Time Data Service
 * Handles fetching live WIG80 data from various sources
 */

// Configuration - PRODUCTION: API only, no static fallback
const DATA_SOURCE_CONFIG = {
  // Backend Python API - REQUIRED in production
  apiUrl: import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/data`
    : (import.meta.env.PROD 
        ? (() => { throw new Error('VITE_API_URL must be set in production'); })()
        : 'http://localhost:8000/data'),
  
  // Refresh interval (milliseconds) - from env or default
  refreshInterval: import.meta.env.VITE_REFRESH_INTERVAL 
    ? parseInt(import.meta.env.VITE_REFRESH_INTERVAL, 10)
    : 30000, // 30 seconds default
};

// Re-export types from unified types file
export type { Company, MarketData, TechnicalPattern, CompanyWithPatterns, PatternsData } from '../types/market';

/**
 * Fetch real-time data for specified index
 * PRODUCTION: Only uses API, no static fallback
 */
export async function fetchRealTimeData(index: 'WIG80' | 'WIG30' = 'WIG80'): Promise<MarketData> {
  const maxRetries = 3;
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const data = await fetchFromAPI(index);
      return data;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      console.warn(`API fetch attempt ${attempt}/${maxRetries} failed:`, lastError);
      
      // Wait before retry (exponential backoff)
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
      }
    }
  }

  // All retries failed - throw error instead of using static data
  throw new Error(`Failed to fetch data from API after ${maxRetries} attempts: ${lastError?.message || 'Unknown error'}`);
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
 * PRODUCTION: Uses API URL from environment variables
 */
async function fetchFromAPI(index: 'WIG80' | 'WIG30' = 'WIG80'): Promise<MarketData> {
  const endpoint = index === 'WIG30' ? '/wig30' : '/data';
  const apiUrl = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}${endpoint}`
    : (() => {
        // In production, API URL must be set
        if (import.meta.env.PROD) {
          throw new Error('VITE_API_URL environment variable is required in production');
        }
        // Development fallback
        return `http://localhost:8000${endpoint}`;
      })();
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API fetch failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // Validate response structure
    if (!data || !data.companies || !Array.isArray(data.companies)) {
      throw new Error('Invalid API response structure');
    }

    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('API request timeout');
    }
    throw error;
  }
}

// REMOVED: fetchFromStaticJSON - Production uses API only

/**
 * Get current data source
 */
export function getDataSource(): string {
  const apiUrl = DATA_SOURCE_CONFIG.apiUrl.replace('/data', '');
  return `Backend Python API (${apiUrl})`;
}

/**
 * Fetch patterns data from Analysis API
 * PRODUCTION: Only uses API, returns empty data on error (non-critical)
 */
export async function fetchPatternsData(): Promise<PatternsData> {
  const analysisUrl = import.meta.env.VITE_ANALYSIS_API_URL 
    ? `${import.meta.env.VITE_ANALYSIS_API_URL}/api/analysis/patterns`
    : (() => {
        if (import.meta.env.PROD) {
          // In production, return empty if not configured (non-critical feature)
          console.warn('VITE_ANALYSIS_API_URL not set, patterns feature disabled');
          return null;
        }
        return 'http://localhost:8001/api/analysis/patterns';
      })();

  if (!analysisUrl) {
    return {
      timestamp: new Date().toISOString(),
      total_with_patterns: 0,
      companies: []
    };
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout

    const response = await fetch(analysisUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Patterns API fetch failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // Validate response
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid patterns API response');
    }

    return {
      timestamp: data.timestamp || new Date().toISOString(),
      total_with_patterns: data.total_with_patterns || (data.companies?.length || 0),
      companies: data.companies || []
    };
  } catch (error) {
    console.error('Error fetching patterns data:', error);
    // Return empty data instead of throwing (patterns are non-critical)
    return {
      timestamp: new Date().toISOString(),
      total_with_patterns: 0,
      companies: []
    };
  }
}

export { DATA_SOURCE_CONFIG };
