'''
Bellman-Ford Arbitrage Detection Algorithm
'''
import networkx as nx
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from utils.data_structures import ArbitrageOpportunity


class BellmanFordArbitrage:
    """
    Bellman-Ford negative cycle detection algorithm
    """

    def __init__(self,
                 min_profit_threshold: float = 0.005,  # 0.5%
                 max_hops: int = 4,
                 base_amount: float = 1.0):
        """
        Initialize algorithm

        Args:
            min_profit_threshold: Minimum profit threshold
            max_hops: Maximum allowed hops
            base_amount: Base trading amount (SOL)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_hops = max_hops
        self.base_amount = base_amount
        self.algorithm_name = "BellmanFordArbitrage"

    def detect_opportunities(self, graph: nx.DiGraph, source_token: str = None) -> List[ArbitrageOpportunity]:
        """
        Use Bellman-Ford algorithm to detect negative cycle arbitrage opportunities in a complete graph
        """
        opportunities = []

        try:
            # Always run Bellman-Ford from every node
            print(f"[{self.algorithm_name}] Running from all {graph.number_of_nodes()} nodes to detect negative cycles...")

            for node in graph.nodes():
                node_opportunities = self.bellman_ford(graph, node)

                # Add new opportunities (avoid duplicates)
                for opp in node_opportunities:
                    # Check if this opportunity is already in the list
                    is_duplicate = False
                    for existing in opportunities:
                        if self._are_same_cycle(opp.path, existing.path):
                            is_duplicate = True
                            break
                    # If not a duplicate, add to opportunities
                    if not is_duplicate:
                        opportunities.append(opp)
                        
            print(f"[{self.algorithm_name}] Found {len(opportunities)} total unique opportunities")

        except Exception as e:
            print(f"Bellman-Ford error: {e}")

        return self._filter_profitable_opportunities(opportunities)

    def bellman_ford(self, graph: nx.DiGraph, source_token: str) -> List[ArbitrageOpportunity]:
        """
        Bellman-Ford implementation for negative cycle detection
        """
        opportunities = []

        if source_token not in graph.nodes():
            print(f"Warning: Starting node {source_token} is not in the graph")
            return opportunities

        # Initialize distance dictionary and predecessors
        distances, predecessors = self._initialize_distances_and_predecessors(graph, source_token)

        # relaxation (|V| - 1 times)
        for _ in range(graph.number_of_nodes() - 1):
            self._relax_edges(graph, distances, predecessors)

        # Detect negative cycles
        negative_cycle_nodes = set()
        for u, v, data in graph.edges(data=True):
            adjusted_weight = self._calculate_adjusted_weight(data)
            if distances[u] != float('inf') and distances[u] + adjusted_weight < distances[v]:
                negative_cycle_nodes.add(v)

        # Reconstruct negative cycle paths
        if negative_cycle_nodes:
            for cycle_node in negative_cycle_nodes:
                cycle_path = self._find_actual_negative_cycle(
                    graph, cycle_node)
                if cycle_path and len(cycle_path) <= self.max_hops + 1:
                    opportunity = self._create_arbitrage_opportunity(
                        graph, cycle_path)
                    if opportunity:
                        #print(f"Created opportunity: profit={opportunity.profit_ratio:.6f}, threshold={self.min_profit_threshold:.6f}")
                        opportunities.append(opportunity)
                    else:
                        print(f"NO opportunity created")

        print(f"Found {len(opportunities)} opportunities from source {source_token}")
        return opportunities

    def _are_same_cycle(self, path1: List[str], path2: List[str]) -> bool:
        """
        Check if two paths represent the same cycle (considering rotations)
        """
        if len(path1) != len(path2):
            return False

        # Remove last duplicate node for comparison
        cycle1 = path1[:-1] if path1[0] == path1[-1] else path1
        cycle2 = path2[:-1] if path2[0] == path2[-1] else path2

        if len(cycle1) != len(cycle2):
            return False

        # Check all rotations
        for i in range(len(cycle1)):
            rotated = cycle1[i:] + cycle1[:i]
            # Check reverse
            if rotated == cycle2 or rotated == cycle2[::-1]:
                return True

        return False

    def _find_actual_negative_cycle(self, graph: nx.DiGraph, start_node: str) -> List[str]:
        """
        Find the actual negative cycle using simple bellman-ford approach
        """
        try:
            # Initialize distances and predecessors
            distances, predecessors = self._initialize_distances_and_predecessors(graph, start_node)
            
            # Standard Bellman-Ford relaxation
            for _ in range(graph.number_of_nodes() - 1):
                self._relax_edges(graph, distances, predecessors)
            
            # Find any node that can still be relaxed (part of negative cycle)
            cycle_node = None
            for u, v, data in graph.edges(data=True):
                adjusted_weight = self._calculate_adjusted_weight(data)
                if distances[u] != float('inf') and distances[u] + adjusted_weight < distances[v]:
                    cycle_node = v
                    break
            
            if cycle_node is None:
                return []
            
            # Find a node definitely in the cycle by following predecessors
            visited = set()
            current = cycle_node
            while current not in visited and current is not None:
                visited.add(current)
                current = predecessors[current]
            
            if current is None:
                return []
            
            # Reconstruct the cycle starting from current
            cycle = [current]
            next_node = predecessors[current]
            while next_node != current and next_node is not None:
                cycle.append(next_node)
                next_node = predecessors[next_node]
                if len(cycle) > self.max_hops:  # Safety check
                    break
            
            if next_node == current and len(cycle) >= 2:
                cycle.append(current)  # Complete the cycle
                #print(f"negative cycle detected: {[node[:8] + '...' for node in cycle]}")
                return cycle
            
        except Exception as e:
            print(f"Error in negative cycle detection: {e}")

        return []

    def _create_arbitrage_opportunity(self, graph: nx.DiGraph, path: List[str]) -> Optional[ArbitrageOpportunity]:
        """
        Create arbitrage opportunity object from path
        """
        path_display = []
        for i in path:
            path_display.append(i[:6]+'...') # Display first 6 characters
        #print(f" Creating opportunity from path: {path_display}")

        try:
            if len(path) < 2:
                print(f"Path too short: {len(path)} nodes")
                return None

            # Calculate total path weight, slippage, and price impact
            total_weight = 0.0
            total_slippage = 0.0
            total_price_impact = 0.0

            #print(f" Building trades from {len(path)} nodes:")
            for i in range(len(path) - 1):
                from_token = path[i]
                to_token = path[i + 1]

                if not graph.has_edge(from_token, to_token):
                    print(f"Missing edge: {from_token[:6]}... -> {to_token[:6]}...")
                    return None  # Invalid path

                edge_data = graph[from_token][to_token]
                weight = edge_data.get('weight', 0)

                slippage_bps = edge_data.get('slippage_bps', 0)
                price_impact_pct = edge_data.get('price_impact_pct', 0)

                slippage_decimal = slippage_bps / 10000.0

                #print(f"Trade {i+1}: {from_token[:6]}... -> {to_token[:6]}..., weight: {weight:.6f}")

                total_weight += weight
                total_slippage += slippage_decimal
                total_price_impact += abs(price_impact_pct)

            adjusted_weight = total_weight + \
                total_slippage + (total_price_impact / 100.0)

            #print(f" Total weight: {total_weight:.6f}, adjusted: {adjusted_weight:.6f}")

            # Calculate profit ratio (negative weight indicates arbitrage opportunity)
            if adjusted_weight >= 0:
                print(f"Path not profitable: adjusted_weight = {adjusted_weight:.6f}")
                return None  # No arbitrage opportunity

            base_profit_ratio = math.exp(-adjusted_weight) - 1
            #print(f"Profitable path: weight = {adjusted_weight:.6f}, profit = {base_profit_ratio:.6f}")

            # No need to deduct total_fee as outAmount already has fees deducted
            actual_profit_ratio = base_profit_ratio

            # Estimated profit (SOL) - profit before gas fee
            estimated_profit = self.base_amount * actual_profit_ratio

            slippage_risk = min(1.0, total_slippage * 10)
            price_impact_risk = min(1.0, total_price_impact / 10)

            # Confidence score calculation based on profit magnitude and market risks
            if estimated_profit > 0:
                # Higher profit = higher confidence
                # Adjust multiplier as needed
                base_confidence = min(1.0, estimated_profit * 10)
            else:
                base_confidence = 0.0

            confidence_score = base_confidence * \
                (1 - slippage_risk) * (1 - price_impact_risk)
            confidence_score = max(0.0, min(1.0, confidence_score))

            # Generate path symbols (for display)
            path_symbols = [f"{addr[:4]}...{addr[-4:]}" for addr in path]

            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=actual_profit_ratio,
                total_weight=adjusted_weight,
                total_fee=0.0,
                hop_count=len(path) - 1,
                confidence_score=confidence_score,
                estimated_profit_sol=estimated_profit
            )

        except Exception as e:
            print(
                f" Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None

    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """Filter opportunities that meet profit threshold"""
        filtered = [opp for opp in opportunities
                    if opp and opp.profit_ratio >= self.min_profit_threshold]
        return filtered

    def _calculate_adjusted_weight(self, edge_data):
        """Calculate adjusted weight including slippage and price impact"""
        base_weight = edge_data.get('weight', 0)
        slippage_bps = edge_data.get('slippage_bps', 0)
        price_impact_pct = edge_data.get('price_impact_pct', 0)
        slippage_decimal = slippage_bps / 10000.0
        return base_weight + slippage_decimal + abs(price_impact_pct) / 100.0

    def _initialize_distances_and_predecessors(self, graph, start_node):
        """Initialize distances and predecessors for Bellman-Ford"""
        distances = {}
        predecessors = {}
        for node in graph.nodes():
            distances[node] = float('inf')
            predecessors[node] = None
        distances[start_node] = 0
        return distances, predecessors

    def _relax_edges(self, graph, distances, predecessors):
        """Perform edge relaxation step of Bellman-Ford algorithm"""
        for u, v, data in graph.edges(data=True):
            adjusted_weight = self._calculate_adjusted_weight(data)
            if distances[u] != float('inf') and distances[u] + adjusted_weight < distances[v]:
                distances[v] = distances[u] + adjusted_weight
                predecessors[v] = u
