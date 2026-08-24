import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta
import btc_sim
from btc_sim import simulate_bitcoin_prices

def test_simulate_bitcoin_prices_basic():
    """Test the basic properties of the returned dataframe."""
    df = simulate_bitcoin_prices(days=30, initial_price=50000)

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ['Date', 'Price']
    assert len(df) == 30
    assert df.iloc[0]['Price'] == 50000

def test_simulate_bitcoin_prices_non_negative():
    """Test that generated prices are non-negative."""
    # Using high volatility to see if prices go negative
    df = simulate_bitcoin_prices(days=100, mu=0.5, sigma=2.0)
    assert (df['Price'] >= 0).all()

def test_simulate_bitcoin_prices_determinism(monkeypatch):
    """Test that setting a numpy seed results in deterministic output."""
    # Mock datetime to return a fixed date so Date columns match exactly
    class MockDatetime(datetime):
        @classmethod
        def today(cls):
            return datetime(2025, 1, 1)

    monkeypatch.setattr(btc_sim, 'datetime', MockDatetime)

    np.random.seed(42)
    df1 = simulate_bitcoin_prices(days=10)

    np.random.seed(42)
    df2 = simulate_bitcoin_prices(days=10)

    pd.testing.assert_frame_equal(df1, df2)

def test_simulate_bitcoin_prices_edge_case_one_day():
    """Test with minimum days=1."""
    df = simulate_bitcoin_prices(days=1, initial_price=100)
    assert len(df) == 1
    assert df.iloc[0]['Price'] == 100

def test_simulate_bitcoin_prices_dates():
    """Test that dates are sequential and end yesterday."""
    df = simulate_bitcoin_prices(days=5)
    # Check that dates are increasing
    assert df['Date'].is_monotonic_increasing

    # Check the last date (i = 4, days = 5)
    # datetime.today() - timedelta(days=5 - 4) = datetime.today() - timedelta(days=1)
    yesterday = datetime.today() - timedelta(days=1)
    last_date = df.iloc[-1]['Date']
    assert abs((yesterday - last_date).total_seconds()) < 10 # Less than 10 seconds diff
