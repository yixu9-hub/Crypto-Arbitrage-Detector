#!/usr/bin/env python3
"""
使用历史数据测试Bellman-Ford算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage
from data.historical_data import new_arbitrage_test_data

def test_bellman_ford_with_historical_data():
    """使用历史数据全面测试Bellman-Ford算法"""
    
    print("🔍 使用历史数据测试Bellman-Ford算法")
    print("=" * 60)
    
    # 使用完整的历史数据
    edges = new_arbitrage_test_data
    print(f"📊 加载历史数据: {len(edges)} 条边")
    
    # 构建图
    graph = build_graph_from_edge_lists(edges)
    print(f"🌐 构建交易图: {graph.number_of_nodes()} 节点, {graph.number_of_edges()} 边")
    
    # 测试不同的参数配置
    test_configs = [
        {
            "name": "保守配置",
            "base_amount": 5.0,
            "min_profit_threshold": 0.01,  # 1%
            "max_hops": 3
        },
        {
            "name": "中等配置", 
            "base_amount": 10.0,
            "min_profit_threshold": 0.005,  # 0.5%
            "max_hops": 4
        },
        {
            "name": "激进配置",
            "base_amount": 1.0,
            "min_profit_threshold": 0.001,  # 0.1%
            "max_hops": 5
        }
    ]
    
    for config in test_configs:
        print(f"\n🎯 测试配置: {config['name']}")
        print("-" * 40)
        print(f"  基础金额: {config['base_amount']} SOL")
        print(f"  最小利润阈值: {config['min_profit_threshold']:.1%}")
        print(f"  最大跳数: {config['max_hops']}")
        print()
        
        # 创建算法实例
        bf_algo = BellmanFordArbitrage(
            min_profit_threshold=config['min_profit_threshold'],
            max_hops=config['max_hops'],
            base_amount=config['base_amount']
        )
        
        # 运行算法
        opportunities = bf_algo.detect_opportunities(graph)
        
        print(f"✅ 发现 {len(opportunities)} 个套利机会")
        
        if opportunities:
            # 按利润率排序并显示前5个
            sorted_opportunities = sorted(opportunities, key=lambda x: x.profit_ratio, reverse=True)
            
            print(f"📈 前 {min(5, len(sorted_opportunities))} 个最佳机会:")
            for i, opp in enumerate(sorted_opportunities[:5], 1):
                print(f"\n  {i}. {' -> '.join(opp.path_symbols)}")
                print(f"     利润率: {opp.profit_ratio:.4%}")
                print(f"     预估利润: {opp.estimated_profit_sol:.6f} SOL")
                print(f"     总费用: {opp.total_fee:.6f} SOL")
                print(f"     跳数: {opp.hop_count}")
                print(f"     权重: {opp.total_weight:.6f}")
                print(f"     置信度: {opp.confidence_score:.4f}")
                
                # 计算收益成本比
                if opp.total_fee > 0:
                    profit_cost_ratio = opp.estimated_profit_sol / opp.total_fee
                    print(f"     收益/成本比: {profit_cost_ratio:.2f}")
        else:
            print("❌ 未发现符合条件的套利机会")
        
        print("\n" + "="*40)

def analyze_path_details():
    """分析套利路径的详细信息"""
    print("\n🔬 详细路径分析")
    print("=" * 60)
    
    edges = new_arbitrage_test_data
    graph = build_graph_from_edge_lists(edges)
    
    # 使用中等配置
    bf_algo = BellmanFordArbitrage(
        min_profit_threshold=0.001,
        max_hops=4,
        base_amount=5.0
    )
    
    opportunities = bf_algo.detect_opportunities(graph)
    
    if opportunities:
        # 分析最佳机会
        best_opp = max(opportunities, key=lambda x: x.profit_ratio)
        
        print(f"🏆 最佳套利机会分析:")
        print(f"路径: {' -> '.join(best_opp.path_symbols)}")
        print(f"利润率: {best_opp.profit_ratio:.6%}")
        print(f"净利润: {best_opp.estimated_profit_sol:.6f} SOL")
        print()
        
        print("📋 逐步交易分析:")
        total_gas_fees = 0
        total_trading_fees = 0
        
        for i in range(len(best_opp.path) - 1):
            from_token = best_opp.path[i]
            to_token = best_opp.path[i + 1]
            
            if graph.has_edge(from_token, to_token):
                edge_data = graph[from_token][to_token]
                
                # 获取边的详细信息
                weight = edge_data.get('weight', 0)
                gas_fee = edge_data.get('gas_fee', 0)
                total_fee = edge_data.get('total_fee', 0)
                edge_in_amount = edge_data.get('in_amount', 1.0)
                price_ratio = edge_data.get('price_ratio', 0)
                slippage_bps = edge_data.get('slippage_bps', 0)
                price_impact = edge_data.get('price_impact_pct', 0)
                
                # 计算缩放后的费用
                scaled_trading_fee = total_fee * (5.0 / edge_in_amount) if edge_in_amount > 0 else 0
                gas_fee_sol = gas_fee * 1e-9
                
                from_symbol = edge_data.get('from_symbol', from_token[:8])
                to_symbol = edge_data.get('to_symbol', to_token[:8])
                
                print(f"\n  步骤 {i+1}: {from_symbol} → {to_symbol}")
                print(f"    权重: {weight:.6f}")
                print(f"    价格比率: {price_ratio:.6f}")
                print(f"    滑点: {slippage_bps} bps")
                print(f"    价格影响: {price_impact:.4%}")
                print(f"    Gas费: {gas_fee_sol:.9f} SOL")
                print(f"    交易费: {scaled_trading_fee:.6f} SOL")
                print(f"    步骤总费用: {gas_fee_sol + scaled_trading_fee:.6f} SOL")
                
                total_gas_fees += gas_fee_sol
                total_trading_fees += scaled_trading_fee
        
        print(f"\n💰 费用汇总:")
        print(f"  总Gas费: {total_gas_fees:.9f} SOL")
        print(f"  总交易费: {total_trading_fees:.6f} SOL")
        print(f"  总费用: {total_gas_fees + total_trading_fees:.6f} SOL")
        print(f"  验证总费用: {best_opp.total_fee:.6f} SOL")
        
        # 验证费用计算
        calculated_total = total_gas_fees + total_trading_fees
        if abs(calculated_total - best_opp.total_fee) < 1e-9:
            print("✅ 费用计算一致")
        else:
            print(f"⚠️  费用计算差异: {abs(calculated_total - best_opp.total_fee):.9f} SOL")

def compare_profit_thresholds():
    """比较不同利润阈值的影响"""
    print("\n📊 利润阈值影响分析")
    print("=" * 60)
    
    edges = new_arbitrage_test_data
    graph = build_graph_from_edge_lists(edges)
    
    thresholds = [0.001, 0.005, 0.01, 0.02, 0.05]  # 0.1%, 0.5%, 1%, 2%, 5%
    base_amount = 5.0
    
    print(f"基础交易金额: {base_amount} SOL")
    print("-" * 40)
    print(f"{'利润阈值':<10} {'机会数量':<10} {'最佳利润率':<15} {'平均利润率':<15}")
    print("-" * 50)
    
    for threshold in thresholds:
        bf_algo = BellmanFordArbitrage(
            min_profit_threshold=threshold,
            max_hops=4,
            base_amount=base_amount
        )
        
        opportunities = bf_algo.detect_opportunities(graph)
        
        if opportunities:
            profit_ratios = [opp.profit_ratio for opp in opportunities]
            max_profit = max(profit_ratios)
            avg_profit = sum(profit_ratios) / len(profit_ratios)
            
            threshold_str = f"{threshold:.1%}"
            max_profit_str = f"{max_profit:.4%}"
            avg_profit_str = f"{avg_profit:.4%}"
            print(f"{threshold_str:<10} {len(opportunities):<10} {max_profit_str:<15} {avg_profit_str:<15}")
        else:
            threshold_str = f"{threshold:.1%}"
            print(f"{threshold_str:<10} {0:<10} {'N/A':<15} {'N/A':<15}")

if __name__ == "__main__":
    test_bellman_ford_with_historical_data()
    analyze_path_details()
    compare_profit_thresholds()
