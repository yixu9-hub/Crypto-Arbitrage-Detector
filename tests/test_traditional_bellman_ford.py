"""
Test Traditional BellmanFord Algorithm
测试传统的BellmanFord算法（移除DFS策略后）
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage
from tests.arbitrage_test_data_simulation import (
    simple_triangle_edges,
    complex_network_edges,
    create_test_graph_from_edges
)


def test_traditional_bellman_ford():
    """测试传统BellmanFord算法"""
    print("🧪 Testing Traditional BellmanFord Algorithm")
    print("=" * 60)
    
    # Initialize algorithm
    algorithm = BellmanFordArbitrage(min_profit_threshold=0.001, max_hops=4, base_amount=1.0)
    
    test_datasets = [
        ("Simple Triangle", simple_triangle_edges),
        ("Complex Network", complex_network_edges)
    ]
    
    for dataset_name, edges in test_datasets:
        print(f"\n📊 Testing {dataset_name} Dataset:")
        print("-" * 40)
        
        graph = create_test_graph_from_edges(edges)
        print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        
        # Test algorithm
        opportunities = algorithm.detect_opportunities(graph)
        
        print(f"\n🎯 Results:")
        print(f"  Opportunities found: {len(opportunities)}")
        
        if opportunities:
            best_profit = max(opp.profit_ratio for opp in opportunities)
            print(f"  Best profit: {best_profit:.4f} ({best_profit*100:.2f}%)")
            
            print(f"\n💰 Top Opportunities:")
            for i, opp in enumerate(opportunities[:3], 1):
                profit_pct = opp.profit_ratio * 100
                print(f"    {i}. {' → '.join(opp.path_symbols)}")
                print(f"       Profit: {profit_pct:.4f}% | Hops: {opp.hop_count}")
        else:
            print(f"  No profitable opportunities found")
    
    print(f"\n✅ Traditional BellmanFord testing completed!")
    print(f"🎯 Algorithm now uses pure Bellman-Ford cycle reconstruction")


if __name__ == "__main__":
    test_traditional_bellman_ford()
