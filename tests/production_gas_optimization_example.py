"""
Production-ready example: Optimized arbitrage detection with gas fee calculation
This example shows how to use the gas fee optimization system in a real arbitrage scenario
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.utils.simulate_gas_fee import simulate_gas_fee
from crypto_arbitrage_detector.configs.gas_fee_config import (
    RATE_LIMIT_CONFIG, 
    GAS_ESTIMATION_MODE,
    set_gas_estimation_mode
)
import asyncio
import time


class OptimizedArbitrageDetector:
    """
    Arbitrage detector with intelligent gas fee optimization
    """
    
    def __init__(self, max_tokens=None):
        self.max_tokens = max_tokens or RATE_LIMIT_CONFIG['max_tokens_with_rpc']
        self.api_call_count = 0
        self.session_start_time = time.time()
        
        print(f"🔧 Initialized OptimizedArbitrageDetector")
        print(f"   Max tokens with RPC: {self.max_tokens}")
        print(f"   Current mode: {GAS_ESTIMATION_MODE}")
    
    def should_use_rpc_simulation(self, token_index, estimated_profit=None):
        """
        Decide whether to use RPC simulation based on token priority and profit potential
        """
        # Always use RPC for top tokens
        if token_index < self.max_tokens:
            return True
        
        # Use RPC for high-profit opportunities regardless of token rank
        if estimated_profit and estimated_profit > 50000:  # 0.05 SOL profit
            return True
        
        return False
    
    def calculate_gas_fee_optimized(self, token_index, transaction_data, estimated_profit=None):
        """
        Calculate gas fee with intelligent optimization
        """
        use_rpc = self.should_use_rpc_simulation(token_index, estimated_profit)
        
        if use_rpc:
            # Use full RPC simulation for accurate gas fee
            gas_fee = simulate_gas_fee(
                transaction_data, 
                use_fallback_first=False
            )
            self.api_call_count += 2  # Quote + Swap calls
            method = "RPC Simulation"
        else:
            # Use quick estimation to save API calls
            gas_fee = simulate_gas_fee(
                transaction_data, 
                use_fallback_first=True
            )
            method = "Quick Estimation"
        
        return gas_fee, method
    
    def simulate_arbitrage_opportunity(self, opportunity_data):
        """
        Simulate processing an arbitrage opportunity with optimized gas calculation
        """
        token_rank = opportunity_data.get('token_rank', 0)
        estimated_profit = opportunity_data.get('estimated_profit', 0)
        token_name = opportunity_data.get('token_name', f'Token_{token_rank}')
        
        # Mock transaction data (in real scenario, this comes from Jupiter API)
        mock_transaction = "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEDAyYU05F/"
        
        # Calculate gas fee with optimization
        gas_fee, method = self.calculate_gas_fee_optimized(
            token_rank, 
            mock_transaction, 
            estimated_profit
        )
        
        # Calculate net profit
        net_profit = estimated_profit - gas_fee
        is_profitable = net_profit > 0
        
        return {
            'token_name': token_name,
            'token_rank': token_rank,
            'estimated_profit': estimated_profit,
            'gas_fee': gas_fee,
            'net_profit': net_profit,
            'is_profitable': is_profitable,
            'calculation_method': method,
            'api_calls_used': 2 if method == "RPC Simulation" else 0
        }


def run_optimized_arbitrage_simulation():
    """
    Run a simulation of arbitrage detection with optimized gas fee calculation
    """
    print("\n🎯 Optimized Arbitrage Detection Simulation")
    print("=" * 80)
    
    # Create detector instance
    detector = OptimizedArbitrageDetector(max_tokens=8)
    
    # Simulate 12 arbitrage opportunities (top 8 + 4 more)
    opportunities = [
        {'token_name': 'SOL', 'token_rank': 0, 'estimated_profit': 80000},    # High profit
        {'token_name': 'USDC', 'token_rank': 1, 'estimated_profit': 25000},   # Medium profit  
        {'token_name': 'USDT', 'token_rank': 2, 'estimated_profit': 15000},   # Low profit
        {'token_name': 'RAY', 'token_rank': 3, 'estimated_profit': 45000},    # Medium profit
        {'token_name': 'SRM', 'token_rank': 4, 'estimated_profit': 12000},    # Low profit
        {'token_name': 'FTT', 'token_rank': 5, 'estimated_profit': 35000},    # Medium profit
        {'token_name': 'COPE', 'token_rank': 6, 'estimated_profit': 8000},    # Very low profit
        {'token_name': 'STEP', 'token_rank': 7, 'estimated_profit': 22000},   # Low profit
        # Beyond API limit - should use quick estimation
        {'token_name': 'MEDIA', 'token_rank': 8, 'estimated_profit': 18000},  # Medium profit
        {'token_name': 'ROPE', 'token_rank': 9, 'estimated_profit': 65000},   # High profit (exception)
        {'token_name': 'ATLAS', 'token_rank': 10, 'estimated_profit': 9000},  # Low profit
        {'token_name': 'POLIS', 'token_rank': 11, 'estimated_profit': 7000},  # Very low profit
    ]
    
    print(f"Processing {len(opportunities)} arbitrage opportunities...\n")
    
    results = []
    total_api_calls = 0
    profitable_count = 0
    
    for i, opportunity in enumerate(opportunities, 1):
        result = detector.simulate_arbitrage_opportunity(opportunity)
        results.append(result)
        
        total_api_calls += result['api_calls_used']
        if result['is_profitable']:
            profitable_count += 1
        
        # Display result
        profit_indicator = "✅" if result['is_profitable'] else "❌"
        print(f"{profit_indicator} {result['token_name']:6} (Rank {result['token_rank']:2d}) | "
              f"Profit: {result['estimated_profit']:6,} | "
              f"Gas: {result['gas_fee']:5,} | "
              f"Net: {result['net_profit']:6,} | "
              f"Method: {result['calculation_method']}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total opportunities: {len(opportunities)}")
    print(f"   Profitable opportunities: {profitable_count}")
    print(f"   Success rate: {profitable_count/len(opportunities)*100:.1f}%")
    print(f"   Total API calls used: {total_api_calls}")
    print(f"   API calls saved: {len(opportunities)*2 - total_api_calls}")
    print(f"   Estimated processing time: {total_api_calls * 0.1:.1f}s")
    
    # Show efficiency
    rpc_used = sum(1 for r in results if r['calculation_method'] == 'RPC Simulation')
    quick_used = len(results) - rpc_used
    
    print(f"\n⚡ Efficiency:")
    print(f"   RPC Simulation: {rpc_used} tokens")
    print(f"   Quick Estimation: {quick_used} tokens")
    print(f"   API efficiency: {(1 - total_api_calls/(len(opportunities)*2))*100:.1f}% saved")
    
    return results


def demonstrate_mode_switching():
    """
    Demonstrate switching between different gas estimation modes
    """
    print(f"\n🔄 Gas Estimation Mode Switching")
    print("=" * 80)
    
    modes = ['hybrid', 'quick', 'rpc_priority']
    mock_transaction = "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEDAyYU05F/"
    
    for mode in modes:
        print(f"\n📋 Testing {mode.upper()} mode:")
        set_gas_estimation_mode(mode)
        
        # Test with different scenarios
        scenarios = [
            ("High-priority token", False),   # Should use RPC in hybrid/rpc_priority
            ("Low-priority token", True),     # Should use fallback in hybrid/quick
        ]
        
        for scenario_name, use_fallback in scenarios:
            gas_fee = simulate_gas_fee(mock_transaction, use_fallback_first=use_fallback)
            print(f"   {scenario_name}: {gas_fee:,} lamports")
    
    # Reset to hybrid mode
    set_gas_estimation_mode('hybrid')


if __name__ == "__main__":
    try:
        # Run the main simulation
        results = run_optimized_arbitrage_simulation()
        
        # Demonstrate mode switching
        demonstrate_mode_switching()
        
        print(f"\n🎉 Production simulation completed successfully!")
        print("💡 This system can handle API rate limits while maintaining accuracy for top tokens.")
        
    except Exception as e:
        print(f"\n❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
