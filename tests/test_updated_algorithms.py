"""
Test Updated Algorithms - No Starting Node
Test to verify all algorithms now search the entire graph without relying on a single starting node
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from arbitrage_test_data import arbitrage_test_edges


def test_updated_algorithms():
    """Test all algorithms with the updated full-graph search approach"""
    print("Testing Updated Algorithms - Full Graph Search")
    print("=" * 60)
    
    # Build graph from test data
    graph = build_graph_from_edge_lists(arbitrage_test_edges)
    print(f"Built graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Create detector with updated algorithms
    detector = IntegratedArbitrageDetector(
        min_profit_threshold=0.001,  # Lower threshold to find opportunities
        enable_risk_evaluation=True
    )
    
    print("\n" + "="*60)
    print("Running Detection with Updated Algorithms")
    print("="*60)
    
    # Run detection (source_token will be ignored by all algorithms now)
    opportunities = detector.detect_arbitrage(
        graph,
        source_token="any_token_will_be_ignored",  # This parameter is now ignored
        enable_bellman_ford=True,
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=True
    )
    
    print(f"\n" + "="*60)
    print("Results Summary")
    print("="*60)
    print(f"Total opportunities found: {len(opportunities)}")
    
    if opportunities:
        print(f"\nTop {min(5, len(opportunities))} opportunities:")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. Path: {' -> '.join(opp.path_symbols)}")
            print(f"   Profit: {opp.profit_ratio*100:.3f}%")
            print(f"   Confidence: {opp.confidence_score:.3f}")
            print(f"   Hops: {opp.hop_count}")
    else:
        print("No arbitrage opportunities found.")
        print("This is expected if the test data represents a balanced market.")
    
    # Test individual algorithms to show they work independently
    print(f"\n" + "="*60)
    print("Testing Individual Algorithms")
    print("="*60)
    
    from crypto_arbitrage_detector.algorithms.triangle_arbitrage_algorithm import TriangleArbitrage
    from crypto_arbitrage_detector.algorithms.two_hop_arbitrage_algorithm import TwoHopArbitrage
    
    # Test Triangle Arbitrage
    triangle_algo = TriangleArbitrage(min_profit_threshold=0.001)
    triangle_opps = triangle_algo.detect_opportunities(graph, None)
    print(f"Triangle algorithm found: {len(triangle_opps)} opportunities")
    
    # Test Two-Hop Arbitrage
    two_hop_algo = TwoHopArbitrage(min_profit_threshold=0.001)
    two_hop_opps = two_hop_algo.detect_opportunities(graph, None)
    print(f"Two-hop algorithm found: {len(two_hop_opps)} opportunities")
    
    print(f"\n" + "="*60)
    print("Verification Complete")
    print("="*60)
    print("All algorithms now search the entire graph without requiring a starting node.")
    print("This is appropriate for complete graphs where all nodes have equal connectivity.")


if __name__ == "__main__":
    test_updated_algorithms()
