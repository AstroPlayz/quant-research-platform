from app.engine.indicators import bollinger_bands, ma, macd, rsi


def test_ma():
    import pandas as pd

    s = pd.Series([1, 2, 3, 4, 5])
    out = ma(s, 3)
    assert round(out.iloc[-1], 5) == 4.0


def test_rsi_range():
    import pandas as pd

    s = pd.Series([100, 101, 102, 101, 103, 104, 102, 101, 105, 108, 107, 109, 110, 111, 113])
    out = rsi(s, 5)
    assert out.between(0, 100).all()


def test_macd_columns():
    import pandas as pd

    s = pd.Series(range(1, 40))
    out = macd(s)
    assert set(out.columns) == {"macd", "macd_signal", "macd_hist"}


def test_bollinger_columns():
    import pandas as pd

    s = pd.Series(range(1, 40))
    out = bollinger_bands(s)
    assert set(out.columns) == {"bb_mid", "bb_upper", "bb_lower"}
