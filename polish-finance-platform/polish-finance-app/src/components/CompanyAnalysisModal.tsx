import { useEffect, useState } from 'react';
import { X, TrendingUp, TrendingDown, Activity, Target, BarChart3, PieChart, AlertTriangle, CheckCircle, Info, Zap, Shield, DollarSign, TrendingUp as TrendUpIcon } from 'lucide-react';
import { formatPLN, formatPercent } from '../lib/formatters';
import { calculateRSI, getRSIInterpretation, getRiskAssessment } from '../lib/trendAnalysis';
import { fetchPatternsData, type CompanyWithPatterns } from '../lib/dataService';
import { checkBackendHealth } from '../lib/backendService';

interface CompanyAnalysisModalProps {
  company: {
    symbol: string;
    company_name: string;
    current_price: number;
    change_percent: number;
    pe_ratio: number | null;
    pb_ratio: number | null;
    trading_volume: string;
    score?: number;
  };
  onClose: () => void;
}

interface TechnicalAnalysis {
  rsi: number;
  macd?: number;
  bollinger_upper?: number;
  bollinger_lower?: number;
  sma_20?: number;
  sma_50?: number;
  support_level?: number;
  resistance_level?: number;
}

interface FundamentalAnalysis {
  value_score: number;
  growth_score: number;
  momentum_score: number;
  overall_score: number;
  recommendation: string;
  risk_level: string;
}

