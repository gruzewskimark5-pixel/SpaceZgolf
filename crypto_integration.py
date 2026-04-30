#!/usr/bin/env python3
from web3 import Web3
import ccxt
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timezone

load_dotenv()

ALCHEMY_URL = os.getenv("ALCHEMY_URL")          # e.g. https://eth-mainnet.g.alchemy.com/v2/...
WEB3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
EXCHANGE = ccxt.binance({'enableRateLimit': True})

# Fallback for local testing when ALCHEMY_URL is not provided
if not ALCHEMY_URL:
    WEB3 = Web3(Web3.HTTPProvider("https://cloudflare-eth.com"))
else:
    WEB3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

def get_onchain_balance(address, token_contract=None):
    if token_contract:
        # ERC-20 balance
        abi = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]
        contract = WEB3.eth.contract(address=token_contract, abi=abi)
        return contract.functions.balanceOf(address).call() / 10**18
    else:
        return WEB3.eth.get_balance(address) / 10**18

def get_whale_movement(token_address, threshold=1000):
    # Simple recent large transfer detection (expand with Moralis or custom subgraph later)
    return "No major whale movement detected in last 1h"  # placeholder

def fetch_ticker_data(short, ticker):
    """Fetch ticker data for a single symbol."""
    try:
        ticker_data = EXCHANGE.fetch_ticker(ticker)
        return {
            "symbol": short,
            "price": ticker_data['last'],
            "signal": "HOLD"  # reuse your existing signal logic here
        }
    except Exception:
        return None

def generate_crypto_feed():
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "tickers": [],
        "onchain": {}
    }

    tickers_to_fetch = {"BTC": "BTC/USDT", "RAVANA": "RAVANA/USDT", "SMSS": "SMSS/USDT"}

    with ThreadPoolExecutor(max_workers=len(tickers_to_fetch)) as executor:
        # Submit all tasks and gather results
        futures = [executor.submit(fetch_ticker_data, short, ticker)
                   for short, ticker in tickers_to_fetch.items()]

        for future in futures:
            result = future.result()
            if result:
                data["tickers"].append(result)

    # Example wallet check (add your own addresses)
    data["onchain"] = {
        "example_wallet_balance": get_onchain_balance("0xYourWalletHere"),
        "whale_alert": get_whale_movement("RAVANA_contract_address")
    }

    return data

if __name__ == "__main__":
    feed = generate_crypto_feed()
    with open("feed.json", "w") as f:
        json.dump(feed, f, indent=2)
    print("✅ zFeedStreamZ crypto integration updated")
