from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TokenInfo:
    # Token information fron Jupiter list
    address: str
    symbol: str
    name: str
    decimals: int
    logoURI: str
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
class QuoteResponse:
    input_mint: str
    output_mint: str
    in_amount: str
    out_amount: str
    other_amount_threshold: str
    swap_mode: str
    slippage_bps: int
    price_impact_pct: float
    route_plan: List[Dict]


@dataclass
class EdgePairs:
    from_token: str
    to_token: str
    price_ratio: float
    weight: float
    slippage_bps: int
    platformFee: float
    priceImpactPct: float
    total_fee: int

