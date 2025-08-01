'''
统一风险分析模块
用于所有套利算法的风险评估和置信度计算
'''
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .data_structures import ArbitrageOpportunity


@dataclass
class RiskParameters:
    """风险评估参数配置"""
    
    # 交易金额相关参数
    small_trade_threshold: float = 1.0      # 小额交易阈值 (SOL)
    large_trade_threshold: float = 10.0     # 大额交易阈值 (SOL)
    
    # Gas费用相关参数
    base_gas_fee: float = 0.000025          # 基础gas费 (SOL)
    gas_multiplier_small: float = 1.2       # 小额交易gas倍数
    gas_multiplier_large: float = 0.8       # 大额交易gas倍数
    
    # 滑点相关参数
    base_slippage_bps: float = 10           # 基础滑点 (basis points)
    slippage_scale_factor: float = 0.1      # 滑点缩放因子
    
    # 价格影响参数
    default_liquidity: float = 1000.0       # 默认流动性 (SOL)
    price_impact_exponent: float = 0.7      # 价格影响指数
    max_price_impact: float = 0.15          # 最大价格影响 (15%)
    
    # 置信度计算参数
    confidence_profit_multiplier: float = 15.0   # 利润置信度倍数
    confidence_hop_penalty: float = 0.1          # 跳数惩罚
    confidence_liquidity_boost: float = 0.2      # 流动性加成
    min_confidence: float = 0.0                  # 最小置信度
    max_confidence: float = 1.0                  # 最大置信度


