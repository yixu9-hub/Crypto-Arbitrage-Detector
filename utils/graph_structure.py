'''
从nova的list建静态图, 处理边的验证和错误处理, 提供下一步的接口
'''
import networkx as nx
from typing import List
from datetime import datetime

from utils.data_structures import EdgePairs


class TokenGraphBuilder:
    """
    Static token trading graph builder

    Features:
    - Build graph from EdgePairs list
    - Data validation and error handling
    - Graph visualization and statistics
    - Detailed edge information display
    """

    def __init__(self):
        '''
        Initialize graph builder
        '''
        self.graph = None
        self.build_history = []
        print("^ ^ TokenGraphBuilder initialized successfully")

    def build_graph_from_edge_lists(self, edges: List[EdgePairs]) -> nx.DiGraph:
        '''
        Build graph from EdgePairs list
        Args:
            edges: List of EdgePairs objects containing trading pair information
        Returns:
            nx.DiGraph: Directed graph containing token pairs and attributes
        '''
        if edges is None:
            raise ValueError("Edges list cannot be None")

        if not isinstance(edges, list):
            raise TypeError(f"Expected list of EdgePairs, got {type(edges)}")

        if len(edges) == 0:
            raise ValueError("Edges list cannot be empty")

        G = nx.DiGraph()

        for i, edge in enumerate(edges):
            try:
                # Validate edge is a EdgePairs object
                if not isinstance(edge, EdgePairs):
                    raise TypeError(
                        f"Edge at index {i} is not an EdgePairs object, got {type(edge)}")

                # validate fields
                required_attrs = ['from_token', 'to_token', 'weight', 'price_ratio',
                                  'slippage_bps', 'platform_fee', 'price_impact_pct', 'total_fee']

                for attr in required_attrs:
                    if not hasattr(edge, attr):
                        raise AttributeError(
                            f"Edge at index {i} is missing required attribute '{attr}'")

                    value = getattr(edge, attr)
                    if value is None:
                        raise ValueError(
                            f"Edge at index {i} has None value for attribute '{attr}'")

                # token address cannot be empty strings
                if not edge.from_token or not edge.to_token:
                    raise ValueError(
                        f"Edge at index {i} has empty token address(es)")

                # Validate numeric attributes
                numeric_attrs = ['price_ratio',
                                 'platform_fee', 'price_impact_pct']
                for attr in numeric_attrs:
                    value = getattr(edge, attr)
                    if not isinstance(value, (int, float)):
                        raise ValueError(
                            f"Edge at index {i} has invalid {attr}: {value} (must be a number)")
                    if value < 0:
                        raise ValueError(
                            f"Edge at index {i} has invalid {attr}: {value} (must be non-negative)")

                # weight must be a number
                if not isinstance(edge.weight, (int, float)):
                    raise ValueError(
                        f"Edge at index {i} has invalid weight: {edge.weight} (must be a number)")

                # 浮点值，total fee验证
                if not isinstance(edge.slippage_bps, int) or edge.slippage_bps < 0:
                    raise ValueError(
                        f"Edge at index {i} has invalid slippage_bps: {edge.slippage_bps} (must be non-negative integer)")

                if not isinstance(edge.total_fee, (int, float)) or edge.total_fee < 0:
                    raise ValueError(
                        f"Edge at index {i} has invalid total_fee: {edge.total_fee} (must be non-negative number)")

                # can add edge to graph
                G.add_edge(
                    edge.from_token,
                    edge.to_token,
                    weight=edge.weight,
                    price_ratio=edge.price_ratio,
                    slippage_bps=edge.slippage_bps,
                    platform_fee=edge.platform_fee,
                    price_impact_pct=edge.price_impact_pct,
                    total_fee=edge.total_fee
                )

            except (AttributeError, ValueError, TypeError) as e:
                raise ValueError(
                    f"Error processing edge at index {i}: {str(e)}")
            except Exception as e:
                raise RuntimeError(
                    f"Unexpected error processing edge at index {i}: {str(e)}")

        # Save built graph and history
        self.graph = G
        self.build_history.append({
            'timestamp': datetime.now(),  # Record build time
            'edges_count': len(edges),
            'nodes_count': G.number_of_nodes(),
            'graph_edges_count': G.number_of_edges()
        })

        print(
            f"- Graph built successfully: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G


# Backward compatible function interface
def build_graph_from_edge_lists(edges: List[EdgePairs]) -> nx.DiGraph:
    """
    Backward compatible function interface for building graph from EdgePairs list.
    For new code, prefer using TokenGraphBuilder class directly.

    Args:
        edges: List of EdgePairs objects

    Returns:
        nx.DiGraph: Built graph
    """
    builder = TokenGraphBuilder()
    return builder.build_graph_from_edge_lists(edges)
