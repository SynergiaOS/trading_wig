/**
 * Format number as Polish PLN currency
 * Example: 1234.56 → "1 234,56 PLN"
 */
export function formatPLN(value: number): string {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  
  // Split into integer and decimal parts
  const [integerPart, decimalPart = '00'] = value.toFixed(2).split('.');
  
  // Add thin space (U+2009) as thousands separator
  const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, '\u2009');
  
  // Use comma as decimal separator (Polish format)
  return `${formattedInteger},${decimalPart} PLN`;
}

/**
 * Format percentage with + sign for positive values
 */
export function formatPercent(value: number): string {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

/**
 * Format large numbers with K/M/B suffixes
 */
export function formatLargeNumber(value: string | number): string {
  if (typeof value === 'string') {
    // Remove non-numeric characters except decimal point
    const numValue = parseFloat(value.replace(/[^\d.]/g, ''));
    if (isNaN(numValue)) return value;
    value = numValue;
  }
  
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
  return value.toFixed(2);
}

/**
 * Get current time in Poland (CET/CEST timezone)
 */
export function getPolandTime(): Date {
  // Get current time in UTC
  const now = new Date();
  
  // Check if DST is active (last Sunday of March to last Sunday of October)
  const isDST = isDaylightSavingTime(now);
  
  // Poland is UTC+1 (CET) or UTC+2 (CEST during DST)
  const offset = isDST ? 2 : 1;
  
  // Create Poland time by adjusting UTC
  const polandTime = new Date(now.getTime() + offset * 60 * 60 * 1000);
  
  return polandTime;
}

/**
 * Check if date is in daylight saving time (for Europe)
 */
function isDaylightSavingTime(date: Date): boolean {
  const year = date.getUTCFullYear();
  
  // DST in Europe: Last Sunday of March (2:00 AM) to Last Sunday of October (3:00 AM)
  const marchLastSunday = getLastSundayOfMonth(year, 2); // March is month 2
  const octoberLastSunday = getLastSundayOfMonth(year, 9); // October is month 9
  
  const timestamp = date.getTime();
  return timestamp >= marchLastSunday.getTime() && timestamp < octoberLastSunday.getTime();
}

/**
 * Get last Sunday of a month in UTC
 */
function getLastSundayOfMonth(year: number, month: number): Date {
  // Get last day of the month
  const lastDay = new Date(Date.UTC(year, month + 1, 0));
  const day = lastDay.getUTCDay();
  
  // Calculate days to subtract to get to Sunday
  const diff = day === 0 ? 0 : day;
  
  // Return last Sunday at 2:00 AM UTC for March, 3:00 AM UTC for October
  const hour = month === 2 ? 2 : 3;
  return new Date(Date.UTC(year, month + 1, -diff, hour, 0, 0));
}

/**
 * Get current WSE market status
 * Trading hours: Mon-Fri 9:00-17:00 CET/CEST (Polish time)
 */
export function getMarketStatus(): {
  status: 'open' | 'closed' | 'pre-market' | 'after-hours';
  label: string;
  color: string;
  polandTime: string;
} {
  const polandTime = getPolandTime();
  const day = polandTime.getUTCDay(); // Day in Poland time
  const hour = polandTime.getUTCHours();
  const minute = polandTime.getUTCMinutes();
  const timeInMinutes = hour * 60 + minute;
  
  // Format Poland time for display
  const timeString = polandTime.toLocaleTimeString('pl-PL', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'UTC' 
  });
  
  // Weekend
  if (day === 0 || day === 6) {
    return {
      status: 'closed',
      label: 'Rynek Zamknięty (Weekend)',
      color: 'text-tertiary',
      polandTime: timeString,
    };
  }
  
  // Pre-market: 8:30-9:00
  if (timeInMinutes >= 510 && timeInMinutes < 540) {
    return {
      status: 'pre-market',
      label: 'Pre-market',
      color: 'text-accent-warning',
      polandTime: timeString,
    };
  }
  
  // Market open: 9:00-17:00
  if (timeInMinutes >= 540 && timeInMinutes < 1020) {
    return {
      status: 'open',
      label: 'Rynek Otwarty',
      color: 'text-accent-success',
      polandTime: timeString,
    };
  }
  
  // After-hours: 17:00-17:10
  if (timeInMinutes >= 1020 && timeInMinutes < 1030) {
    return {
      status: 'after-hours',
      label: 'Po Sesji',
      color: 'text-accent-warning',
      polandTime: timeString,
    };
  }
  
  // Closed
  return {
    status: 'closed',
    label: 'Rynek Zamknięty',
    color: 'text-tertiary',
    polandTime: timeString,
  };
}

