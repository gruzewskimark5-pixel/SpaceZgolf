import pytest
from unittest.mock import patch, MagicMock
from crypto_integration import get_onchain_balance, generate_crypto_feed, get_whale_movement

@patch('crypto_integration.WEB3')
def test_get_onchain_balance_native(mock_web3):
    # Setup mock for native balance
    mock_web3.eth.get_balance.return_value = 1000000000000000000 # 1 ETH in wei

    balance = get_onchain_balance("0x1234567890123456789012345678901234567890")
    assert balance == 1.0

@patch('crypto_integration.WEB3')
def test_get_onchain_balance_token(mock_web3):
    # Setup mock for token balance
    mock_contract = MagicMock()
    mock_contract.functions.balanceOf.return_value.call.return_value = 5000000000000000000 # 5 tokens in wei
    mock_web3.eth.contract.return_value = mock_contract

    balance = get_onchain_balance("0x1234567890123456789012345678901234567890", "0x0987654321098765432109876543210987654321")
    assert balance == 5.0


def test_get_whale_movement():
    result = get_whale_movement("0xDummyAddress", threshold=500)
    assert result == "No major whale movement detected in last 1h"

@patch('crypto_integration.get_onchain_balance')
@patch('crypto_integration.EXCHANGE')
def test_generate_crypto_feed(mock_exchange, mock_get_balance):
    # Setup mocks
    mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
    mock_get_balance.return_value = 10.5

    feed = generate_crypto_feed()

    # Assertions
    assert 'timestamp' in feed
    assert len(feed['tickers']) > 0
    assert feed['tickers'][0]['price'] == 50000.0
    assert feed['onchain']['example_wallet_balance'] == 10.5
    assert 'whale_alert' in feed['onchain']
