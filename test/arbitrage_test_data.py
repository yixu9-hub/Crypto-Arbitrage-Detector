'''
Arbitrage test data - Contains artificial arbitrage opportunities for testing
'''
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_structures import EdgePairs


arbitrage_test_edges = [
    # Expected cycle: 1 SOL -> 180 USDC -> 184.5 USDT -> 1.08 SOL (8% arbitrage before costs)

    EdgePairs(
        from_token="SOL",
        to_token="USDC",
        price_ratio=180.0,
        weight=-math.log(180.0),
        slippage_bps=20,
        platform_fee=0.0005,
        price_impact_pct=0.02,
        total_fee=0.001
    ),

    EdgePairs(
        from_token="USDC",
        to_token="USDT",
        price_ratio=1.03,
        weight=-math.log(1.03),
        slippage_bps=15,
        platform_fee=0.0003,
        price_impact_pct=0.01,
        total_fee=0.0005
    ),

    EdgePairs(
        from_token="USDT",
        to_token="SOL",
        price_ratio=0.0065,
        weight=-math.log(0.0065),
        slippage_bps=25,
        platform_fee=0.0008,
        price_impact_pct=0.015,
        total_fee=0.001
    ),

    # Enhanced two-hop arbitrage: SOL -> BTC -> SOL
    EdgePairs(
        from_token="SOL",
        to_token="BTC",
        price_ratio=0.0035,  # 1 SOL = 0.0035 BTC (favorable rate)
        weight=-math.log(0.0035),
        slippage_bps=30,
        platform_fee=0.0008,
        price_impact_pct=0.05,
        total_fee=0.002
    ),

    EdgePairs(
        from_token="BTC",
        to_token="SOL",
        price_ratio=300.0,
        weight=-math.log(300.0),
        slippage_bps=35,
        platform_fee=0.001,
        price_impact_pct=0.08,
        total_fee=0.003
    ),

    # Additional paths for more complex arbitrage
    EdgePairs(
        from_token="USDC",
        to_token="SOL",
        price_ratio=0.0054,
        weight=-math.log(0.0054),
        slippage_bps=25,
        platform_fee=0.0008,
        price_impact_pct=0.03,
        total_fee=0.0015
    ),

    EdgePairs(
        from_token="USDT",
        to_token="USDC",
        price_ratio=0.96,
        weight=-math.log(0.96),
        slippage_bps=20,
        platform_fee=0.0005,
        price_impact_pct=0.02,
        total_fee=0.001
    ),

    # strong arbitrage path: SOL -> ETH -> USDC -> SOL
    EdgePairs(
        from_token="SOL",
        to_token="ETH",
        price_ratio=0.09,
        weight=-math.log(0.09),
        slippage_bps=30,
        platform_fee=0.0008,
        price_impact_pct=0.04,
        total_fee=0.002
    ),

    EdgePairs(
        from_token="ETH",
        to_token="USDC",
        price_ratio=2200.0,
        weight=-math.log(2200.0),
        slippage_bps=25,
        platform_fee=0.001,
        price_impact_pct=0.03,
        total_fee=0.0025
    )
]

# no arbitrage after costs
balanced_test_edges = [
    EdgePairs(
        from_token="SOL",
        to_token="USDC",
        price_ratio=175.0,
        weight=-math.log(175.0),
        slippage_bps=50,
        platform_fee=0.0025,
        price_impact_pct=0.1,
        total_fee=0.01
    ),

    EdgePairs(
        from_token="USDC",
        to_token="SOL",
        price_ratio=0.00571,
        weight=-math.log(0.00571),
        slippage_bps=50,
        platform_fee=0.0025,
        price_impact_pct=0.1,
        total_fee=0.01
    ),

    EdgePairs(
        from_token="USDC",
        to_token="USDT",
        price_ratio=1.0,
        weight=-math.log(1.0),
        slippage_bps=30,
        platform_fee=0.002,
        price_impact_pct=0.05,
        total_fee=0.005
    ),

    EdgePairs(
        from_token="USDT",
        to_token="USDC",
        price_ratio=1.0,
        weight=-math.log(1.0),
        slippage_bps=30,
        platform_fee=0.002,
        price_impact_pct=0.05,
        total_fee=0.005
    )
]