/**
 * Calculate composite score for a company (0-100)
 */
export function calculateScore(company: any): number {
  let score = 50; // Base score
  
  // Positive price change
  if (company.change_percent > 0) score += Math.min(company.change_percent * 2, 20);
  else score += Math.max(company.change_percent * 2, -20);
  
  // Low P/E is good (below 15 is excellent)
  if (company.pe_ratio) {
    if (company.pe_ratio < 10) score += 15;
    else if (company.pe_ratio < 15) score += 10;
    else if (company.pe_ratio < 20) score += 5;
    else score -= 5;
  }
  
  // Low P/B is good (below 2 is excellent)
  if (company.pb_ratio) {
    if (company.pb_ratio < 1) score += 15;
    else if (company.pb_ratio < 2) score += 10;
    else if (company.pb_ratio < 3) score += 5;
  }
  
  return Math.max(0, Math.min(100, score));
}

/**
 * Get color class based on change percentage
 */
export function getChangeColor(change: number): string {
  return change >= 0 ? 'text-accent-success' : 'text-accent-danger';
}

/**
 * Get background color with opacity for heat map
 */
export function getHeatMapColor(changePercent: number): string {
  if (changePercent > 10) return 'rgba(16, 185, 129, 1)'; // Strong gain
  if (changePercent > 5) return 'rgba(16, 185, 129, 0.6)'; // Moderate gain
  if (changePercent > 0) return 'rgba(16, 185, 129, 0.3)'; // Slight gain
  if (changePercent === 0) return '#1E2433'; // Neutral
  if (changePercent > -5) return 'rgba(239, 68, 68, 0.3)'; // Slight loss
  if (changePercent > -10) return 'rgba(239, 68, 68, 0.6)'; // Moderate loss
  return 'rgba(239, 68, 68, 1)'; // Strong loss
}


/**
 * Check if data is fresh (less than 2 minutes old)
 */
export function isDataFresh(lastUpdate: string | Date): boolean {
  const updateTime = new Date(lastUpdate);
  const now = new Date();
  const diffInMinutes = (now.getTime() - updateTime.getTime()) / (1000 * 60);
  return diffInMinutes < 2;
}

/**
 * Get data freshness indicator
 */
export function getDataFreshnessStatus(lastUpdate: string | Date): {
  status: 'fresh' | 'stale' | 'very_stale';
  label: string;
  color: string;
} {
  const updateTime = new Date(lastUpdate);
  const now = new Date();
  const diffInMinutes = (now.getTime() - updateTime.getTime()) / (1000 * 60);
  
  if (diffInMinutes < 2) {
    return {
      status: 'fresh',
      label: 'Dane na żywo',
      color: 'text-accent-success',
    };
  } else if (diffInMinutes < 60) {
    return {
      status: 'stale',
      label: `Aktualizacja ${Math.floor(diffInMinutes)} min temu`,
      color: 'text-accent-warning',
    };
  } else {
    const hours = Math.floor(diffInMinutes / 60);
    return {
      status: 'very_stale',
      label: `Aktualizacja ${hours}h temu`,
      color: 'text-accent-danger',
    };
  }
}

/**
 * Detect volume spike (volume significantly above average)
 */
export function isVolumeSpike(currentVolume: string, avgVolume: string): boolean {
  const parseVolume = (vol: string): number => {
    const num = parseFloat(vol.replace(/[^\d.]/g, ''));
    if (vol.includes('M')) return num * 1000000;
    if (vol.includes('K')) return num * 1000;
    return num;
  };
  
  const current = parseVolume(currentVolume);
  const average = parseVolume(avgVolume);
  
  return current > average * 2; // Volume is 2x average
}

/**
 * Format time ago string
 */
export function formatTimeAgo(date: string | Date): string {
  const updateTime = new Date(date);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - updateTime.getTime()) / 1000);
  
  if (diffInSeconds < 60) return `${diffInSeconds}s temu`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}min temu`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h temu`;
  return `${Math.floor(diffInSeconds / 86400)}d temu`;
}
