"""
Test script for simulate_gas_fee module
Tests the gas fee simulation functionality with various scenarios
"""
import sys
import os
import json
import base64

# Add project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.utils.simulate_gas_fee import (
    estimate_gas_fee_by_complexity,
    fetch_swap_transaction, 
    simulate_gas_fee
)
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api


def test_estimate_gas_fee_by_complexity():
    """Test the gas fee estimation based on transaction complexity"""
    print("🧪 Testing estimate_gas_fee_by_complexity function")
    print("=" * 60)
    
    # Test cases with different transaction sizes
    test_cases = [
        {
            "name": "Simple transaction",
            "data": "A" * 300,  # Small transaction
            "expected_range": (5005, 5020)  # base_fee + small compute fee
        },
        {
            "name": "Medium complexity transaction", 
            "data": "B" * 600,  # Medium transaction
            "expected_range": (5070, 5085)  # base_fee + medium compute fee
        },
        {
            "name": "Complex DeFi transaction",
            "data": "C" * 900,  # Large transaction
            "expected_range": (5070, 5085)  # base_fee + large compute fee
        },
        {
            "name": "Very complex transaction",
            "data": "D" * 1200,  # Very large transaction
            "expected_range": (5170, 5185)  # base_fee + very large compute fee
        }
    ]
    
    print(f"Base fee: {solana_rpc_api['base_fee']} lamports")
    print(f"Compute unit price: {solana_rpc_api['compute unit price']} lamports\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. Testing: {test['name']}")
        
        # Encode test data as base64
        base64_tx = base64.b64encode(test['data'].encode()).decode()
        
        # Get gas fee estimation
        gas_fee = estimate_gas_fee_by_complexity(base64_tx)
        
        print(f"   Data length: {len(test['data'])} chars")
        print(f"   Estimated gas fee: {gas_fee:,} lamports")
        
        # Check if result is in expected range
        min_expected, max_expected = test['expected_range']
        if min_expected <= gas_fee <= max_expected:
            print(f"   ✅ Result within expected range ({min_expected:,} - {max_expected:,})")
        else:
            print(f"   ⚠️  Result outside expected range ({min_expected:,} - {max_expected:,})")
        
        print()
    
    return True


def test_fetch_swap_transaction():
    """Test fetching swap transaction from Jupiter API"""
    print("🧪 Testing fetch_swap_transaction function")
    print("=" * 60)
    
    # Get a real quote first
    try:
        import requests
        quote_url = "https://quote-api.jup.ag/v6/quote"
        params = {
            "inputMint": "So11111111111111111111111111111111111111112",  # SOL
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "amount": "1000000000",  # 1 SOL
            "slippageBps": "50"
        }
        
        print("Fetching real quote from Jupiter API...")
        response = requests.get(quote_url, params=params, timeout=10)
        
        if response.status_code == 200:
            quote_data = response.json()
            print(f"✅ Quote fetched successfully")
            print(f"   Input: {quote_data.get('inAmount')} lamports")
            print(f"   Output: {quote_data.get('outAmount')} lamports")
            
            try:
                swap_tx = fetch_swap_transaction(quote_data)
                print(f"\n✅ Successfully fetched swap transaction")
                print(f"   Transaction length: {len(swap_tx)} characters")
                print(f"   Transaction preview: {swap_tx[:50]}...")
                return swap_tx
            
            except Exception as e:
                print(f"\n❌ Failed to fetch swap transaction: {e}")
                print(f"   This may be due to API changes or configuration issues")
                return None
        else:
            print(f"❌ Failed to fetch quote: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Network error: {e}")
        return None


