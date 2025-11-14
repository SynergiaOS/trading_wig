/**
 * Watchlist Service
 * Manages user's favorite/watchlist companies using localStorage
 */

export interface WatchlistItem {
  symbol: string;
  company_name: string;
  addedAt: string;
}

const WATCHLIST_KEY = 'wig80_watchlist';

export function getWatchlist(): WatchlistItem[] {
  try {
    const stored = localStorage.getItem(WATCHLIST_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function addToWatchlist(symbol: string, company_name: string): boolean {
  try {
    const watchlist = getWatchlist();
    if (watchlist.some(item => item.symbol === symbol)) {
      return false; // Already in watchlist
    }
    
    watchlist.push({
      symbol,
      company_name,
      addedAt: new Date().toISOString()
    });
    
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(watchlist));
    return true;
  } catch {
    return false;
  }
}

export function removeFromWatchlist(symbol: string): boolean {
  try {
    const watchlist = getWatchlist();
    const filtered = watchlist.filter(item => item.symbol !== symbol);
    localStorage.setItem(WATCHLIST_KEY, JSON.stringify(filtered));
    return true;
  } catch {
    return false;
  }
}

export function isInWatchlist(symbol: string): boolean {
  const watchlist = getWatchlist();
  return watchlist.some(item => item.symbol === symbol);
}

export function clearWatchlist(): void {
  try {
    localStorage.removeItem(WATCHLIST_KEY);
  } catch {
    // Ignore errors
  }
}

