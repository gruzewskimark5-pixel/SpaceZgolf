import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_bitcoin_prices(days=60, initial_price=60000, mu=0.5, sigma=0.6):
    """Simulate Bitcoin prices using Geometric Brownian Motion."""
    dt = 1/365.0
    prices = [initial_price]
    for _ in range(days - 1):
        # S_t = S_{t-1} * exp((mu - sigma^2 / 2) * dt + sigma * sqrt(dt) * Z)
        drift = (mu - 0.5 * sigma**2) * dt
        shock = sigma * np.sqrt(dt) * np.random.normal()
        price = prices[-1] * np.exp(drift + shock)
        prices.append(price)

    dates = [datetime.today() - timedelta(days=days - i) for i in range(days)]
    return pd.DataFrame({'Date': dates, 'Price': prices})

def run_trading_bot():
    # Simulate data
    df = simulate_bitcoin_prices(days=60)

    # Calculate MAs
    df['MA7'] = df['Price'].rolling(window=7).mean()
    df['MA30'] = df['Price'].rolling(window=30).mean()

    # Initialize portfolio
    initial_cash = 10000.0
    cash = initial_cash
    btc = 0.0

    print("=== Daily Trading Ledger ===")

    for index, row in df.iterrows():
        date_str = row['Date'].strftime('%Y-%m-%d')
        price = row['Price']
        ma7 = row['MA7']
        ma30 = row['MA30']

        if pd.isna(ma7) or pd.isna(ma30):
            print(f"{date_str} - Price: ${price:,.2f} - Gathering data for MAs...")
            continue

        # Decision logic
        if ma7 > ma30 and cash > 0:
            btc_bought = cash / price
            print(f"{date_str} - Price: ${price:,.2f} - MA7: ${ma7:,.2f} - MA30: ${ma30:,.2f} | BUYING {btc_bought:.4f} BTC")
            btc = btc_bought
            cash = 0.0

        elif ma7 < ma30 and btc > 0:
            cash_gained = btc * price
            print(f"{date_str} - Price: ${price:,.2f} - MA7: ${ma7:,.2f} - MA30: ${ma30:,.2f} | SELLING {btc:.4f} BTC")
            cash = cash_gained
            btc = 0.0
        else:
            action = "HOLDING BTC" if btc > 0 else "HOLDING CASH"
            print(f"{date_str} - Price: ${price:,.2f} - MA7: ${ma7:,.2f} - MA30: ${ma30:,.2f} | {action}")

    # Final portfolio value
    final_price = df.iloc[-1]['Price']
    final_portfolio_value = cash + (btc * final_price)

    print("\n=== Final Portfolio Performance ===")
    print(f"Initial Investment: ${initial_cash:,.2f}")
    print(f"Final Value:        ${final_portfolio_value:,.2f}")
    print(f"Total Return:       {((final_portfolio_value / initial_cash) - 1) * 100:.2f}%")
    print(f"Holdings:           ${cash:,.2f} Cash, {btc:.4f} BTC")

if __name__ == '__main__':
    np.random.seed(42)
    run_trading_bot()
