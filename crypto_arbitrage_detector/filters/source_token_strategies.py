"""
起始token选择策略实现
"""
from typing import Dict, Any
import networkx as nx
from .base_strategy import SourceTokenStrategy


class HighestDegreeStrategy(SourceTokenStrategy):
    """选择度数最高的节点作为起始token"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="highest_degree",
            description="选择度数最高的节点作为起始token",
            config=config
        )
    
    def select_source_token(self, graph: nx.DiGraph, suggested_token: str = None) -> str:
        if graph.number_of_nodes() == 0:
            return None
        
        # 如果有建议的token且存在于图中，直接使用
        if suggested_token and suggested_token in graph.nodes():
            return suggested_token
        
        # 计算每个节点的度数（入度 + 出度）
        degrees = {node: graph.in_degree(node) + graph.out_degree(node)
                   for node in graph.nodes()}
        
        # 选择度数最高的节点
        best_node = max(degrees.keys(), key=lambda x: degrees[x])
        
        print(f"[HighestDegreeStrategy] Selected: {best_node[:8]}... (degree: {degrees[best_node]})")
        return best_node


class HighestLiquidityStrategy(SourceTokenStrategy):
    """选择流动性最高的token作为起始token（基于边权重）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="highest_liquidity",
            description="选择流动性最高的token作为起始token",
            config=config
        )
    
    def select_source_token(self, graph: nx.DiGraph, suggested_token: str = None) -> str:
        if graph.number_of_nodes() == 0:
            return None
        
        # 如果有建议的token且存在于图中，直接使用
        if suggested_token and suggested_token in graph.nodes():
            return suggested_token
        
        # 计算每个节点的总流动性（基于连接边的权重）
        liquidity_scores = {}
        for node in graph.nodes():
            total_liquidity = 0.0
            
            # 计算出边的总权重
            for _, target, data in graph.out_edges(node, data=True):
                weight = data.get('weight', 0)
                # 权重越小表示流动性越好（负对数价格比）
                total_liquidity += abs(weight)
            
            # 计算入边的总权重
            for source, _, data in graph.in_edges(node, data=True):
                weight = data.get('weight', 0)
                total_liquidity += abs(weight)
            
            liquidity_scores[node] = total_liquidity
        
        # 选择流动性最高的节点
        best_node = max(liquidity_scores.keys(), key=lambda x: liquidity_scores[x])
        
        print(f"[HighestLiquidityStrategy] Selected: {best_node[:8]}... (liquidity score: {liquidity_scores[best_node]:.2f})")
        return best_node


class ManualSelectionStrategy(SourceTokenStrategy):
    """手动指定起始token"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="manual_selection",
            description="手动指定起始token",
            config=config
        )
        self.preferred_tokens = self.config.get('preferred_tokens', [])
    
    def select_source_token(self, graph: nx.DiGraph, suggested_token: str = None) -> str:
        if graph.number_of_nodes() == 0:
            return None
        
        # 如果有建议的token且存在于图中，直接使用
        if suggested_token and suggested_token in graph.nodes():
            print(f"[ManualSelectionStrategy] Using suggested token: {suggested_token[:8]}...")
            return suggested_token
        
        # 检查首选token列表
        for token in self.preferred_tokens:
            if token in graph.nodes():
                print(f"[ManualSelectionStrategy] Using preferred token: {token[:8]}...")
                return token
        
        # 如果没有匹配的首选token，回退到度数最高的策略
        print(f"[ManualSelectionStrategy] No preferred tokens found, falling back to highest degree")
        fallback_strategy = HighestDegreeStrategy()
        return fallback_strategy.select_source_token(graph, suggested_token)


class SOLPriorityStrategy(SourceTokenStrategy):
    """优先选择SOL作为起始token"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="sol_priority",
            description="优先选择SOL作为起始token",
            config=config
        )
        self.sol_address = self.config.get('sol_address', 'So11111111111111111111111111111111111111112')
    
    def select_source_token(self, graph: nx.DiGraph, suggested_token: str = None) -> str:
        if graph.number_of_nodes() == 0:
            return None
        
        # 如果有建议的token且存在于图中，直接使用
        if suggested_token and suggested_token in graph.nodes():
            print(f"[SOLPriorityStrategy] Using suggested token: {suggested_token[:8]}...")
            return suggested_token
        
        # 首先尝试使用SOL
        if self.sol_address in graph.nodes():
            print(f"[SOLPriorityStrategy] Using SOL: {self.sol_address[:8]}...")
            return self.sol_address
        
        # 如果SOL不在图中，回退到度数最高的策略
        print(f"[SOLPriorityStrategy] SOL not found, falling back to highest degree")
        fallback_strategy = HighestDegreeStrategy()
        return fallback_strategy.select_source_token(graph, suggested_token)
