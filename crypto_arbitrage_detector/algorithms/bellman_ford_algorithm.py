'''
Bellman-Ford Arbitrage Detection Algorithm
多跳的负环检测套利算法, 目前允许4跳
'''
import networkx as nx
import math
import sys
import os
# Add project path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from utils.data_structures import ArbitrageOpportunity


class BellmanFordArbitrage:
    """
    Bellman-Ford negative cycle detection algorithm
    """
    
    def __init__(self, 
                 min_profit_threshold: float = 0.01,
                 max_hops: int = 4,
                 base_amount: float = 1.0):
        """
        Initialize algorithm
        
        Args:
            min_profit_threshold: Minimum profit threshold (0.01 = 1%)
            max_hops: Maximum allowed hops
            base_amount: Base trading amount (SOL)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_hops = max_hops
        self.base_amount = base_amount
        self.algorithm_name = "BellmanFordArbitrage"
    
    def detect_opportunities(self, graph: nx.DiGraph, source_token: str = None) -> List[ArbitrageOpportunity]:
        """
        Use Bellman-Ford algorithm to detect negative cycle arbitrage opportunities
        """
        opportunities = []
        
        if not source_token:
            source_token = self._select_best_source_token(graph)
        
        if source_token not in graph.nodes():
            print(f"Warning: Starting node {source_token} is not in the graph")
            return opportunities
        
        try:
            # Initialize distance dictionary
            distances = {node: float('inf') for node in graph.nodes()}
            distances[source_token] = 0
            predecessors = {node: None for node in graph.nodes()}
            
            # 松弛操作 (|V| - 1 次)
            for _ in range(graph.number_of_nodes() - 1):
                for u, v, data in graph.edges(data=True):
                    # base
                    base_weight = data.get('weight', 0)
                    
                    # slippage and price impact
                    slippage_bps = data.get('slippage_bps', 0)
                    price_impact_pct = data.get('price_impact_pct', 0)
                    
                    slippage_decimal = slippage_bps / 10000.0
                    adjusted_weight = base_weight + slippage_decimal + abs(price_impact_pct) / 100.0
                    
                    if distances[u] != float('inf') and distances[u] + adjusted_weight < distances[v]:
                        distances[v] = distances[u] + adjusted_weight
                        predecessors[v] = u  # 前驱节点记录
            
            # 检测负环
            negative_cycle_nodes = set()
            for u, v, data in graph.edges(data=True):
                # 使用相同的权重调整逻辑
                base_weight = data.get('weight', 0)
                slippage_bps = data.get('slippage_bps', 0)
                price_impact_pct = data.get('price_impact_pct', 0)
                slippage_decimal = slippage_bps / 10000.0
                adjusted_weight = base_weight + slippage_decimal + abs(price_impact_pct) / 100.0
                
                if distances[u] != float('inf') and distances[u] + adjusted_weight < distances[v]:
                    negative_cycle_nodes.add(v)
            
            # 重建负环路径
            if negative_cycle_nodes:
                for cycle_node in negative_cycle_nodes:
                    cycle_path = self._find_actual_negative_cycle(graph, cycle_node)
                    # len(path) = 5 (节点数量)
                    if cycle_path and len(cycle_path) <= self.max_hops + 1:
                        opportunity = self._create_arbitrage_opportunity(graph, cycle_path)
                        if opportunity:
                            opportunities.append(opportunity)
                                
        except Exception as e:
            print(f" Bellman-Ford error: {e}")

        return self._filter_profitable_opportunities(opportunities)
    
    def _select_best_source_token(self, graph: nx.DiGraph) -> str:
        """
        Automatically select the best source token based on node degrees
        """
        if graph.number_of_nodes() == 0:
            return None
            
        # indegree 和 outdegree 之和
        degrees = {node: graph.in_degree(node) + graph.out_degree(node) 
                  for node in graph.nodes()}
        
        # 选择度数最高的节点
        best_node = max(degrees.keys(), key=lambda x: degrees[x])
        return best_node
    
    def _find_actual_negative_cycle(self, graph: nx.DiGraph, start_node: str) -> List[str]:
        """
        find the actual negative cycle containing the specified node
        两种策略：
        1. 从起始节点出发，寻找短环
        2. 从图中所有节点出发，寻找包含起始节点的环
        """
        try:
            # 简单策略：检查所有从 start_node 开始的短环路径
            def find_cycles_from_node(current, path, depth):
                if depth > self.max_hops:
                    return []
                
                cycles = []
                
                # 检查是否回到路径中的任一节点形成环
                for neighbor in graph.successors(current):
                    new_path = path + [neighbor]
                    
                    # 如果邻居在路径中，形成了环
                    if neighbor in path:
                        cycle_start_idx = path.index(neighbor)
                        cycle = path[cycle_start_idx:] + [neighbor]
                        
                        # 验证环的权重
                        total_weight = 0
                        valid_cycle = True
                        
                        for i in range(len(cycle) - 1):
                            if graph.has_edge(cycle[i], cycle[i + 1]):
                                edge_data = graph[cycle[i]][cycle[i + 1]]
                                # 使用调整后的权重计算
                                base_weight = edge_data.get('weight', 0)
                                slippage_bps = edge_data.get('slippage_bps', 0)
                                price_impact_pct = edge_data.get('price_impact_pct', 0)
                                slippage_decimal = slippage_bps / 10000.0
                                adjusted_weight = base_weight + slippage_decimal + abs(price_impact_pct) / 100.0
                                total_weight += adjusted_weight
                            else:
                                valid_cycle = False
                                break
                        
                        if valid_cycle and total_weight < -1e-10:  # 有效负环
                            cycles.append(cycle)
                    
                    # 继续深度搜索
                    elif neighbor not in path and depth < self.max_hops:
                        cycles.extend(find_cycles_from_node(neighbor, new_path, depth + 1))
                
                return cycles
            
            # 寻找从 start_node 开始的所有负环
            cycles = find_cycles_from_node(start_node, [start_node], 0)
            
            if cycles:
                # 返回最短的负环
                best_cycle = min(cycles, key=len)
                print(f"   🔍 找到负环: {[node[:8] + '...' for node in best_cycle]}")
                return best_cycle
            
            # 如果没找到，尝试从图中的所有节点开始搜索包含 start_node 的负环
            for node in graph.nodes():
                if node != start_node:
                    cycles = find_cycles_from_node(node, [node], 0)
                    
                    # 寻找包含 start_node 的环
                    for cycle in cycles:
                        if start_node in cycle:
                            print(f"   🔍 找到包含目标节点的负环: {[n[:8] + '...' for n in cycle]}")
                            return cycle
            
        except Exception as e:
            print(f" an error occurs in negative path detection: {e}")
        
        return []
    
    def _create_arbitrage_opportunity(self, graph: nx.DiGraph, path: List[str]) -> Optional[ArbitrageOpportunity]:
        """Create arbitrage opportunity object from path
        考虑滑点值和交易平台费用"""
        try:
            if len(path) < 2:
                return None
            
            # Calculate total path weight, fees, slippage, and price impact
            total_weight = 0.0
            total_fee = 0.0
            total_slippage = 0.0
            total_price_impact = 0.0
            platform_fees = 0.0
            
            for i in range(len(path) - 1):
                from_token = path[i]
                to_token = path[i + 1]
                
                if not graph.has_edge(from_token, to_token):
                    return None  # Invalid path
                
                edge_data = graph[from_token][to_token]
                weight = edge_data.get('weight', 0)
                fee = edge_data.get('total_fee', 0)
                
                # 获取滑点和平台费用信息
                slippage_bps = edge_data.get('slippage_bps', 0)  # basis points
                platform_fee = edge_data.get('platform_fee', 0)
                price_impact_pct = edge_data.get('price_impact_pct', 0)
                
                # 将滑点从基点转换为小数 (1 bps = 0.0001)
                slippage_decimal = slippage_bps / 10000.0
                
                # 累加各项费用和影响
                total_weight += weight
                total_fee += fee
                total_slippage += slippage_decimal
                total_price_impact += abs(price_impact_pct)  # 价格影响通常为负值
                platform_fees += platform_fee

            adjusted_weight = total_weight + total_slippage + (total_price_impact / 100.0)
            
            # Calculate profit ratio (negative weight indicates arbitrage opportunity)
            if total_weight >= 0:
                return None  # No arbitrage opportunity

            base_profit_ratio = math.exp(-adjusted_weight) - 1

            #total_all_fees = total_fee + platform_fees

            #actual_profit_ratio = base_profit_ratio - (total_all_fees / self.base_amount)
            actual_profit_ratio = base_profit_ratio # 不考虑交易费用，jupiter quote已经扣除了fee的费用返回outAmount
            
            # Estimated profit (SOL)
            estimated_profit = self.base_amount * actual_profit_ratio 

            slippage_risk = min(1.0, total_slippage * 10)  # 滑点风险因子
            price_impact_risk = min(1.0, total_price_impact / 10)  # 价格影响风险因子
            
            # Confidence score calculation
            #if total_all_fees > 0:
            #    profit_fee_ratio = max(0, estimated_profit / total_all_fees)
            #    base_confidence = min(1.0, profit_fee_ratio / 5)  # 利润费用比
            #else:
            base_confidence = 0.5
 
            confidence_score = base_confidence * (1 - slippage_risk) * (1 - price_impact_risk)
            confidence_score = max(0.0, min(1.0, confidence_score))
            
            # Generate path symbols (for display)
            path_symbols = [f"{addr[:4]}...{addr[-4:]}" for addr in path]
            
            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=actual_profit_ratio,
                total_weight=adjusted_weight,
                total_fee=0.0,  # 交易费用,设置为0，因为当前jupiter quote已经扣除了fee的费用返回outAmount
                hop_count=len(path) - 1,
                confidence_score=confidence_score,
                estimated_profit_sol=estimated_profit
            )
            
        except Exception as e:
            print(f" Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None
    
    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter opportunities that meet profit threshold"""
        filtered = [opp for opp in opportunities
                    if opp and opp.profit_ratio >= self.min_profit_threshold]
        return filtered