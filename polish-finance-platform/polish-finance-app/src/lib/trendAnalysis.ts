/**
 * Enhanced trend analysis and technical indicators for Polish financial platform
 */

/**
 * Calculate trend momentum based on change percentage
 */
export function getTrendMomentum(changePercent: number): {
  strength: 'strong' | 'moderate' | 'weak' | 'neutral';
  direction: 'upward' | 'downward' | 'sideways';
  label: string;
  labelPL: string;
  color: string;
} {
  const absChange = Math.abs(changePercent);
  
  if (changePercent >= 5) {
    return {
      strength: 'strong',
      direction: 'upward',
      label: 'Strong Upward',
      labelPL: 'Silny wzrost',
      color: 'text-accent-success'
    };
  } else if (changePercent >= 2) {
    return {
      strength: 'moderate',
      direction: 'upward',
      label: 'Bullish Momentum',
      labelPL: 'Ruch wzrostowy',
      color: 'text-accent-success'
    };
  } else if (changePercent > 0) {
    return {
      strength: 'weak',
      direction: 'upward',
      label: 'Slight Uptrend',
      labelPL: 'Lekki wzrost',
      color: 'text-accent-success'
    };
  } else if (changePercent <= -5) {
    return {
      strength: 'strong',
      direction: 'downward',
      label: 'Strong Downward',
      labelPL: 'Silny spadek',
      color: 'text-accent-danger'
    };
  } else if (changePercent <= -2) {
    return {
      strength: 'moderate',
      direction: 'downward',
      label: 'Bearish Pressure',
      labelPL: 'Ruch zjazdowy',
      color: 'text-accent-danger'
    };
  } else if (changePercent < 0) {
    return {
      strength: 'weak',
      direction: 'downward',
      label: 'Slight Downtrend',
      labelPL: 'Lekki spadek',
      color: 'text-accent-danger'
    };
  }
  
  return {
    strength: 'neutral',
    direction: 'sideways',
    label: 'Sideways',
    labelPL: 'Boczny trend',
    color: 'text-text-secondary'
  };
}

/**
 * Get trend description based on technical indicators
 */
export function getTrendDescription(company: any): {
  description: string;
  descriptionPL: string;
  category: string;
  categoryPL: string;
} {
  const change = company.change_percent;
  const pe = company.pe_ratio;
  const pb = company.pb_ratio;
  const volume = parseFloat(company.trading_volume?.replace(/[^\d.]/g, '') || '0');
  
  // Strong breakout
  if (change >= 10 && volume > 100000) {
    return {
      description: 'Breaking resistance with high volume - strong bullish signal',
      descriptionPL: 'Przełamanie oporu z wysokim wolumenem - silny sygnał wzrostowy',
      category: 'Breaking Resistance',
      categoryPL: 'Przełom cenowy'
    };
  }
  
  // Moderate uptrend with value
  if (change >= 5 && change < 10) {
    if (pe && pe < 15 && pb && pb < 2) {
      return {
        description: 'Strong upward momentum with attractive valuation',
        descriptionPL: 'Silny wzrost przy atrakcyjnej wycenie',
        category: 'Value Breakout',
        categoryPL: 'Wartościowy wzrost'
      };
    }
    return {
      description: 'Bullish momentum building - potential continuation',
      descriptionPL: 'Budujący się impet wzrostowy - potencjalna kontynuacja',
      category: 'Bullish Momentum',
      categoryPL: 'Impet wzrostowy'
    };
  }
  
  // Moderate uptrend
  if (change >= 2 && change < 5) {
    return {
      description: 'Positive trend with steady buying interest',
      descriptionPL: 'Pozytywny trend z stałym zainteresowaniem kupujących',
      category: 'Steady Uptrend',
      categoryPL: 'Stabilny wzrost'
    };
  }
  
  // Slight gain
  if (change > 0 && change < 2) {
    return {
      description: 'Minor gains - consolidation phase',
      descriptionPL: 'Niewielkie zyski - faza konsolidacji',
      category: 'Consolidating',
      categoryPL: 'Konsolidacja'
    };
  }
  
  // Strong decline
  if (change <= -10) {
    return {
      description: 'Heavy selling pressure - caution advised',
      descriptionPL: 'Silna presja sprzedaży - ostrożność zalecana',
      category: 'Strong Decline',
      categoryPL: 'Silny spadek'
    };
  }
  
  // Moderate decline
  if (change <= -5 && change > -10) {
    return {
      description: 'Bearish pressure increasing - watch support levels',
      descriptionPL: 'Rosnąca presja spadkowa - obserwować wsparcie',
      category: 'Bearish Pressure',
      categoryPL: 'Presja spadkowa'
    };
  }
  
  // Slight decline
  if (change < 0 && change > -5) {
    return {
      description: 'Minor pullback - potential buying opportunity',
      descriptionPL: 'Niewielka korekta - potencjalna okazja do zakupu',
      category: 'Slight Pullback',
      categoryPL: 'Lekka korekta'
    };
  }
  
  return {
    description: 'Neutral - awaiting direction',
    descriptionPL: 'Neutralny - oczekiwanie na kierunek',
    category: 'Neutral',
    categoryPL: 'Neutralny'
  };
}

