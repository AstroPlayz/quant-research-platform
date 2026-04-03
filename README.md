# Quantitative Strategy Analytics Platform

Full-stack quantitative research and backtesting platform with:

- FastAPI backend for strategy simulation and optimization
- Next.js frontend for interactive analysis
- Plotly visualizations for price, equity, and drawdown

This README explains both developer architecture and end-user behavior in detail, including what every dashboard control means.

## 1. What This App Does

You choose:

- A symbol such as AAPL
- A history window such as 1 year
- A strategy (MA crossover, RSI, or combined)
- Parameters via sliders

The backend then:

- Loads market data from Yahoo Finance (with local cache)
- Generates strategy signals
- Simulates realistic trade execution with transaction costs and slippage
- Tracks portfolio equity over time
- Computes performance metrics

The frontend displays:

- Candlestick chart with indicator overlays and trade markers
- Equity curve
- Drawdown curve
- Performance cards

## 2. Quick Start

### Backend

```bash
cd backend
python -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open the app at http://localhost:3000.

## 3. Dashboard Guide (Everything on the Webpage)

The main UI lives in frontend/components/Dashboard.jsx.

### Left Control Panel

1. Symbol
- Text input for ticker (example: AAPL, MSFT, NVDA)
- Sent to backend as symbol

2. Period
- Dropdown controlling historical lookback
- Options: 6 months, 1 year, 2 years, 5 years
- Affects number of candles, number of signals, and optimization behavior

3. Strategy
- Dropdown selecting strategy logic:
  - MA Crossover
  - RSI
  - Combined

4. Sliders

MA Short
- Short moving average window
- Lower values react faster to price changes
- Higher values are smoother and slower

MA Long
- Long moving average window
- Usually greater than short window

RSI Period
- Number of bars used to compute RSI
- Smaller period means more volatile RSI

RSI Lower
- Oversold threshold for RSI strategy entries
- Typical values around 20 to 35

RSI Upper
- Overbought threshold for RSI strategy exits
- Typical values around 65 to 80

5. Buttons

Grid Search
- Tries a predefined parameter grid
- Ranks combinations by selected objective (currently Sharpe)

Genetic Opt
- Runs a genetic algorithm to search parameter space
- Useful when full grid would be expensive

Save Strategy
- Stores current strategy + params + symbol + period in backend storage

Load Strategy
- Loads a previously saved strategy configuration

Select saved strategy
- Dropdown listing all saved strategy names

### Right Analytics Panel

1. Metric Cards

Return
- Total strategy return over selected period
- Formula: final_equity / initial_equity - 1

Max Drawdown
- Largest peak-to-trough decline in equity
- Usually negative

Sharpe
- Risk-adjusted return using total volatility
- Annualized by sqrt(252)

Sortino
- Risk-adjusted return using downside volatility only

Win Rate
- Percent of closed trades with positive pnl

Profit Factor
- gross_profit / gross_loss
- Above 1 means gains exceed losses

2. Candlestick and Indicators chart
- Candles show OHLC prices
- Overlays can include MA and Bollinger lines
- Green triangles mark buys
- Red triangles mark sells

3. Equity Curve chart
- Portfolio value over time
- Should move when trades are executed and/or open positions are marked to market

4. Drawdown chart
- Running drawdown through time
- Helps visualize depth and duration of losses

5. Status bar
- Shows running state and total trade count

## 4. Glossary of Key Terms

Backtest
- Simulation of historical strategy performance

Signal
- Strategy instruction per bar:
  - 1 = buy
  - -1 = sell
  - 0 = hold

Position
- Whether portfolio is currently invested:
  - 0 = flat
  - 1 = long

Entry Price
- Fill price when a new long is opened

Equity
- cash + shares * current_price

Drawdown
- Percentage drop from running equity peak

Slippage
- Adverse execution price adjustment to mimic real fills

Transaction Cost
- Fee per trade side

Buy and Hold baseline
- Invest all cash in first bar and hold to end
- Used to compare active strategy against passive exposure

MA (Moving Average)
- Rolling mean of closing prices

RSI (Relative Strength Index)
- Momentum oscillator between 0 and 100

MACD
- Difference of fast and slow EMAs plus signal line

Bollinger Bands
- Midline moving average with upper/lower bands around volatility

## 5. Strategy Behavior Summary

### MA Crossover
- Buy when short MA is above long MA
- Sell when short MA is below long MA

### RSI
- Buy when RSI is below lower threshold
- Sell when RSI is above upper threshold

### Combined
- Uses MA, RSI, and MACD logic together
- Built to fire more realistically than strict all-conditions-must-match logic

## 6. Portfolio Simulation Rules

Current backtester uses realistic long-only simulation:

1. Start with initial cash (default 10,000)
2. On buy signal while flat:
  - Buy shares
  - Apply transaction cost and slippage
  - Store entry price
3. On sell signal while long:
  - Close shares
  - Apply transaction cost and slippage
  - Realize pnl
4. On every bar:
  - Mark to market and append equity

## 7. Metrics Formulas

Let equity_t be portfolio equity at time t.

Period return series:

returns_t = equity_t / equity_(t-1) - 1

Total return:

total_return = equity_final / equity_initial - 1

Max drawdown:

drawdown_t = equity_t / running_peak_t - 1

max_drawdown = min(drawdown_t)

Sharpe:

sharpe = mean(returns) / std(returns) * sqrt(252)

Win rate:

win_rate = number_of_profitable_closed_trades / total_closed_trades

Profit factor:

profit_factor = gross_profit / gross_loss

## 8. API Overview

Main endpoint used by the dashboard:

- POST /api/backtest

Response includes both compatibility and explicit fields:

- result.equity_curve
- result.drawdown_curve
- result.buy_hold_equity
- result.trades
- result.metrics

Also exposed top-level aliases:

- equity_curve
- drawdown
- buy_hold_equity
- trades
- metrics

Other endpoints:

- GET /health
- POST /api/optimize/grid
- POST /api/optimize/genetic
- POST /api/strategy-builder/run
- POST /api/strategies/save
- GET /api/strategies
- GET /api/strategies/{name}
- POST /api/export

## 9. Project Structure

### Backend

- backend/app/main.py
- backend/app/api/routes.py
- backend/app/api/schemas.py
- backend/app/data/yahoo_data.py
- backend/app/data/cache.py
- backend/app/data/strategy_store.py
- backend/app/engine/indicators.py
- backend/app/engine/strategies.py
- backend/app/engine/portfolio.py
- backend/app/engine/backtester.py
- backend/app/engine/metrics.py
- backend/app/optimization/grid_search.py
- backend/app/optimization/genetic.py

### Frontend

- frontend/app/page.js
- frontend/components/Dashboard.jsx
- frontend/components/PlotlyChart.jsx
- frontend/components/MetricCard.jsx
- frontend/components/ControlSlider.jsx
- frontend/lib/api.js

## 10. Testing

Run backend tests:

```bash
cd backend
source ../.venv/bin/activate
pytest
```

## 11. Deployment

Free deployment setup files are included:

- Dockerfile for Hugging Face Spaces backend deployment
- frontend/vercel.json for frontend
- DEPLOYMENT_GUIDE.md with step-by-step instructions

## 12. Practical Notes and Pitfalls

1. Free hosting tiers can sleep when idle, causing first-request latency.
2. Metrics can vary significantly by period and symbol.
3. Overfitting is easy when repeatedly tuning on one ticker/time range.
4. Backtest performance is not a guarantee of live performance.
5. Costs and slippage materially change strategy outcomes.

## 13. Disclaimer

This project is for education and research. It is not financial advice.
