#!/usr/bin/env python3
"""
Validation script for arbitrage test data
Tests data integrity, graph structure, and algorithm compatibility
"""

import sys
import os
import networkx as nx
from collections import defaultdict
import math

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.arbitrage_test_data import arbitrage_test_edges, create_test_graph_for_bellman_ford
from crypto_arbitrage_detector.utils.data_structures import EdgePairs
from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage

def validate_edge_data():
    """Validate EdgePairs data structure and values"""
    print("🔍 Validating EdgePairs data structure...")
    
    errors = []
    warnings = []
    
    # Check if we have any edges
    if not arbitrage_test_edges:
        errors.append("No edges found in arbitrage_test_edges")
        return errors, warnings
    
    print(f"📊 Total edges: {len(arbitrage_test_edges)}")
    
    # Collect unique tokens
    tokens = set()
    
    for i, edge in enumerate(arbitrage_test_edges):
        # Check data types
        if not isinstance(edge, EdgePairs):
            errors.append(f"Edge {i}: Not an EdgePairs instance")
            continue
            
        # Check required fields
        required_fields = ['from_token', 'to_token', 'out_amount', 'price_ratio', 'weight']
        for field in required_fields:
            if not hasattr(edge, field):
                errors.append(f"Edge {i}: Missing {field}")
            elif getattr(edge, field) is None:
                errors.append(f"Edge {i}: {field} is None")
        
        # Collect tokens
        tokens.add(edge.from_token)
        tokens.add(edge.to_token)
        
        # Validate numeric values
        if hasattr(edge, 'out_amount') and edge.out_amount <= 0:
            warnings.append(f"Edge {i}: out_amount is non-positive ({edge.out_amount})")
        
        if hasattr(edge, 'price_ratio') and edge.price_ratio <= 0:
            errors.append(f"Edge {i}: price_ratio is non-positive ({edge.price_ratio})")
        
        # Check weight calculation (should be negative log of price_ratio)
        if hasattr(edge, 'price_ratio') and hasattr(edge, 'weight'):
            expected_weight = -math.log(edge.price_ratio)
            if abs(edge.weight - expected_weight) > 0.001:
                warnings.append(f"Edge {i}: weight ({edge.weight}) doesn't match -log(price_ratio) ({expected_weight})")
    
    print(f"🪙 Unique tokens: {len(tokens)}")
    
    # Check for duplicate edges
    edge_pairs = set()
    for i, edge in enumerate(arbitrage_test_edges):
        pair = (edge.from_token, edge.to_token)
        if pair in edge_pairs:
            warnings.append(f"Edge {i}: Duplicate edge from {edge.from_token[:8]}... to {edge.to_token[:8]}...")
        edge_pairs.add(pair)
    
    return errors, warnings, tokens

def validate_graph_structure():
    """Validate the graph structure created from test data"""
    print("\n🕸️ Validating graph structure...")
    
    errors = []
    warnings = []
    
    try:
        graph = create_test_graph_for_bellman_ford()
        
        print(f"📈 Graph nodes: {len(graph.nodes())}")
        print(f"📊 Graph edges: {len(graph.edges())}")
        
        # Check if graph is connected
        if not nx.is_weakly_connected(graph):
            warnings.append("Graph is not weakly connected - some tokens may be isolated")
        
        # Check for self-loops
        self_loops = list(nx.selfloop_edges(graph))
        if self_loops:
            warnings.append(f"Found {len(self_loops)} self-loops in graph")
        
        # Check node degrees
        in_degrees = dict(graph.in_degree())
        out_degrees = dict(graph.out_degree())
        
        isolated_nodes = [node for node in graph.nodes() if in_degrees[node] == 0 and out_degrees[node] == 0]
        if isolated_nodes:
            errors.append(f"Found {len(isolated_nodes)} isolated nodes")
        
        # Check for nodes with only incoming or only outgoing edges
        sink_nodes = [node for node in graph.nodes() if out_degrees[node] == 0 and in_degrees[node] > 0]
        source_nodes = [node for node in graph.nodes() if in_degrees[node] == 0 and out_degrees[node] > 0]
        
        if sink_nodes:
            warnings.append(f"Found {len(sink_nodes)} sink nodes (only incoming edges)")
        if source_nodes:
            warnings.append(f"Found {len(source_nodes)} source nodes (only outgoing edges)")
        
        # Check edge attributes
        for u, v, data in graph.edges(data=True):
            required_attrs = ['weight', 'out_amount', 'price_ratio']
            for attr in required_attrs:
                if attr not in data:
                    errors.append(f"Edge ({u[:8]}..., {v[:8]}...): Missing {attr} attribute")
        
        return errors, warnings, graph
        
    except Exception as e:
        errors.append(f"Failed to create graph: {str(e)}")
        return errors, warnings, None

