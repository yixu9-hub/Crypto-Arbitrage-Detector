"""
Data structures for crypto arbitrage detection.
This module defines the data structures used in the crypto arbitrage detector,
including token information, edge pairs, and arbitrage opportunities.
"""
from typing import List
from dataclasses import dataclass

@dataclass
class VolumeRanking:
    address: str # token address
    symbol: str # token symbol
    volume_24h: float # volume of the token in the last 24 hours
    liquidity_usd: float # liquidity of the token in USD
    rank: int # rank of the token by volume
    creation_date: str # creation date of the token


@dataclass
class TokenInfo:
    # Token information fron Jupiter list
    address: str # token address
    symbol: str # token symbol
    name: str # token name
    decimals: int # token decimals
    logoURI: str # token logo URI
    tags: List[str] # token tags

    # Volume data from DexScreener
    volume_24h: float = 0.0 # volume of the token in the last 24 hours
    liquidity: float = 0.0 # liquidity of the token in USD
    price_usd: float = 0.0 # price of the token in USD
    market_cap: float = 0.0 # market cap of the token in USD
    price_change_24h: float = 0.0 # price change of the token in the last 24 hours

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class EdgePairs:
    from_token: str  # from quote api inputMint
    to_token: str  # from quote api outputMint
    from_symbol: str  # optional, can be derived from TokenInfo
    to_symbol: str  # optional, can be derived from TokenInfo
    in_amount: float  # from quote api inAmount in sol
    out_amount: float  # from quote api outAmount in sol
    price_ratio: float  # calculated from quote api inAmount and outAmount
    weight: float  # calculated from price_ratio
    slippage_bps: int  # from quote api slippageBps
    platform_fee: float  # from quote api platformFee
    price_impact_pct: float  # from quote api priceImpactPct
    total_fee: float  # calculated from quote api routePlan
    gas_fee: int  # gas fee in lamports, default to 25000


@dataclass
class ArbitrageOpportunity:
    path: List[str] # list of token addresses in the path
    path_symbols: List[str] # symbols of tokens in the path
    profit_ratio: float 
    total_weight: float # total weight of the path
    total_fee: float # total fee for the arbitrage
    hop_count: int # number of hops in the path
    confidence_score: float # confidence score of the opportunity
    estimated_profit_sol: float # estimated profit in SOL

# Ensure hop_count is set correctly
    def __post_init__(self):
        if not self.hop_count:
            self.hop_count = len(self.path) - 1
