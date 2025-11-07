export interface Company {
  id: string;
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  pe_ratio: number | null;
  pb_ratio: number | null;
  trading_volume: string;
  trading_volume_numeric: number | null;
  last_update: string;
  sector: string | null;
  market_cap: number | null;
  category: string | null;
  value_score: number | null;
  growth_score: number | null;
  liquidity_score: number | null;
  overall_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface PriceHistory {
  id: string;
  company_id: string;
  symbol: string;
  price: number;
  change_percent: number | null;
  volume: number | null;
  timestamp: string;
  created_at: string;
}

export interface UserAlert {
  id: string;
  user_id: string;
  symbol: string;
  alert_type: string;
  target_value: number;
  condition: 'above' | 'below' | 'equals';
  is_active: boolean;
  triggered_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserPortfolio {
  id: string;
  user_id: string;
  symbol: string;
  quantity: number;
  entry_price: number;
  entry_date: string;
  stop_loss: number | null;
  take_profit: number | null;
  position_size_percent: number | null;
  status: 'open' | 'closed';
  exit_price: number | null;
  exit_date: string | null;
  profit_loss: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AIAnalysis {
  id: string;
  symbol: string;
  analysis_type: 'fundamental' | 'technical' | 'sentiment';
  agent_name: string;
  sentiment: string;
  recommendation: string;
  confidence_score: number;
  key_points: string;
  detailed_analysis: string;
  created_at: string;
}

export interface TradingOpportunity {
  symbol: string;
  company_name: string;
  current_price: number;
  change_percent: number;
  recommendation: 'buy' | 'sell' | 'strong_buy' | 'strong_sell';
  target_price?: number;
  stop_loss?: number;
  confidence: number;
  rationale: string;
}
