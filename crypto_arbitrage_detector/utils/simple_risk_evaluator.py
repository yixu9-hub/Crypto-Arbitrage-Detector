'''
简化版风险评估模块
专为10个token检测场景设计
'''
import math
from typing import Dict, List, Optional
from dataclasses import dataclass
from .data_structures import ArbitrageOpportunity


@dataclass
class SimpleRiskParams:
    """简化风险参数"""
    
    # 基础评估参数
    base_confidence_multiplier: float = 15.0   # 提高基础置信度倍数
    hop_penalty_factor: float = 0.1            # 降低跳数惩罚系数
    min_profit_for_confidence: float = 0.005   # 最小利润要求
    
    # 置信度范围
    min_confidence: float = 0.0
    max_confidence: float = 1.0


class SimpleRiskEvaluator:
    """简化风险评估器 - 专为检测工具设计"""
    
    def __init__(self, params: Optional[SimpleRiskParams] = None):
        self.params = params or SimpleRiskParams()
    
    def calculate_simple_confidence(self, opportunity: ArbitrageOpportunity) -> float:
        """
        计算简化置信度分数
        只基于利润率和跳数，不依赖交易金额
        """
        # 基础利润置信度
        profit_confidence = min(1.0, 
                               opportunity.profit_ratio * self.params.base_confidence_multiplier)
        
        # 跳数惩罚（跳数越多，风险越高）
        hop_penalty = opportunity.hop_count * self.params.hop_penalty_factor
        
        # 最终置信度
        confidence = max(0.0, profit_confidence - hop_penalty)
        
        return min(self.params.max_confidence, confidence)
    
    def estimate_execution_costs(self, opportunity: ArbitrageOpportunity, 
                                edge_data_list: List[Dict]) -> Dict:
        """
        基于实际边数据估算执行成本
        
        Args:
            opportunity: 套利机会
            edge_data_list: 实际的边数据列表
        """
        if not edge_data_list:
            # 如果没有边数据，返回保守估计
            return {
                'total_gas_cost_sol': 0.001,  # 保守估计
                'total_slippage_pct': 0.5,    # 保守估计0.5%
                'estimated_net_profit_pct': opportunity.profit_ratio * 100,
                'profitability_after_costs': opportunity.profit_ratio > 0.01,
                'data_source': 'fallback_estimate'
            }
        
        # 基于实际边数据计算
        total_gas_cost = 0.0
        total_slippage = 0.0
        
        for edge_data in edge_data_list:
            # 实际gas费用
            gas_fee = edge_data.get('gas_fee', 0)
            total_gas_cost += gas_fee * 1e-9  # 转换为SOL
            
            # 实际滑点
            slippage_bps = edge_data.get('slippage_bps', 0)
            total_slippage += slippage_bps / 10000.0  # 转换为小数
        
        # 计算净利润（扣除实际成本）
        net_profit_ratio = opportunity.profit_ratio - total_slippage
        
        return {
            'total_gas_cost_sol': total_gas_cost,
            'total_slippage_pct': total_slippage * 100,
            'estimated_net_profit_pct': net_profit_ratio * 100,
            'profitability_after_costs': net_profit_ratio > self.params.min_profit_for_confidence,
            'data_source': 'actual_edge_data'
        }
    
    def categorize_opportunity_quality(self, opportunity: ArbitrageOpportunity, 
                                      edge_data_list: List[Dict]) -> str:
        """
        基于实际边数据的机会质量分类
        """
        confidence = self.calculate_simple_confidence(opportunity)
        cost_analysis = self.estimate_execution_costs(opportunity, edge_data_list)
        
        if not cost_analysis['profitability_after_costs']:
            return "POOR"  # 扣除成本后不盈利
        elif confidence >= 0.7:
            return "EXCELLENT"  # 高置信度
        elif confidence >= 0.5:
            return "GOOD"       # 中等置信度
        elif confidence >= 0.3:
            return "FAIR"       # 一般
        else:
            return "RISKY"      # 低置信度
    
    def evaluate_opportunity(self, opportunity: ArbitrageOpportunity, 
                           edge_data_list: List[Dict] = None) -> Dict:
        """
        综合评估套利机会（基于实际边数据）
        
        Args:
            opportunity: 套利机会
            edge_data_list: 实际边数据列表
        """
        if edge_data_list is None:
            edge_data_list = []
        
        confidence = self.calculate_simple_confidence(opportunity)
        cost_analysis = self.estimate_execution_costs(opportunity, edge_data_list)
        quality = self.categorize_opportunity_quality(opportunity, edge_data_list)
        
        # 简单的建议
        if quality in ["EXCELLENT", "GOOD"]:
            recommendation = "RECOMMENDED"
        elif quality == "FAIR":
            recommendation = "CONSIDER"
        else:
            recommendation = "NOT_RECOMMENDED"
        
        return {
            'confidence_score': confidence,
            'quality_rating': quality,
            'recommendation': recommendation,
            'cost_analysis': cost_analysis,
            'summary': self._generate_summary(opportunity, confidence, quality, cost_analysis)
        }
    
    def _generate_summary(self, opportunity: ArbitrageOpportunity, 
                         confidence: float, quality: str, cost_analysis: Dict) -> str:
        """生成基于实际数据的文字总结"""
        profit_pct = opportunity.profit_ratio * 100
        net_profit_pct = cost_analysis['estimated_net_profit_pct']
        data_source = cost_analysis['data_source']
        
        if quality == "EXCELLENT":
            return f"优秀机会：{profit_pct:.2f}%利润（净利润{net_profit_pct:.2f}%），{opportunity.hop_count}跳，高置信度 [{data_source}]"
        elif quality == "GOOD":
            return f"良好机会：{profit_pct:.2f}%利润（净利润{net_profit_pct:.2f}%），{opportunity.hop_count}跳，中等置信度 [{data_source}]"
        elif quality == "FAIR":
            return f"一般机会：{profit_pct:.2f}%利润（净利润{net_profit_pct:.2f}%），{opportunity.hop_count}跳，需谨慎 [{data_source}]"
        elif quality == "RISKY":
            return f"风险机会：{profit_pct:.2f}%利润（净利润{net_profit_pct:.2f}%），{opportunity.hop_count}跳，高风险 [{data_source}]"
        else:
            return f"差劲机会：{profit_pct:.2f}%利润可能不足以覆盖成本 [{data_source}]"


def evaluate_opportunity_simple(opportunity: ArbitrageOpportunity,
                               edge_data_list: List[Dict] = None,
                               evaluator: Optional[SimpleRiskEvaluator] = None) -> Dict:
    """
    简便的机会评估函数（基于实际边数据）
    
    Args:
        opportunity: 套利机会
        edge_data_list: 实际边数据列表
        evaluator: 风险评估器
    """
    evaluator = evaluator or SimpleRiskEvaluator()
    return evaluator.evaluate_opportunity(opportunity, edge_data_list)


# 为现有算法提供简单的置信度计算
def calculate_simple_confidence_score(profit_ratio: float, hop_count: int) -> float:
    """
    最简单的置信度计算 - 可以直接在算法中使用
    
    Args:
        profit_ratio: 利润比例
        hop_count: 跳数
        
    Returns:
        float: 置信度分数 (0-1)
    """
    # 基础置信度（提高倍数）
    base_confidence = min(1.0, profit_ratio * 15.0)
    
    # 跳数惩罚（降低惩罚）
    hop_penalty = hop_count * 0.1
    
    # 最终置信度
    return max(0.0, base_confidence - hop_penalty)
