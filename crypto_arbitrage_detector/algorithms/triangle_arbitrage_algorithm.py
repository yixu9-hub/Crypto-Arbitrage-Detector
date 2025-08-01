'''
Triangle Arbitrage Detection Algorithm
'''
from utils.data_structures import ArbitrageOpportunity
from typing import List, Optional
import networkx as nx
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TriangleArbitrage:
    """
    Triangle arbitrage detection algorithm
    """

    def __init__(self,
                 min_profit_threshold: float = 0.005,
                 max_hops: int = 4,
                 base_amount: float = 1.0):
        """
        Initialize algorithm

        Args:
            min_profit_threshold: Minimum profit threshold (0.005 = 0.5%)
            max_hops: Maximum allowed hops
            base_amount: Base trading amount (SOL)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_hops = max_hops
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
            if len(path) < 2:
                return None

            # Calculate adjusted weight with market factors
            adjusted_weight = self._calculate_adjusted_weight(graph, path)
            if adjusted_weight is None or adjusted_weight >= 0:
                return None

            # Calculate profit and confidence
            profit_ratio = math.exp(-adjusted_weight) - 1
            estimated_profit = self.base_amount * profit_ratio
            confidence_score = self._calculate_confidence_score(
                graph, path, estimated_profit)

            # Generate display symbols
            path_symbols = [f"{addr[:4]}...{addr[-4:]}" for addr in path]

            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=profit_ratio,
                total_weight=adjusted_weight,
                total_fee=0.0,
                hop_count=len(path) - 1,
                confidence_score=confidence_score,
                estimated_profit_sol=estimated_profit
            )

        except Exception as e:
            print(
                f"Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None

    def _calculate_adjusted_weight(self, graph: nx.DiGraph, path: List[str]) -> Optional[float]:
        """
        Calculate path weight adjusted for slippage and price impact
        """
        total_weight = 0.0
        total_slippage = 0.0
        total_price_impact = 0.0

        for i in range(len(path) - 1):
            from_token, to_token = path[i], path[i + 1]

            if not graph.has_edge(from_token, to_token):
                return None

            edge_data = graph[from_token][to_token]
            total_weight += edge_data.get('weight', 0)
            total_slippage += edge_data.get('slippage_bps', 0) / 10000.0
            total_price_impact += abs(edge_data.get('price_impact_pct', 0))

            adjusted_weight = total_weight + \
                total_slippage + (total_price_impact / 100.0)
        return adjusted_weight

    def _calculate_confidence_score(self, graph: nx.DiGraph, path: List[str], estimated_profit: float) -> float:
        """Calculate confidence score based on profit and market risks"""
        if estimated_profit <= 0:
            return 0.0

        # Calculate risk factors
        total_slippage = sum(graph[path[i]][path[i + 1]].get('slippage_bps', 0) / 10000.0
                             for i in range(len(path) - 1))
        total_price_impact = sum(abs(graph[path[i]][path[i + 1]].get('price_impact_pct', 0))
                                 for i in range(len(path) - 1))

        slippage_risk = min(1.0, total_slippage * 10)
        price_impact_risk = min(1.0, total_price_impact / 10)
        base_confidence = min(1.0, estimated_profit * 10)

        confidence_score = base_confidence * \
            (1 - slippage_risk) * (1 - price_impact_risk)
        return max(0.0, min(1.0, confidence_score))

    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter and sort opportunities by profit threshold"""
        filtered = [
            opp for opp in opportunities if opp and opp.profit_ratio >= self.min_profit_threshold]
        return sorted(filtered, key=lambda x: x.profit_ratio, reverse=True)
