'''
整合套利检测器
'''
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.two_hop_arbitrage_algorithm import TwoHopArbitrage
from src.triangle_arbitrage_algorithm import TriangleArbitrage
from src.bellman_ford_algorithm import BellmanFordArbitrage
from utils.data_structures import ArbitrageOpportunity
from typing import List, Dict, Tuple, Optional, Set
import networkx as nx


class IntegratedArbitrageDetector:
    """Arbitrage Opportunity Detector - Main Coordinator"""

    def __init__(self,
                 min_profit_threshold: float = 0.01,  # Minimum profit threshold 1%
                 max_hops: int = 4,                   # Maximum hops
                 base_amount: float = 1.0):           # Base trading amount (SOL)
        """
        Initialize Integrated Arbitrage Detector

        Args:
            min_profit_threshold: Minimum profit threshold (0.01 = 1%)
            max_hops: Maximum allowed hops
            base_amount: Base trading amount (SOL)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_hops = max_hops
        self.base_amount = base_amount

        self.bellman_ford = BellmanFordArbitrage(
            min_profit_threshold, max_hops, base_amount)
        self.triangle_arbitrage = TriangleArbitrage(
            min_profit_threshold, max_hops, base_amount)
        self.two_hop_arbitrage = TwoHopArbitrage(
            min_profit_threshold, max_hops, base_amount)

        print(f"IntegratedArbitrageDetector initialized:")
        print(f"   Min profit threshold: {min_profit_threshold*100:.1f}%")
        print(f"   Max hops: {max_hops}")
        print(f"   Base amount: {base_amount} SOL")
        print(f"   Available algorithms: Bellman-Ford, Triangle, Two-Hop")

    def detect_arbitrage(self, graph: nx.DiGraph,
                         source_token: str = None,
                         enable_bellman_ford: bool = True,
                         enable_triangle: bool = True,
                         enable_two_hop: bool = True) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities in the token swap graph

        Args:
            graph: Trading graph
            source_token: Starting token address, automatically selected if None
            enable_bellman_ford: Enable Bellman-Ford algorithm
            enable_triangle: Enable triangle arbitrage detection
            enable_two_hop: Enable two-hop arbitrage detection

        Returns:
            List[ArbitrageOpportunity]: List of detected arbitrage opportunities
        """
        if not graph or graph.number_of_nodes() == 0:
            print("Warning: Graph is empty, cannot detect arbitrage")
            return []

        opportunities = []

        print(f"\nStarting arbitrage detection...")
        print(
            f"Graph statistics: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

        # Automatically select starting token (highest degree node)
        if source_token is None:
            source_token = self._select_best_source_token(graph)

        print(f"Starting token: {source_token[:8]}...")

        # Method 1: Bellman-Ford negative cycle detection
        if enable_bellman_ford:
            print("\nRunning Bellman-Ford negative cycle detection...")
            bf_opportunities = self.bellman_ford.detect_opportunities(
                graph, source_token)
            opportunities.extend(bf_opportunities)
            print(f"Bellman-Ford found {len(bf_opportunities)} opportunities")

        # Method 2: Triangle arbitrage detection
        if enable_triangle:
            print("\nRunning triangle arbitrage detection...")
            triangle_opportunities = self.triangle_arbitrage.detect_opportunities(
                graph, source_token)
            opportunities.extend(triangle_opportunities)
            print(
                f"Triangle arbitrage found {len(triangle_opportunities)} opportunities")

        # Method 3: Two-hop arbitrage detection
        if enable_two_hop:
            print("\nRunning two-hop arbitrage detection...")
            two_hop_opportunities = self.two_hop_arbitrage.detect_opportunities(
                graph, source_token)
            opportunities.extend(two_hop_opportunities)
            print(
                f"Two-hop arbitrage found {len(two_hop_opportunities)} opportunities")

        # Deduplicate and rank
        opportunities = self._deduplicate_and_rank(opportunities)

        print(f"\nTotal {len(opportunities)} arbitrage opportunities found")
        return opportunities

    def _select_best_source_token(self, graph: nx.DiGraph) -> str:
        """Select the best starting token (highest degree node)"""
        if graph.number_of_nodes() == 0:
            return None

        # Calculate degree (in-degree + out-degree) for each node
        degrees = {node: graph.in_degree(node) + graph.out_degree(node)
                   for node in graph.nodes()}

        # Select the node with the highest degree
        best_node = max(degrees.keys(), key=lambda x: degrees[x])
        print(
            f"Automatically selected starting token: {best_node[:8]}... (degree: {degrees[best_node]})")
        return best_node

    def _deduplicate_and_rank(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Deduplicate and rank arbitrage opportunities"""
        if not opportunities:
            return []

        # Deduplicate based on path
        unique_opportunities = {}
        for opp in opportunities:
            # Create a standardized key for the path (handle circular paths)
            # Exclude the last repeated node
            path_key = tuple(sorted(opp.path[:-1]))

            if path_key not in unique_opportunities:
                unique_opportunities[path_key] = opp
            else:
                # Keep the opportunity with higher profit
                if opp.profit_ratio > unique_opportunities[path_key].profit_ratio:
                    unique_opportunities[path_key] = opp

        # Sort by profit ratio
        sorted_opportunities = sorted(
            unique_opportunities.values(),
            key=lambda x: (x.profit_ratio, x.confidence_score),
            reverse=True
        )

        print(
            f"Deduplicated to {len(sorted_opportunities)} unique arbitrage opportunities")
        return sorted_opportunities

    def print_opportunities(self, opportunities: List[ArbitrageOpportunity],
                            max_display: int = 10):
        """Print arbitrage opportunities"""
        if not opportunities:
            print("No arbitrage opportunities found")
            return

        print(
            f"\nArbitrage Opportunity Report (showing top {min(len(opportunities), max_display)}):")
        print("=" * 80)

        for i, opp in enumerate(opportunities[:max_display], 1):
            print(f"\n{i:2d}. {'→'.join(opp.path_symbols)}")
            print(f"    Profit Ratio: {opp.profit_ratio*100:.2f}%")
            print(f"    Estimated Profit: {opp.estimated_profit_sol:.4f} SOL")
            print(f"    Hops: {opp.hop_count}")
            print(f"    Total Fee: {opp.total_fee:.4f} SOL")
            print(f"    Confidence Score: {opp.confidence_score:.2f}")
            print(f"    Total Weight: {opp.total_weight:.6f}")


#
def detect_arbitrage(graph: nx.DiGraph,
                     min_profit: float = 0.01,
                     max_display: int = 10) -> List[ArbitrageOpportunity]:
    """
    Convenient arbitrage detection function

    Args:
        graph: Trading graph
        min_profit: Minimum profit threshold (0.01 = 1%)
        max_display: Maximum display quantity

    Returns:
        List[ArbitrageOpportunity]: List of arbitrage opportunities
    """
    detector = IntegratedArbitrageDetector(min_profit_threshold=min_profit)
    opportunities = detector.detect_arbitrage(graph)
    detector.print_opportunities(opportunities, max_display)
    return opportunities
