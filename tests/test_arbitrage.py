'''
Arbitrage Detection Test Script
Tests the arbitrage detection algorithms with known arbitrage opportunities
'''
import pickle
import sys
import os
from typing import List
import asyncio
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crypto_arbitrage_detector.utils.get_quote_pair import get_edge_pairs
from crypto_arbitrage_detector.utils.data_structures import EdgePairs, TokenInfo
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.utils.graph_utils import analyze_graph
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector, detect_arbitrage
from arbitrage_test_data import arbitrage_test_edges, balanced_test_edges


async def retrive_edges():
    """Retrieve edges from the test data."""
    # 读取真实数据用于测试
    with open("../data/enriched_tokens.pkl", "rb") as f:
        TokenLists: List[TokenInfo] = pickle.load(f)
    print(f"✅ Loaded {len(TokenLists)} tokens from pickle file\n")
    
    edge_pairs: List[EdgePairs] = await get_edge_pairs(TokenLists)
    return edge_pairs


def test_arbitrage_detection():
    """测试套利检测算法"""
    print("🧪 套利检测算法测试")
    print("=" * 60)
    
    # 先获取边信息
    edges = asyncio.run(retrive_edges())

    # 测试1：包含套利机会的数据
    print("\n" + "="*60)
    print("🎯 测试1: 包含套利机会的数据")
    print("="*60)
    
    

    graph_with_arbitrage = build_graph_from_edge_lists(edges)
    print(f"📊 构建图: {graph_with_arbitrage.number_of_nodes()} 节点, {graph_with_arbitrage.number_of_edges()} 边")
    
    # 显示图的基本信息
    print("\n📋 图的边信息:")
    for i, (from_node, to_node, data) in enumerate(graph_with_arbitrage.edges(data=True), 1):
        from_short = from_node[:4] if len(from_node) > 4 else from_node
        to_short = to_node[:4] if len(to_node) > 4 else to_node
        print(f"  {i}. {from_short}→{to_short}: weight={data['weight']:.4f}, fee={data['total_fee']:.4f}")
    
    # 运行套利检测
    print(f"\n🔍 运行套利检测 (最小利润阈值: 0.5%)...")
    detector = IntegratedArbitrageDetector(min_profit_threshold=0.005)  # 0.5%
    opportunities = detector.detect_arbitrage(graph_with_arbitrage)
    
    # 显示结果
    detector.print_opportunities(opportunities)
    
    # 测试2：均衡市场数据（应该没有套利）
    print("\n" + "="*60)
    print("🎯 测试2: 均衡市场数据 (预期无套利)")
    print("="*60)
    
    balanced_graph = build_graph_from_edge_lists(balanced_test_edges)
    print(f"📊 构建图: {balanced_graph.number_of_nodes()} 节点, {balanced_graph.number_of_edges()} 边")
    
    print(f"\n🔍 运行套利检测 (最小利润阈值: 0.5%)...")
    balanced_opportunities = detect_arbitrage(balanced_graph, min_profit=0.005)
    
    # 测试3：可视化套利图
    print("\n" + "="*60)
    print("🎯 测试3: 可视化套利图")
    print("="*60)
    
    print("🎨 显示包含套利机会的图:")
    analyze_graph(graph_with_arbitrage, show_visualization=True, show_statistics=True, show_edge_summary=False)
    
    # 总结
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60)
    print(f"✅ 套利数据测试: 找到 {len(opportunities)} 个套利机会")
    print(f"✅ 均衡数据测试: 找到 {len(balanced_opportunities)} 个套利机会")
    
    if opportunities:
        best = opportunities[0]
        print(f"💎 最佳套利机会:")
        print(f"   路径: {'→'.join(best.path_symbols)}")
        print(f"   利润率: {best.profit_ratio*100:.2f}%")
        print(f"   预估利润: {best.estimated_profit_sol:.4f} SOL")
    
    print(f"\n🎯 算法验证: {'✅ 通过' if len(opportunities) > 0 and len(balanced_opportunities) == 0 else '❌ 需要调试'}")


def test_individual_algorithms():
    """分别测试各个算法组件"""
    print("\n🔬 算法组件单独测试")
    print("="*60)
    edges = asyncio.run(retrive_edges())
    graph = build_graph_from_edge_lists(edges)
    detector = IntegratedArbitrageDetector(min_profit_threshold=0.005)
    
    # 测试Bellman-Ford
    print("\n1️⃣ 测试 Bellman-Ford 算法:")
    bf_opps = detector.detect_arbitrage(graph, 
                                       enable_bellman_ford=True,
                                       enable_triangle=False, 
                                       enable_two_hop=False)
    print(f"   结果: {len(bf_opps)} 个机会")
    
    # 测试三角套利
    print("\n2️⃣ 测试三角套利算法:")
    tri_opps = detector.detect_arbitrage(graph,
                                        enable_bellman_ford=False,
                                        enable_triangle=True,
                                        enable_two_hop=False)
    print(f"   结果: {len(tri_opps)} 个机会")
    
    # 测试双跳套利
    print("\n3️⃣ 测试双跳套利算法:")
    two_hop_opps = detector.detect_arbitrage(graph,
                                            enable_bellman_ford=False,
                                            enable_triangle=False,
                                            enable_two_hop=True)
    print(f"   结果: {len(two_hop_opps)} 个机会")


if __name__ == "__main__":
    try:
        test_arbitrage_detection()
        test_individual_algorithms()
        
        print(f"\n🎉 所有测试完成!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
