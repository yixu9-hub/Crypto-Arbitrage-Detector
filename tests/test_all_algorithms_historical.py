#!/usr/bin/env python3
"""
Comprehensive test of all arbitrage algorithms
"""

import sys
import os

# Add the parent directory to the path to access the data module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), 'crypto_arbitrage_detector'))

from data.historical_data import new_arbitrage_test_data
from crypto_arbitrage_detector.utils.graph_structure import TokenGraphBuilder
from crypto_arbitrage_detector.algorithms.triangle_arbitrage_algorithm import TriangleArbitrage
from crypto_arbitrage_detector.algorithms.two_hop_arbitrage_algorithm import TwoHopArbitrage
from crypto_arbitrage_detector.algorithms.exhaustive_dfs_algorithm import ExhaustiveDFSArbitrage
from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage

def test_all_algorithms():
    """Comprehensive test of all arbitrage algorithms"""
    
    print(f"=== Comprehensive Arbitrage Algorithm Test - Using {len(new_arbitrage_test_data)} Historical Data Points ===\n")
    
    # Create graph structure
    print("Creating graph structure...")
    graph_builder = TokenGraphBuilder()
    graph = graph_builder.build_graph_from_edge_lists(new_arbitrage_test_data)
    
    print(f"Graph structure created: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges\n")
    
    # Test parameters
    base_amount = 5  # SOL
    min_profit_threshold = 0.005  # 0.5% minimum profit
    
    algorithms = [
        ("Bellman-Ford", BellmanFordArbitrage(min_profit_threshold=min_profit_threshold, base_amount=base_amount)),
        ("Two-Hop Arbitrage", TwoHopArbitrage(min_profit_threshold=min_profit_threshold, base_amount=base_amount)),
        ("Triangle Arbitrage", TriangleArbitrage(min_profit_threshold=min_profit_threshold, base_amount=base_amount)),
        ("Exhaustive DFS", ExhaustiveDFSArbitrage(min_profit_threshold=min_profit_threshold, max_hops=4, base_amount=base_amount))
    ]
    
    results = {}
    
    for algo_name, algorithm in algorithms:
        print(f"=== Testing {algo_name} ===")
        
        # Detect opportunities
        opportunities = algorithm.detect_opportunities(graph)
        
        results[algo_name] = {
            'opportunities': opportunities,
            'count': len(opportunities),
            'best_profit': opportunities[0].profit_ratio if opportunities else 0,
            'avg_profit': sum(opp.profit_ratio for opp in opportunities) / len(opportunities) if opportunities else 0,
            'total_estimated_profit': sum(opp.estimated_profit_sol for opp in opportunities)
        }
        
        print(f"Found {len(opportunities)} arbitrage opportunities")
        
        if opportunities:
            print(f"Best profit ratio: {opportunities[0].profit_ratio:.4f} ({opportunities[0].profit_ratio*100:.2f}%)")
            print(f"Average profit ratio: {results[algo_name]['avg_profit']:.4f} ({results[algo_name]['avg_profit']*100:.2f}%)")
            print(f"Total estimated profit: {results[algo_name]['total_estimated_profit']:.4f} SOL")
            
            # Show top 3 opportunities
            print("Top 3 opportunities:")
            for i, opp in enumerate(opportunities[:3]):
                print(f"  {i+1}. {' -> '.join(opp.path_symbols)} | "
                      f"Profit: {opp.profit_ratio:.4f} ({opp.profit_ratio*100:.2f}%) | "
                      f"Fees: {opp.total_fee:.6f} SOL | "
                      f"Net profit: {opp.estimated_profit_sol:.6f} SOL")
        
        # Get algorithm-specific stats if available
        if hasattr(algorithm, 'get_algorithm_stats'):
            stats = algorithm.get_algorithm_stats()
            print(f"Algorithm stats: {stats['paths_explored']} paths explored, {stats['cycles_found']} cycles found, {stats['pruning_efficiency']:.2f}% pruning efficiency")
        
        print()
    
    # Summary comparison
    print("=== Algorithm Performance Comparison ===")
    print(f"{'Algorithm Name':<20} {'Opportunities':<12} {'Best Profit':<15} {'Avg Profit':<15} {'Total Profit':<15}")
    print("-" * 77)
    
    for algo_name in results:
        result = results[algo_name]
        print(f"{algo_name:<20} {result['count']:<12} "
              f"{result['best_profit']*100:<14.2f}% "
              f"{result['avg_profit']*100:<14.2f}% "
              f"{result['total_estimated_profit']:<14.4f} SOL")

if __name__ == "__main__":
    test_all_algorithms()