/**
 * Calculate simplified RSI (Relative Strength Index)
 * Returns a value between 0-100
 */
export function calculateRSI(changePercent: number): number {
  // Simplified RSI based on current change
  // In real implementation, this would use historical data
  if (changePercent >= 10) return 85; // Overbought territory
  if (changePercent >= 5) return 70;
  if (changePercent >= 2) return 60;
  if (changePercent > 0) return 55;
  if (changePercent === 0) return 50;
  if (changePercent > -2) return 45;
  if (changePercent > -5) return 40;
  if (changePercent > -10) return 30;
  return 20; // Oversold territory
}

/**
 * Get RSI interpretation
 */
export function getRSIInterpretation(rsi: number): {
  label: string;
  labelPL: string;
  color: string;
  signal: string;
  signalPL: string;
} {
  if (rsi >= 70) {
    return {
      label: 'Overbought',
      labelPL: 'Wykupione',
      color: 'text-accent-warning',
      signal: 'Potential reversal',
      signalPL: 'Potencjalne odwrócenie'
    };
  } else if (rsi >= 60) {
    return {
      label: 'Strong',
      labelPL: 'Silne',
      color: 'text-accent-success',
      signal: 'Bullish strength',
      signalPL: 'Siła wzrostowa'
    };
  } else if (rsi >= 40) {
    return {
      label: 'Neutral',
      labelPL: 'Neutralne',
      color: 'text-text-secondary',
      signal: 'Balanced',
      signalPL: 'Zrównoważone'
    };
  } else if (rsi >= 30) {
    return {
      label: 'Weak',
      labelPL: 'Słabe',
      color: 'text-accent-danger',
      signal: 'Bearish pressure',
      signalPL: 'Presja spadkowa'
    };
  } else {
    return {
      label: 'Oversold',
      labelPL: 'Wyprzedane',
      color: 'text-accent-info',
      signal: 'Potential bounce',
      signalPL: 'Potencjalne odbicie'
    };
  }
}

/**
 * Calculate volume strength relative to average
 */
export function getVolumeStrength(volume: string): {
  strength: 'very-high' | 'high' | 'normal' | 'low';
  label: string;
  labelPL: string;
  color: string;
} {
  const numericVolume = parseFloat(volume.replace(/[^\d.]/g, '') || '0');
  
  if (numericVolume > 500000) {
    return {
      strength: 'very-high',
      label: 'Very High Volume',
      labelPL: 'Bardzo wysoki wolumen',
      color: 'text-accent-success'
    };
  } else if (numericVolume > 200000) {
    return {
      strength: 'high',
      label: 'High Volume',
      labelPL: 'Wysoki wolumen',
      color: 'text-accent-info'
    };
  } else if (numericVolume > 50000) {
    return {
      strength: 'normal',
      label: 'Normal Volume',
      labelPL: 'Normalny wolumen',
      color: 'text-text-secondary'
    };
  } else {
    return {
      strength: 'low',
      label: 'Low Volume',
      labelPL: 'Niski wolumen',
      color: 'text-text-tertiary'
    };
  }
}