def validate_algorithm_compatibility():
    """Test compatibility with Bellman-Ford algorithm"""
    print("\n🤖 Testing algorithm compatibility...")
    
    errors = []
    warnings = []
    
    try:
        # Create graph
        graph = create_test_graph_for_bellman_ford()
        if graph is None:
            errors.append("Cannot create graph for algorithm testing")
            return errors, warnings
        
        # Test Bellman-Ford algorithm
        bf_detector = BellmanFordArbitrage()
        
        # Test with first node as source
        nodes = list(graph.nodes())
        if not nodes:
            errors.append("Graph has no nodes")
            return errors, warnings
        
        source_token = nodes[0]
        print(f"🎯 Testing with source token: {source_token[:8]}...")
        
        # Run algorithm
        opportunities = bf_detector.detect_opportunities(graph, source_token=source_token)
        
        print(f"💰 Found {len(opportunities)} arbitrage opportunities")
        
        # Validate opportunities
        for i, opp in enumerate(opportunities):
            if not hasattr(opp, 'path') or not opp.path:
                errors.append(f"Opportunity {i}: Missing or empty path")
            
            if not hasattr(opp, 'profit_ratio') or opp.profit_ratio <= 1.0:
                warnings.append(f"Opportunity {i}: Low profit ratio ({getattr(opp, 'profit_ratio', 'N/A')})")
        
        # Test with all nodes (complete graph behavior)
        print("🔄 Testing all-tokens detection...")
        all_opportunities = bf_detector.detect_opportunities(graph, source_token=None)
        print(f"💎 Total opportunities from all nodes: {len(all_opportunities)}")
        
        return errors, warnings
        
    except Exception as e:
        errors.append(f"Algorithm test failed: {str(e)}")
        return errors, warnings

def check_market_realism():
    """Check if the data represents realistic market conditions"""
    print("\n💹 Checking market realism...")
    
    warnings = []
    
    # Analyze price ratios
    price_ratios = [edge.price_ratio for edge in arbitrage_test_edges if hasattr(edge, 'price_ratio')]
    
    if price_ratios:
        min_ratio = min(price_ratios)
        max_ratio = max(price_ratios)
        
        print(f"📊 Price ratio range: {min_ratio:.8f} to {max_ratio:.2f}")
        
        # Check for extreme ratios
        if min_ratio < 1e-8:
            warnings.append(f"Very small price ratios detected (min: {min_ratio})")
        
        if max_ratio > 1e6:
            warnings.append(f"Very large price ratios detected (max: {max_ratio})")
    
    # Analyze fees
    gas_fees = [edge.gas_fee for edge in arbitrage_test_edges if hasattr(edge, 'gas_fee')]
    total_fees = [edge.total_fee for edge in arbitrage_test_edges if hasattr(edge, 'total_fee')]
    
    if gas_fees:
        avg_gas = sum(gas_fees) / len(gas_fees)
        print(f"⛽ Average gas fee: {avg_gas:.2f}")
    
    if total_fees:
        avg_total = sum(total_fees) / len(total_fees)
        print(f"💸 Average total fee: {avg_total:.2f}")
    
    return warnings

def main():
    """Run all validation checks"""
    print("🚀 Starting arbitrage test data validation...\n")
    
    all_errors = []
    all_warnings = []
    
    # Validate edge data
    errors, warnings, tokens = validate_edge_data()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Validate graph structure
    if not errors:  # Only if edge data is valid
        errors, warnings, graph = validate_graph_structure()
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Test algorithm compatibility
    if not all_errors:  # Only if no critical errors
        errors, warnings = validate_algorithm_compatibility()
        all_errors.extend(errors)
        all_warnings.extend(warnings)
    
    # Check market realism
    market_warnings = check_market_realism()
    all_warnings.extend(market_warnings)
    
    # Final report
    print("\n" + "="*60)
    print("📋 VALIDATION REPORT")
    print("="*60)
    
    if all_errors:
        print(f"❌ ERRORS ({len(all_errors)}):")
        for error in all_errors:
            print(f"  • {error}")
    
    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)}):")
        for warning in all_warnings:
            print(f"  • {warning}")
    
    if not all_errors and not all_warnings:
        print("✅ All checks passed! Test data is ready for use.")
    elif not all_errors:
        print("✅ No critical errors. Test data can be used with minor considerations.")
    else:
        print("❌ Critical errors found. Test data needs fixes before use.")
    
    print("\n" + "="*60)
    
    return len(all_errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