class RiskAnalyzer:
    """统一风险分析器"""
    
    def __init__(self, risk_params: Optional[RiskParameters] = None):
        """
        初始化风险分析器
        
        Args:
            risk_params: 风险参数配置，如果None则使用默认参数
        """
        self.params = risk_params or RiskParameters()
        
    def calculate_adjusted_edge_weight(self, 
                                     edge_data: Dict, 
                                     trade_amount: float) -> float:
        """
        计算考虑交易金额的调整边权重
        
        Args:
            edge_data: 边数据字典
            trade_amount: 交易金额 (SOL)
            
        Returns:
            float: 调整后的边权重
        """
        # 基础权重
        base_weight = edge_data.get('weight', 0)
        
        # 1. 基础滑点
        base_slippage_bps = edge_data.get('slippage_bps', self.params.base_slippage_bps)
        base_slippage = base_slippage_bps / 10000.0
        
        # 2. 交易金额相关的滑点调整
        slippage_adjustment = self._calculate_slippage_adjustment(trade_amount)
        
        # 3. 价格影响计算
        price_impact = self._calculate_price_impact(edge_data, trade_amount)
        
        # 4. Gas费影响
        gas_impact = self._calculate_gas_impact(edge_data, trade_amount)
        
        # 总调整权重
        adjusted_weight = (base_weight + 
                          base_slippage + 
                          slippage_adjustment + 
                          price_impact + 
                          gas_impact)
        
        return adjusted_weight
    
    def calculate_advanced_confidence_score(self, 
                                          opportunity: ArbitrageOpportunity,
                                          edge_data_list: List[Dict],
                                          trade_amount: float) -> float:
        """
        计算高级置信度分数
        
        Args:
            opportunity: 套利机会
            edge_data_list: 边数据列表
            trade_amount: 交易金额
            
        Returns:
            float: 置信度分数 (0-1)
        """
        # 基础利润置信度
        profit_confidence = min(1.0, opportunity.profit_ratio * self.params.confidence_profit_multiplier)
        
        # 跳数惩罚
        hop_penalty = opportunity.hop_count * self.params.confidence_hop_penalty
        
        # 流动性加成
        liquidity_boost = self._calculate_liquidity_confidence(edge_data_list)
        
        # 交易金额影响
        amount_factor = self._calculate_amount_confidence_factor(trade_amount)
        
        # 市场风险调整
        market_risk_factor = self._calculate_market_risk_factor(edge_data_list, trade_amount)
        
        # 综合置信度
        confidence = ((profit_confidence + liquidity_boost) * 
                     amount_factor * 
                     market_risk_factor - 
                     hop_penalty)
        
        # 限制在合理范围内
        return max(self.params.min_confidence, 
                  min(self.params.max_confidence, confidence))
    
    def assess_trade_risk(self, 
                         opportunity: ArbitrageOpportunity,
                         edge_data_list: List[Dict],
                         trade_amount: float) -> Dict:
        """
        综合交易风险评估
        
        Args:
            opportunity: 套利机会
            edge_data_list: 边数据列表
            trade_amount: 交易金额
            
        Returns:
            Dict: 风险评估结果
        """
        # 计算各种风险指标
        total_gas_cost = sum(self._calculate_gas_impact(edge, trade_amount) 
                           for edge in edge_data_list) * trade_amount
        
        total_slippage = sum(edge.get('slippage_bps', 0) for edge in edge_data_list) / 10000.0
        
        total_price_impact = sum(self._calculate_price_impact(edge, trade_amount) 
                               for edge in edge_data_list)
        
        # 流动性风险
        min_liquidity = min(edge.get('liquidity', self.params.default_liquidity) 
                          for edge in edge_data_list)
        liquidity_ratio = trade_amount / min_liquidity if min_liquidity > 0 else 1.0
        
        # 风险等级评估
        risk_level = self._determine_risk_level(
            total_gas_cost, total_slippage, total_price_impact, liquidity_ratio
        )
        
        # 建议的最大交易金额
        max_recommended_amount = self._calculate_max_recommended_amount(
            edge_data_list, opportunity.profit_ratio
        )
        
        return {
            'risk_level': risk_level,
            'confidence_score': self.calculate_advanced_confidence_score(
                opportunity, edge_data_list, trade_amount
            ),
            'total_gas_cost_sol': total_gas_cost,
            'total_slippage_pct': total_slippage * 100,
            'total_price_impact_pct': total_price_impact * 100,
            'liquidity_ratio': liquidity_ratio,
            'min_liquidity_sol': min_liquidity,
            'max_recommended_amount_sol': max_recommended_amount,
            'risk_adjusted_profit': opportunity.profit_ratio - total_slippage - total_price_impact,
            'trade_amount_category': self._categorize_trade_amount(trade_amount)
        }
    
    def _calculate_slippage_adjustment(self, trade_amount: float) -> float:
        """计算交易金额相关的滑点调整"""
        if trade_amount <= self.params.small_trade_threshold:
            # 小额交易：滑点影响较小
            return 0.0
        elif trade_amount >= self.params.large_trade_threshold:
            # 大额交易：滑点影响增加
            excess = trade_amount - self.params.large_trade_threshold
            return excess * self.params.slippage_scale_factor / 100.0
        else:
            # 中等交易：线性插值
            ratio = ((trade_amount - self.params.small_trade_threshold) / 
                    (self.params.large_trade_threshold - self.params.small_trade_threshold))
            return ratio * self.params.slippage_scale_factor / 100.0
    
    def _calculate_price_impact(self, edge_data: Dict, trade_amount: float) -> float:
        """计算非线性价格影响"""
        liquidity = edge_data.get('liquidity', self.params.default_liquidity)
        
        if liquidity <= 0:
            return self.params.max_price_impact
        
        # 使用改进的AMM价格影响模型
        # 价格影响 = (交易金额 / 流动性) ^ 指数
        raw_impact = (trade_amount / liquidity) ** self.params.price_impact_exponent
        
        # 限制最大价格影响
        return min(self.params.max_price_impact, raw_impact)
    
    def _calculate_gas_impact(self, edge_data: Dict, trade_amount: float) -> float:
        """计算Gas费对权重的影响"""
        gas_fee = edge_data.get('gas_fee', 250000)  # lamports
        gas_fee_sol = gas_fee * 1e-9
        
        # 根据交易金额调整gas影响
        if trade_amount <= self.params.small_trade_threshold:
            gas_multiplier = self.params.gas_multiplier_small
        elif trade_amount >= self.params.large_trade_threshold:
            gas_multiplier = self.params.gas_multiplier_large
        else:
            # 线性插值
            ratio = ((trade_amount - self.params.small_trade_threshold) / 
                    (self.params.large_trade_threshold - self.params.small_trade_threshold))
            gas_multiplier = (self.params.gas_multiplier_small * (1 - ratio) + 
                            self.params.gas_multiplier_large * ratio)
        
        adjusted_gas = gas_fee_sol * gas_multiplier
        return adjusted_gas / trade_amount  # 转换为权重影响
    
    def _calculate_liquidity_confidence(self, edge_data_list: List[Dict]) -> float:
        """计算流动性置信度加成"""
        total_liquidity = sum(edge.get('liquidity', self.params.default_liquidity) 
                            for edge in edge_data_list)
        avg_liquidity = total_liquidity / len(edge_data_list) if edge_data_list else 0
        
        # 流动性越高，置信度加成越大
        return min(self.params.confidence_liquidity_boost, 
                  avg_liquidity / (self.params.default_liquidity * 10))
    
    def _calculate_amount_confidence_factor(self, trade_amount: float) -> float:
        """计算交易金额置信度因子"""
        if trade_amount <= self.params.small_trade_threshold:
            return 1.0  # 小额交易风险低，置信度不打折
        elif trade_amount >= self.params.large_trade_threshold:
            return 0.8  # 大额交易风险高，置信度打折
        else:
            # 线性插值
            ratio = ((trade_amount - self.params.small_trade_threshold) / 
                    (self.params.large_trade_threshold - self.params.small_trade_threshold))
            return 1.0 - (ratio * 0.2)
    
    def _calculate_market_risk_factor(self, edge_data_list: List[Dict], trade_amount: float) -> float:
        """计算市场风险因子"""
        # 基于平均滑点和价格影响计算市场风险
        avg_slippage = sum(edge.get('slippage_bps', 0) for edge in edge_data_list) / len(edge_data_list) / 10000.0
        avg_price_impact = sum(self._calculate_price_impact(edge, trade_amount) for edge in edge_data_list) / len(edge_data_list)
        
        # 市场风险越高，置信度因子越低
        market_risk = avg_slippage + avg_price_impact
        return max(0.5, 1.0 - market_risk * 2)
    
    def _determine_risk_level(self, gas_cost: float, slippage: float, 
                            price_impact: float, liquidity_ratio: float) -> str:
        """确定风险等级"""
        total_cost = gas_cost + slippage + price_impact
        
        if total_cost < 0.002 and liquidity_ratio < 0.1:
            return "LOW"
        elif total_cost < 0.01 and liquidity_ratio < 0.3:
            return "MEDIUM"
        elif total_cost < 0.05 and liquidity_ratio < 0.7:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _calculate_max_recommended_amount(self, edge_data_list: List[Dict], 
                                        profit_ratio: float) -> float:
        """计算建议的最大交易金额"""
        min_liquidity = min(edge.get('liquidity', self.params.default_liquidity) 
                          for edge in edge_data_list)
        
        # 基于流动性和利润率计算安全的最大交易金额
        # 规则：不超过最小流动性的10%，且保证价格影响不超过利润的50%
        liquidity_limit = min_liquidity * 0.1
        
        # 基于价格影响的限制
        profit_limit = profit_ratio * 0.5  # 价格影响不超过利润的50%
        impact_limit = (profit_limit / self.params.price_impact_exponent) ** (1/self.params.price_impact_exponent) * min_liquidity
        
        return min(liquidity_limit, impact_limit, self.params.large_trade_threshold)
    
    def _categorize_trade_amount(self, trade_amount: float) -> str:
        """分类交易金额"""
        if trade_amount <= self.params.small_trade_threshold:
            return "SMALL"
        elif trade_amount <= self.params.large_trade_threshold:
            return "MEDIUM"
        else:
            return "LARGE"


# 便捷函数
def create_default_risk_analyzer() -> RiskAnalyzer:
    """创建默认风险分析器"""
    return RiskAnalyzer()


def analyze_opportunity_risk(opportunity: ArbitrageOpportunity,
                           edge_data_list: List[Dict],
                           trade_amount: float,
                           risk_analyzer: Optional[RiskAnalyzer] = None) -> Dict:
    """
    分析套利机会风险的便捷函数
    
    Args:
        opportunity: 套利机会
        edge_data_list: 边数据列表
        trade_amount: 交易金额
        risk_analyzer: 风险分析器，如果None则使用默认配置
        
    Returns:
        Dict: 风险分析结果
    """
    analyzer = risk_analyzer or create_default_risk_analyzer()
    return analyzer.assess_trade_risk(opportunity, edge_data_list, trade_amount)
