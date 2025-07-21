from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class TokenInfo:
    # Token information from Jupiter list
    address: str = ""
    symbol: str = ""
    name: str = ""
    decimals: int = 0
    logoURI: str = ""
    tags: List[str] = None

    # Volume data from DexScreener
    volume_24h: float = 0.0
    liquidity: float = 0.0
    price_usd: float = 0.0
    market_cap: float = 0.0
    price_change_24h: float = 0.0

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class EdgePairs:
    from_token: str = ""  # from quote api inputMint
    to_token: str = ""  # from quote api outputMint
    price_ratio: float = 0.0  # calculated from quote api inAmount and outAmount
    weight: float = 0.0  # calculated from price_ratio
    slippage_bps: int = 0  # from quote api slippageBps
    platform_fee: float = 0.0  # from quote api platformFee
    price_impact_pct: float = 0.0  # from quote api priceImpactPct
    total_fee: float = 0.0  # calculated from quote api routePlan


@dataclass
class ArbitrageOpportunity:
    """表示一个套利机会"""
    path: List[str] = None
    path_symbols: List[str] = None
    profit_ratio: float = 0.0
    total_weight: float = 0.0
    total_fee: float = 0.0
    hop_count: int = 0
    confidence_score: float = 0.0  # 置信度分数 (0-1)
    estimated_profit_sol: float = 0.0  # 预估利润 (SOL)

    def __post_init__(self):
        if self.path is None:
            self.path = []
        if self.path_symbols is None:
            self.path_symbols = []
        if not self.hop_count and self.path:
            self.hop_count = len(self.path) - 1
