'''
Triangle Arbitrage Detection Algorithm
Arbitrage through three-token cycles
'''

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs.strategy_config import get_algorithm_config
from utils.data_structures import ArbitrageOpportunity
from utils.graph_utils import get_node_symbol
import math
import networkx as nx
from typing import List, Optional


class TriangleArbitrage:
    """
    Triangle arbitrage detection algorithm
    """

    def __init__(self,
                 min_profit_threshold: float = None,
                 max_hops: int = None,
                 base_amount: float = None):
        """
        Initialize algorithm

        Args:
            min_profit_threshold: Minimum profit threshold
            max_hops: Maximum allowed hops
            base_amount: Base trading amount in SOL
        """
        # Get algorithm configuration
        config = get_algorithm_config("triangle_arbitrage")

        # Set parameters from config
        self.min_profit_threshold = config["min_profit_threshold"]
        self.max_hops = config["max_hops"]
        self.base_amount = config["base_amount"]

        # Override with provided parameters if not None
        if min_profit_threshold is not None:
            self.min_profit_threshold = min_profit_threshold
        if max_hops is not None:
            self.max_hops = max_hops
        if base_amount is not None:
            self.base_amount = base_amount
        self.algorithm_name = "TriangleArbitrage"

    def detect_opportunities(self, graph: nx.DiGraph, source_token: str = None) -> List[ArbitrageOpportunity]:
        """
        Detect triangle arbitrage opportunities across entire graph
        source_token parameter is ignored as we search all possible triangles
        """
        opportunities = []
        print(
            f"[{self.algorithm_name}] Searching for triangle arbitrage paths across entire graph...")

        # Find all possible triangular cycles in the complete graph
        nodes = list(graph.nodes())
        for i, node_a in enumerate(nodes):
            for j, node_b in enumerate(nodes):
                if j <= i:  # Avoid duplicate combinations and self-loops
                    continue
                for k, node_c in enumerate(nodes):
                    if k <= j:  # Avoid duplicate combinations
                        continue

                    # Check if triangular cycle exists: A->B->C->A
                    if (graph.has_edge(node_a, node_b) and
                        graph.has_edge(node_b, node_c) and
                            graph.has_edge(node_c, node_a)):

                        path = [node_a, node_b, node_c, node_a]
                        opportunity = self._create_arbitrage_opportunity(
                            graph, path)
                        if opportunity:
                            opportunities.append(opportunity)

                    # Check reverse triangular cycle: A->C->B->A
                    if (graph.has_edge(node_a, node_c) and
                        graph.has_edge(node_c, node_b) and
                            graph.has_edge(node_b, node_a)):

                        path = [node_a, node_c, node_b, node_a]
                        opportunity = self._create_arbitrage_opportunity(
                            graph, path)
                        if opportunity:
                            opportunities.append(opportunity)

        filtered = self._filter_profitable_opportunities(opportunities)
        print(
            f"[{self.algorithm_name}] Found {len(filtered)} triangle arbitrage opportunities")
        return filtered

    def _create_arbitrage_opportunity(self, graph: nx.DiGraph, path: List[str]) -> Optional[ArbitrageOpportunity]:
        """
        Create arbitrage opportunity object from path
        """
        try:
            if len(path) < 2:  # Must have at least 2 hops
                return None

            # Calculate path weight and trading fees
            # Since weight already contains information about slippage, price impact,
            # etc, we can use it directly to avoid double counting
            total_weight = 0.0
            total_trading_fee = 0.0
            total_gas_fee = 0.0

            for i in range(len(path) - 1):
                from_token, to_token = path[i], path[i + 1]

                if not graph.has_edge(from_token, to_token):
                    return None

                edge_data = graph[from_token][to_token]
                total_weight += edge_data.get('weight', 0)
                total_gas_fee += edge_data.get('gas_fee', 0)
                
                # Calculate proportional trading fee
                edge_in_amount = edge_data.get('in_amount', 1)
                edge_total_fee = edge_data.get('total_fee', 0)
                scaled_trading_fee = edge_total_fee * (self.base_amount / edge_in_amount)
                total_trading_fee += scaled_trading_fee

            if total_weight >= 0:
                return None

            # Calculate profit ratio using path weight
            profit_ratio = math.exp(-total_weight) - 1
            
            # Convert gas fees from lamports to SOL and calculate total fees
            gas_fee_sol = total_gas_fee * 1e-9
            total_fee_sol = total_trading_fee + gas_fee_sol
            
            # Calculate net profit after all fees
            gross_profit = self.base_amount * profit_ratio
            net_profit = gross_profit - total_fee_sol
            net_profit_ratio = net_profit / self.base_amount
            
            # Basic confidence score
            confidence_score = min(1.0, max(0.0, profit_ratio * 10))

            # Generate display symbols
            path_symbols = []
            for addr in path:
                path_symbols.append(get_node_symbol(graph, addr))

            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=net_profit_ratio,
                total_weight=total_weight,
                total_fee=total_fee_sol,
                hop_count=len(path) - 1,  # 3 hops in triangle
                confidence_score=confidence_score,
                estimated_profit_sol=net_profit
            )

        except Exception as e:
            print(
                f"Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None

    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter and sort opportunities by profit threshold"""
        filtered = [
            opp for opp in opportunities if opp and opp.profit_ratio >= self.min_profit_threshold]
        return sorted(filtered, key=lambda x: x.profit_ratio, reverse=True)