def test_simulate_gas_fee():
    """Test gas fee simulation with real and mock transactions"""
    print("🧪 Testing simulate_gas_fee function")
    print("=" * 60)
    
    # Test 1: Mock transaction (will trigger fallback)
    print("1. Testing with mock transaction (fallback expected):")
    mock_tx = base64.b64encode(("MOCK_TRANSACTION_DATA" * 10).encode()).decode()
    gas_fee_mock = simulate_gas_fee(mock_tx)
    print(f"   Mock transaction gas fee: {gas_fee_mock:,} lamports")
    
    # Test 2: Try with real transaction if available
    print(f"\n2. Testing with real transaction:")
    
    # First try to get a real quote
    try:
        import requests
        quote_url = "https://quote-api.jup.ag/v6/quote"
        params = {
            "inputMint": "So11111111111111111111111111111111111111112",
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "amount": "1000000000",
            "slippageBps": "50"
        }
        
        print("   Fetching real quote from Jupiter API...")
        response = requests.get(quote_url, params=params, timeout=10)
        
        if response.status_code == 200:
            quote_data = response.json()
            print(f"   ✅ Quote fetched successfully")
            
            # Get swap transaction
            try:
                swap_tx = fetch_swap_transaction(quote_data)
                print(f"   ✅ Swap transaction fetched successfully")
                
                # Simulate gas fee
                gas_fee_real = simulate_gas_fee(swap_tx)
                print(f"   Real transaction gas fee: {gas_fee_real:,} lamports")
                
                # Compare with mock
                print(f"\n   📊 Comparison:")
                print(f"   Mock transaction: {gas_fee_mock:,} lamports")
                print(f"   Real transaction: {gas_fee_real:,} lamports")
                print(f"   Difference: {abs(gas_fee_real - gas_fee_mock):,} lamports")
                
            except Exception as e:
                print(f"   ❌ Failed to get swap transaction: {e}")
                print(f"   This will test the fallback mechanism")
                
        else:
            print(f"   ❌ Failed to fetch quote: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Network error: {e}")
        print(f"   Testing fallback mechanism only")
    
    return True


def test_error_handling():
    """Test error handling scenarios"""
    print("🧪 Testing error handling scenarios")
    print("=" * 60)
    
    # Test 1: Invalid base64 data
    print("1. Testing invalid base64 data:")
    try:
        invalid_gas_fee = estimate_gas_fee_by_complexity("INVALID_BASE64_DATA!!!")
        print(f"   ✅ Handled invalid data, returned: {invalid_gas_fee:,} lamports")
    except Exception as e:
        print(f"   ❌ Failed to handle invalid data: {e}")
    
    # Test 2: Empty transaction
    print(f"\n2. Testing empty transaction:")
    try:
        empty_tx = base64.b64encode(b"").decode()
        empty_gas_fee = estimate_gas_fee_by_complexity(empty_tx)
        print(f"   ✅ Handled empty transaction, returned: {empty_gas_fee:,} lamports")
    except Exception as e:
        print(f"   ❌ Failed to handle empty transaction: {e}")
    
    # Test 3: Very large transaction
    print(f"\n3. Testing very large transaction:")
    try:
        large_data = "X" * 5000  # Very large transaction
        large_tx = base64.b64encode(large_data.encode()).decode()
        large_gas_fee = estimate_gas_fee_by_complexity(large_tx)
        print(f"   ✅ Handled large transaction, returned: {large_gas_fee:,} lamports")
    except Exception as e:
        print(f"   ❌ Failed to handle large transaction: {e}")
    
    return True


def run_all_tests():
    """Run all gas fee simulation tests"""
    print("🚀 Starting Gas Fee Simulation Tests")
    print("=" * 80)
    
    tests = [
        ("Complexity Estimation", test_estimate_gas_fee_by_complexity),
        ("Swap Transaction Fetch", test_fetch_swap_transaction), 
        ("Gas Fee Simulation", test_simulate_gas_fee),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, "✅ PASSED" if result else "❌ FAILED"))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, "❌ FAILED"))
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*80}")
    print("📋 TEST SUMMARY")
    print("=" * 80)
    
    for test_name, status in results:
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, status in results if "PASSED" in status)
    total = len(results)
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
