from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class TokenInfo:
    # Token information fron Jupiter list
    address: str
    symbol: str
    name: str
    decimals: int
    logoURI: str
    tags: List[str]

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
    from_token: str  # from quote api inputMint
    to_token: str  # from quote api outputMint
    price_ratio: float  # calculated from quote api inAmount and outAmount
    weight: float  # calculated from price_ratio
    slippage_bps: int  # from quote api slippageBps
    platform_fee: float  # from quote api platformFee
    price_impact_pct: float  # from quote api priceImpactPct
    total_fee: float  # calculated from quote api routePlan
@dataclass
class ArbitrageOpportunity:
    path: List[str]
    path_symbols: List[str]
    profit_ratio: float
    total_weight: float
    total_fee: float
    hop_count: int
    confidence_score: float  # 置信度分数 (0-1)
    estimated_profit_sol: float  # 预估利润 (SOL)

    def __post_init__(self):
        if not self.hop_count:
            self.hop_count = len(self.path) - 1
