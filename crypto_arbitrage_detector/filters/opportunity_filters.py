"""
套利机会过滤策略实现
"""
from typing import List, Dict, Any
from .base_strategy import FilterStrategy
from utils.data_structures import ArbitrageOpportunity


class ProfitThresholdFilter(FilterStrategy):
    """利润阈值过滤器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="profit_threshold",
            description="基于利润阈值过滤套利机会",
            config=config
        )
        self.min_profit = self.config.get('min_profit_threshold', 0.005)
        self.filtered_count = 0
        self.total_count = 0
    
    def filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        self.total_count = len(opportunities)
        filtered = [opp for opp in opportunities if opp.profit_ratio >= self.min_profit]
        self.filtered_count = self.total_count - len(filtered)
        return filtered
    
    def get_filter_stats(self) -> Dict[str, Any]:
        return {
            'filter_name': self.name,
            'total_opportunities': self.total_count,
            'filtered_out': self.filtered_count,
            'remaining': self.total_count - self.filtered_count,
            'min_profit_threshold': self.min_profit
        }


class HopCountFilter(FilterStrategy):
    """跳数过滤器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="hop_count",
            description="基于跳数限制过滤套利机会",
            config=config
        )
        self.max_hops = self.config.get('max_hops', 4)
        self.filtered_count = 0
        self.total_count = 0
    
    def filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        self.total_count = len(opportunities)
        filtered = [opp for opp in opportunities if opp.hop_count <= self.max_hops]
        self.filtered_count = self.total_count - len(filtered)
        return filtered
    
    def get_filter_stats(self) -> Dict[str, Any]:
        return {
            'filter_name': self.name,
            'total_opportunities': self.total_count,
            'filtered_out': self.filtered_count,
            'remaining': self.total_count - self.filtered_count,
            'max_hops': self.max_hops
        }


class ConfidenceScoreFilter(FilterStrategy):
    """置信度分数过滤器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="confidence_score",
            description="基于置信度分数过滤套利机会",
            config=config
        )
        self.min_confidence = self.config.get('min_confidence_score', 0.3)
        self.filtered_count = 0
        self.total_count = 0
    
    def filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        self.total_count = len(opportunities)
        filtered = [opp for opp in opportunities if opp.confidence_score >= self.min_confidence]
        self.filtered_count = self.total_count - len(filtered)
        return filtered
    
    def get_filter_stats(self) -> Dict[str, Any]:
        return {
            'filter_name': self.name,
            'total_opportunities': self.total_count,
            'filtered_out': self.filtered_count,
            'remaining': self.total_count - self.filtered_count,
            'min_confidence_score': self.min_confidence
        }


class DuplicatePathFilter(FilterStrategy):
    """重复路径过滤器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="duplicate_path",
            description="去除重复路径的套利机会",
            config=config
        )
        self.keep_highest_profit = self.config.get('keep_highest_profit', True)
        self.filtered_count = 0
        self.total_count = 0
    
    def filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        self.total_count = len(opportunities)
        
        if not opportunities:
            return []
        
        # 去重逻辑
        unique_opportunities = {}
        for opp in opportunities:
            # 创建标准化的路径键（处理循环路径）
            # 排除最后重复的节点
            path_key = tuple(sorted(opp.path[:-1]))
            
            if path_key not in unique_opportunities:
                unique_opportunities[path_key] = opp
            else:
                # 保留利润更高的机会
                if self.keep_highest_profit and opp.profit_ratio > unique_opportunities[path_key].profit_ratio:
                    unique_opportunities[path_key] = opp
        
        filtered = list(unique_opportunities.values())
        self.filtered_count = self.total_count - len(filtered)
        return filtered
    
    def get_filter_stats(self) -> Dict[str, Any]:
        return {
            'filter_name': self.name,
            'total_opportunities': self.total_count,
            'filtered_out': self.filtered_count,
            'remaining': self.total_count - self.filtered_count,
            'keep_highest_profit': self.keep_highest_profit
        }


class TopNFilter(FilterStrategy):
    """Top N过滤器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="top_n",
            description="保留Top N个最佳套利机会",
            config=config
        )
        self.max_count = self.config.get('max_opportunities', 10)
        self.sort_by = self.config.get('sort_by', 'profit_ratio')  # 'profit_ratio', 'confidence_score'
        self.filtered_count = 0
        self.total_count = 0
    
    def filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        self.total_count = len(opportunities)
        
        if not opportunities:
            return []
        
        # 排序
        if self.sort_by == 'profit_ratio':
            sorted_opps = sorted(opportunities, key=lambda x: x.profit_ratio, reverse=True)
        elif self.sort_by == 'confidence_score':
            sorted_opps = sorted(opportunities, key=lambda x: x.confidence_score, reverse=True)
        else:
            # 综合排序
            sorted_opps = sorted(opportunities, 
                               key=lambda x: (x.profit_ratio, x.confidence_score), 
                               reverse=True)
        
        filtered = sorted_opps[:self.max_count]
        self.filtered_count = self.total_count - len(filtered)
        return filtered
    
    def get_filter_stats(self) -> Dict[str, Any]:
        return {
            'filter_name': self.name,
            'total_opportunities': self.total_count,
            'filtered_out': self.filtered_count,
            'remaining': self.total_count - self.filtered_count,
            'max_opportunities': self.max_count,
            'sort_by': self.sort_by
        }
