"""
检测算法策略实现
"""
from typing import Dict, Any
from .base_strategy import DetectionStrategy


class BellmanFordStrategy(DetectionStrategy):
    """Bellman-Ford算法策略"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="bellman_ford",
            description="Bellman-Ford负环检测算法",
            config=config
        )
    
    def is_enabled(self) -> bool:
        return self.config.get('enabled', True)
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        return {
            'min_profit_threshold': self.config.get('min_profit_threshold', 0.005),
            'max_hops': self.config.get('max_hops', 4),
            'base_amount': self.config.get('base_amount', 1.0)
        }


class TriangleArbitrageStrategy(DetectionStrategy):
    """三角套利算法策略"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="triangle_arbitrage",
            description="三角套利检测算法",
            config=config
        )
    
    def is_enabled(self) -> bool:
        return self.config.get('enabled', True)
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        return {
            'min_profit_threshold': self.config.get('min_profit_threshold', 0.005),
            'max_hops': self.config.get('max_hops', 4),
            'base_amount': self.config.get('base_amount', 1.0)
        }


class TwoHopArbitrageStrategy(DetectionStrategy):
    """两跳套利算法策略"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="two_hop_arbitrage",
            description="两跳套利检测算法",
            config=config
        )
    
    def is_enabled(self) -> bool:
        return self.config.get('enabled', True)
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        return {
            'min_profit_threshold': self.config.get('min_profit_threshold', 0.005),
            'max_hops': self.config.get('max_hops', 4),
            'base_amount': self.config.get('base_amount', 1.0)
        }


class ExhaustiveDFSStrategy(DetectionStrategy):
    """穷举DFS算法策略"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="exhaustive_dfs",
            description="穷举DFS检测算法",
            config=config
        )
    
    def is_enabled(self) -> bool:
        return self.config.get('enabled', True)
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        return {
            'min_profit_threshold': self.config.get('min_profit_threshold', 0.005),
            'max_hops': self.config.get('max_hops', 5),
            'base_amount': self.config.get('base_amount', 1.0),
            'profit_pruning_threshold': self.config.get('profit_pruning_threshold', 0.5)
        }
