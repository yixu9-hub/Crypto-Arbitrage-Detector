'''
Mock token info for testing.
token list:
    SOL
    USDC
    USDT
    WIF
    JUP
    mSOL
'''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crypto_arbitrage_detector.utils.data_structures import TokenInfo, EdgePairs


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
    ),
    TokenInfo(
        address="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        symbol="USDT",
        name="Tether USD",
        decimals=6,
        logoURI="https://example.com/usdt.png",
        tags=["stablecoin"],
        volume_24h=800_000_000,
        liquidity=400_000_000,
        price_usd=1.0,
        market_cap=25_000_000_000,
        price_change_24h=0.0
    ),
    TokenInfo(
        address="EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        symbol="WIF",
        name="dogwifhat",
        decimals=6,
        logoURI="https://example.com/wif.png",
        tags=["meme", "solana"],
        volume_24h=75_000_000,
        liquidity=45_000_000,
        price_usd=3.42,
        market_cap=3_200_000_000,
        price_change_24h=-5.8
    ),
    TokenInfo(
        address="JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        symbol="JUP",
        name="Jupiter",
        decimals=6,
        logoURI="https://example.com/jup.png",
        tags=["defi", "dex"],
        volume_24h=120_000_000,
        liquidity=80_000_000,
        price_usd=0.85,
        market_cap=850_000_000,
        price_change_24h=8.5
    ),
    TokenInfo(
        address="mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
        symbol="mSOL",
        name="Marinade staked SOL",
        decimals=9,
        logoURI="https://example.com/msol.png",
        tags=["staking", "solana"],
        volume_24h=30_000_000,
        liquidity=150_000_000,
        price_usd=185.67,
        market_cap=1_200_000_000,
        price_change_24h=2.1
    )
]

# For testing purposes, we can use a smaller subset of tokens
small_test_tokens = test_tokens[:3]  # SOL, USDC, USDT

# 静态测试边数据, 3个币六个边
static_test_edges = [
    EdgePairs(
        from_token="SOL",
        to_token="USDC",
        price_ratio=175.23,
        weight=0.95,
        slippage_bps=50,
        platform_fee=0.0025,
        price_impact_pct=0.1,
        total_fee=100
    ),
    EdgePairs(
        from_token="USDC",
        to_token="SOL",
        price_ratio=0.0057,
        weight=0.94,
        slippage_bps=50,
        platform_fee=0.0025,
        price_impact_pct=0.1,
        total_fee=100
    ),
    EdgePairs(
        from_token="SOL",
        to_token="USDT",
        price_ratio=175.23,
        weight=0.93,
        slippage_bps=30,
        platform_fee=0.002,
        price_impact_pct=0.05,
        total_fee=80
    ),
    EdgePairs(
        from_token="USDT",
        to_token="SOL",
        price_ratio=0.0057,
        weight=0.92,
        slippage_bps=30,
        platform_fee=0.002,
        price_impact_pct=0.05,
        total_fee=80
    ),
    EdgePairs(
        from_token="USDC",
        to_token="USDT",
        price_ratio=1.0001,
        weight=0.98,
        slippage_bps=10,
        platform_fee=0.001,
        price_impact_pct=0.01,
        total_fee=20
    ),
    EdgePairs(
        from_token="USDT",
        to_token="USDC",
        price_ratio=0.9999,
        weight=0.98,
        slippage_bps=10,
        platform_fee=0.001,
        price_impact_pct=0.01,
        total_fee=20
    )
]