/**
 * Get risk assessment based on volatility and valuation
 */
export function getRiskAssessment(company: any): {
  level: 'high' | 'medium' | 'low';
  label: string;
  labelPL: string;
  color: string;
  description: string;
  descriptionPL: string;
} {
  const change = Math.abs(company.change_percent);
  const pe = company.pe_ratio || 0;
  const pb = company.pb_ratio || 0;
  
  // High risk: high volatility or extreme valuations
  if (change > 10 || pe > 40 || pb > 8) {
    return {
      level: 'high',
      label: 'High Risk',
      labelPL: 'Wysokie ryzyko',
      color: 'text-accent-danger',
      description: 'High volatility or stretched valuations',
      descriptionPL: 'Wysoka zmienność lub napięte wyceny'
    };
  }
  
  // Medium risk: moderate volatility
  if (change > 5 || (pe > 20 && pe < 40)) {
    return {
      level: 'medium',
      label: 'Medium Risk',
      labelPL: 'Średnie ryzyko',
      color: 'text-accent-warning',
      description: 'Moderate volatility and valuations',
      descriptionPL: 'Umiarkowana zmienność i wyceny'
    };
  }
  
  // Low risk: stable with good valuations
  return {
    level: 'low',
    label: 'Low Risk',
    labelPL: 'Niskie ryzyko',
    color: 'text-accent-success',
    description: 'Stable performance with attractive valuations',
    descriptionPL: 'Stabilne zachowanie z atrakcyjnymi wycenami'
  };
}

/**
 * Simulate price fluctuation for real-time effect
 * In production, this would come from WebSocket/API
 */
export function simulatePriceFluctuation(currentPrice: number, changePercent: number): number {
  // Add small random fluctuation (-0.5% to +0.5%)
  const fluctuation = (Math.random() - 0.5) * 0.01;
  const baseChange = changePercent / 100;
  const totalChange = baseChange + fluctuation;
  
  return currentPrice * (1 + totalChange);
}

/**
 * Format last update timestamp
 */
export function formatLastUpdate(date: Date): {
  time: string;
  relative: string;
  relativePL: string;
} {
  const now = new Date();
  const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  let relative = '';
  let relativePL = '';
  
  if (diffSeconds < 60) {
    relative = `${diffSeconds}s ago`;
    relativePL = `${diffSeconds}s temu`;
  } else if (diffSeconds < 3600) {
    const minutes = Math.floor(diffSeconds / 60);
    relative = `${minutes}m ago`;
    relativePL = `${minutes}m temu`;
  } else {
    const hours = Math.floor(diffSeconds / 3600);
    relative = `${hours}h ago`;
    relativePL = `${hours}h temu`;
  }
  
  return {
    time: date.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    relative,
    relativePL
  };
}

/**
 * Get market countdown timer
 */
export function getMarketCountdown(): {
  message: string;
  messagePL: string;
  time: string;
} {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const timeInMinutes = hour * 60 + minute;
  
  // Market opens at 9:00 (540 minutes)
  if (timeInMinutes < 540) {
    const minutesToOpen = 540 - timeInMinutes;
    const hours = Math.floor(minutesToOpen / 60);
    const mins = minutesToOpen % 60;
    return {
      message: `Market opens in ${hours}h ${mins}m`,
      messagePL: `Rynek otwiera się za ${hours}h ${mins}m`,
      time: `${hours}:${mins.toString().padStart(2, '0')}`
    };
  }
  
  // Market closes at 17:00 (1020 minutes)
  if (timeInMinutes < 1020) {
    const minutesToClose = 1020 - timeInMinutes;
    const hours = Math.floor(minutesToClose / 60);
    const mins = minutesToClose % 60;
    return {
      message: `Market closes in ${hours}h ${mins}m`,
      messagePL: `Rynek zamyka się za ${hours}h ${mins}m`,
      time: `${hours}:${mins.toString().padStart(2, '0')}`
    };
  }
  
  // After market close
  return {
    message: 'Market closed',
    messagePL: 'Rynek zamknięty',
    time: '--:--'
  };
}
