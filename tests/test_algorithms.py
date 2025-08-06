#!/usr/bin/env python3
"""
algorithms test with historical data
This script tests various arbitrage detection algorithms using historical data.
"""

import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data.historical_data import new_arbitrage_test_data
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.algorithms.bellman_ford_algorithm import BellmanFordArbitrage
from crypto_arbitrage_detector.algorithms.triangle_arbitrage_algorithm import TriangleArbitrage
from crypto_arbitrage_detector.algorithms.two_hop_arbitrage_algorithm import TwoHopArbitrage
from crypto_arbitrage_detector.algorithms.exhaustive_dfs_algorithm import ExhaustiveDFSArbitrage
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector


def test_graph_construction():
    """
    Test graph construction from historical data.
    Returns the constructed graph if successful, None otherwise.
    """
    print("=" * 80)
    print("🔧 测试图构建...")
    print("=" * 80)
    
    try:
        graph = build_graph_from_edge_lists(new_arbitrage_test_data)
        print(f"✅ 图构建成功!")
        print(f"   节点数量: {graph.number_of_nodes()}")
        print(f"   边数量: {graph.number_of_edges()}")
        print(f"   数据源: {len(new_arbitrage_test_data)} 条 EdgePairs")
        
        # 检查一些基本属性
        if graph.number_of_nodes() > 0 and graph.number_of_edges() > 0:
            print("   ✅ 图结构正常")
            return graph
        else:
            print("   ❌ 图结构异常：节点或边数量为0")
            return None
            
    except Exception as e:
        print(f"❌ 图构建失败: {e}")
        traceback.print_exc()
        return None


def test_algorithm(algorithm_class, algorithm_name, graph, verbose=True):
    """测试单个算法"""
    print(f"\n📊 测试 {algorithm_name}...")
    print("-" * 60)
    
    try:
        # 创建算法实例
        algorithm = algorithm_class()
        print(f"   ✅ {algorithm_name} 实例创建成功")
        
        # 对于Bellman-Ford算法，临时重定向详细输出以减少噪音
        if "Bellman" in algorithm_name and not verbose:
            import io
            import contextlib
            
            # 保存原始stdout
            original_stdout = sys.stdout
            captured_output = io.StringIO()
            
            try:
                # 重定向stdout来捕获详细输出
                with contextlib.redirect_stdout(captured_output):
                    opportunities = algorithm.detect_opportunities(graph)
                
                # 恢复stdout
                sys.stdout = original_stdout
                
                # 只显示关键信息
                output_lines = captured_output.getvalue().split('\n')
                for line in output_lines:
                    if ('[BellmanFordArbitrage]' in line and 
                        ('Running from all' in line or 'Found' in line and 'unique opportunities' in line)):
                        print(f"   {line}")
                        
            except Exception:
                # 如果重定向失败，恢复正常输出
                sys.stdout = original_stdout
                opportunities = algorithm.detect_opportunities(graph)
        else:
            # 正常运行算法
            opportunities = algorithm.detect_opportunities(graph)
            
        print(f"   ✅ {algorithm_name} 运行完成")
        print(f"   发现机会数量: {len(opportunities)}")
        
        # 显示前几个机会的详细信息
        if opportunities:
            print(f"   前3个机会详情:")
            for i, opp in enumerate(opportunities[:3]):
                print(f"     {i+1}. 路径: {' -> '.join(opp.path_symbols)}")
                print(f"        利润率: {opp.profit_ratio:.6f}")
                print(f"        跳数: {opp.hop_count}")
                print(f"        置信度: {opp.confidence_score:.6f}")
                print(f"        估计利润(SOL): {opp.estimated_profit_sol:.6f}")
        
        return True, len(opportunities)
        
    except Exception as e:
        print(f"   ❌ {algorithm_name} 运行失败: {e}")
        traceback.print_exc()
        return False, 0


