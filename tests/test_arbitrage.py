'''
Arbitrage Detection Test Script
Tests the arbitrage detection algorithms with known arbitrage opportunities

更新说明 (2025-07-28):
- 适配新的"无起始节点"算法架构
- 所有算法现在搜索整个图而不依赖单一起始节点
- 集成风险评估系统测试
- 新增穷举DFS算法测试
- source_token 参数现在被所有算法忽略
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
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector
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
    
    # 运行套利检测 (注意：新版本不需要source_token参数)
    print(f"\n🔍 运行套利检测 (最小利润阈值: 0.5%)...")
    detector = IntegratedArbitrageDetector(
        min_profit_threshold=0.005,  # 0.5%
        enable_risk_evaluation=True
    )
    opportunities = detector.detect_arbitrage(
        graph_with_arbitrage,
        source_token="any_token_ignored",  # 此参数现在被忽略
        enable_bellman_ford=True,
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=True
    )
    
    # 显示结果
    detector.print_opportunities(opportunities)
    
    # 测试2：均衡市场数据（应该没有套利）
    print("\n" + "="*60)
    print("🎯 测试2: 均衡市场数据 (预期无套利)")
    print("="*60)
    
    balanced_graph = build_graph_from_edge_lists(balanced_test_edges)
    print(f"📊 构建图: {balanced_graph.number_of_nodes()} 节点, {balanced_graph.number_of_edges()} 边")
    
    print(f"\n🔍 运行套利检测 (最小利润阈值: 0.5%)...")
    balanced_detector = IntegratedArbitrageDetector(
        min_profit_threshold=0.005,
        enable_risk_evaluation=True
    )
    balanced_opportunities = balanced_detector.detect_arbitrage(
        balanced_graph,
        source_token="any_token_ignored",  # 此参数现在被忽略
        enable_bellman_ford=True,
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=True
    )
    
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
    
    # 重新获取边数据
    edges = asyncio.run(retrive_edges())
    graph = build_graph_from_edge_lists(edges)
    detector = IntegratedArbitrageDetector(
        min_profit_threshold=0.005,
        enable_risk_evaluation=True
    )
    
    # 测试Bellman-Ford
    print("\n1️⃣ 测试 Bellman-Ford 算法:")
    bf_opps = detector.detect_arbitrage(
        graph, 
        source_token="ignored",
        enable_bellman_ford=True,
        enable_triangle=False, 
        enable_two_hop=False,
        enable_exhaustive_dfs=False
    )
    print(f"   结果: {len(bf_opps)} 个机会")
    
    # 测试三角套利
    print("\n2️⃣ 测试三角套利算法:")
    tri_opps = detector.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=False,
        enable_triangle=True,
        enable_two_hop=False,
        enable_exhaustive_dfs=False
    )
    print(f"   结果: {len(tri_opps)} 个机会")
    
    # 测试双跳套利
    print("\n3️⃣ 测试双跳套利算法:")
    two_hop_opps = detector.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=False,
        enable_triangle=False,
        enable_two_hop=True,
        enable_exhaustive_dfs=False
    )
    print(f"   结果: {len(two_hop_opps)} 个机会")
    
    # 测试穷举DFS算法
    print("\n4️⃣ 测试穷举DFS算法:")
    dfs_opps = detector.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=False,
        enable_triangle=False,
        enable_two_hop=False,
        enable_exhaustive_dfs=True
    )
    print(f"   结果: {len(dfs_opps)} 个机会")


def test_risk_evaluation():
    """测试风险评估功能"""
    print("\n🛡️ 风险评估功能测试")
    print("="*60)
    
    # 获取边数据
    edges = asyncio.run(retrive_edges())
    graph = build_graph_from_edge_lists(edges)
    
    # 测试无风险评估
    print("\n📊 无风险评估模式:")
    detector_no_risk = IntegratedArbitrageDetector(
        min_profit_threshold=0.001,  # 更低阈值
        enable_risk_evaluation=False
    )
    opportunities_no_risk = detector_no_risk.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=True,
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=True
    )
    print(f"   找到机会: {len(opportunities_no_risk)} 个")
    
    # 测试有风险评估
    print("\n🛡️ 启用风险评估模式:")
    detector_with_risk = IntegratedArbitrageDetector(
        min_profit_threshold=0.001,  # 更低阈值
        enable_risk_evaluation=True
    )
    opportunities_with_risk = detector_with_risk.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=True,
        enable_triangle=True,
        enable_two_hop=True,
        enable_exhaustive_dfs=True
    )
    print(f"   找到机会: {len(opportunities_with_risk)} 个")
    print(f"   风险过滤效果: 过滤了 {len(opportunities_no_risk) - len(opportunities_with_risk)} 个高风险机会")
    
    # 显示风险评估详情
    if opportunities_with_risk:
        print(f"\n💎 风险评估后的最佳机会:")
        best = opportunities_with_risk[0]
        print(f"   路径: {'→'.join(best.path_symbols)}")
        print(f"   利润率: {best.profit_ratio*100:.2f}%")
        print(f"   置信度: {best.confidence_score:.3f}")
        print(f"   跳数: {best.hop_count}")
        if hasattr(best, 'risk_score'):
            print(f"   风险分数: {best.risk_score:.3f}")


def test_individual_algorithms():
    """分别测试各个算法组件"""
    print("\n🔬 算法组件单独测试")
    print("="*60)
    
    # 重新获取边数据
    edges = asyncio.run(retrive_edges())
    graph = build_graph_from_edge_lists(edges)
    detector = IntegratedArbitrageDetector(
        min_profit_threshold=0.005,
        enable_risk_evaluation=True
    )
    
    # 测试Bellman-Ford
    print("\n1️⃣ 测试 Bellman-Ford 算法:")
    bf_opps = detector.detect_arbitrage(
        graph, 
        source_token="ignored",
        enable_bellman_ford=True,
        enable_triangle=False, 
        enable_two_hop=False,
        enable_exhaustive_dfs=False
    )
    print(f"   结果: {len(bf_opps)} 个机会")
    
    # 测试三角套利
    print("\n2️⃣ 测试三角套利算法:")
    tri_opps = detector.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=False,
        enable_triangle=True,
        enable_two_hop=False,
        enable_exhaustive_dfs=False
    )
    print(f"   结果: {len(tri_opps)} 个机会")
    
    # 测试双跳套利
    print("\n3️⃣ 测试双跳套利算法:")
    two_hop_opps = detector.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=False,
        enable_triangle=False,
        enable_two_hop=True,
        enable_exhaustive_dfs=False
    )
    print(f"   结果: {len(two_hop_opps)} 个机会")
    
    # 测试穷举DFS算法
    print("\n4️⃣ 测试穷举DFS算法:")
    dfs_opps = detector.detect_arbitrage(
        graph,
        source_token="ignored",
        enable_bellman_ford=False,
        enable_triangle=False,
        enable_two_hop=False,
        enable_exhaustive_dfs=True
    )
    print(f"   结果: {len(dfs_opps)} 个机会")


if __name__ == "__main__":
    try:
        test_arbitrage_detection()
        test_individual_algorithms()
        test_risk_evaluation()
        
        print(f"\n🎉 所有测试完成!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
