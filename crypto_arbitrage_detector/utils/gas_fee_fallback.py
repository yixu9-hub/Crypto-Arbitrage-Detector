#!/usr/bin/env python3
"""
备用的 Gas 费用估算方法
当网络连接有问题时使用
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.request_config import solana_rpc_api

def estimate_gas_fee_offline(quote_data):
    """
    基于报价数据离线估算 Gas 费用
    
    Args:
        quote_data: Jupiter API 返回的报价数据
        
    Returns:
        int: 估算的 Gas 费用 (lamports)
    """
    base_fee = solana_rpc_api["base_fee"]  # 5000 lamports
    compute_unit_price = solana_rpc_api["compute unit price"]  # 0.005 lamports
    
    # 基于交换复杂度估算计算单元消耗
    route_plan = quote_data.get("routePlan", [])
    
    if not route_plan:
        # 简单直接交换，使用基础费用
        estimated_units = 10000  # 基础计算单元
    else:
        # 复杂路由，根据跳数估算
        hop_count = len(route_plan)
        estimated_units = 5000 + (hop_count * 8000)  # 每跳增加计算单元
        
        # 考虑每个路由的复杂度
        for route in route_plan:
            swap_info = route.get("swapInfo", {})
            if swap_info:
                # 如果有特殊的交换信息，增加复杂度
                estimated_units += 2000
    
    # 计算总费用
    total_fee = base_fee + int(estimated_units * compute_unit_price)
    
    return total_fee

def get_gas_fee_with_fallback(quote_data):
    """
    获取 Gas 费用，包含多重回退机制
    
    Args:
        quote_data: Jupiter API 返回的报价数据
        
    Returns:
        int: Gas 费用 (lamports)
    """
    try:
        # 尝试方法1: 真实模拟
        from simulte_gas_fee import fetch_swap_transaction, simulate_gas_fee
        
        swap_tx = fetch_swap_transaction(quote_data)
        gas_fee = simulate_gas_fee(swap_tx)
        print(f"[INFO] 使用真实模拟的 Gas 费用: {gas_fee} lamports")
        return gas_fee
        
    except Exception as e:
        print(f"[WARN] 真实模拟失败: {e}")
        
        try:
            # 尝试方法2: 离线估算
            estimated_fee = estimate_gas_fee_offline(quote_data)
            print(f"[INFO] 使用离线估算的 Gas 费用: {estimated_fee} lamports")
            return estimated_fee
            
        except Exception as e2:
            print(f"[WARN] 离线估算失败: {e2}")
            
            # 方法3: 使用默认值
            default_fee = solana_rpc_api["base_fee"]
            print(f"[INFO] 使用默认 Gas 费用: {default_fee} lamports")
            return default_fee

# 测试函数
if __name__ == "__main__":
    # 测试离线估算
    test_quote = {
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "inAmount": "1000000000",
        "outAmount": "191000000",
        "routePlan": [
            {
                "swapInfo": {
                    "ammKey": "test123",
                    "label": "Jupiter",
                    "inputMint": "So11111111111111111111111111111111111111112",
                    "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
                }
            }
        ]
    }
    
    print("🧪 测试备用 Gas 费用估算...")
    
    # 测试离线估算
    offline_fee = estimate_gas_fee_offline(test_quote)
    print(f"离线估算结果: {offline_fee} lamports")
    
    # 测试完整的回退机制
    final_fee = get_gas_fee_with_fallback(test_quote)
    print(f"最终费用: {final_fee} lamports")
