#!/usr/bin/env python3
"""
详细测试套利机会的dataclass信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage
from crypto_arbitrage_detector.algorithms.triangle_arbitrage_algorithm import TriangleArbitrage
from crypto_arbitrage_detector.algorithms.two_hop_arbitrage_algorithm import TwoHopArbitrage
from data.historical_data import new_arbitrage_test_data


def print_dataclass_info(obj, indent=0):
    """递归打印dataclass对象的所有字段"""
    prefix = "  " * indent
    print(f"{prefix}{obj.__class__.__name__}:")
    
    # 获取所有字段
    if hasattr(obj, '__dataclass_fields__'):
        # 这是一个dataclass
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            print(f"{prefix}  {field_name}: {value} ({type(value).__name__})")
    else:
        # 不是dataclass，直接打印属性
        for attr_name in dir(obj):
            if not attr_name.startswith('_'):
                try:
                    value = getattr(obj, attr_name)
                    if not callable(value):
                        print(f"{prefix}  {attr_name}: {value} ({type(value).__name__})")
                except:
                    pass


def test_edge_data_structure():
    """测试边数据结构"""
    print("=" * 80)
    print("🔍 检查EdgePairs数据结构")
    print("=" * 80)
    
    print(f"历史数据总数: {len(new_arbitrage_test_data)}")
    print("\n前3条EdgePairs详细信息:")
    
    for i, edge in enumerate(new_arbitrage_test_data[:3]):
        print(f"\n边 {i+1}:")
        print_dataclass_info(edge, indent=1)


def test_graph_edge_data():
    """测试图中的边数据"""
    print("\n" + "=" * 80)
    print("🔍 检查图中的边数据")
    print("=" * 80)
    
    graph = build_graph_from_edge_lists(new_arbitrage_test_data)
    print(f"图构建完成: {graph.number_of_nodes()} 节点, {graph.number_of_edges()} 边")
    
    # 检查前几条边的数据
    print("\n前3条边在图中的数据:")
    edge_count = 0
    for u, v, data in graph.edges(data=True):
        if edge_count >= 3:
            break
        print(f"\n边 {edge_count + 1}: {data.get('from_symbol', u[:8])} -> {data.get('to_symbol', v[:8])}")
        for key, value in data.items():
            print(f"  {key}: {value} ({type(value).__name__})")
        edge_count += 1


def test_arbitrage_opportunities(algorithm_class, algorithm_name):
    """测试特定算法的套利机会详细信息"""
    print(f"\n" + "=" * 80)
    print(f"🔍 检查 {algorithm_name} 的套利机会详细信息")
    print("=" * 80)
    
    graph = build_graph_from_edge_lists(new_arbitrage_test_data)
    algorithm = algorithm_class()
    
    print(f"算法配置:")
    if hasattr(algorithm, 'min_profit_threshold'):
        print(f"  最小利润阈值: {algorithm.min_profit_threshold}")
    if hasattr(algorithm, 'max_hops'):
        print(f"  最大跳数: {algorithm.max_hops}")
    if hasattr(algorithm, 'base_amount'):
        print(f"  基础金额: {algorithm.base_amount}")
    
    opportunities = algorithm.detect_opportunities(graph)
    print(f"\n发现套利机会数量: {len(opportunities)}")
    
    if opportunities:
        print(f"\n前3个机会的详细信息:")
        for i, opp in enumerate(opportunities[:3]):
            print(f"\n机会 {i+1}:")
            print_dataclass_info(opp, indent=1)
            
            # 额外计算和验证
            if hasattr(opp, 'path') and opp.path:
                print(f"  路径验证:")
                print(f"    路径长度: {len(opp.path)}")
                print(f"    跳数: {opp.hop_count}")
                print(f"    路径一致性: {len(opp.path) - 1 == opp.hop_count}")
                
                if hasattr(opp, 'path_symbols') and opp.path_symbols:
                    print(f"    符号路径: {' -> '.join(opp.path_symbols)}")
                    print(f"    符号路径长度: {len(opp.path_symbols)}")
                    
            # 费用分析
            if hasattr(opp, 'total_fee'):
                print(f"  费用分析:")
                print(f"    总费用(SOL): {opp.total_fee}")
                print(f"    费用是否合理: {0 <= opp.total_fee <= 1.0}")  # 假设费用不超过1 SOL
                
            # 利润分析
            if hasattr(opp, 'profit_ratio') and hasattr(opp, 'estimated_profit_sol'):
                print(f"  利润分析:")
                print(f"    利润率: {opp.profit_ratio:.6f}")
                print(f"    估计利润(SOL): {opp.estimated_profit_sol:.6f}")
                if hasattr(algorithm, 'base_amount'):
                    expected_profit = algorithm.base_amount * opp.profit_ratio
                    print(f"    期望利润(SOL): {expected_profit:.6f}")
                    print(f"    利润计算一致性: {abs(expected_profit - opp.estimated_profit_sol) < 1e-6}")
    else:
        print("没有发现套利机会")


def analyze_fee_calculation():
    """分析费用计算过程"""
    print(f"\n" + "=" * 80)
    print("🔍 分析费用计算过程")
    print("=" * 80)
    
    graph = build_graph_from_edge_lists(new_arbitrage_test_data)
    
    # 找一个简单的路径进行分析
    print("寻找简单的两跳路径进行费用分析...")
    
    nodes = list(graph.nodes())
    if len(nodes) >= 2:
        # 寻找A->B->A的路径
        for start_node in nodes[:3]:  # 只检查前3个节点
            for intermediate_node in graph.successors(start_node):
                if graph.has_edge(intermediate_node, start_node):
                    # 找到了A->B->A路径
                    path = [start_node, intermediate_node, start_node]
                    print(f"\n分析路径: {path}")
                    
                    total_gas_fee = 0
                    total_trading_fee = 0
                    
                    for i in range(len(path) - 1):
                        from_node = path[i]
                        to_node = path[i + 1]
                        edge_data = graph[from_node][to_node]
                        
                        gas_fee = edge_data.get('gas_fee', 0)
                        trading_fee = edge_data.get('total_fee', 0)
                        from_symbol = edge_data.get('from_symbol', from_node[:8])
                        to_symbol = edge_data.get('to_symbol', to_node[:8])
                        
                        print(f"  边 {i+1}: {from_symbol} -> {to_symbol}")
                        print(f"    gas_fee: {gas_fee} lamports")
                        print(f"    total_fee: {trading_fee}")
                        print(f"    weight: {edge_data.get('weight', 'N/A')}")
                        
                        total_gas_fee += gas_fee
                        total_trading_fee += trading_fee
                    
                    print(f"  路径费用汇总:")
                    print(f"    总gas费用: {total_gas_fee} lamports = {total_gas_fee * 1e-9:.9f} SOL")
                    print(f"    总交易费用: {total_trading_fee}")
                    print(f"    期望的total_fee: {total_gas_fee * 1e-9:.9f} SOL")
                    
                    # 只分析第一个找到的路径
                    break
            else:
                continue
            break


def main():
    """主测试函数"""
    print("🧪 套利机会详细信息测试")
    print("=" * 80)
    
    # 1. 检查原始数据结构
    test_edge_data_structure()
    
    # 2. 检查图中的数据结构
    test_graph_edge_data()
    
    # 3. 分析费用计算
    analyze_fee_calculation()
    
    # 4. 测试不同算法的套利机会
    algorithms = [
        (BellmanFordArbitrage, "Bellman-Ford算法"),
        (TriangleArbitrage, "三角套利算法"),
        (TwoHopArbitrage, "两跳套利算法")
    ]
    
    for algorithm_class, algorithm_name in algorithms:
        try:
            test_arbitrage_opportunities(algorithm_class, algorithm_name)
        except Exception as e:
            print(f"\n❌ {algorithm_name} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "=" * 80)
    print("🎯 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
