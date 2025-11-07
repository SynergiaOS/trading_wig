import { useEffect, useState, useRef, useCallback } from 'react';
import { X, TrendingUp, TrendingDown, Activity, Target } from 'lucide-react';
import { formatPLN } from '../lib/formatters';
import { generateHistoricalData, calculateTechnicalIndicators, filterByTimeframe, calculatePriceTarget, type CandlestickData, type TechnicalIndicators } from '../lib/chartData';

interface ChartModalProps {
  company: {
    symbol: string;
    company_name: string;
    current_price: number;
    change_percent: number;
    pe_ratio: number | null;
    pb_ratio: number | null;
  };
  onClose: () => void;
}

type Timeframe = '1D' | '1W' | '1M' | '3M' | '1Y';

export default function ChartModal({ company, onClose }: ChartModalProps) {
  const [timeframe, setTimeframe] = useState<Timeframe>('1M');
  const [historicalData, setHistoricalData] = useState<CandlestickData[]>([]);
  const [indicators, setIndicators] = useState<TechnicalIndicators | null>(null);
  const [showIndicators, setShowIndicators] = useState({
    sma20: true,
    sma50: true,
    bollinger: false,
    volume: true,
    rsi: false,
    macd: false
  });
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const volumeCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Generate historical data
    const fullData = generateHistoricalData(
      company.current_price,
      company.change_percent,
      company.symbol,
      365
    );
    
    const filtered = filterByTimeframe(fullData, timeframe);
    setHistoricalData(filtered);
    
    const tech = calculateTechnicalIndicators(fullData);
    setIndicators(tech);
  }, [company, timeframe]);

  const drawChart = useCallback(() => {
    const canvas = canvasRef.current;
    const volumeCanvas = volumeCanvasRef.current;
    if (!canvas || !volumeCanvas || historicalData.length === 0) return;

    const ctx = canvas.getContext('2d');
    const volCtx = volumeCanvas.getContext('2d');
    if (!ctx || !volCtx) return;

    // Set canvas size
    const width = canvas.parentElement?.clientWidth || 800;
    const height = 400;
    const volHeight = 100;
    
    canvas.width = width;
    canvas.height = height;
    volumeCanvas.width = width;
    volumeCanvas.height = volHeight;

    // Clear canvas
    ctx.fillStyle = '#0A0E27';
    ctx.fillRect(0, 0, width, height);
    volCtx.fillStyle = '#0A0E27';
    volCtx.fillRect(0, 0, width, volHeight);

    // Calculate price range
    const prices = historicalData.flatMap(d => [d.high, d.low]);
    const maxPrice = Math.max(...prices);
    const minPrice = Math.min(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = priceRange * 0.1;

    // Calculate volume range
    const volumes = historicalData.map(d => d.volume);
    const maxVolume = Math.max(...volumes);

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = (height / 5) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();

      // Price labels
      const price = maxPrice + padding - ((maxPrice - minPrice + 2 * padding) / 5) * i;
      ctx.fillStyle = '#A1A1AA';
      ctx.font = '12px JetBrains Mono';
      ctx.textAlign = 'right';
      ctx.fillText(price.toFixed(2), width - 5, y - 5);
    }

    // Draw candlesticks
    const candleWidth = Math.max(2, (width / historicalData.length) * 0.6);
    const candleSpacing = width / historicalData.length;

    historicalData.forEach((candle, index) => {
      const x = index * candleSpacing + candleSpacing / 2;
      const openY = ((maxPrice + padding - candle.open) / (maxPrice - minPrice + 2 * padding)) * height;
      const closeY = ((maxPrice + padding - candle.close) / (maxPrice - minPrice + 2 * padding)) * height;
      const highY = ((maxPrice + padding - candle.high) / (maxPrice - minPrice + 2 * padding)) * height;
      const lowY = ((maxPrice + padding - candle.low) / (maxPrice - minPrice + 2 * padding)) * height;

      const isGreen = candle.close >= candle.open;
      ctx.strokeStyle = isGreen ? '#10B981' : '#EF4444';
      ctx.fillStyle = isGreen ? '#10B981' : '#EF4444';

      // Draw wick
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, highY);
      ctx.lineTo(x, lowY);
      ctx.stroke();

      // Draw body
      const bodyTop = Math.min(openY, closeY);
      const bodyHeight = Math.abs(closeY - openY) || 1;
      ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, bodyHeight);

      // Draw volume bar
      const volY = ((maxVolume - candle.volume) / maxVolume) * volHeight;
      volCtx.fillStyle = isGreen ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)';
      volCtx.fillRect(x - candleWidth / 2, volY, candleWidth, volHeight - volY);
    });

    // Draw indicators
    if (indicators) {
      // SMA 20
      if (showIndicators.sma20) {
        drawLine(ctx, indicators.sma20, '#3B82F6', 2);
      }

      // SMA 50
      if (showIndicators.sma50) {
        drawLine(ctx, indicators.sma50, '#F59E0B', 2);
      }

      // Bollinger Bands
      if (showIndicators.bollinger) {
        drawLine(ctx, indicators.bollingerUpper, '#06B6D4', 1, [5, 5]);
        drawLine(ctx, indicators.bollingerMiddle, '#06B6D4', 1);
        drawLine(ctx, indicators.bollingerLower, '#06B6D4', 1, [5, 5]);
      }
    }

    function drawLine(
      context: CanvasRenderingContext2D,
      values: number[],
      color: string,
      lineWidth: number,
      dash: number[] = []
    ) {
      const startIndex = Math.max(0, historicalData.length - values.length);
      context.strokeStyle = color;
      context.lineWidth = lineWidth;
      context.setLineDash(dash);
      context.beginPath();

      let started = false;
      historicalData.forEach((_, index) => {
        const valueIndex = index - startIndex;
        if (valueIndex < 0 || valueIndex >= values.length) return;

        const value = values[valueIndex];
        if (isNaN(value)) return;

        const x = index * candleSpacing + candleSpacing / 2;
        const y = ((maxPrice + padding - value) / (maxPrice - minPrice + 2 * padding)) * height;

        if (!started) {
          context.moveTo(x, y);
          started = true;
        } else {
          context.lineTo(x, y);
        }
      });

      context.stroke();
      context.setLineDash([]);
    }
  }, [historicalData, indicators, showIndicators]);

  useEffect(() => {
    if (historicalData.length > 0 && canvasRef.current) {
      drawChart();
    }
  }, [historicalData, showIndicators, drawChart]);

  const priceTarget = indicators ? calculatePriceTarget(historicalData, indicators) : null;
  const currentRSI = indicators ? indicators.rsi[indicators.rsi.length - 1] : 50;
  const latestMACD = indicators ? indicators.macd[indicators.macd.length - 1] : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
      <div className="bg-bg-near-black rounded-lg shadow-modal border-subtle w-full max-w-7xl max-h-[90vh] overflow-y-auto custom-scrollbar">
        {/* Header */}
        <div className="sticky top-0 bg-bg-pure-black border-b border-subtle p-xl flex items-center justify-between z-10">
          <div>
            <h2 className="text-3xl font-bold text-text-primary font-display flex items-center space-x-3">
              <span>{company.symbol}</span>
              <span className={`text-2xl font-semibold font-mono ${
                company.change_percent >= 0 ? 'text-accent-success' : 'text-accent-danger'
              }`}>
                {company.change_percent >= 0 ? '+' : ''}{company.change_percent.toFixed(2)}%
              </span>
            </h2>
            <p className="text-base text-text-secondary mt-1">{company.company_name}</p>
            <p className="text-2xl font-bold text-text-primary font-mono mt-2">
              {formatPLN(company.current_price)}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-3 hover:bg-bg-surface-hover rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-text-secondary" />
          </button>
        </div>

        {/* Timeframe Selector */}
        <div className="p-xl border-b border-subtle">
          <div className="flex items-center space-x-4">
            {(['1D', '1W', '1M', '3M', '1Y'] as Timeframe[]).map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-lg py-sm rounded-lg text-base font-semibold transition-all ${
                  timeframe === tf
                    ? 'bg-accent-primary text-text-inverse'
                    : 'bg-bg-surface-dark text-text-secondary hover:bg-bg-surface-hover'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* Chart */}
        <div className="p-xl">
          <div className="bg-bg-pure-black rounded-lg p-lg border-subtle">
            <canvas ref={canvasRef} className="w-full" />
            {showIndicators.volume && (
              <canvas ref={volumeCanvasRef} className="w-full mt-2" />
            )}
          </div>
        </div>

        {/* Technical Indicators Toggle */}
        <div className="px-xl pb-xl">
          <h3 className="text-xl font-semibold text-text-primary mb-lg">Wskaźniki techniczne</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-md">
            {Object.entries({
              sma20: 'SMA 20',
              sma50: 'SMA 50',
              bollinger: 'Bollinger',
              volume: 'Wolumen',
              rsi: 'RSI',
              macd: 'MACD'
            }).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setShowIndicators(prev => ({ ...prev, [key]: !prev[key as keyof typeof prev] }))}
                className={`px-lg py-md rounded-lg text-sm font-medium transition-all ${
                  showIndicators[key as keyof typeof showIndicators]
                    ? 'bg-accent-primary text-text-inverse'
                    : 'bg-bg-surface-dark text-text-secondary hover:bg-bg-surface-hover'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Technical Analysis Summary */}
        <div className="px-xl pb-xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-xl">
            {/* Price Target */}
            {priceTarget && (
              <div className="bg-bg-surface-dark rounded-lg p-xl border-subtle">
                <div className="flex items-center space-x-3 mb-md">
                  <Target className="w-6 h-6 text-accent-info" />
                  <h4 className="text-lg font-semibold text-text-primary">Cel cenowy</h4>
                </div>
                <p className="text-3xl font-bold text-accent-info font-mono mb-2">
                  {formatPLN(priceTarget.target)}
                </p>
                <p className="text-sm text-text-secondary mb-3">{priceTarget.reasoningPL}</p>
                <div className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                  priceTarget.confidence === 'high'
                    ? 'bg-accent-success/20 text-accent-success'
                    : priceTarget.confidence === 'medium'
                    ? 'bg-accent-warning/20 text-accent-warning'
                    : 'bg-text-tertiary/20 text-text-tertiary'
                }`}>
                  Pewność: {priceTarget.confidence === 'high' ? 'Wysoka' : priceTarget.confidence === 'medium' ? 'Średnia' : 'Niska'}
                </div>
              </div>
            )}

            {/* RSI */}
            <div className="bg-bg-surface-dark rounded-lg p-xl border-subtle">
              <div className="flex items-center space-x-3 mb-md">
                <Activity className="w-6 h-6 text-accent-primary" />
                <h4 className="text-lg font-semibold text-text-primary">RSI (14)</h4>
              </div>
              <p className="text-3xl font-bold text-accent-primary font-mono mb-2">
                {currentRSI.toFixed(1)}
              </p>
              <div className="w-full h-3 bg-bg-surface-hover rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full transition-all ${
                    currentRSI >= 70 ? 'bg-accent-danger' : currentRSI <= 30 ? 'bg-accent-success' : 'bg-accent-primary'
                  }`}
                  style={{ width: `${currentRSI}%` }}
                />
              </div>
              <p className="text-sm text-text-secondary">
                {currentRSI >= 70 ? 'Wykupione' : currentRSI <= 30 ? 'Wyprzedane' : 'Neutralne'}
              </p>
            </div>

            {/* MACD */}
            <div className="bg-bg-surface-dark rounded-lg p-xl border-subtle">
              <div className="flex items-center space-x-3 mb-md">
                {latestMACD >= 0 ? (
                  <TrendingUp className="w-6 h-6 text-accent-success" />
                ) : (
                  <TrendingDown className="w-6 h-6 text-accent-danger" />
                )}
                <h4 className="text-lg font-semibold text-text-primary">MACD</h4>
              </div>
              <p className={`text-3xl font-bold font-mono mb-2 ${
                latestMACD >= 0 ? 'text-accent-success' : 'text-accent-danger'
              }`}>
                {latestMACD.toFixed(2)}
              </p>
              <p className="text-sm text-text-secondary">
                {latestMACD >= 0 ? 'Sygnał wzrostowy' : 'Sygnał spadkowy'}
              </p>
            </div>
          </div>
        </div>

        {/* Support and Resistance Levels */}
        {indicators && (indicators.supportLevels.length > 0 || indicators.resistanceLevels.length > 0) && (
          <div className="px-xl pb-xl">
            <h3 className="text-xl font-semibold text-text-primary mb-lg">Poziomy wsparcia i oporu</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-xl">
              {/* Support Levels */}
              {indicators.supportLevels.length > 0 && (
                <div className="bg-bg-surface-dark rounded-lg p-xl border-subtle">
                  <h4 className="text-lg font-semibold text-accent-success mb-lg">Wsparcie</h4>
                  <div className="space-y-3">
                    {indicators.supportLevels.map((level, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm text-text-secondary">Poziom {index + 1}</span>
                        <span className="text-lg font-bold text-accent-success font-mono">
                          {formatPLN(level)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Resistance Levels */}
              {indicators.resistanceLevels.length > 0 && (
                <div className="bg-bg-surface-dark rounded-lg p-xl border-subtle">
                  <h4 className="text-lg font-semibold text-accent-danger mb-lg">Opór</h4>
                  <div className="space-y-3">
                    {indicators.resistanceLevels.map((level, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm text-text-secondary">Poziom {index + 1}</span>
                        <span className="text-lg font-bold text-accent-danger font-mono">
                          {formatPLN(level)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
