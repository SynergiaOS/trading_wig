import { useEffect, useState, useCallback, useMemo } from 'react';
import { useTheme } from 'next-themes';
import { toast } from 'sonner';
import { TrendingUp, TrendingDown, BarChart3, Search, Activity, RefreshCw, Clock, AlertTriangle, Zap, LineChart, Wifi, WifiOff, Moon, Sun, Star, Download, Heart, HeartOff, Server } from 'lucide-react';
import { formatPLN, formatPercent, getMarketStatus, calculateScore, getChangeColor, getHeatMapColor, getDataFreshnessStatus, formatTimeAgo } from '../lib/formatters';
import { getTrendMomentum, getTrendDescription, calculateRSI, getRSIInterpretation, getVolumeStrength, getRiskAssessment, formatLastUpdate, getMarketCountdown } from '../lib/trendAnalysis';
import { getDataSource } from '../lib/dataService';
import { getWatchlist, addToWatchlist, removeFromWatchlist, isInWatchlist } from '../lib/watchlistService';
import { exportToCSV, exportToJSON } from '../lib/exportService';
import { checkBackendHealth, getBackendStats } from '../lib/backendService';
import ChartModal from '../components/ChartModal';
import CompanyAnalysisModal from '../components/CompanyAnalysisModal';
import { useMarketData } from '../features/market-dashboard/hooks/useMarketData';
import { usePatterns } from '../features/market-dashboard/hooks/usePatterns';
import type { Company, MarketIndex, SortBy, SortOrder, ViewMode, FilterCategory } from '../types/market';

