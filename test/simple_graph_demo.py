'''
Simple Graph System Demo
'''
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.mock_data import static_test_edges
from utils.graph_utils import visualize_graph, analyze_graph
from utils.graph_structure import TokenGraphBuilder, build_graph_from_edge_lists


def simple_graph_demo():
    '''
    Simple demonstration of core graph functionality
    '''
    print(" Simple Graph System Demo")
    print("=" * 40)

    # Show available test data
    print(f"Using {len(static_test_edges)} test edge pairs")

    # Build graph using both methods
    print("\n1. Building Graph")
    print("-" * 20)

    builder = TokenGraphBuilder()
    graph = builder.build_graph_from_edge_lists(static_test_edges)

    # Quick analysis
    print("\n2. Graph Analysis")
    print("-" * 20)
    analyze_graph(graph, show_visualization=True,
                  show_statistics=True, show_edge_summary=False)
    print(">>>>> Graph analysis complete <<<<<")


if __name__ == "__main__":
    simple_graph_demo()
