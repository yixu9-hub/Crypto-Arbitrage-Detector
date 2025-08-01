"""
Test Risk Evaluator Integration
Simple test to verify risk evaluator works with arbitrage detector
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.utils.data_structures import ArbitrageOpportunity
from crypto_arbitrage_detector.algorithms.risk_evaluator import ArbitrageRiskEvaluator
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from arbitrage_test_data import arbitrage_test_edges


def test_risk_evaluator_standalone():
    """Test risk evaluator with manually created opportunities"""
    print("Testing Risk Evaluator - Standalone")
    print("=" * 50)
    
    # Create test opportunities
    high_profit_opp = ArbitrageOpportunity(
        path=['SOL', 'USDC', 'SOL'],
        path_symbols=['SOL', 'USDC', 'SOL'],
        profit_ratio=0.025,  # 2.5%
        total_weight=-0.025,
        total_fee=0.001,
        hop_count=2,
        confidence_score=0.8,
        estimated_profit_sol=0.025
    )
    
    risky_opp = ArbitrageOpportunity(
        path=['SOL', 'USDC', 'BONK', 'RAY', 'SOL'],
        path_symbols=['SOL', 'USDC', 'BONK', 'RAY', 'SOL'],
        profit_ratio=0.008,  # 0.8%
        total_weight=-0.008,
        total_fee=0.002,
        hop_count=4,
        confidence_score=0.3,
        estimated_profit_sol=0.008
    )
    
    # Initialize risk evaluator
    risk_evaluator = ArbitrageRiskEvaluator()
    
    # Test both opportunities
    opportunities = [high_profit_opp, risky_opp]
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\nOpportunity {i}:")
        print(f"  Path: {' -> '.join(opp.path_symbols)}")
        print(f"  Profit: {opp.profit_ratio*100:.2f}%")
        print(f"  Hops: {opp.hop_count}")
        
        # Evaluate risk
        risk_result = risk_evaluator.evaluate_opportunity(opp)
        
        print(f"  Risk Score: {risk_result['risk_score']:.3f}")
        print(f"  Risk Level: {risk_result['risk_level']}")
        print(f"  Recommendation: {risk_result['recommendation']}")
        print(f"  Gas Cost Ratio: {risk_result['gas_cost_ratio']:.3f}")
        print(f"  Total Slippage: {risk_result['total_slippage_pct']:.3f}%")


def test_integrated_detector_with_risk():
    """Test integrated detector with risk evaluation enabled"""
    print("\n\nTesting Integrated Detector with Risk Evaluation")
    print("=" * 50)
    
    # Build graph from test data
    graph = build_graph_from_edge_lists(arbitrage_test_edges)
    print(f"Built graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    
    # Test with risk evaluation enabled
    detector_with_risk = IntegratedArbitrageDetector(
        min_profit_threshold=0.001,  # Low threshold to find opportunities
        enable_risk_evaluation=True
    )
    
    print("\n--- Detection with Risk Evaluation ---")
    opportunities_with_risk = detector_with_risk.detect_arbitrage(
        graph,
        enable_bellman_ford=False,  # Focus on simpler algorithms for testing
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=False
    )
    
    print(f"\nOpportunities found with risk evaluation: {len(opportunities_with_risk)}")
    
    # Test without risk evaluation for comparison
    detector_without_risk = IntegratedArbitrageDetector(
        min_profit_threshold=0.001,
        enable_risk_evaluation=False
    )
    
    print("\n--- Detection without Risk Evaluation ---")
    opportunities_without_risk = detector_without_risk.detect_arbitrage(
        graph,
        enable_bellman_ford=False,
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=False
    )
    
    print(f"\nOpportunities found without risk evaluation: {len(opportunities_without_risk)}")
    
    # Compare results
    print(f"\n--- Comparison ---")
    print(f"Risk evaluation filtered out: {len(opportunities_without_risk) - len(opportunities_with_risk)} opportunities")
    
    if opportunities_with_risk:
        best_opp = opportunities_with_risk[0]
        print(f"Best opportunity after risk filtering:")
        print(f"  Path: {' -> '.join(best_opp.path_symbols)}")
        print(f"  Profit: {best_opp.profit_ratio*100:.3f}%")
        print(f"  Confidence: {best_opp.confidence_score:.3f}")


if __name__ == "__main__":
    test_risk_evaluator_standalone()
    test_integrated_detector_with_risk()