export default function CompanyAnalysisModal({ company, onClose }: CompanyAnalysisModalProps) {
  const [technicalAnalysis, setTechnicalAnalysis] = useState<TechnicalAnalysis | null>(null);
  const [fundamentalAnalysis, setFundamentalAnalysis] = useState<FundamentalAnalysis | null>(null);
  const [patterns, setPatterns] = useState<CompanyWithPatterns | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'technical' | 'fundamental' | 'patterns'>('overview');

  useEffect(() => {
    loadAnalysis();
  }, [company]);

  const loadAnalysis = async () => {
    setLoading(true);
    try {
      // Fetch technical analysis from API
      const analysisApiUrl = import.meta.env.VITE_ANALYSIS_API_URL || 'http://localhost:8001';
      let tech: TechnicalAnalysis | null = null;

      try {
        const techResponse = await fetch(`${analysisApiUrl}/api/analysis/technical/${company.symbol}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: AbortSignal.timeout(5000),
        });

        if (techResponse.ok) {
          const techData = await techResponse.json();
          tech = {
            rsi: techData.rsi || calculateRSI(company.change_percent),
            macd: techData.macd,
            bollinger_upper: techData.bb_upper || techData.bollinger_upper,
            bollinger_lower: techData.bb_lower || techData.bollinger_lower,
            sma_20: techData.sma_20,
            sma_50: techData.sma_50,
            support_level: techData.support_level || company.current_price * 0.92,
            resistance_level: techData.resistance_level || company.current_price * 1.08,
          };
        }
      } catch (apiError) {
        console.warn('Technical analysis API not available, using calculated values:', apiError);
      }

      // Fallback to calculated values if API not available
      if (!tech) {
        const rsi = calculateRSI(company.change_percent);
        tech = {
          rsi,
          sma_20: company.current_price * 0.98,
          sma_50: company.current_price * 0.95,
          bollinger_upper: company.current_price * 1.05,
          bollinger_lower: company.current_price * 0.95,
          support_level: company.current_price * 0.92,
          resistance_level: company.current_price * 1.08,
        };
      }

      setTechnicalAnalysis(tech);

      // Calculate fundamental analysis
      const valueScore = company.pb_ratio && company.pb_ratio < 2 ? 80 : company.pb_ratio && company.pb_ratio < 3 ? 60 : 40;
      const growthScore = company.change_percent > 5 ? 85 : company.change_percent > 0 ? 60 : 30;
      const momentumScore = Math.abs(company.change_percent) > 5 ? 75 : 50;
      const overallScore = (valueScore + growthScore + momentumScore) / 3;

      const recommendation = overallScore > 70 ? 'STRONG_BUY' :
                            overallScore > 55 ? 'BUY' :
                            overallScore > 40 ? 'HOLD' :
                            overallScore > 25 ? 'SELL' : 'STRONG_SELL';

      const riskInfo = getRiskAssessment(company);
      
      setFundamentalAnalysis({
        value_score: valueScore,
        growth_score: growthScore,
        momentum_score: momentumScore,
        overall_score: overallScore,
        recommendation,
        risk_level: riskInfo.level,
      });

      // Load patterns
      try {
        const patternsData = await fetchPatternsData();
        const companyPatterns = patternsData.companies.find(c => c.symbol === company.symbol);
        if (companyPatterns) {
          setPatterns(companyPatterns);
        }
      } catch (error) {
        console.error('Error loading patterns:', error);
      }
    } catch (error) {
      console.error('Error loading analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const rsiInfo = technicalAnalysis ? getRSIInterpretation(technicalAnalysis.rsi) : null;
  const riskInfo = getRiskAssessment(company);

  const getRecommendationColor = (rec: string) => {
    switch (rec) {
      case 'STRONG_BUY': return 'text-success-400';
      case 'BUY': return 'text-success-300';
      case 'HOLD': return 'text-warning-400';
      case 'SELL': return 'text-danger-300';
      case 'STRONG_SELL': return 'text-danger-400';
      default: return 'text-text-secondary';
    }
  };

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'STRONG_BUY': return 'badge-success';
      case 'BUY': return 'badge-success';
      case 'HOLD': return 'badge-warning';
      case 'SELL': return 'badge-danger';
      case 'STRONG_SELL': return 'badge-danger';
      default: return 'badge-neutral';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
        <div className="bg-surface-elevated rounded-xl p-8 border border-border-subtle">
          <div className="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-text-secondary">Ładowanie analizy...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-surface-elevated rounded-xl border border-border-subtle max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-surface-elevated border-b border-border-subtle p-6 flex items-center justify-between z-10">
          <div className="flex-1">
            <h2 className="text-3xl font-bold text-text-primary font-display mb-2">
              {company.symbol}
            </h2>
            <p className="text-text-secondary">{company.company_name}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-surface-hover transition-colors"
          >
            <X className="w-6 h-6 text-text-secondary" />
          </button>
        </div>

        {/* Quick Stats */}
        <div className="p-6 border-b border-border-subtle">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-surface-hover rounded-xl p-4 border border-border-subtle">
              <p className="text-sm text-text-tertiary mb-1">Cena</p>
              <p className="text-2xl font-bold text-text-primary font-mono">
                {formatPLN(company.current_price)}
              </p>
            </div>
            <div className={`bg-surface-hover rounded-xl p-4 border border-border-subtle ${
              company.change_percent >= 0 ? 'border-success-400/30' : 'border-danger-400/30'
            }`}>
              <p className="text-sm text-text-tertiary mb-1">Zmiana</p>
              <p className={`text-2xl font-bold font-mono ${
                company.change_percent >= 0 ? 'text-success-400' : 'text-danger-400'
              }`}>
                {formatPercent(company.change_percent)}
              </p>
            </div>
            <div className="bg-surface-hover rounded-xl p-4 border border-border-subtle">
              <p className="text-sm text-text-tertiary mb-1">P/E</p>
              <p className="text-2xl font-bold text-text-primary font-mono">
                {company.pe_ratio ? company.pe_ratio.toFixed(2) : 'N/A'}
              </p>
            </div>
            <div className="bg-surface-hover rounded-xl p-4 border border-border-subtle">
              <p className="text-sm text-text-tertiary mb-1">P/B</p>
              <p className="text-2xl font-bold text-text-primary font-mono">
                {company.pb_ratio ? company.pb_ratio.toFixed(2) : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-border-subtle px-6">
          <div className="flex space-x-2">
            {[
              { id: 'overview', label: 'Przegląd', icon: BarChart3 },
              { id: 'technical', label: 'Analiza Techniczna', icon: Activity },
              { id: 'fundamental', label: 'Analiza Fundamentalna', icon: DollarSign },
              { id: 'patterns', label: 'Wzorce', icon: Target },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 px-4 py-3 border-b-2 transition-all duration-250 ${
                    activeTab === tab.id
                      ? 'border-primary-400 text-primary-400'
                      : 'border-transparent text-text-secondary hover:text-text-primary'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-semibold">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Recommendation Card */}
              {fundamentalAnalysis && (
                <div className={`bg-gradient-to-br from-surface-elevated to-surface-hover rounded-xl p-6 border-2 ${
                  fundamentalAnalysis.recommendation === 'STRONG_BUY' || fundamentalAnalysis.recommendation === 'BUY'
                    ? 'border-success-400/50'
                    : fundamentalAnalysis.recommendation === 'STRONG_SELL' || fundamentalAnalysis.recommendation === 'SELL'
                    ? 'border-danger-400/50'
                    : 'border-warning-400/50'
                }`}>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-text-primary">Rekomendacja</h3>
                    <span className={`badge ${getRecommendationBadge(fundamentalAnalysis.recommendation)} text-lg px-4 py-2`}>
                      {fundamentalAnalysis.recommendation.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-text-tertiary mb-1">Ocena Ogólna</p>
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 h-2 bg-surface-hover rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              fundamentalAnalysis.overall_score > 70 ? 'bg-success-gradient' :
                              fundamentalAnalysis.overall_score > 40 ? 'bg-warning-gradient' : 'bg-danger-gradient'
                            }`}
                            style={{ width: `${fundamentalAnalysis.overall_score}%` }}
                          />
                        </div>
                        <span className="text-lg font-bold text-text-primary font-mono">
                          {Math.round(fundamentalAnalysis.overall_score)}%
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-text-tertiary mb-1">Wartość</p>
                      <p className="text-xl font-bold text-text-primary font-mono">
                        {Math.round(fundamentalAnalysis.value_score)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-text-tertiary mb-1">Wzrost</p>
                      <p className="text-xl font-bold text-text-primary font-mono">
                        {Math.round(fundamentalAnalysis.growth_score)}%
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Risk Assessment */}
              <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                <div className="flex items-center space-x-3 mb-4">
                  <Shield className="w-6 h-6 text-warning-400" />
                  <h3 className="text-xl font-bold text-text-primary">Ocena Ryzyka</h3>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-2xl font-bold ${
                      riskInfo.level === 'low' ? 'text-success-400' :
                      riskInfo.level === 'medium' ? 'text-warning-400' : 'text-danger-400'
                    }`}>
                      {riskInfo.labelPL}
                    </p>
                    <p className="text-sm text-text-tertiary mt-1">{riskInfo.descriptionPL}</p>
                  </div>
                  <div className={`badge ${
                    riskInfo.level === 'low' ? 'badge-success' :
                    riskInfo.level === 'medium' ? 'badge-warning' : 'badge-danger'
                  } text-lg px-4 py-2`}>
                    {riskInfo.level.toUpperCase()}
                  </div>
                </div>
              </div>

              {/* Technical Summary */}
              {technicalAnalysis && rsiInfo && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center">
                      <Activity className="w-5 h-5 mr-2 text-primary-400" />
                      RSI (Relative Strength Index)
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-text-secondary">Wartość</span>
                        <span className={`text-2xl font-bold font-mono ${rsiInfo.color}`}>
                          {technicalAnalysis.rsi}
                        </span>
                      </div>
                      <div className="w-full h-3 bg-surface-elevated rounded-full overflow-hidden">
                        <div
                          className={`h-full ${
                            technicalAnalysis.rsi > 70 ? 'bg-danger-gradient' :
                            technicalAnalysis.rsi < 30 ? 'bg-success-gradient' : 'bg-warning-gradient'
                          }`}
                          style={{ width: `${technicalAnalysis.rsi}%` }}
                        />
                      </div>
                      <p className={`badge ${
                        rsiInfo.labelPL === 'Wykupiony' ? 'badge-danger' :
                        rsiInfo.labelPL === 'Wyprzedany' ? 'badge-success' : 'badge-warning'
                      }`}>
                        {rsiInfo.labelPL}
                      </p>
                    </div>
                  </div>

                  <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                    <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-primary-400" />
                      Poziomy Wsparcia/Oporu
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-text-secondary">Wsparcie</span>
                        <span className="text-lg font-bold text-success-400 font-mono">
                          {formatPLN(technicalAnalysis.support_level || 0)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-text-secondary">Cena Aktualna</span>
                        <span className="text-lg font-bold text-text-primary font-mono">
                          {formatPLN(company.current_price)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-text-secondary">Opór</span>
                        <span className="text-lg font-bold text-danger-400 font-mono">
                          {formatPLN(technicalAnalysis.resistance_level || 0)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'technical' && technicalAnalysis && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* RSI */}
                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4">RSI</h3>
                  {rsiInfo && (
                    <div className="space-y-4">
                      <div className="text-center">
                        <p className={`text-5xl font-bold font-mono ${rsiInfo.color}`}>
                          {technicalAnalysis.rsi}
                        </p>
                        <p className={`badge mt-2 ${
                          rsiInfo.labelPL === 'Wykupiony' ? 'badge-danger' :
                          rsiInfo.labelPL === 'Wyprzedany' ? 'badge-success' : 'badge-warning'
                        }`}>
                          {rsiInfo.labelPL}
                        </p>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-text-tertiary">Wyprzedany</span>
                          <span className="text-text-tertiary">Wykupiony</span>
                        </div>
                        <div className="w-full h-4 bg-surface-elevated rounded-full overflow-hidden relative">
                          <div className="absolute inset-0 flex">
                            <div className="flex-1 bg-success-gradient/30"></div>
                            <div className="flex-1 bg-warning-gradient/30"></div>
                            <div className="flex-1 bg-danger-gradient/30"></div>
                          </div>
                          <div
                            className="absolute top-0 bottom-0 w-1 bg-text-primary"
                            style={{ left: `${technicalAnalysis.rsi}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-xs text-text-tertiary">
                          <span>0</span>
                          <span>30</span>
                          <span>70</span>
                          <span>100</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Moving Averages */}
                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4">Średnie Kroczące</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">SMA 20</span>
                      <span className="text-lg font-bold text-text-primary font-mono">
                        {formatPLN(technicalAnalysis.sma_20 || 0)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">SMA 50</span>
                      <span className="text-lg font-bold text-text-primary font-mono">
                        {formatPLN(technicalAnalysis.sma_50 || 0)}
                      </span>
                    </div>
                    <div className="pt-4 border-t border-border-subtle">
                      <div className="flex items-center justify-between">
                        <span className="text-text-secondary">Cena Aktualna</span>
                        <span className="text-lg font-bold text-primary-400 font-mono">
                          {formatPLN(company.current_price)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Bollinger Bands */}
                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4">Bollinger Bands</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Górna</span>
                      <span className="text-lg font-bold text-danger-400 font-mono">
                        {formatPLN(technicalAnalysis.bollinger_upper || 0)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Cena</span>
                      <span className="text-lg font-bold text-text-primary font-mono">
                        {formatPLN(company.current_price)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Dolna</span>
                      <span className="text-lg font-bold text-success-400 font-mono">
                        {formatPLN(technicalAnalysis.bollinger_lower || 0)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Support/Resistance */}
                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4">Wsparcie/Opór</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-text-secondary">Poziom Oporu</span>
                        <span className="text-lg font-bold text-danger-400 font-mono">
                          {formatPLN(technicalAnalysis.resistance_level || 0)}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-surface-elevated rounded-full overflow-hidden">
                        <div className="h-full bg-danger-gradient/30" style={{ width: '100%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-text-secondary">Cena Aktualna</span>
                        <span className="text-lg font-bold text-primary-400 font-mono">
                          {formatPLN(company.current_price)}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-surface-elevated rounded-full overflow-hidden">
                        <div className="h-full bg-primary-gradient" style={{ width: '50%', marginLeft: '25%' }} />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-text-secondary">Poziom Wsparcia</span>
                        <span className="text-lg font-bold text-success-400 font-mono">
                          {formatPLN(technicalAnalysis.support_level || 0)}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-surface-elevated rounded-full overflow-hidden">
                        <div className="h-full bg-success-gradient/30" style={{ width: '100%' }} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'fundamental' && fundamentalAnalysis && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center">
                    <DollarSign className="w-5 h-5 mr-2 text-success-400" />
                    Ocena Wartości
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Score</span>
                      <span className="text-2xl font-bold text-text-primary font-mono">
                        {Math.round(fundamentalAnalysis.value_score)}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-surface-elevated rounded-full overflow-hidden">
                      <div
                        className="h-full bg-success-gradient"
                        style={{ width: `${fundamentalAnalysis.value_score}%` }}
                      />
                    </div>
                    <div className="pt-2 border-t border-border-subtle">
                      <p className="text-sm text-text-tertiary">
                        {company.pb_ratio && company.pb_ratio < 2
                          ? 'Spółka jest niedowartościowana'
                          : company.pb_ratio && company.pb_ratio < 3
                          ? 'Spółka jest w rozsądnej wycenie'
                          : 'Spółka może być przewartościowana'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center">
                    <TrendUpIcon className="w-5 h-5 mr-2 text-primary-400" />
                    Ocena Wzrostu
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Score</span>
                      <span className="text-2xl font-bold text-text-primary font-mono">
                        {Math.round(fundamentalAnalysis.growth_score)}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-surface-elevated rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-gradient"
                        style={{ width: `${fundamentalAnalysis.growth_score}%` }}
                      />
                    </div>
                    <div className="pt-2 border-t border-border-subtle">
                      <p className="text-sm text-text-tertiary">
                        {company.change_percent > 5
                          ? 'Silny wzrost cenowy'
                          : company.change_percent > 0
                          ? 'Umiarkowany wzrost'
                          : 'Spadek cenowy'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                  <h3 className="text-lg font-bold text-text-primary mb-4 flex items-center">
                    <Zap className="w-5 h-5 mr-2 text-warning-400" />
                    Ocena Momentum
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Score</span>
                      <span className="text-2xl font-bold text-text-primary font-mono">
                        {Math.round(fundamentalAnalysis.momentum_score)}%
                      </span>
                    </div>
                    <div className="w-full h-3 bg-surface-elevated rounded-full overflow-hidden">
                      <div
                        className="h-full bg-warning-gradient"
                        style={{ width: `${fundamentalAnalysis.momentum_score}%` }}
                      />
                    </div>
                    <div className="pt-2 border-t border-border-subtle">
                      <p className="text-sm text-text-tertiary">
                        {Math.abs(company.change_percent) > 5
                          ? 'Wysoka zmienność'
                          : 'Umiarkowana zmienność'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Financial Ratios */}
              <div className="bg-surface-hover rounded-xl p-6 border border-border-subtle">
                <h3 className="text-lg font-bold text-text-primary mb-4">Wskaźniki Finansowe</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">P/E Ratio</p>
                    <p className="text-xl font-bold text-text-primary font-mono">
                      {company.pe_ratio ? company.pe_ratio.toFixed(2) : 'N/A'}
                    </p>
                    <p className="text-xs text-text-tertiary mt-1">
                      {company.pe_ratio && company.pe_ratio < 15
                        ? 'Niskie (wartościowe)'
                        : company.pe_ratio && company.pe_ratio < 25
                        ? 'Średnie'
                        : 'Wysokie'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">P/B Ratio</p>
                    <p className="text-xl font-bold text-text-primary font-mono">
                      {company.pb_ratio ? company.pb_ratio.toFixed(2) : 'N/A'}
                    </p>
                    <p className="text-xs text-text-tertiary mt-1">
                      {company.pb_ratio && company.pb_ratio < 2
                        ? 'Niskie (wartościowe)'
                        : company.pb_ratio && company.pb_ratio < 3
                        ? 'Średnie'
                        : 'Wysokie'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">Wolumen</p>
                    <p className="text-xl font-bold text-text-primary font-mono">
                      {company.trading_volume}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-text-tertiary mb-1">Ocena Ogólna</p>
                    <p className="text-xl font-bold text-text-primary font-mono">
                      {company.score || 0}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'patterns' && (
            <div className="space-y-6">
              {patterns && patterns.patterns && patterns.patterns.length > 0 ? (
                <div className="space-y-4">
                  {patterns.patterns.map((pattern, index) => {
                    const directionColor = pattern.direction === 'bullish' ? 'success' :
                                         pattern.direction === 'bearish' ? 'danger' : 'warning';
                    
                    return (
                      <div
                        key={index}
                        className="bg-surface-hover rounded-xl p-6 border border-border-subtle"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-xl font-bold text-text-primary">
                            {pattern.pattern_name}
                          </h3>
                          <span className={`badge badge-${directionColor}`}>
                            {pattern.direction.toUpperCase()}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-sm text-text-tertiary mb-1">Siła</p>
                            <p className="text-lg font-bold text-text-primary">
                              {Math.round(pattern.strength * 100)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-text-tertiary mb-1">Pewność</p>
                            <p className="text-lg font-bold text-text-primary">
                              {Math.round(pattern.confidence * 100)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-text-tertiary mb-1">Prawdopodobieństwo</p>
                            <p className="text-lg font-bold text-text-primary">
                              {Math.round(pattern.probability * 100)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-text-tertiary mb-1">Czas trwania</p>
                            <p className="text-lg font-bold text-text-primary">
                              {pattern.duration}
                            </p>
                          </div>
                        </div>
                        {Object.keys(pattern.key_levels).length > 0 && (
                          <div className="mt-4 pt-4 border-t border-border-subtle">
                            <p className="text-sm text-text-tertiary mb-2">Kluczowe poziomy:</p>
                            <div className="flex flex-wrap gap-2">
                              {Object.entries(pattern.key_levels).map(([key, value]) => (
                                <span
                                  key={key}
                                  className="px-3 py-1 bg-surface-elevated rounded-lg text-sm text-text-secondary border border-border-subtle"
                                >
                                  {key}: {formatPLN(value)}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <AlertTriangle className="w-16 h-16 text-text-tertiary mx-auto mb-4" />
                  <p className="text-text-secondary">Brak wykrytych wzorców technicznych dla tej spółki</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