def test_integrated_detector(graph):
    """测试集成检测器"""
    print(f"\n🔄 测试集成套利检测器...")
    print("-" * 60)
    
    try:
        # 创建集成检测器实例
        detector = IntegratedArbitrageDetector()
        print(f"   ✅ 集成检测器实例创建成功")
        
        # 临时重定向Bellman-Ford的详细输出
        import io
        import contextlib
        original_stdout = sys.stdout
        
        try:
            # 运行集成检测，捕获输出
            captured_output = io.StringIO()
            with contextlib.redirect_stdout(captured_output):
                all_opportunities = detector.detect_arbitrage(graph)
            
            # 恢复stdout
            sys.stdout = original_stdout
            
            # 只显示关键信息，过滤重复的Bellman-Ford输出
            output_lines = captured_output.getvalue().split('\n')
            for line in output_lines:
                # 只显示重要的总结信息，过滤掉重复的循环检测信息
                if (line.strip() and 
                    not line.strip().startswith('negative cycle detected:') and
                    not line.strip().startswith('Creating opportunity from path:') and
                    not line.strip().startswith('Building trades from') and
                    not line.strip().startswith('Trade ') and
                    not line.strip().startswith('Total weight:') and
                    not line.strip().startswith('Profitable path:') and
                    not line.strip().startswith('Created opportunity:') and
                    not line.strip().startswith('Found ') and 'opportunities from source' in line):
                    print(f"   {line}")
                elif ('Starting arbitrage detection' in line or
                      'Graph statistics:' in line or
                      'Running ' in line and 'detection' in line or
                      'found ' in line and 'opportunities' in line or
                      'Deduplicated to' in line or
                      'Total ' in line and 'arbitrage opportunities found' in line):
                    print(f"   {line}")
                    
        except Exception:
            # 如果重定向失败，恢复正常输出
            sys.stdout = original_stdout
            all_opportunities = detector.detect_arbitrage(graph)
            
        print(f"   ✅ 集成检测器运行完成")
        print(f"   总机会数量: {len(all_opportunities)}")
        
        # 显示各算法的结果统计
        if hasattr(detector, 'algorithm_results') and detector.algorithm_results:
            print(f"   各算法结果统计:")
            for alg_name, opportunities in detector.algorithm_results.items():
                print(f"     {alg_name}: {len(opportunities)} 个机会")
        
        # 显示风险评估后的顶级机会
        if all_opportunities:
            print(f"   风险评估后的前3个机会:")
            for i, opp in enumerate(all_opportunities[:3]):
                print(f"     {i+1}. 路径: {' -> '.join(opp.path_symbols)}")
                print(f"        利润率: {opp.profit_ratio:.6f}")
                print(f"        置信度: {opp.confidence_score:.6f}")
                print(f"        风险评估: 已完成")
        
        return True, len(all_opportunities)
        
    except Exception as e:
        print(f"   ❌ 集成检测器运行失败: {e}")
        traceback.print_exc()
        return False, 0


def main():
    """主测试函数"""
    print("🚀 开始算法测试...")
    print(f"测试数据: {len(new_arbitrage_test_data)} 条 EdgePairs")
    
    # 1. 测试图构建
    graph = test_graph_construction()
    if not graph:
        print("❌ 图构建失败，终止测试")
        return
    
    # 2. 测试各个算法
    algorithms_to_test = [
        (BellmanFordArbitrage, "Bellman-Ford 算法", False),  # verbose=False for Bellman-Ford
        (TriangleArbitrage, "三角套利算法", True), 
        (TwoHopArbitrage, "两跳套利算法", True),
        (ExhaustiveDFSArbitrage, "穷举DFS算法", True)
    ]
    
    test_results = []
    total_opportunities = 0
    
    for algorithm_class, algorithm_name, verbose in algorithms_to_test:
        success, count = test_algorithm(algorithm_class, algorithm_name, graph, verbose)
        test_results.append((algorithm_name, success, count))
        if success:
            total_opportunities += count
    
    # 3. 测试集成检测器
    integrated_success, integrated_count = test_integrated_detector(graph)
    test_results.append(("集成检测器", integrated_success, integrated_count))
    
    # 4. 总结测试结果
    print("\n" + "=" * 80)
    print("📋 测试结果总结")
    print("=" * 80)
    
    successful_tests = 0
    failed_tests = 0
    
    for name, success, count in test_results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name:20} | {status:8} | 机会数量: {count:4}")
        if success:
            successful_tests += 1
        else:
            failed_tests += 1
    
    print("-" * 80)
    print(f"总测试数量: {len(test_results)}")
    print(f"成功测试: {successful_tests}")
    print(f"失败测试: {failed_tests}")
    print(f"成功率: {(successful_tests/len(test_results)*100):.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 所有算法测试通过！新的测试数据可以正常使用。")
    else:
        print(f"\n⚠️  有 {failed_tests} 个测试失败，需要检查相关算法。")


if __name__ == "__main__":
    main()
