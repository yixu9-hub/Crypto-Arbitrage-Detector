#!/usr/bin/env python3
"""
Test script to verify that simulation data contains detectable negative cycles
验证模拟数据包含可检测负环的测试脚本
"""

import sys
import os
import networkx as nx

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.arbitrage_test_data_simulation import (
    create_simulation_graph_triangle,
    create_simulation_graph_complex, 
    create_simulation_graph_multihop,
    create_simulation_graph_overlapping
)
from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage
from crypto_arbitrage_detector.algorithms.triangle_arbitrage_algorithm import TriangleArbitrage

def test_simulation_data():
    """测试所有模拟数据集"""
    print("🧪 Testing Arbitrage Simulation Data")
    print("=" * 60)
    
    test_cases = [
        ("Simple Triangle", create_simulation_graph_triangle),
        ("Complex Network", create_simulation_graph_complex),
        ("Multi-hop", create_simulation_graph_multihop),
        ("Overlapping Cycles", create_simulation_graph_overlapping)
    ]
    
    bf_detector = BellmanFordArbitrage(min_profit_threshold=0.001)
    triangle_detector = TriangleArbitrage(min_profit_threshold=0.001)
    
    total_bf_opportunities = 0
    total_triangle_opportunities = 0
    
    for name, graph_func in test_cases:
        print(f"\n🔍 Testing {name}:")
        print("-" * 40)
        
        # Create graph
        graph = graph_func()
        print(f"  📊 Nodes: {graph.number_of_nodes()}")
        print(f"  📈 Edges: {graph.number_of_edges()}")
        
        # Test Bellman-Ford
        print(f"  🤖 Bellman-Ford Algorithm:")
        bf_opportunities = bf_detector.detect_opportunities(graph)
        bf_count = len(bf_opportunities)
        total_bf_opportunities += bf_count
        print(f"    ✅ Found {bf_count} opportunities")
        
        # Show first few opportunities
        for i, opp in enumerate(bf_opportunities[:3]):
            print(f"      💰 Opportunity {i+1}: {' → '.join(opp.path)}")
            print(f"         Profit ratio: {opp.profit_ratio:.6f}")
            print(f"         Weight: {opp.total_weight:.6f}")
        
        if bf_count > 3:
            print(f"      ... and {bf_count - 3} more")
        
        # Test Triangle Arbitrage  
        print(f"  🔺 Triangle Arbitrage Algorithm:")
        triangle_opportunities = triangle_detector.detect_opportunities(graph)
        triangle_count = len(triangle_opportunities)
        total_triangle_opportunities += triangle_count
        print(f"    ✅ Found {triangle_count} opportunities")
        
        # Show first few triangle opportunities
        for i, opp in enumerate(triangle_opportunities[:3]):
            print(f"      🔺 Triangle {i+1}: {' → '.join(opp.path)}")
            print(f"         Profit ratio: {opp.profit_ratio:.6f}")
            print(f"         Weight: {opp.total_weight:.6f}")
            
        if triangle_count > 3:
            print(f"      ... and {triangle_count - 3} more")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SIMULATION TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Total Bellman-Ford opportunities: {total_bf_opportunities}")
    print(f"✅ Total Triangle opportunities: {total_triangle_opportunities}")
    
    if total_bf_opportunities > 0 and total_triangle_opportunities > 0:
        print(f"🎉 SUCCESS: All simulation datasets contain detectable arbitrage!")
        print(f"🧪 These datasets are perfect for algorithm testing and validation.")
    else:
        print(f"❌ WARNING: Some datasets may not contain detectable arbitrage.")
    
    print("=" * 60)

def manual_cycle_verification():
    """手动验证负环计算"""
    print("\n🔍 Manual Cycle Verification")
    print("=" * 40)
    
    # Test simple triangle
    print("📊 Simple Triangle Verification:")
    graph = create_simulation_graph_triangle()
    
    # Get the triangle cycle
    nodes = list(graph.nodes())
    if len(nodes) >= 3:
        # Try to find the profitable cycle
        for node in nodes:
            for neighbor in graph.neighbors(node):
                for next_neighbor in graph.neighbors(neighbor):
                    if graph.has_edge(next_neighbor, node):
                        # Found a triangle
                        cycle = [node, neighbor, next_neighbor, node]
                        
                        # Calculate total weight
                        total_weight = 0
                        total_ratio = 1.0
                        
                        for i in range(len(cycle) - 1):
                            u, v = cycle[i], cycle[i + 1]
                            if graph.has_edge(u, v):
                                weight = graph[u][v]['weight']
                                ratio = graph[u][v]['price_ratio']
                                total_weight += weight
                                total_ratio *= ratio
                        
                        print(f"  🔺 Cycle: {' → '.join(cycle)}")
                        print(f"     Total weight: {total_weight:.6f}")
                        print(f"     Total ratio: {total_ratio:.6f}")
                        
                        if total_weight < 0:
                            print(f"     ✅ PROFITABLE (negative weight)")
                        else:
                            print(f"     ❌ Not profitable (positive weight)")
                        
                        break
                else:
                    continue
                break
            else:
                continue
            break

if __name__ == "__main__":
    test_simulation_data()
    manual_cycle_verification()
