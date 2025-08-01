"""
Comprehensive Algorithm Comparison - Including Exhaustive DFS
包含新增的全路径DFS算法的综合比较测试
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage
from crypto_arbitrage_detector.algorithms.triangle_arbitrage_algorithm import TriangleArbitrage
from crypto_arbitrage_detector.algorithms.two_hop_arbitrage_algorithm import TwoHopArbitrage
from crypto_arbitrage_detector.algorithms.exhaustive_dfs_algorithm import ExhaustiveDFSArbitrage
from tests.arbitrage_test_data_simulation import (
    simple_triangle_edges,
    complex_network_edges,
    multi_hop_edges,
    overlapping_cycles_edges,
    create_test_graph_from_edges
)


def compare_all_algorithms():
    """比较所有算法在不同数据集上的性能"""
    print("🏆 Comprehensive Algorithm Comparison")
    print("=" * 70)
    
    # Initialize all algorithms
    algorithms = {
        "BellmanFord": BellmanFordArbitrage(min_profit_threshold=0.001, max_hops=4, base_amount=1.0),
        "Triangle": TriangleArbitrage(min_profit_threshold=0.001, base_amount=1.0),
        "TwoHop": TwoHopArbitrage(min_profit_threshold=0.001, base_amount=1.0),
        "ExhaustiveDFS": ExhaustiveDFSArbitrage(min_profit_threshold=0.001, max_hops=4, base_amount=1.0, profit_pruning_threshold=-0.3)
    }
    
    test_datasets = [
        ("Simple Triangle", simple_triangle_edges),
        ("Complex Network", complex_network_edges),
        ("Multi-hop", multi_hop_edges),
        ("Overlapping Cycles", overlapping_cycles_edges)
    ]
    
    results = {}
    
    for dataset_name, edges in test_datasets:
        print(f"\n📊 Testing Dataset: {dataset_name}")
        print("-" * 50)
        
        graph = create_test_graph_from_edges(edges)
        print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        results[dataset_name] = {}
        
        for algo_name, algorithm in algorithms.items():
            print(f"\n🔍 Running {algo_name}...")
            
            start_time = time.time()
            opportunities = algorithm.detect_opportunities(graph)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            # Get best profit
            best_profit = max([opp.profit_ratio for opp in opportunities]) if opportunities else 0
            
            # Store results
            results[dataset_name][algo_name] = {
                'count': len(opportunities),
                'best_profit': best_profit,
                'execution_time': execution_time
            }
            
            # Get algorithm-specific stats
            if hasattr(algorithm, 'get_algorithm_stats'):
                stats = algorithm.get_algorithm_stats()
                results[dataset_name][algo_name]['stats'] = stats
            
            print(f"  ✅ Found {len(opportunities)} opportunities")
            print(f"  💰 Best profit: {best_profit:.4f} ({best_profit*100:.2f}%)")
            print(f"  ⏱️ Execution time: {execution_time:.4f}s")
    
    # Generate summary report
    print_summary_report(results)


def print_summary_report(results):
    """打印总结报告"""
    print(f"\n🏆 ALGORITHM PERFORMANCE SUMMARY")
    print("=" * 70)
    
    # Header
    print(f"{'Dataset':<18} {'Algorithm':<15} {'Count':<6} {'Best%':<8} {'Time(s)':<8} {'Special':<15}")
    print("-" * 70)
    
    for dataset_name, dataset_results in results.items():
        first_row = True
        for algo_name, result in dataset_results.items():
            dataset_col = dataset_name if first_row else ""
            count = result['count']
            profit_pct = result['best_profit'] * 100
            exec_time = result['execution_time']
            
            # Special info for ExhaustiveDFS
            special_info = ""
            if algo_name == "ExhaustiveDFS" and 'stats' in result:
                stats = result['stats']
                special_info = f"Prune:{stats['pruning_efficiency']:.0f}%"
            
            print(f"{dataset_col:<18} {algo_name:<15} {count:<6} {profit_pct:<7.2f} {exec_time:<7.4f} {special_info:<15}")
            first_row = False
        print("-" * 70)
    
    # Algorithm comparison analysis
    print(f"\n📊 ALGORITHM ANALYSIS:")
    print("-" * 30)
    
    total_stats = {}
    for dataset_results in results.values():
        for algo_name, result in dataset_results.items():
            if algo_name not in total_stats:
                total_stats[algo_name] = {'total_count': 0, 'total_time': 0, 'max_profit': 0}
            
            total_stats[algo_name]['total_count'] += result['count']
            total_stats[algo_name]['total_time'] += result['execution_time']
            total_stats[algo_name]['max_profit'] = max(total_stats[algo_name]['max_profit'], result['best_profit'])
    
    for algo_name, stats in total_stats.items():
        print(f"{algo_name}:")
        print(f"  • Total opportunities: {stats['total_count']}")
        print(f"  • Max profit found: {stats['max_profit']*100:.2f}%")
        print(f"  • Total execution time: {stats['total_time']:.4f}s")
        print(f"  • Avg time per dataset: {stats['total_time']/len(results):.4f}s")
        
        if algo_name == "ExhaustiveDFS":
            print(f"  • Advantage: Most comprehensive search, finds ALL cycles")
            print(f"  • Trade-off: Higher computational cost, but with smart pruning")
        
        print()


if __name__ == "__main__":
    compare_all_algorithms()
