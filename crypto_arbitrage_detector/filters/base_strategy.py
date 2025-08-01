"""
过滤器基类和接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from utils.data_structures import ArbitrageOpportunity
import networkx as nx


class FilterStrategy(ABC):
    """过滤策略基类"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
    
    @abstractmethod
    def filter_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        过滤套利机会
        
        Args:
            opportunities: 待过滤的套利机会列表
            
        Returns:
            List[ArbitrageOpportunity]: 过滤后的套利机会列表
        """
        pass
    
    @abstractmethod
    def get_filter_stats(self) -> Dict[str, Any]:
        """
        获取过滤统计信息
        
        Returns:
            Dict: 过滤统计信息
        """
        pass


class DetectionStrategy(ABC):
    """检测策略基类"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """是否启用此检测策略"""
        pass
    
    @abstractmethod
    def get_algorithm_config(self) -> Dict[str, Any]:
        """获取算法配置参数"""
        pass


class SourceTokenStrategy(ABC):
    """起始token选择策略基类"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
    
    @abstractmethod
    def select_source_token(self, graph: nx.DiGraph, suggested_token: str = None) -> str:
        """
        选择起始token
        
        Args:
            graph: 交易图
            suggested_token: 建议的起始token
            
        Returns:
            str: 选择的起始token
        """
        pass
