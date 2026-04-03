from app.engine.backtester import BacktestConfig, EventDrivenBacktester


def test_backtester_output_shape():
    import pandas as pd

    frame = pd.DataFrame(
        {
            "Datetime": pd.date_range("2024-01-01", periods=120, freq="D"),
            "Open": [100 + i * 0.2 for i in range(120)],
            "High": [101 + i * 0.2 for i in range(120)],
            "Low": [99 + i * 0.2 for i in range(120)],
            "Close": [100 + i * 0.2 for i in range(120)],
            "Volume": [1_000_000 for _ in range(120)],
        }
    )

    bt = EventDrivenBacktester()
    res = bt.run(frame, BacktestConfig(strategy_name="ma_crossover", strategy_params={"short_window": 10, "long_window": 20}))

    assert len(res.equity_curve) == len(frame)
    assert len(res.timestamps) == len(frame)
    assert "return" in res.metrics
    assert "sharpe" in res.metrics
