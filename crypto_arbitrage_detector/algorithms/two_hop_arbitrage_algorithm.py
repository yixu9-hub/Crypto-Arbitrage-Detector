'''
Two-Hop Arbitrage Detection Algorithm
'''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs.strategy_config import get_algorithm_config
from utils.graph_utils import get_node_symbol
from utils.data_structures import ArbitrageOpportunity
from typing import List, Optional
import networkx as nx
import math


class TwoHopArbitrage:
    """
    Two-hop arbitrage detection algorithm
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
        config = get_algorithm_config("two_hop_arbitrage")

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
        self.algorithm_name = "TwoHopArbitrage"

    def detect_opportunities(self, graph: nx.DiGraph, source_token: str = None) -> List[ArbitrageOpportunity]:
        """Detect two-hop arbitrage opportunities"""
        opportunities = []

        # Find all possible two-hop cycles in the complete graph: A -> B -> A
        nodes = list(graph.nodes())
        for node_a in nodes:
            for node_b in nodes:
                if node_a != node_b:  # Avoid self-loops
                    # Check if two-hop cycle exists: A->B->A
                    if (graph.has_edge(node_a, node_b) and
                            graph.has_edge(node_b, node_a)):

                        path = [node_a, node_b, node_a]
                        opportunity = self._create_arbitrage_opportunity(
                            graph, path)
                        if opportunity:
                            opportunities.append(opportunity)

        filtered_opportunities = self._filter_profitable_opportunities(
            opportunities)
        print(
            f"[{self.algorithm_name}] Found {len(filtered_opportunities)} two-hop arbitrage opportunities")

        return filtered_opportunities

    def _create_arbitrage_opportunity(self, graph: nx.DiGraph, path: List[str]) -> Optional[ArbitrageOpportunity]:
        """Create arbitrage opportunity from two-hop path"""
        try:
            if len(path) < 2:  # Two-hop requires at least 2 hops
                return None

            # Calculate adjusted weight with market factors
            weight_result = self._calculate_adjusted_weight(graph, path)
            if weight_result is None:
                return None
                
            adjusted_weight, total_gas_fee = weight_result
            if adjusted_weight >= 0:
                return None

            # Calculate gas fees only (outAmount already accounts for trading fees)
            profit_ratio = math.exp(-adjusted_weight) - 1
            gas_fee_sol = total_gas_fee * 1e-9  # Convert lamports to SOL
            total_fee_sol = gas_fee_sol  # Only gas fees, trading fees already in outAmount
            
            # Calculate net profit after all fees
            gross_profit = self.base_amount * profit_ratio
            net_profit = gross_profit - total_fee_sol
            net_profit_ratio = net_profit / self.base_amount
            
            # Basic confidence score, 1% profit = 10 confidence
            confidence_score = min(1.0, max(0.0, profit_ratio * 10))

            # Generate display symbols
            path_symbols = []
            for addr in path:
                path_symbols.append(get_node_symbol(graph, addr))

            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=net_profit_ratio,
                total_weight=adjusted_weight,
                total_fee=total_fee_sol,
                hop_count=len(path) - 1,
                confidence_score=confidence_score,
                estimated_profit_sol=net_profit
            )

        except Exception as e:
            print(
                f"Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None

    def _calculate_adjusted_weight(self, graph: nx.DiGraph, path: List[str]) -> Optional[tuple]:
        """Calculate path weight adjusted for slippage and price impact, return weight and gas fees"""
        total_weight = 0.0
        total_slippage = 0.0
        total_price_impact = 0.0
        total_gas_fee = 0.0

        for i in range(len(path) - 1):
            from_token, to_token = path[i], path[i + 1]

            if not graph.has_edge(from_token, to_token):
                return None

            edge_data = graph[from_token][to_token]
            total_weight += edge_data.get('weight', 0)
            total_slippage += edge_data.get('slippage_bps', 0) / 10000.0
            total_price_impact += abs(edge_data.get('price_impact_pct', 0))
            total_gas_fee += edge_data.get('gas_fee', 0)

        adjusted_weight = total_weight + total_slippage + total_price_impact
        return adjusted_weight, total_gas_fee

    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter and sort opportunities by profit threshold"""
        filtered = [
            opp for opp in opportunities if opp and opp.profit_ratio >= self.min_profit_threshold]
        return sorted(filtered, key=lambda x: x.profit_ratio, reverse=True)
