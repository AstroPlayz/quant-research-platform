'use client'

import { useEffect, useMemo, useState } from 'react'

import ControlSlider from './ControlSlider'
import MetricCard from './MetricCard'
import PlotlyChart from './PlotlyChart'
import { listStrategies, loadStrategy, runBacktest, runGenetic, runGridSearch, saveStrategy } from '../lib/api'

function pct(value) {
  return `${(value * 100).toFixed(2)}%`
}

export default function Dashboard() {
  const [symbol, setSymbol] = useState('AAPL')
  const [period, setPeriod] = useState('1y')
  const [strategy, setStrategy] = useState('combined')

  const [shortWindow, setShortWindow] = useState(20)
  const [longWindow, setLongWindow] = useState(50)
  const [rsiPeriod, setRsiPeriod] = useState(14)
  const [rsiLower, setRsiLower] = useState(30)
  const [rsiUpper, setRsiUpper] = useState(70)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [backtest, setBacktest] = useState(null)

  const [savedNames, setSavedNames] = useState([])
  const [selectedSaved, setSelectedSaved] = useState('')

  const params = useMemo(
    () => ({
      short_window: shortWindow,
      long_window: longWindow,
      rsi_period: rsiPeriod,
      rsi_lower: rsiLower,
      rsi_upper: rsiUpper,
    }),
    [shortWindow, longWindow, rsiPeriod, rsiLower, rsiUpper],
  )

  async function refresh() {
    setLoading(true)
    setError('')
    try {
      const data = await runBacktest({
        symbol,
        period,
        interval: '1d',
        strategy,
        params,
      })
      setBacktest(data)
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || 'Backtest failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      refresh()
    }, 250)
    return () => clearTimeout(timer)
  }, [symbol, period, strategy, params])

  useEffect(() => {
    listStrategies().then((d) => setSavedNames(d.strategies || [])).catch(() => {})
  }, [])

  const candles = backtest?.candles
  const result = backtest?.result

  const priceData = useMemo(() => {
    if (!candles || !result) return []

    const traces = [
      {
        x: candles.dates,
        open: candles.open,
        high: candles.high,
        low: candles.low,
        close: candles.close,
        type: 'candlestick',
        name: `${symbol} Price`,
      },
    ]

    for (const [name, values] of Object.entries(result.indicators || {})) {
      if (name.includes('ma') || name.includes('bb_')) {
        traces.push({
          x: candles.dates,
          y: values,
          type: 'scatter',
          mode: 'lines',
          name,
        })
      }
    }

    const buys = (result.trades || []).filter((t) => t.side === 'buy')
    const sells = (result.trades || []).filter((t) => t.side === 'sell')

    traces.push({
      x: buys.map((t) => t.timestamp),
      y: buys.map((t) => t.price),
      mode: 'markers',
      type: 'scatter',
      marker: { color: '#22c55e', symbol: 'triangle-up', size: 8 },
      name: 'Buy',
    })

    traces.push({
      x: sells.map((t) => t.timestamp),
      y: sells.map((t) => t.price),
      mode: 'markers',
      type: 'scatter',
      marker: { color: '#f43f5e', symbol: 'triangle-down', size: 8 },
      name: 'Sell',
    })

    return traces
  }, [candles, result, symbol])

  const equityData = useMemo(() => {
    if (!result) return []
    return [
      {
        x: result.timestamps,
        y: result.equity_curve,
        mode: 'lines',
        type: 'scatter',
        line: { color: '#22d3ee', width: 2 },
        name: 'Equity',
      },
    ]
  }, [result])

  const ddData = useMemo(() => {
    if (!result) return []
    return [
      {
        x: result.timestamps,
        y: result.drawdown_curve,
        mode: 'lines',
        type: 'scatter',
        line: { color: '#f43f5e', width: 2 },
        fill: 'tozeroy',
        name: 'Drawdown',
      },
    ]
  }, [result])

  async function runGrid() {
    const output = await runGridSearch({
      symbol,
      period,
      interval: '1d',
      strategy,
      objective: 'sharpe',
      param_grid: {
        short_window: [10, 15, 20, 25],
        long_window: [40, 50, 60, 80],
        rsi_period: [10, 14, 20],
      },
    })
    alert(`Grid best score: ${output.best_score.toFixed(3)} with ${JSON.stringify(output.best_params)}`)
  }

  async function runGA() {
    const output = await runGenetic({
      symbol,
      period,
      interval: '1d',
      strategy,
      objective: 'sharpe',
      gene_space: {
        short_window: { min_value: 5, max_value: 30, is_int: true },
        long_window: { min_value: 35, max_value: 120, is_int: true },
        rsi_period: { min_value: 5, max_value: 30, is_int: true },
      },
      generations: 8,
      population_size: 14,
      mutation_rate: 0.25,
      seed: 42,
    })
    alert(`GA best score: ${output.best_score.toFixed(3)} with ${JSON.stringify(output.best_params)}`)
  }

  async function onSave() {
    const name = prompt('Strategy name')
    if (!name) return
    await saveStrategy(name, { strategy, params, symbol, period })
    const listing = await listStrategies()
    setSavedNames(listing.strategies || [])
  }

  async function onLoad() {
    if (!selectedSaved) return
    const loaded = await loadStrategy(selectedSaved)
    const payload = loaded.payload || {}
    setStrategy(payload.strategy || 'combined')
    setShortWindow(payload.params?.short_window || 20)
    setLongWindow(payload.params?.long_window || 50)
    setRsiPeriod(payload.params?.rsi_period || 14)
    setRsiLower(payload.params?.rsi_lower || 30)
    setRsiUpper(payload.params?.rsi_upper || 70)
    setSymbol(payload.symbol || 'AAPL')
    setPeriod(payload.period || '1y')
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-4 p-4 md:p-6 lg:flex-row">
      <section className="w-full rounded-2xl border border-slate-700/80 bg-slate-900/80 p-4 shadow-2xl shadow-black/40 md:p-6 lg:max-w-sm">
        <h1 className="text-xl font-semibold text-slate-100">Quant Research Platform</h1>
        <p className="mt-1 text-sm text-slate-400">Event-driven backtesting with optimization and strategy persistence.</p>

        <div className="mt-4 space-y-4">
          <label className="block">
            <p className="mb-2 text-sm text-slate-300">Symbol</p>
            <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" />
          </label>

          <label className="block">
            <p className="mb-2 text-sm text-slate-300">Period</p>
            <select value={period} onChange={(e) => setPeriod(e.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2">
              <option value="6mo">6 Months</option>
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="5y">5 Years</option>
            </select>
          </label>

          <label className="block">
            <p className="mb-2 text-sm text-slate-300">Strategy</p>
            <select value={strategy} onChange={(e) => setStrategy(e.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2">
              <option value="ma_crossover">MA Crossover</option>
              <option value="rsi">RSI</option>
              <option value="combined">Combined</option>
            </select>
          </label>

          <ControlSlider label="MA Short" value={shortWindow} min={2} max={80} onChange={setShortWindow} />
          <ControlSlider label="MA Long" value={longWindow} min={5} max={160} onChange={setLongWindow} />
          <ControlSlider label="RSI Period" value={rsiPeriod} min={5} max={30} onChange={setRsiPeriod} />
          <ControlSlider label="RSI Lower" value={rsiLower} min={10} max={45} onChange={setRsiLower} />
          <ControlSlider label="RSI Upper" value={rsiUpper} min={55} max={90} onChange={setRsiUpper} />

          <div className="grid grid-cols-2 gap-2">
            <button onClick={runGrid} className="rounded bg-cyan-500 px-3 py-2 text-xs font-semibold text-slate-950">Grid Search</button>
            <button onClick={runGA} className="rounded bg-indigo-400 px-3 py-2 text-xs font-semibold text-slate-950">Genetic Opt</button>
            <button onClick={onSave} className="rounded bg-emerald-400 px-3 py-2 text-xs font-semibold text-slate-950">Save Strategy</button>
            <button onClick={onLoad} className="rounded bg-amber-300 px-3 py-2 text-xs font-semibold text-slate-950">Load Strategy</button>
          </div>

          <select value={selectedSaved} onChange={(e) => setSelectedSaved(e.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm">
            <option value="">Select saved strategy</option>
            {savedNames.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
      </section>

      <section className="flex min-w-0 flex-1 flex-col gap-4">
        {error ? <div className="rounded-lg border border-rose-700 bg-rose-950/40 px-4 py-2 text-rose-200">{error}</div> : null}

        <div className="grid gap-3 md:grid-cols-3">
          <MetricCard title="Return" value={result ? pct(result.metrics.return) : '--'} />
          <MetricCard title="Max Drawdown" value={result ? pct(result.metrics.max_drawdown) : '--'} />
          <MetricCard title="Sharpe" value={result ? result.metrics.sharpe.toFixed(2) : '--'} />
          <MetricCard title="Sortino" value={result ? result.metrics.sortino.toFixed(2) : '--'} />
          <MetricCard title="Win Rate" value={result ? pct(result.metrics.win_rate) : '--'} />
          <MetricCard title="Profit Factor" value={result ? result.metrics.profit_factor.toFixed(2) : '--'} />
        </div>

        <article className="rounded-2xl border border-slate-700/80 bg-slate-900/75 p-3">
          <h2 className="mb-2 text-sm font-medium text-slate-200">Candlestick and Indicators</h2>
          <PlotlyChart
            data={priceData}
            layout={{
              paper_bgcolor: 'rgba(0,0,0,0)',
              plot_bgcolor: '#0f172a',
              font: { color: '#cbd5e1' },
              margin: { l: 40, r: 20, t: 10, b: 40 },
              xaxis: { rangeslider: { visible: false }, gridcolor: '#1e293b' },
              yaxis: { gridcolor: '#1e293b' },
              legend: { orientation: 'h', y: 1.1 },
            }}
            style={{ width: '100%', height: '420px' }}
          />
        </article>

        <div className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-2xl border border-slate-700/80 bg-slate-900/75 p-3">
            <h2 className="mb-2 text-sm font-medium text-slate-200">Equity Curve</h2>
            <PlotlyChart
              data={equityData}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: '#0f172a',
                font: { color: '#cbd5e1' },
                margin: { l: 40, r: 20, t: 10, b: 40 },
                xaxis: { gridcolor: '#1e293b' },
                yaxis: { gridcolor: '#1e293b' },
              }}
              style={{ width: '100%', height: '280px' }}
            />
          </article>

          <article className="rounded-2xl border border-slate-700/80 bg-slate-900/75 p-3">
            <h2 className="mb-2 text-sm font-medium text-slate-200">Drawdown</h2>
            <PlotlyChart
              data={ddData}
              layout={{
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: '#0f172a',
                font: { color: '#cbd5e1' },
                margin: { l: 40, r: 20, t: 10, b: 40 },
                xaxis: { gridcolor: '#1e293b' },
                yaxis: { gridcolor: '#1e293b' },
              }}
              style={{ width: '100%', height: '280px' }}
            />
          </article>
        </div>

        <div className="rounded-xl border border-slate-700/80 bg-slate-900/75 px-4 py-3 text-sm text-slate-400">
          {loading ? 'Running backtest...' : `Trades: ${result?.trades?.length || 0}`}
        </div>
      </section>
    </main>
  )
}
