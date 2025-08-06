"""
Strategy Configuration for Arbitrage Detection Algorithms
This module centralizes all algorithm parameters for easy management and consistency.
"""

from typing import Dict, Any


# Default configuration template
DEFAULT_CONFIG = {
    # Core algorithm parameters
    "min_profit_threshold": 0.005,  # 0.5% minimum profit threshold
    "max_hops": 4,                  # Maximum allowed hops in arbitrage path
    "base_amount": 1.0,             # Base trading amount in SOL
    
    # Risk management parameters
    "enable_risk_evaluation": True, 
    "profit_pruning_threshold": 0.5, # pruning threshold for exhaustive DFS, 50% of path weight for unprofitable paths
}

# Algorithm-specific configurations
ALGORITHM_CONFIGS = {
    "bellman_ford": {
        "min_profit_threshold": 0.003,
        "max_hops": 4,
        "base_amount": 1.0
    },
    
    "triangle_arbitrage": {
        "min_profit_threshold": 0.005,
        "max_hops": 4,  # Triangle = 3 hops, but allow buffer
        "base_amount": 1.0
    },
    
    "two_hop_arbitrage": {
        "min_profit_threshold": 0.005,
        "max_hops": 3,  # Two-hop = 2 hops, but allow buffer
        "base_amount": 1.0
    },
    
    "exhaustive_dfs": {
        "min_profit_threshold": 0.005,
        "max_hops": 5,  # Allow more hops for comprehensive search
        "base_amount": 1.0
    },
    
    "integrated_detector": {
        "min_profit_threshold": 0.005,
        "max_hops": 4,
        "base_amount": 1.0
    }
}

# Risk evaluation configuration
RISK_CONFIG = {
    "low_risk_threshold": 0.3,        # Risk score <= 0.3 is considered low risk
    "medium_risk_threshold": 0.6,     # Risk score <= 0.6 is considered medium risk
    "high_risk_threshold": 1.0,       # Risk score > 0.6 is considered high risk
    "max_acceptable_slippage": 0.02,  # 2% maximum acceptable slippage
    "max_acceptable_price_impact": 0.02,  # 2%
    "max_gas_cost_ratio": 0.1,        # 10% of profit - gas fee threshold
    "min_confidence_threshold": 0.3,  # 30% minimum confidence threshold
    "min_profit_threshold": 0.005,    # 0.5% minimum profit for CONSIDER recommendation
    
    # Risk assessment weights
    "risk_weights": {
        "slippage": 0.5,     # Weight for slippage risk
        "gas": 0.3,          # Weight for gas cost risk  
        "complexity": 0.2    # Weight for complexity risk
    },
    
    # Default cost estimates when edge data is not available
    "default_gas_per_hop": 0.0005,     # 0.0005 SOL per hop
    "default_slippage_per_hop": 0.001  # 0.1% slippage per hop
}

# Function to get algorithm configuration
def get_algorithm_config(algorithm_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific algorithm
    
    Args:
        algorithm_name: Name of the algorithm
        
    Returns:
        Dict[str, Any]: Configuration dictionary for the algorithm
        
    Raises:
        KeyError: If algorithm name is not found
    """
    if algorithm_name not in ALGORITHM_CONFIGS:
        raise KeyError(f"Unknown algorithm: {algorithm_name}. "
                      f"Available: {list(ALGORITHM_CONFIGS.keys())}")
    
    # Merge default config with algorithm-specific config
    config = DEFAULT_CONFIG.copy()
    config.update(ALGORITHM_CONFIGS[algorithm_name])
    return config

# Function to get default configuration
def get_risk_config() -> Dict[str, Any]:
    """Get risk evaluation configuration"""
    return RISK_CONFIG.copy()