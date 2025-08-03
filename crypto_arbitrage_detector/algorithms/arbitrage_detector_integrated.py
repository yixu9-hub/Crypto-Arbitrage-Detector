# Integrated Arbitrage Detector
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx
from typing import List, Dict, Optional
from utils.data_structures import ArbitrageOpportunity
from risk_evaluator import ArbitrageRiskEvaluator
from exhaustive_dfs_algorithm import ExhaustiveDFSArbitrage
from bellman_ford_algorithm import BellmanFordArbitrage
from triangle_arbitrage_algorithm import TriangleArbitrage
from two_hop_arbitrage_algorithm import TwoHopArbitrage


class IntegratedArbitrageDetector:
    """Arbitrage Opportunity Detector - Main Coordinator"""

    def __init__(self,
                 min_profit_threshold: float = 0.005,  # Minimum profit threshold 0.5%
                 max_hops: int = 4,                   # Maximum hops
                 # Base trading amount (SOL)
                 base_amount: float = 1.0,
                 enable_risk_evaluation: bool = True):  # Enable risk assessment
        """
        Initialize Integrated Arbitrage Detector

        Args:
            min_profit_threshold: Minimum profit threshold (0.005 = 0.5%)
            max_hops: Maximum allowed hops
            base_amount: Base trading amount (SOL)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_hops = max_hops
        self.base_amount = base_amount
        self.enable_risk_evaluation = enable_risk_evaluation

        self.bellman_ford = BellmanFordArbitrage(
            min_profit_threshold, max_hops, base_amount)
        self.triangle_arbitrage = TriangleArbitrage(
            min_profit_threshold, max_hops, base_amount)
        self.two_hop_arbitrage = TwoHopArbitrage(
            min_profit_threshold, max_hops, base_amount)
        self.exhaustive_dfs = ExhaustiveDFSArbitrage(
            min_profit_threshold, max_hops, base_amount)

        # Initialize risk evaluator if enabled
        if self.enable_risk_evaluation:
            self.risk_evaluator = ArbitrageRiskEvaluator()
        else:
            self.risk_evaluator = None

        print(f"IntegratedArbitrageDetector initialized:")
        print(f"   Min profit threshold: {min_profit_threshold*100:.1f}%")
        print(f"   Max hops: {max_hops}")
        print(f"   Base amount: {base_amount} SOL")
        print(
            f"   Risk evaluation: {'Enabled' if enable_risk_evaluation else 'Disabled'}")
        print(f"   Available algorithms: Bellman-Ford, Triangle, Two-Hop, Exhaustive DFS")

    def detect_arbitrage(self, graph: nx.DiGraph,
                         source_token: str = None,
                         enable_bellman_ford: bool = True,
                         enable_triangle: bool = True,
                         enable_two_hop: bool = True,
                         enable_exhaustive_dfs: bool = True) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities in the token swap graph

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

        # no specific starting token
        print(
            f"Searching for negative cycles across all {graph.number_of_nodes()} nodes...")

        # Method 1: Bellman-Ford negative cycle detection
        if enable_bellman_ford:
            print("\nRunning Bellman-Ford negative cycle detection...")
            bf_opportunities = self.bellman_ford.detect_opportunities(
                graph, None)
            opportunities.extend(bf_opportunities)
            print(f"Bellman-Ford found {len(bf_opportunities)} opportunities")

        # Method 2: Triangle arbitrage detection
        if enable_triangle:
            print("\nRunning triangle arbitrage detection...")
            triangle_opportunities = self.triangle_arbitrage.detect_opportunities(
                graph, None)
            opportunities.extend(triangle_opportunities)
            print(
                f"Triangle arbitrage found {len(triangle_opportunities)} opportunities")

        # Method 3: Two-hop arbitrage detection
        if enable_two_hop:
            print("\nRunning two-hop arbitrage detection...")
            two_hop_opportunities = self.two_hop_arbitrage.detect_opportunities(
                graph, None)
            opportunities.extend(two_hop_opportunities)
            print(
                f"Two-hop arbitrage found {len(two_hop_opportunities)} opportunities")

        # Method 4: Exhaustive DFS detection
        if enable_exhaustive_dfs:
            print("\nRunning exhaustive DFS detection...")
            dfs_opportunities = self.exhaustive_dfs.detect_opportunities(
                graph, None)
            opportunities.extend(dfs_opportunities)
            print(
                f"Exhaustive DFS found {len(dfs_opportunities)} opportunities")

        # Deduplicate and rank
        opportunities = self._deduplicate_and_rank(opportunities)

        # Apply risk evaluation if enabled
        if self.enable_risk_evaluation and self.risk_evaluator and opportunities:
            print(
                f"\nApplying risk evaluation to {len(opportunities)} opportunities...")
            opportunities = self._apply_risk_evaluation(opportunities, graph)

        print(f"\nTotal {len(opportunities)} arbitrage opportunities found")
        return opportunities

    def _deduplicate_and_rank(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        Deduplicate and rank arbitrage opportunities
        """
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

    def _apply_risk_evaluation(self, opportunities: List[ArbitrageOpportunity],
                               graph: nx.DiGraph) -> List[ArbitrageOpportunity]:
        """
        Apply risk evaluation to filter and rank opportunities
        """
        if not opportunities or not self.risk_evaluator:
            return opportunities

        risk_evaluated_opportunities = []

        for opportunity in opportunities:
            # Extract edge data for this opportunity path
            edge_data_list = self._extract_edge_data(graph, opportunity.path)

            # Evaluate risk
            risk_result = self.risk_evaluator.evaluate_opportunity(
                opportunity, edge_data_list)

            # Only keep opportunities that are not marked as AVOID
            if risk_result['recommendation'] != 'AVOID':
                # Update opportunity with risk-adjusted confidence
                opportunity.confidence_score = min(opportunity.confidence_score,
                                                   1.0 - risk_result['risk_score'])
                risk_evaluated_opportunities.append(opportunity)

        # Sort by risk-adjusted profit ratio
        risk_evaluated_opportunities.sort(
            key=lambda x: x.profit_ratio * x.confidence_score,
            reverse=True
        )

        # Print risk evaluation summary
        total_original = len(opportunities)
        total_filtered = len(risk_evaluated_opportunities)
        print(
            f"Risk evaluation filtered {total_original - total_filtered} high-risk opportunities")
        print(
            f"Remaining {total_filtered} opportunities after risk assessment")

        return risk_evaluated_opportunities

    def _extract_edge_data(self, graph: nx.DiGraph, path: List[str]) -> List[Dict]:
        """
        Extract edge data from graph for a given path
        """
        edge_data_list = []

        for i in range(len(path) - 1):
            from_token = path[i]
            to_token = path[i + 1]

            if graph.has_edge(from_token, to_token):
                edge_data = graph[from_token][to_token]
                edge_data_list.append(edge_data)

        return edge_data_list

    def print_opportunities(self, opportunities: List[ArbitrageOpportunity],
                            max_display: int = 10):
        """Print arbitrage opportunities"""
        if not opportunities:
            print("No arbitrage opportunities found")
            return

        print(
            f"\nArbitrage Opportunity Report (showing top {min(len(opportunities), max_display)}):")

        for i, opp in enumerate(opportunities[:max_display], 1):
            print(f"\n{i:2d}. {'→'.join(opp.path_symbols)}")
            print(f"    Profit Ratio: {opp.profit_ratio*100:.2f}%")
            print(f"    Estimated Profit: {opp.estimated_profit_sol:.4f} SOL")
            print(f"    Hops: {opp.hop_count}")
            print(f"    Total Fee: {opp.total_fee:.4f} SOL")
            print(f"    Confidence Score: {opp.confidence_score:.2f}")
            print(f"    Total Weight: {opp.total_weight:.6f}")


# Convenient function for quick detection
def detect_arbitrage(graph: nx.DiGraph,
                     min_profit: float = 0.005,
                     max_display: int = 10) -> List[ArbitrageOpportunity]:
    """
    Convenient arbitrage detection function

    Args:
        graph: Trading graph
        min_profit: Minimum profit threshold
        max_display: Maximum display quantity

    Returns:
        List[ArbitrageOpportunity]: List of arbitrage opportunities
    """
    detector = IntegratedArbitrageDetector(min_profit_threshold=min_profit)
    opportunities = detector.detect_arbitrage(graph)
    detector.print_opportunities(opportunities, max_display)
    return opportunities
