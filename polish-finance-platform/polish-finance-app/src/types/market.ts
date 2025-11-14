/**
 * Unified Market Types
 * Single source of truth for market data types
 */

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

export interface TechnicalPattern {
  pattern_name: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  strength: number;
  confidence: number;
  duration: string;
  key_levels: Record<string, number>;
  probability: number;
}

export interface CompanyAnalysis {
  value_score: number;
  growth_score: number;
  momentum_score: number;
  overall_score: number;
  recommendation: string;
  sentiment: string;
  risk_level: string;
  confidence: number;
}

export interface CompanyWithPatterns extends Company {
  patterns?: TechnicalPattern[];
  analysis?: CompanyAnalysis;
}

export interface PatternsData {
  timestamp: string;
  total_with_patterns: number;
  companies: CompanyWithPatterns[];
}

export type MarketIndex = 'WIG80' | 'WIG30';
export type SortBy = 'change' | 'pe' | 'pb' | 'score';
export type SortOrder = 'asc' | 'desc';
export type ViewMode = 'table' | 'heatmap';
export type FilterCategory = 'all' | 'gainers' | 'losers' | 'value' | 'momentum';

