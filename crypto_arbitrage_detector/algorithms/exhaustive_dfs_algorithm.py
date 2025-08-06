'''
Exhaustive DFS with Profit Pruning
This module implements an exhaustive DFS algorithm to find arbitrage 
opportunities.
'''

import networkx as nx
import math
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional, Set, Dict
from utils.data_structures import ArbitrageOpportunity
from utils.graph_utils import get_node_symbol
from configs.strategy_config import get_algorithm_config


class ExhaustiveDFSArbitrage:
    """
    Exhaustive DFS with Profit Pruning Algorithm
    """

    def __init__(self,
                 min_profit_threshold: float = None,
                 max_hops: int = None,
                 base_amount: float = None,
                 profit_pruning_threshold: float = None):
        """
        Initialize algorithm

        Args:
            min_profit_threshold: Minimum profit threshold
            max_hops: Maximum allowed hops
            base_amount: Base trading amount in SOL
            profit_pruning_threshold: Early pruning threshold
        """
        # Get algorithm configuration
        config = get_algorithm_config("exhaustive_dfs")

        # Set parameters from config
        self.min_profit_threshold = config["min_profit_threshold"]
        self.max_hops = config["max_hops"]
        self.base_amount = config["base_amount"]
        self.profit_pruning_threshold = config["profit_pruning_threshold"]
        
        # Override with provided parameters if not None
        if min_profit_threshold is not None:
            self.min_profit_threshold = min_profit_threshold
        if max_hops is not None:
            self.max_hops = max_hops
        if base_amount is not None:
            self.base_amount = base_amount
        if profit_pruning_threshold is not None:
            self.profit_pruning_threshold = profit_pruning_threshold
        self.algorithm_name = "ExhaustiveDFSArbitrage"
        
        # Initialize counters
        self.paths_explored = 0
        self.paths_pruned = 0
        self.cycles_found = 0

    def detect_opportunities(self, graph: nx.DiGraph, source_token: str = None) -> List[ArbitrageOpportunity]:
        """
        Use exhaustive DFS to find all profitable arbitrage cycles
        """
        opportunities = []
        
        self.paths_explored = 0
        self.paths_pruned = 0
        self.cycles_found = 0

        try:

            cycles = []
            
            for node in graph.nodes():
                node_cycles = self._exhaustive_dfs_from_node(graph, node)
                cycles.extend(node_cycles)
            
            # Convert cycles to arbitrage opportunities
            for cycle in cycles:
                opportunity = self._create_arbitrage_opportunity(graph, cycle)
                if opportunity:
                    opportunities.append(opportunity)
            
            # Remove duplicate cycles
            opportunities = self._deduplicate_opportunities(opportunities)
            
            print(f"[{self.algorithm_name}] Stats: {self.paths_explored} paths, {self.cycles_found} cycles, {len(opportunities)} opportunities")

        except Exception as e:
            print(f"Exhaustive DFS error: {e}")

        return self._filter_profitable_opportunities(opportunities)

    def _exhaustive_dfs_from_node(self, graph: nx.DiGraph, start_node: str) -> List[List[str]]:
        """
        Perform exhaustive DFS from a single starting node to find all cycles
        """
        cycles = []
        
        def dfs_recursive(current_node: str, 
                         path: List[str], 
                         path_weight: float, 
                         depth: int,
                         visited_in_path: Set[str]):
            
            """          
            Recursive DFS helper function
            """
            # Increment paths explored counter
            self.paths_explored += 1
            
            # Early pruning: if current path is too unprofitable, stop exploring
            if path_weight > self.profit_pruning_threshold:
                self.paths_pruned += 1
                return
            
            # Maximum depth reached
            if depth >= self.max_hops:
                return
            
            # Explore all neighbors
            for neighbor in graph.successors(current_node):
                
                # Check if we've found a cycle back to start
                if neighbor == start_node and len(path) >= 2:
                    # Calculate final cycle weight
                    if graph.has_edge(current_node, neighbor):
                        edge_data = graph[current_node][neighbor]
                        final_weight = edge_data.get('weight', 0)
                        total_cycle_weight = path_weight + final_weight
                        
                        # Check if this is a profitable cycle (negative weight = profitable)
                        if total_cycle_weight < 0:
                            cycle = path + [neighbor]
                            cycles.append(cycle)
                            self.cycles_found += 1
                
                # Continue DFS if node not visited in current path
                elif neighbor not in visited_in_path and depth < self.max_hops - 1:
                    if graph.has_edge(current_node, neighbor):
                        edge_data = graph[current_node][neighbor]
                        edge_weight = edge_data.get('weight', 0)
                        new_weight = path_weight + edge_weight
                        
                        # Recursive call with updated state
                        new_visited = visited_in_path.copy()
                        new_visited.add(neighbor)
                        
                        dfs_recursive(
                            neighbor,
                            path + [neighbor],
                            new_weight,
                            depth + 1,
                            new_visited
                        )
        
        # Start DFS from the starting node
        initial_visited = {start_node}
        dfs_recursive(start_node, [start_node], 0.0, 0, initial_visited)
        
        return cycles

    def _calculate_adjusted_weight(self, edge_data: Dict) -> float:
        """
        Calculate adjusted edge weight including slippage and price impact
        """
        base_weight = edge_data.get('weight', 0)
        slippage_bps = edge_data.get('slippage_bps', 0)
        price_impact_pct = edge_data.get('price_impact_pct', 0)
        
        # Convert slippage from basis points to decimal
        slippage_decimal = slippage_bps / 10000.0
        
        # Adjust weight with market factors
        adjusted_weight = base_weight + slippage_decimal + abs(price_impact_pct)
        
        return adjusted_weight

    def _deduplicate_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        Remove duplicate cycles (same cycle starting from different nodes)
        """
        unique_opportunities = []
        seen_cycles = set()
        
        for opp in opportunities:
            # Create normalized cycle representation
            cycle = opp.path[:-1]  # Remove duplicate end node
            min_idx = cycle.index(min(cycle))
            normalized_cycle = tuple(cycle[min_idx:] + cycle[:min_idx])
            
            # Check if this cycle has been seen before
            if normalized_cycle not in seen_cycles:
                seen_cycles.add(normalized_cycle)
                unique_opportunities.append(opp)
        
        return unique_opportunities

    def _create_arbitrage_opportunity(self, graph: nx.DiGraph, path: List[str]) -> Optional[ArbitrageOpportunity]:
        """
        Create arbitrage opportunity object from cycle path
        """
        try:
            if len(path) < 3:
                return None

            # Calculate path weight and trading fees separately
            total_weight = 0.0
            total_trading_fee = 0.0
            total_gas_fee = 0.0

            for i in range(len(path) - 1):
                from_token = path[i]
                to_token = path[i + 1]

                if not graph.has_edge(from_token, to_token):
                    return None

                # Get edge data
                edge_data = graph[from_token][to_token]
                total_weight += edge_data.get('weight', 0)
                total_gas_fee += edge_data.get('gas_fee', 0)
                
                # Calculate proportional trading fee
                edge_in_amount = edge_data.get('in_amount', 1)
                edge_total_fee = edge_data.get('total_fee', 0)
                scaled_trading_fee = edge_total_fee * (self.base_amount / edge_in_amount)
                total_trading_fee += scaled_trading_fee

            # Check profitability
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

            # Simple confidence score based on profit magnitude
            confidence_score = min(1.0, max(0.0, net_profit_ratio * 10))

            # Generate path symbols
            path_symbols = []
            for addr in path:
                path_symbols.append(get_node_symbol(graph, addr))

            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=net_profit_ratio,
                total_weight=total_weight,
                total_fee=total_fee_sol,
                hop_count=len(path) - 1,
                confidence_score=confidence_score,
                estimated_profit_sol=net_profit
            )

        except Exception as e:
            print(f"Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None

    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        Filter opportunities that meet profit threshold
        """
        filtered = [opp for opp in opportunities
                    if opp and opp.profit_ratio >= self.min_profit_threshold]
        
        # Sort by profit ratio (descending)
        filtered.sort(key=lambda x: x.profit_ratio, reverse=True)
        
        return filtered

    def get_algorithm_stats(self) -> Dict[str, int]:
        """
        Get performance statistics for the last run
        """
        return {
            'paths_explored': self.paths_explored,
            'paths_pruned': self.paths_pruned,
            'cycles_found': self.cycles_found,
            'pruning_efficiency': self.paths_pruned / max(1, self.paths_explored) * 100
        }
