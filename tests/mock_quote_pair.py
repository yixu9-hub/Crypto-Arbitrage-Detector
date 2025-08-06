"""
Mock quote pair for testing.
This module provides mock data for quote pairs used in testing the crypto arbitrage detector.
"""
from dataclasses import dataclass
from typing import List
from crypto_arbitrage_detector.utils.data_structures import TokenInfo


test_tokens = [
    TokenInfo(
        address="So11111111111111111111111111111111111111112",
        symbol="SOL",
        name="Solana",
        decimals=9,
        logoURI="https://example.com/solana.png",
        tags=["native", "solana"],
        volume_24h=250_000_000,
        liquidity=180_000_000,
        price_usd=175.23,
        market_cap=8_500_000_000,
        price_change_24h=2.4
    ),
    TokenInfo(
        address="2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",
        symbol="USDC",
        name="USD Coin",
        decimals=6,
        logoURI="https://example.com/usdc.png",
        tags=["stablecoin"],
        volume_24h=1_000_000_000,
        liquidity=500_000_000,
        price_usd=1.0,
        market_cap=30_000_000_000,
        price_change_24h=0.0
    )
]