export default function Dashboard() {
  const { theme, setTheme } = useTheme();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<FilterCategory>('all');
  const [sortBy, setSortBy] = useState<SortBy>('change');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [viewMode, setViewMode] = useState<ViewMode>('table');
  const [countdown, setCountdown] = useState(30);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState<MarketIndex>('WIG80');
  const [watchlist, setWatchlist] = useState<string[]>([]);
  const [backendHealth, setBackendHealth] = useState<'healthy' | 'degraded' | 'down' | 'checking'>('checking');
  const [showWatchlistOnly, setShowWatchlistOnly] = useState(false);

  // React Query hooks for data fetching
  const { 
    companies: rawCompanies, 
    metadata, 
    isLoading: loading, 
    isRefetching: isRefreshing,
    error: marketError,
    refresh 
  } = useMarketData(selectedIndex);

  const { 
    companiesWithPatterns, 
    isLoading: patternsLoading 
  } = usePatterns();

  // Calculate scores and prepare companies
  const companies = useMemo(() => {
    return rawCompanies.map(c => ({
      ...c,
      score: calculateScore(c)
    }));
  }, [rawCompanies]);

  const lastUpdate = useMemo(() => {
    return metadata?.collection_date ? new Date(metadata.collection_date) : new Date();
  }, [metadata]);

  const dataSourceInfo = useMemo(() => getDataSource(), []);
  const connectionError = marketError ? 'Błąd połączenia z danymi. Pokazywanie ostatnich dostępnych danych.' : null;

  const marketStatus = getMarketStatus();
  const marketCountdown = getMarketCountdown();

  // Load watchlist on mount
  useEffect(() => {
    const watchlistItems = getWatchlist();
    setWatchlist(watchlistItems.map(item => item.symbol));
  }, []);

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      const health = await checkBackendHealth();
      if (health) {
        setBackendHealth(health.status);
      }
    };
    
    checkHealth();
    const healthInterval = setInterval(checkHealth, 60000); // Check every minute
    return () => clearInterval(healthInterval);
  }, []);

  const handleToggleWatchlist = (company: Company) => {
    const inWatchlist = isInWatchlist(company.symbol);
    if (inWatchlist) {
      removeFromWatchlist(company.symbol);
      setWatchlist(prev => prev.filter(s => s !== company.symbol));
      toast.success(`${company.symbol} usunięto z obserwowanych`);
    } else {
      addToWatchlist(company.symbol, company.company_name);
      setWatchlist(prev => [...prev, company.symbol]);
      toast.success(`${company.symbol} dodano do obserwowanych`);
    }
  };

  // Calculate statistics
  const avgChange = useMemo(() => {
    return companies.length > 0
      ? companies.reduce((sum, c) => sum + c.change_percent, 0) / companies.length
      : 0;
  }, [companies]);

  const topGainers = useMemo(() => {
    return [...companies]
      .filter(c => c.change_percent > 0)
      .sort((a, b) => b.change_percent - a.change_percent)
      .slice(0, 4);
  }, [companies]);

  const topLosers = useMemo(() => {
    return [...companies]
      .filter(c => c.change_percent < 0)
      .sort((a, b) => a.change_percent - b.change_percent)
      .slice(0, 4);
  }, [companies]);

  const volumeLeaders = useMemo(() => {
    return [...companies]
      .sort((a, b) => {
        const aVol = parseFloat(a.trading_volume?.replace(/[^\d.]/g, '') || '0');
        const bVol = parseFloat(b.trading_volume?.replace(/[^\d.]/g, '') || '0');
        return bVol - aVol;
      })
      .slice(0, 3);
  }, [companies]);

  // Filtering and sorting
  const filteredCompanies = useMemo(() => {
    return companies
      .filter(company => {
        const matchesSearch = 
          company.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          company.symbol.toLowerCase().includes(searchTerm.toLowerCase());
        
        // Watchlist filter
        if (showWatchlistOnly && !isInWatchlist(company.symbol)) {
          return false;
        }
        
        if (filterCategory === 'all') return matchesSearch;
        if (filterCategory === 'gainers') return matchesSearch && company.change_percent > 0;
        if (filterCategory === 'losers') return matchesSearch && company.change_percent < 0;
        if (filterCategory === 'value') return matchesSearch && company.pb_ratio && company.pb_ratio < 2;
        if (filterCategory === 'momentum') return matchesSearch && Math.abs(company.change_percent) >= 5;
        return matchesSearch;
      })
      .sort((a, b) => {
        let aValue, bValue;
        
        switch (sortBy) {
          case 'change':
            aValue = a.change_percent;
            bValue = b.change_percent;
            break;
          case 'pe':
            aValue = a.pe_ratio || 999;
            bValue = b.pe_ratio || 999;
            break;
          case 'pb':
            aValue = a.pb_ratio || 999;
            bValue = b.pb_ratio || 999;
            break;
          case 'score':
            aValue = a.score || 0;
            bValue = b.score || 0;
            break;
          default:
            aValue = a.change_percent;
            bValue = b.change_percent;
        }
        
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
      });
  }, [companies, searchTerm, filterCategory, sortBy, sortOrder, showWatchlistOnly]);

  const handleExportCSV = () => {
    try {
      exportToCSV(filteredCompanies, `wig80_${selectedIndex.toLowerCase()}`);
      toast.success('Dane wyeksportowano do CSV');
    } catch (error) {
      toast.error('Błąd podczas eksportu do CSV');
    }
  };

  const handleExportJSON = () => {
    try {
      exportToJSON(filteredCompanies, `wig80_${selectedIndex.toLowerCase()}`);
      toast.success('Dane wyeksportowano do JSON');
    } catch (error) {
      toast.error('Błąd podczas eksportu do JSON');
    }
  };

  const handleRefresh = () => {
    refresh();
    setCountdown(30);
    toast.success(`Odświeżanie danych...`, { duration: 1000 });
  };

  // Countdown timer
  useEffect(() => {
    const countdownInterval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          return 30;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(countdownInterval);
  }, []);

  const lastUpdateInfo = formatLastUpdate(lastUpdate);

  // Loading state with enhanced skeleton
  if (loading) {
    return (
      <div className="min-h-screen bg-bg-near-black">
        {/* Loading Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 bg-bg-pure-black border-b border-subtle h-20">
          <div className="max-w-screen-2xl mx-auto px-lg md:px-2xl h-full flex items-center justify-between">
            <div className="h-8 bg-surface-elevated rounded loading-pulse w-64"></div>
            <div className="h-6 bg-surface-elevated rounded loading-pulse w-32"></div>
          </div>
        </nav>
        
        {/* Loading Content */}
        <main className="pt-28 pb-20 max-w-screen-2xl mx-auto px-lg md:px-2xl space-y-3xl">
          {/* Loading Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-xl">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-surface-elevated rounded-xl p-8 border border-border-subtle">
                <div className="space-y-4">
                  <div className="h-4 bg-surface-overlay rounded loading-pulse w-24"></div>
                  <div className="h-12 bg-surface-overlay rounded loading-pulse w-16"></div>
                  <div className="h-3 bg-surface-overlay rounded loading-pulse w-20"></div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Loading Table */}
          <div className="bg-surface-elevated rounded-xl border border-border-subtle overflow-hidden">
            <div className="p-8">
              <div className="space-y-4">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="flex items-center space-x-6">
                    <div className="h-6 bg-surface-overlay rounded loading-pulse w-16"></div>
                    <div className="h-6 bg-surface-overlay rounded loading-pulse flex-1"></div>
                    <div className="h-6 bg-surface-overlay rounded loading-pulse w-20"></div>
                    <div className="h-6 bg-surface-overlay rounded loading-pulse w-16"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
        
        <div className="fixed inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center bg-surface-elevated rounded-xl p-8 border border-border-subtle backdrop-blur-sm">
            <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto mb-6"></div>
            <p className="text-xl text-text-secondary font-body">Ładowanie danych rynkowych WIG80...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-near-black">
      {/* Enhanced Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-surface-elevated/95 backdrop-blur-md border-b border-border-subtle h-20 transition-all duration-250">
        <div className="max-w-screen-2xl mx-auto px-lg md:px-2xl h-full flex items-center justify-between">
          <div className="flex items-center space-x-xl">
            <h1 className="text-2xl md:text-3xl font-bold text-text-primary font-display tracking-tight">
              Polish Financial Platform
            </h1>
            
            {/* Index Selector - Professional Toggle */}
            <div className="hidden md:flex items-center space-x-2 bg-surface-hover rounded-xl p-1 border border-border-subtle">
              <button
                onClick={() => setSelectedIndex('WIG30')}
                className={`px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-250 ${
                  selectedIndex === 'WIG30'
                    ? 'bg-primary-gradient text-text-inverse shadow-lg shadow-primary-400/20'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                WIG30
              </button>
              <button
                onClick={() => setSelectedIndex('WIG80')}
                className={`px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-250 ${
                  selectedIndex === 'WIG80'
                    ? 'bg-primary-gradient text-text-inverse shadow-lg shadow-primary-400/20'
                    : 'text-text-secondary hover:text-text-primary'
                }`}
              >
                WIG80
              </button>
            </div>
            
            <div className="hidden md:flex items-center space-x-md">
              {/* Enhanced Market Status Badge */}
              <div className={`px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center space-x-3 border transition-all duration-250 ${
                marketStatus.status === 'open' 
                  ? 'bg-success-gradient border-success-400/30 shadow-glow-success' 
                  : 'bg-surface-hover border-border-subtle'
              }`}>
                <div className={`w-2.5 h-2.5 rounded-full transition-all duration-250 ${
                  marketStatus.status === 'open' 
                    ? 'bg-success-300 animate-pulse-slow shadow-sm' 
                    : 'bg-text-tertiary'
                }`}></div>
                <span className={`${marketStatus.color} font-medium`}>{marketStatus.label}</span>
              </div>
              
              {/* Market Countdown Badge */}
              {marketStatus.status === 'open' && (
                <div className="px-4 py-2.5 rounded-xl bg-warning-gradient border border-warning-400/30 text-sm font-medium flex items-center space-x-2 transition-all duration-250">
                  <Clock className="w-4 h-4 text-warning-300" />
                  <span className="text-warning-100">{marketCountdown.messagePL}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Enhanced Refresh Controls */}
          <div className="flex items-center space-x-lg">
            <div className="flex items-center space-x-3 text-text-secondary text-sm">
              <div className={`p-2 rounded-lg transition-all duration-250 ${
                isRefreshing 
                  ? 'bg-primary-gradient text-text-inverse' 
                  : 'bg-surface-hover hover:bg-surface-modal'
              }`}>
                <RefreshCw className={`w-4 h-4 transition-transform duration-250 ${
                  isRefreshing ? 'animate-spin' : 'hover:rotate-180'
                }`} />
              </div>
              <div className="hidden md:flex flex-col items-end">
                <span className="text-xs text-text-tertiary">{lastUpdateInfo.relativePL}</span>
                <div className="flex items-center space-x-1">
                  <span className="text-xs text-text-secondary">Następne odświeżenie</span>
                  <span className="text-sm font-mono font-bold text-primary-400">({countdown}s)</span>
                </div>
              </div>
            </div>
            
            {/* Backend Health Indicator */}
            <div className="flex items-center space-x-2">
              <div className={`p-2 rounded-lg transition-all duration-250 ${
                backendHealth === 'healthy' ? 'bg-success-gradient/20' :
                backendHealth === 'degraded' ? 'bg-warning-gradient/20' :
                backendHealth === 'down' ? 'bg-danger-gradient/20' :
                'bg-surface-hover'
              }`}>
                <Server className={`w-4 h-4 ${
                  backendHealth === 'healthy' ? 'text-success-400' :
                  backendHealth === 'degraded' ? 'text-warning-400' :
                  backendHealth === 'down' ? 'text-danger-400' :
                  'text-text-tertiary'
                }`} />
              </div>
              
              {/* Dark Mode Toggle */}
              <button
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                className="p-2 rounded-lg bg-surface-hover hover:bg-surface-modal transition-all duration-250"
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5 text-text-secondary hover:text-warning-400 transition-colors" />
                ) : (
                  <Moon className="w-5 h-5 text-text-secondary hover:text-primary-400 transition-colors" />
                )}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-28 pb-20 max-w-screen-2xl mx-auto px-lg md:px-2xl space-y-3xl">
        {/* Enhanced Market Dashboard Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-xl">
          {/* Total Companies Card */}
          <div className="card-interactive bg-gradient-to-br from-surface-elevated to-surface-hover rounded-xl p-8 border border-border-subtle hover:border-primary-400/50 transition-all duration-250 group relative overflow-hidden shadow-lg hover:shadow-xl">
            {/* Animated background gradient */}
            <div className="absolute inset-0 bg-primary-gradient opacity-0 group-hover:opacity-10 transition-opacity duration-500"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-primary-400/5 via-transparent to-transparent"></div>
            
            <div className="relative flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-3">
                  <p className="text-sm text-text-secondary font-medium">Wszystkie spółki</p>
                  <div className={`badge ${selectedIndex === 'WIG30' ? 'badge-primary' : 'badge-neutral'}`}>
                    {selectedIndex}
                  </div>
                </div>
                <p className="text-5xl font-bold text-text-primary font-mono mb-2 tracking-tight bg-gradient-to-r from-text-primary to-text-secondary bg-clip-text">
                  {companies.length}
                </p>
                <p className="text-sm text-text-tertiary">Indeks warszawski</p>
              </div>
              <div className="w-16 h-16 rounded-xl bg-primary-gradient/20 border border-primary-400/30 flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all duration-250 shadow-lg shadow-primary-400/10">
                <BarChart3 className="w-8 h-8 text-primary-400" />
              </div>
            </div>
          </div>

          {/* Average Change Card */}
          <div className="card-interactive bg-gradient-to-br from-surface-elevated to-surface-hover rounded-xl p-8 border border-border-subtle hover:border-primary-400/50 transition-all duration-250 group relative overflow-hidden shadow-lg hover:shadow-xl">
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity duration-500 ${
              avgChange >= 0 ? 'bg-success-gradient' : 'bg-danger-gradient'
            }`}></div>
            <div className={`absolute inset-0 bg-gradient-to-br ${
              avgChange >= 0 ? 'from-success-400/5' : 'from-danger-400/5'
            } via-transparent to-transparent`}></div>
            
            <div className="relative flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-3">
                  <p className="text-sm text-text-secondary font-medium">Średnia zmiana</p>
                  <div className={`badge ${avgChange >= 0 ? 'badge-success' : 'badge-danger'}`}>
                    {avgChange >= 0 ? 'WZROST' : 'SPADEK'}
                  </div>
                </div>
                <p className={`text-5xl font-bold font-mono mb-2 tracking-tight transition-colors duration-250 ${
                  avgChange >= 0 ? 'text-success-400' : 'text-danger-400'
                }`}>
                  {formatPercent(avgChange)}
                </p>
                <p className="text-sm text-text-tertiary">Średnia rynkowa</p>
              </div>
              <div className={`w-16 h-16 rounded-xl border flex items-center justify-center group-hover:scale-110 transition-transform duration-250 ${
                avgChange >= 0 
                  ? 'bg-success-gradient/10 border-success-400/20' 
                  : 'bg-danger-gradient/10 border-danger-400/20'
              }`}>
                {avgChange >= 0 ? (
                  <TrendingUp className="w-8 h-8 text-success-400" />
                ) : (
                  <TrendingDown className="w-8 h-8 text-danger-400" />
                )}
              </div>
            </div>
          </div>

          {/* Top Gainer Card */}
          <div className="card-interactive bg-gradient-to-br from-surface-elevated via-success-500/5 to-surface-hover rounded-xl p-8 border-l-4 border-l-success-400 border-t border-r border-b border-border-subtle hover:border-success-400/50 transition-all duration-250 group relative overflow-hidden shadow-lg shadow-success-400/10 hover:shadow-xl hover:shadow-success-400/20">
            <div className="absolute inset-0 bg-success-gradient opacity-0 group-hover:opacity-10 transition-opacity duration-500"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-success-400/10 via-transparent to-transparent"></div>
            
            <div className="relative flex items-start justify-between">
              <div className="flex-1 mr-4">
                <div className="flex items-center space-x-2 mb-3">
                  <p className="text-sm text-text-secondary font-medium">Największy wzrost</p>
                  <div className="badge badge-success">TOP GAINER</div>
                </div>
                <p className="text-4xl font-bold text-success-400 font-mono mb-2 tracking-tight">
                  {topGainers[0]?.symbol || 'N/A'}
                </p>
                <p className="text-xl font-semibold text-success-300 font-mono mb-2">
                  {topGainers[0] && formatPercent(topGainers[0].change_percent)}
                </p>
                <p className="text-xs text-text-secondary truncate">
                  {topGainers[0]?.company_name}
                </p>
              </div>
              <div className="flex-shrink-0">
                <TrendingUp className="w-12 h-12 text-success-400 group-hover:scale-110 transition-transform duration-250" />
              </div>
            </div>
          </div>

          {/* Top Loser Card */}
          <div className="card-interactive bg-gradient-to-br from-surface-elevated via-danger-500/5 to-surface-hover rounded-xl p-8 border-l-4 border-l-danger-400 border-t border-r border-b border-border-subtle hover:border-danger-400/50 transition-all duration-250 group relative overflow-hidden shadow-lg shadow-danger-400/10 hover:shadow-xl hover:shadow-danger-400/20">
            <div className="absolute inset-0 bg-danger-gradient opacity-0 group-hover:opacity-10 transition-opacity duration-500"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-danger-400/10 via-transparent to-transparent"></div>
            
            <div className="relative flex items-start justify-between">
              <div className="flex-1 mr-4">
                <div className="flex items-center space-x-2 mb-3">
                  <p className="text-sm text-text-secondary font-medium">Największy spadek</p>
                  <div className="badge badge-danger">TOP LOSER</div>
                </div>
                <p className="text-4xl font-bold text-danger-400 font-mono mb-2 tracking-tight">
                  {topLosers[0]?.symbol || 'N/A'}
                </p>
                <p className="text-xl font-semibold text-danger-300 font-mono mb-2">
                  {topLosers[0] && formatPercent(topLosers[0].change_percent)}
                </p>
                <p className="text-xs text-text-secondary truncate">
                  {topLosers[0]?.company_name}
                </p>
              </div>
              <div className="flex-shrink-0">
                <TrendingDown className="w-12 h-12 text-danger-400 group-hover:scale-110 transition-transform duration-250" />
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Volume Leaders Section */}
        <div className="bg-surface-elevated rounded-xl p-8 border border-border-subtle">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-text-primary font-display flex items-center">
              <div className="p-2 rounded-lg bg-warning-gradient/10 border border-warning-400/20 mr-3">
                <Zap className="w-6 h-6 text-warning-400" />
              </div>
              Liderzy wolumenu
            </h2>
            <div className="badge badge-warning">TOP VOLUME</div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {volumeLeaders.map((company, index) => {
              const volumeInfo = getVolumeStrength(company.trading_volume);
              return (
                <div 
                  key={company.symbol} 
                  className="card-interactive bg-surface-hover rounded-xl p-6 border border-border-subtle hover:border-warning-400/30 transition-all duration-250 group relative overflow-hidden"
                >
                  {/* Subtle animation background */}
                  <div className="absolute inset-0 bg-warning-gradient opacity-0 group-hover:opacity-5 transition-opacity duration-250"></div>
                  
                  <div className="relative">
                    {/* Header with rank and change */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-2xl font-bold text-warning-400 font-mono">#{index + 1}</span>
                        <div className="w-2 h-8 bg-warning-gradient rounded-full"></div>
                      </div>
                      <span className={`badge ${
                        company.change_percent >= 0 ? 'badge-success' : 'badge-danger'
                      }`}>
                        {formatPercent(company.change_percent)}
                      </span>
                    </div>
                    
                    {/* Company info */}
                    <div className="mb-4">
                      <h3 className="text-xl font-bold text-text-primary font-mono mb-1 group-hover:text-warning-400 transition-colors duration-250">
                        {company.symbol}
                      </h3>
                      <p className="text-sm text-text-secondary truncate">{company.company_name}</p>
                    </div>
                    
                    {/* Volume info with progress bar */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-text-tertiary font-medium">{volumeInfo.labelPL}</span>
                        <span className={`text-xs font-semibold ${volumeInfo.color}`}>
                          {volumeInfo.strength}
                        </span>
                      </div>
                      
                      {/* Volume amount */}
                      <div className="bg-surface-elevated rounded-lg p-3 border border-border-subtle">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-text-tertiary">Wolumen</span>
                          <span className="text-sm font-bold text-text-primary font-mono">
                            {company.trading_volume}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Technical Patterns Section */}
        {companiesWithPatterns.length > 0 && (
          <div className="bg-surface-elevated border border-border-subtle rounded-xl p-8 space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="p-3 rounded-xl bg-primary-gradient/10 border border-primary-400/20">
                  <Zap className="w-6 h-6 text-primary-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-text-primary">Wzorce Techniczne</h2>
                  <p className="text-sm text-text-secondary">Wykryte formacje cenowe i trendy</p>
                </div>
              </div>
              <div className="badge badge-primary">
                {companiesWithPatterns.length} spółek
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {companiesWithPatterns.slice(0, 9).map((company) => {
                const mainPattern = company.patterns?.[0];
                if (!mainPattern) return null;

                const patternEmoji = mainPattern.pattern_name.includes('Flaga') ? '🚩' :
                                   mainPattern.pattern_name.includes('Trójkąt') ? '🔺' :
                                   mainPattern.pattern_name.includes('Kanał') ? '📐' :
                                   mainPattern.pattern_name.includes('Breakout') ? '⚡' :
                                   mainPattern.pattern_name.includes('Momentum') ? '📈' :
                                   mainPattern.pattern_name.includes('Wzrostowy') ? '📈' :
                                   mainPattern.pattern_name.includes('Spadkowy') ? '📉' : '📊';

                const directionColor = mainPattern.direction === 'bullish' ? 'success' :
                                     mainPattern.direction === 'bearish' ? 'danger' : 'warning';

                return (
                  <div
                    key={company.symbol}
                    className="card-interactive bg-surface-hover rounded-xl p-6 border border-border-subtle hover:border-primary-400/50 transition-all duration-250 group relative overflow-hidden cursor-pointer"
                    onClick={() => setSelectedCompany(company)}
                  >
                    <div className="relative">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-text-primary font-mono mb-1 group-hover:text-primary-400 transition-colors">
                            {company.symbol}
                          </h3>
                          <p className="text-xs text-text-secondary truncate">{company.company_name}</p>
                        </div>
                        <div className="text-3xl">{patternEmoji}</div>
                      </div>

                      {/* Pattern Info */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold text-text-primary">
                            {mainPattern.pattern_name}
                          </span>
                          <span className={`badge badge-${directionColor}`}>
                            {mainPattern.direction.toUpperCase()}
                          </span>
                        </div>

                        {/* Price and Change */}
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-lg font-bold text-text-primary font-mono">
                              {formatPLN(company.current_price)}
                            </p>
                            <p className={`text-sm font-semibold font-mono ${
                              company.change_percent >= 0 ? 'text-success-400' : 'text-danger-400'
                            }`}>
                              {formatPercent(company.change_percent)}
                            </p>
                          </div>
                        </div>

                        {/* Pattern Strength */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-text-tertiary">Siła wzorca</span>
                            <span className="font-semibold text-text-primary">
                              {Math.round(mainPattern.strength * 100)}%
                            </span>
                          </div>
                          <div className="w-full bg-surface-elevated rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all duration-500 ${
                                directionColor === 'success' ? 'bg-success-gradient' :
                                directionColor === 'danger' ? 'bg-danger-gradient' :
                                'bg-warning-gradient'
                              }`}
                              style={{ width: `${mainPattern.strength * 100}%` }}
                            />
                          </div>
                        </div>

                        {/* Additional patterns count */}
                        {company.patterns && company.patterns.length > 1 && (
                          <div className="pt-2 border-t border-border-subtle">
                            <p className="text-xs text-text-tertiary">
                              +{company.patterns.length - 1} dodatkow{company.patterns.length - 1 === 1 ? 'y' : 'e'} wzorzec{company.patterns.length - 1 > 1 ? 'e' : ''}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {companiesWithPatterns.length > 9 && (
              <div className="text-center pt-4">
                <p className="text-sm text-text-secondary">
                  I {companiesWithPatterns.length - 9} więcej spółek z wykrytymi wzorcami
                </p>
              </div>
            )}
          </div>
        )}

        {/* Enhanced Real-Time Ticker */}
        <div className="bg-surface-elevated border border-border-subtle rounded-xl h-16 overflow-hidden relative group">
          {/* Background gradient animation */}
          <div className="absolute inset-0 bg-gradient-to-r from-primary-gradient via-transparent to-primary-gradient opacity-5 animate-shimmer"></div>
          
          {/* Ticker content */}
          <div className="flex items-center h-full animate-ticker-scroll hover:pause whitespace-nowrap relative z-10">
            {[...companies, ...companies].map((company, index) => {
              const trend = getTrendMomentum(company.change_percent);
              const isPositive = company.change_percent >= 0;
              
              return (
                <div 
                  key={`${company.symbol}-${index}`} 
                  className="inline-flex items-center px-8 space-x-4 hover:bg-surface-hover/50 transition-colors duration-200 cursor-pointer group/item"
                  onClick={() => setSelectedCompany(company)}
                >
                  {/* Symbol */}
                  <span className="text-base font-bold text-text-primary font-mono group-hover/item:text-primary-400 transition-colors duration-200">
                    {company.symbol}
                  </span>
                  
                  {/* Price */}
                  <span className="text-base text-text-secondary font-mono">
                    {formatPLN(company.current_price)}
                  </span>
                  
                  {/* Change with enhanced styling */}
                  <div className={`flex items-center space-x-1.5 px-2 py-1 rounded-lg transition-all duration-200 ${
                    isPositive 
                      ? 'bg-success-gradient/10 text-success-400 group-hover/item:bg-success-gradient/20' 
                      : 'bg-danger-gradient/10 text-danger-400 group-hover/item:bg-danger-gradient/20'
                  }`}>
                    {trend.direction === 'upward' && <TrendingUp className="w-3.5 h-3.5" />}
                    {trend.direction === 'downward' && <TrendingDown className="w-3.5 h-3.5" />}
                    <span className="text-sm font-semibold font-mono">{formatPercent(company.change_percent)}</span>
                  </div>
                  
                  {/* Separator */}
                  <div className="w-px h-6 bg-border-subtle"></div>
                </div>
              );
            })}
          </div>
          
          {/* Fade edges */}
          <div className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-surface-elevated to-transparent pointer-events-none z-20"></div>
          <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-surface-elevated to-transparent pointer-events-none z-20"></div>
          
          {/* Live indicator */}
          <div className="absolute top-2 right-2 flex items-center space-x-1 text-xs z-30">
            <div className="w-2 h-2 rounded-full bg-success-400 animate-pulse-slow"></div>
            <span className="text-text-tertiary font-medium">LIVE</span>
          </div>
        </div>

        {/* Enhanced Quick Profit Opportunities */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <h2 className="text-3xl font-bold text-text-primary font-display tracking-tight">
                Szybkie okazje inwestycyjne
              </h2>
              <div className="badge badge-success">HOT PICKS</div>
            </div>
            <button
              onClick={loadCompanies}
              className="btn-primary flex items-center space-x-2 focus-ring"
              disabled={isRefreshing}
            >
              <RefreshCw className={`w-4 h-4 transition-transform duration-250 ${
                isRefreshing ? 'animate-spin' : 'group-hover:rotate-180'
              }`} />
              <span>Odśwież dane</span>
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {topGainers.map((company, index) => {
              const trend = getTrendMomentum(company.change_percent);
              const description = getTrendDescription(company);
              const rsi = calculateRSI(company.change_percent);
              const rsiInfo = getRSIInterpretation(rsi);
              const volumeInfo = getVolumeStrength(company.trading_volume);
              const riskInfo = getRiskAssessment(company);

              return (
                <div
                  key={company.symbol}
                  className="card-interactive bg-surface-elevated rounded-xl p-6 border border-border-subtle hover:border-success-400/50 transition-all duration-250 group cursor-pointer relative overflow-hidden"
                  onClick={() => setSelectedCompany(company)}
                >
                  {/* Gradient background overlay */}
                  <div className="absolute inset-0 bg-success-gradient opacity-0 group-hover:opacity-5 transition-opacity duration-250"></div>
                  
                  {/* Top rank badge */}
                  <div className="absolute top-4 right-4 z-10">
                    <div className="badge badge-success text-xs">#{index + 1}</div>
                  </div>
                  
                  <div className="relative space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-2xl font-bold text-success-400 font-mono mb-1 group-hover:text-success-300 transition-colors duration-250">
                          {company.symbol}
                        </h3>
                        <p className="text-sm text-text-secondary truncate pr-12">
                          {company.company_name}
                        </p>
                      </div>
                    </div>

                    {/* Main metrics */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-text-tertiary">Cena aktualna</span>
                        <span className="text-lg font-bold text-text-primary font-mono">
                          {formatPLN(company.current_price)}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-text-tertiary">Zmiana</span>
                        <div className="flex items-center space-x-2">
                          <TrendingUp className="w-4 h-4 text-success-400" />
                          <span className="text-lg font-bold text-success-400 font-mono">
                            {formatPercent(company.change_percent)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Trend description */}
                    <div className="bg-surface-hover rounded-lg p-3 border border-border-subtle">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`badge ${trend.direction === 'upward' ? 'badge-success' : trend.direction === 'downward' ? 'badge-danger' : 'badge-neutral'}`}>
                          {description.categoryPL}
                        </span>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        {description.descriptionPL}
                      </p>
                    </div>

                    {/* Financial ratios */}
                    <div className="grid grid-cols-2 gap-3">
                      {company.pe_ratio && (
                        <div className="bg-surface-elevated rounded-lg p-3 border border-border-subtle">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-text-tertiary">P/E</span>
                            <span className="text-sm font-semibold text-text-secondary font-mono">
                              {company.pe_ratio.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      )}
                      {company.pb_ratio && (
                        <div className="bg-surface-elevated rounded-lg p-3 border border-border-subtle">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-text-tertiary">P/B</span>
                            <span className="text-sm font-semibold text-text-secondary font-mono">
                              {company.pb_ratio.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Technical indicators */}
                    <div className="space-y-2 pt-3 border-t border-border-subtle">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-text-tertiary">RSI:</span>
                        <div className="flex items-center space-x-2">
                          <span className={`font-semibold ${rsiInfo.color}`}>{rsi}</span>
                          <span className={`badge text-xs ${
                            rsiInfo.labelPL === 'Wykupiony' ? 'badge-danger' :
                            rsiInfo.labelPL === 'Wyprzedany' ? 'badge-success' : 'badge-neutral'
                          }`}>
                            {rsiInfo.labelPL}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-text-tertiary">Wolumen:</span>
                        <span className={`badge text-xs ${
                          volumeInfo.strength === 'very-high' || volumeInfo.strength === 'high' ? 'badge-success' :
                          volumeInfo.strength === 'normal' ? 'badge-warning' : 'badge-neutral'
                        }`}>
                          {volumeInfo.labelPL}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-text-tertiary">Ryzyko:</span>
                        <span className={`badge text-xs ${
                          riskInfo.level === 'low' ? 'badge-success' :
                          riskInfo.level === 'medium' ? 'badge-warning' : 'badge-danger'
                        }`}>
                          {riskInfo.labelPL}
                        </span>
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center justify-center gap-2 pt-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedCompany(company);
                          setShowAnalysisModal(true);
                        }}
                        className="flex items-center space-x-2 px-3 py-1.5 bg-primary-gradient/10 hover:bg-primary-gradient/20 text-primary-400 rounded-lg text-xs font-semibold transition-all duration-250 border border-primary-400/30"
                      >
                        <Activity className="w-3 h-3" />
                        <span>Analiza</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedCompany(company);
                          setShowAnalysisModal(false);
                        }}
                        className="flex items-center space-x-2 px-3 py-1.5 bg-surface-hover hover:bg-surface-modal text-text-secondary hover:text-text-primary rounded-lg text-xs font-semibold transition-all duration-250 border border-border-subtle"
                      >
                        <LineChart className="w-3 h-3" />
                        <span>Wykres</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Enhanced Filter Bar */}
        <div className="mb-8">
          <div className="bg-surface-elevated rounded-xl p-6 border border-border-subtle">
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
              {/* Filter Categories */}
              <div className="flex flex-wrap gap-3">
                {[
                  { id: 'all', label: 'Wszystkie kategorie', icon: BarChart3 },
                  { id: 'gainers', label: 'Wzrosty', icon: TrendingUp },
                  { id: 'losers', label: 'Spadki', icon: TrendingDown },
                  { id: 'value', label: 'Wartościowe', icon: Activity },
                  { id: 'momentum', label: 'Momentum', icon: Zap }
                ].map((category) => {
                  const Icon = category.icon;
                  return (
                    <button
                      key={category.id}
                      onClick={() => setFilterCategory(category.id)}
                      className={`flex items-center space-x-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-250 min-h-[44px] focus-ring ${
                        filterCategory === category.id
                          ? 'bg-primary-gradient text-text-inverse shadow-glow-primary border border-primary-400/30'
                          : 'bg-surface-hover text-text-secondary hover:text-text-primary hover:bg-surface-modal border border-border-subtle hover:border-primary-400/30'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{category.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Search and View Controls */}
              <div className="flex items-center gap-4 w-full lg:w-auto">
                {/* Watchlist Toggle */}
                <button
                  onClick={() => {
                    setShowWatchlistOnly(!showWatchlistOnly);
                    toast.info(showWatchlistOnly ? 'Pokazuję wszystkie spółki' : 'Pokazuję tylko obserwowane');
                  }}
                  className={`flex items-center space-x-2 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-250 min-h-[44px] focus-ring ${
                    showWatchlistOnly
                      ? 'bg-primary-gradient text-text-inverse shadow-glow-primary border border-primary-400/30'
                      : 'bg-surface-hover text-text-secondary hover:text-text-primary hover:bg-surface-modal border border-border-subtle hover:border-primary-400/30'
                  }`}
                >
                  <Star className={`w-4 h-4 ${showWatchlistOnly ? 'fill-current' : ''}`} />
                  <span className="hidden sm:inline">Obserwowane</span>
                  {watchlist.length > 0 && (
                    <span className="px-2 py-0.5 rounded-full bg-primary-400/20 text-xs font-bold">
                      {watchlist.length}
                    </span>
                  )}
                </button>

                {/* Export Buttons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleExportCSV}
                    className="p-3 rounded-xl bg-surface-hover hover:bg-surface-modal border border-border-subtle hover:border-success-400/30 transition-all duration-250"
                    title="Eksportuj do CSV"
                  >
                    <Download className="w-4 h-4 text-text-secondary hover:text-success-400 transition-colors" />
                  </button>
                  <button
                    onClick={handleExportJSON}
                    className="p-3 rounded-xl bg-surface-hover hover:bg-surface-modal border border-border-subtle hover:border-primary-400/30 transition-all duration-250"
                    title="Eksportuj do JSON"
                  >
                    <Download className="w-4 h-4 text-text-secondary hover:text-primary-400 transition-colors" />
                  </button>
                </div>

                {/* Enhanced Search */}
                <div className="relative flex-1 lg:flex-initial">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-tertiary" />
                  <input
                    type="text"
                    placeholder="Szukaj spółek..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-12 pr-4 py-3 bg-surface-hover border border-border-subtle rounded-xl text-sm text-text-primary placeholder-text-tertiary focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-400/20 w-full lg:min-w-[300px] transition-all duration-250"
                  />
                  {searchTerm && (
                    <button
                      onClick={() => setSearchTerm('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full bg-surface-modal hover:bg-text-tertiary/20 flex items-center justify-center transition-colors duration-200"
                    >
                      <span className="text-text-tertiary text-xs">×</span>
                    </button>
                  )}
                </div>

                {/* View Mode Toggle */}
                <div className="flex gap-2 p-1 bg-surface-hover rounded-xl border border-border-subtle">
                  <button
                    onClick={() => setViewMode('table')}
                    className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 min-h-[44px] ${
                      viewMode === 'table'
                        ? 'bg-primary-gradient text-text-inverse shadow-sm'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-modal'
                    }`}
                  >
                    <BarChart3 className="w-4 h-4" />
                    <span className="hidden sm:inline">Tabela</span>
                  </button>
                  <button
                    onClick={() => setViewMode('heatmap')}
                    className={`flex items-center space-x-2 px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 min-h-[44px] ${
                      viewMode === 'heatmap'
                        ? 'bg-primary-gradient text-text-inverse shadow-sm'
                        : 'text-text-secondary hover:text-text-primary hover:bg-surface-modal'
                    }`}
                  >
                    <Activity className="w-4 h-4" />
                    <span className="hidden sm:inline">Mapa ciepła</span>
                  </button>
                </div>
              </div>
            </div>
            
            {/* Results counter */}
            <div className="flex items-center justify-between pt-4 border-t border-border-subtle mt-4">
              <div className="flex items-center space-x-2 text-sm text-text-tertiary">
                <span>Znaleziono:</span>
                <span className="font-semibold text-text-secondary">{filteredCompanies.length}</span>
                <span>z {companies.length} spółek</span>
              </div>
              
              {searchTerm && (
                <div className="flex items-center space-x-2 text-sm">
                  <span className="text-text-tertiary">Fraza:</span>
                  <span className="px-2 py-1 bg-primary-gradient/10 text-primary-400 rounded font-mono text-xs">
                    "{searchTerm}"
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Enhanced Data Table View */}
        {viewMode === 'table' && (
          <div className="bg-surface-elevated rounded-xl border border-border-subtle overflow-hidden">
            <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-border-subtle scrollbar-track-transparent">
              <table className="min-w-full">
                <thead className="bg-surface-hover border-b border-border-subtle">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-bold text-text-primary">
                      <div className="flex items-center space-x-2">
                        <span>Symbol</span>
                      </div>
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-text-primary hidden md:table-cell">
                      Spółka
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-bold text-text-primary hidden lg:table-cell">
                      Trend
                    </th>
                    <th className="px-6 py-4 text-right text-sm font-bold text-text-primary">
                      Cena
                    </th>
                    <th 
                      className="px-6 py-4 text-right text-sm font-bold text-text-primary cursor-pointer hover:text-primary-400 transition-colors duration-200"
                      onClick={() => {
                        if (sortBy === 'change') {
                          setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                        } else {
                          setSortBy('change');
                          setSortOrder('desc');
                        }
                      }}
                    >
                      <div className="flex items-center justify-end space-x-1">
                        <span>Zmiana</span>
                        {sortBy === 'change' && (
                          <span className="text-primary-400">
                            {sortOrder === 'asc' ? '▲' : '▼'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th className="px-6 py-4 text-right text-sm font-bold text-text-primary hidden lg:table-cell">
                      <div className="flex items-center justify-end space-x-1">
                        <span>RSI</span>
                      </div>
                    </th>
                    <th 
                      className="px-6 py-4 text-right text-sm font-bold text-text-primary cursor-pointer hover:text-primary-400 transition-colors duration-200 hidden xl:table-cell"
                      onClick={() => {
                        if (sortBy === 'pe') {
                          setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                        } else {
                          setSortBy('pe');
                          setSortOrder('asc');
                        }
                      }}
                    >
                      <div className="flex items-center justify-end space-x-1">
                        <span>P/E</span>
                        {sortBy === 'pe' && (
                          <span className="text-primary-400">
                            {sortOrder === 'asc' ? '▲' : '▼'}
                          </span>
                        )}
                      </div>
                    </th>
                    <th 
                      className="px-6 py-4 text-right text-sm font-bold text-text-primary cursor-pointer hover:text-primary-400 transition-colors duration-200"
                      onClick={() => {
                        if (sortBy === 'score') {
                          setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                        } else {
                          setSortBy('score');
                          setSortOrder('desc');
                        }
                      }}
                    >
                      <div className="flex items-center justify-end space-x-1">
                        <span>Ocena</span>
                        {sortBy === 'score' && (
                          <span className="text-primary-400">
                            {sortOrder === 'asc' ? '▲' : '▼'}
                          </span>
                        )}
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCompanies.map((company, index) => {
                    const trend = getTrendMomentum(company.change_percent);
                    const rsi = calculateRSI(company.change_percent);
                    const rsiInfo = getRSIInterpretation(rsi);
                    const isPositive = company.change_percent >= 0;
                    
                    return (
                      <tr
                        key={company.symbol}
                        onClick={() => {
                          setSelectedCompany(company);
                          setShowAnalysisModal(false);
                        }}
                        className={`border-b border-border-subtle hover:bg-surface-hover transition-all duration-200 cursor-pointer group ${
                          index % 2 === 0 ? 'bg-surface-elevated' : 'bg-transparent'
                        }`}
                      >
                        {/* Symbol - Always visible */}
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-2">
                            <div className="flex flex-col space-y-1">
                              <span className="text-lg font-bold text-primary-400 font-mono group-hover:text-primary-300 transition-colors duration-200">
                                {company.symbol}
                              </span>
                              {/* Company name on mobile */}
                              <span className="text-xs text-text-secondary md:hidden truncate max-w-[120px]">
                                {company.company_name}
                              </span>
                            </div>
                            {/* Watchlist Button */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleToggleWatchlist(company);
                              }}
                              className="p-1.5 rounded-lg hover:bg-surface-hover transition-colors"
                              title={isInWatchlist(company.symbol) ? 'Usuń z obserwowanych' : 'Dodaj do obserwowanych'}
                            >
                              {isInWatchlist(company.symbol) ? (
                                <Heart className="w-4 h-4 text-danger-400 fill-current" />
                              ) : (
                                <HeartOff className="w-4 h-4 text-text-tertiary hover:text-danger-400" />
                              )}
                            </button>
                          </div>
                        </td>

                        {/* Company Name - Hidden on mobile */}
                        <td className="px-6 py-4 hidden md:table-cell">
                          <span className="text-sm text-text-primary group-hover:text-text-secondary transition-colors duration-200">
                            {company.company_name}
                          </span>
                        </td>

                        {/* Trend - Hidden on mobile/tablet */}
                        <td className="px-6 py-4 hidden lg:table-cell">
                          <div className="flex items-center space-x-2">
                            <div className={`p-1.5 rounded-lg ${
                              trend.direction === 'upward' ? 'bg-success-gradient/10' : 
                              trend.direction === 'downward' ? 'bg-danger-gradient/10' : 'bg-surface-hover'
                            }`}>
                              {trend.direction === 'upward' && <TrendingUp className="w-4 h-4 text-success-400" />}
                              {trend.direction === 'downward' && <TrendingDown className="w-4 h-4 text-danger-400" />}
                            </div>
                            <span className={`text-xs font-medium ${trend.color}`}>
                              {trend.labelPL}
                            </span>
                          </div>
                        </td>

                        {/* Price - Always visible */}
                        <td className="px-6 py-4 text-right">
                          <div className="flex flex-col items-end space-y-1">
                            <span className="text-lg font-bold text-text-primary font-mono">
                              {formatPLN(company.current_price)}
                            </span>
                            {/* Trend on mobile */}
                            <div className="flex items-center space-x-1 lg:hidden">
                              {trend.direction === 'upward' && <TrendingUp className="w-3 h-3 text-success-400" />}
                              {trend.direction === 'downward' && <TrendingDown className="w-3 h-3 text-danger-400" />}
                              <span className={`text-xs ${trend.color}`}>
                                {trend.labelPL}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* Change - Always visible */}
                        <td className="px-6 py-4 text-right">
                          <div className="flex flex-col items-end space-y-1">
                            <div className={`flex items-center space-x-1 px-2 py-1 rounded-lg ${
                              isPositive ? 'bg-success-gradient/10' : 'bg-danger-gradient/10'
                            }`}>
                              <span className={`text-sm font-bold font-mono ${isPositive ? 'text-success-400' : 'text-danger-400'}`}>
                                {company.change_percent >= 0 ? '↑' : '↓'} {formatPercent(company.change_percent)}
                              </span>
                            </div>
                            {/* RSI on mobile */}
                            <div className="lg:hidden">
                              <span className={`badge text-xs ${
                                rsiInfo.labelPL === 'Wykupiony' ? 'badge-danger' :
                                rsiInfo.labelPL === 'Wyprzedany' ? 'badge-success' : 'badge-neutral'
                              }`}>
                                RSI {rsi}
                              </span>
                            </div>
                          </div>
                        </td>

                        {/* RSI - Hidden on mobile/tablet */}
                        <td className="px-6 py-4 text-right hidden lg:table-cell">
                          <div className="flex items-center justify-end space-x-2">
                            <span className={`text-sm font-semibold font-mono ${rsiInfo.color}`}>
                              {rsi}
                            </span>
                            <span className={`badge text-xs ${
                              rsiInfo.labelPL === 'Wykupiony' ? 'badge-danger' :
                              rsiInfo.labelPL === 'Wyprzedany' ? 'badge-success' : 'badge-neutral'
                            }`}>
                              {rsiInfo.labelPL}
                            </span>
                          </div>
                        </td>

                        {/* P/E - Hidden except desktop */}
                        <td className="px-6 py-4 text-right hidden xl:table-cell">
                          <span className="text-sm text-text-secondary font-mono">
                            {company.pe_ratio ? company.pe_ratio.toFixed(2) : 'N/A'}
                          </span>
                        </td>

                        {/* Score - Always visible */}
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end space-x-3">
                            {/* Progress bar */}
                            <div className="w-16 lg:w-24 h-2 bg-surface-hover rounded-full overflow-hidden">
                              <div
                                className="h-full rounded-full transition-all duration-300"
                                style={{
                                  width: `${company.score}%`,
                                  background: company.score && company.score > 70 
                                    ? 'linear-gradient(90deg, #10B981, #059669)' 
                                    : company.score && company.score > 40
                                    ? 'linear-gradient(90deg, #F59E0B, #D97706)'
                                    : 'linear-gradient(90deg, #EF4444, #DC2626)'
                                }}
                              ></div>
                            </div>
                            {/* Score value */}
                            <span className="text-sm font-semibold text-text-secondary font-mono min-w-[40px]">
                              {company.score}%
                            </span>
                            {/* Analysis button */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedCompany(company);
                                setShowAnalysisModal(true);
                              }}
                              className="p-1.5 rounded-lg hover:bg-primary-gradient/20 text-primary-400 hover:text-primary-300 transition-all duration-250"
                              title="Szczegółowa analiza"
                            >
                              <Activity className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            
            {/* Mobile-friendly pagination hint */}
            {filteredCompanies.length > 20 && (
              <div className="p-4 bg-surface-hover border-t border-border-subtle text-center">
                <p className="text-sm text-text-tertiary">
                  Pokazano {filteredCompanies.length} spółek. Użyj filtrów aby zawęzić wyniki.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Enhanced Heat Map View */}
        {viewMode === 'heatmap' && (
          <div className="bg-surface-elevated rounded-xl p-8 border border-border-subtle">
            <div className="grid grid-cols-3 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-3">
              {filteredCompanies.map((company) => {
                const trend = getTrendMomentum(company.change_percent);
                const isPositive = company.change_percent >= 0;
                const intensity = Math.min(Math.abs(company.change_percent) / 10, 1); // Cap at 10% for color intensity
                
                return (
                  <div
                    key={company.symbol}
                    onClick={() => setSelectedCompany(company)}
                    className="relative rounded-xl p-4 flex flex-col items-center justify-center text-center cursor-pointer hover:scale-105 hover:z-10 transition-all duration-250 min-h-[100px] group border border-border-subtle hover:border-white/20"
                    style={{ 
                      backgroundColor: getHeatMapColor(company.change_percent),
                      boxShadow: `0 4px 20px ${getHeatMapColor(company.change_percent)}20`
                    }}
                  >
                    {/* Company symbol */}
                    <span className="text-sm font-bold text-white font-mono mb-1 drop-shadow-lg">
                      {company.symbol}
                    </span>
                    
                    {/* Change percentage */}
                    <div className="flex items-center space-x-1 mb-1">
                      {trend.direction === 'upward' && <TrendingUp className="w-3 h-3 text-white drop-shadow-lg" />}
                      {trend.direction === 'downward' && <TrendingDown className="w-3 h-3 text-white drop-shadow-lg" />}
                      <span className="text-sm font-bold text-white font-mono drop-shadow-lg">
                        {formatPercent(company.change_percent)}
                      </span>
                    </div>
                    
                    {/* Price on hover */}
                    <span className="text-xs text-white/80 opacity-0 group-hover:opacity-100 transition-opacity duration-250 drop-shadow-lg">
                      {formatPLN(company.current_price)}
                    </span>
                    
                    {/* Detailed hover overlay */}
                    <div className="absolute inset-0 bg-black/90 opacity-0 group-hover:opacity-100 transition-opacity duration-250 rounded-xl flex flex-col items-center justify-center p-3 space-y-2">
                      <p className="text-sm text-white font-semibold mb-1 line-clamp-2 text-center">
                        {company.company_name}
                      </p>
                      <div className="space-y-1 text-center">
                        <p className="text-sm text-white/90 font-mono font-bold">
                          {formatPLN(company.current_price)}
                        </p>
                        <div className="flex items-center space-x-1">
                          <span className={`text-xs px-1.5 py-0.5 rounded font-semibold ${
                            isPositive ? 'bg-success-gradient' : 'bg-danger-gradient'
                          } text-white`}>
                            {formatPercent(company.change_percent)}
                          </span>
                        </div>
                        <p className="text-xs text-white/70">{trend.labelPL}</p>
                        {company.score && (
                          <div className="flex items-center space-x-1">
                            <span className="text-xs text-white/70">Ocena:</span>
                            <span className="text-xs font-semibold text-white">{company.score}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Performance indicator */}
                    <div className="absolute top-1 right-1">
                      <div className={`w-2 h-2 rounded-full ${
                        Math.abs(company.change_percent) > 5 ? 'bg-white animate-pulse-slow' : 'bg-white/50'
                      }`}></div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Legend */}
            <div className="mt-8 flex items-center justify-center space-x-8">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-text-tertiary">Legenda:</span>
                <div className="flex items-center space-x-1">
                  <div className="w-4 h-4 rounded bg-success-400"></div>
                  <span className="text-xs text-text-secondary">Wzrost</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-4 h-4 rounded bg-danger-400"></div>
                  <span className="text-xs text-text-secondary">Spadek</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-4 h-4 rounded bg-text-tertiary"></div>
                  <span className="text-xs text-text-secondary">Bez zmian</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Enhanced No Results */}
        {filteredCompanies.length === 0 && (
          <div className="text-center py-20">
            <div className="bg-surface-elevated rounded-xl p-12 border border-border-subtle max-w-md mx-auto">
              <div className="w-16 h-16 mx-auto mb-6 p-4 bg-warning-gradient/10 rounded-xl border border-warning-400/20">
                <AlertTriangle className="w-full h-full text-warning-400" />
              </div>
              <h3 className="text-xl font-semibold text-text-primary mb-3">
                Brak wyników
              </h3>
              <p className="text-text-secondary mb-6">
                Nie znaleziono spółek spełniających wybrane kryteria wyszukiwania.
              </p>
              <div className="space-y-2">
                <p className="text-sm text-text-tertiary">Spróbuj:</p>
                <ul className="text-sm text-text-secondary space-y-1">
                  <li>• Zmienić kategorię filtra</li>
                  <li>• Wyczyścić wyszukiwanie</li>
                  <li>• Wybrać "Wszystkie kategorie"</li>
                </ul>
              </div>
              <button
                onClick={() => {
                  setFilterCategory('all');
                  setSearchTerm('');
                }}
                className="btn-primary mt-6"
              >
                Wyczyść filtry
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Enhanced Footer */}
      <footer className="border-t border-border-subtle bg-surface-elevated/50 backdrop-blur-sm py-8">
        <div className="max-w-screen-2xl mx-auto px-lg md:px-2xl">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-primary-gradient rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-text-inverse" />
              </div>
              <div>
                <p className="text-sm font-semibold text-text-primary">
                  Polish Financial Analysis Platform
                </p>
                <p className="text-xs text-text-tertiary">
                  Dane rynkowe WIG80 w czasie rzeczywistym
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-text-tertiary">Ostatnia aktualizacja:</span>
                <span className="text-xs font-mono text-text-secondary">
                  {lastUpdateInfo.time}
                </span>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-success-400 animate-pulse-slow"></div>
                <span className="text-xs text-success-400 font-medium">LIVE</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-xs text-text-tertiary">Następne odświeżenie:</span>
                <span className="text-xs font-mono font-bold text-primary-400">
                  {countdown}s
                </span>
              </div>
            </div>
          </div>
          
          {/* Additional footer info */}
          <div className="mt-6 pt-6 border-t border-border-subtle text-center">
            <p className="text-xs text-text-tertiary">
              Dane pochodzą ze źródeł publicznych. Platforma służy celom informacyjnym.
            </p>
          </div>
        </div>
      </footer>

      {/* Chart Modal */}
      {selectedCompany && !showAnalysisModal && (
        <ChartModal
          company={selectedCompany}
          onClose={() => setSelectedCompany(null)}
        />
      )}

      {/* Company Analysis Modal */}
      {selectedCompany && showAnalysisModal && (
        <CompanyAnalysisModal
          company={selectedCompany}
          onClose={() => {
            setShowAnalysisModal(false);
            setSelectedCompany(null);
          }}
        />
      )}
    </div>
  );
}
