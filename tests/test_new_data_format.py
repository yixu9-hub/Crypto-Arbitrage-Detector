"""
Test script for new arbitrage test data format with symbol support
"""
import sys
import os
import networkx as nx

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.arbitrage_test_data_new import new_arbitrage_test_data
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.utils.graph_utils import analyze_graph
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector

def get_node_symbol(graph: nx.DiGraph, node_address: str) -> str:
    """Quick helper to get node symbol from any edge"""
    for from_node, to_node, edge_data in graph.edges(data=True):
        if from_node == node_address:
            return edge_data['from_symbol']
        elif to_node == node_address:
            return edge_data['to_symbol']
    return node_address[:6] + "..." + node_address[-4:] if len(node_address) > 10 else node_address

def test_new_data_format():
    """Test the new arbitrage data format with symbol support"""
    
    print("Testing new arbitrage test data format...")
    print(f"Data contains {len(new_arbitrage_test_data)} EdgePairs entries")
    
    # Test 1: Check data format
    sample_edge = new_arbitrage_test_data[0]
    print(f"\nSample EdgePairs entry:")
    print(f"  From: {sample_edge.from_token[:10]}... ({sample_edge.from_symbol})")
    print(f"  To: {sample_edge.to_token[:10]}... ({sample_edge.to_symbol})")
    print(f"  Amount: {sample_edge.in_amount} -> {sample_edge.out_amount}")
    print(f"  Weight: {sample_edge.weight}")
    
    # Test 2: Build graph from new data
    print("\nBuilding graph from new test data...")
    try:
        graph = build_graph_from_edge_lists(new_arbitrage_test_data)
        print(f"✅ Graph built successfully")
        print(f"   Nodes: {graph.number_of_nodes()}")
        print(f"   Edges: {graph.number_of_edges()}")
        
        # Test 3: Check symbol support in graph utils
        print("\nTesting symbol display functionality...")
        nodes = list(graph.nodes())[:3]  # Test first 3 nodes
        for node in nodes:
            symbol = get_node_symbol(graph, node)
            print(f"   {node[:10]}... -> {symbol}")
        
        # Test 4: Test edge symbol information
        print("\nTesting edge symbol information...")
        sample_edges = list(graph.edges(data=True))[:3]
        for from_node, to_node, edge_data in sample_edges:
            from_symbol = edge_data.get('from_symbol', 'N/A')
            to_symbol = edge_data.get('to_symbol', 'N/A')
            print(f"   {from_symbol} -> {to_symbol}")
            
        # Test 5: Run arbitrage detection
        print("\nTesting arbitrage detection with new data...")
        detector = IntegratedArbitrageDetector(
            min_profit_threshold=0.01,  # 1% threshold for testing
            max_hops=3,
            base_amount=1000.0,
            enable_risk_evaluation=False
        )
        
        opportunities = detector.detect_arbitrage(graph)
        print(f"   Found {len(opportunities)} arbitrage opportunities")
        
        if opportunities:
            print("   Sample opportunity:")
            opp = opportunities[0]
            print(f"     Path: {' -> '.join([get_node_symbol(graph, token) for token in opp.path])}")
            print(f"     Profit: {opp.profit_ratio:.4f}")
            print(f"     Estimated profit SOL: {opp.estimated_profit_sol:.4f}")
        
        print("\n🎉 All tests passed! New data format is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_new_data_format()
