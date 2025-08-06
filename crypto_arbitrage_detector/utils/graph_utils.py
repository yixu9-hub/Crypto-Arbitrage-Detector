'''
Graph utility functions for visualization and detailed information display
'''
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def visualize_graph(G: nx.DiGraph, figsize=(12, 8), node_size=1000, font_size=8, show_plot=True):
    '''
    Visualizes a directed graph with edge labels showing weight and total_fee.

    Args:
        G: NetworkX directed graph to visualize
        figsize: Figure size as (width, height) tuple
        node_size: Size of nodes in the visualization
        font_size: font size for labels
        show_plot: where to display the plot (False for Streamlit, True for console)

    Returns:
        fig: matplotlib figure object for Streamlit display, 
        or call in console if show_plot is True(default)
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    if G.number_of_nodes() == 0:
        print("Warning: Graph has no nodes to visualize")
        return None

    fig, ax = plt.subplots(figsize=figsize)

    # Create layout for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50)

    # Draw nodes with token symbols
    node_labels = {}
    for node in G.nodes():
        node_labels[node] = get_node_symbol(G, node)

    # Draw the graph
    nx.draw_networkx_nodes(G, pos, node_size=node_size,
                           node_color='lightblue', alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G, pos, node_labels,
                            font_size=font_size, font_weight='bold', ax=ax)

    # Group edges by node pairs to identify bidirectional edges
    edge_pairs = {}
    for from_node, to_node, edge_data in G.edges(data=True):
        pair = tuple(sorted([from_node, to_node]))
        if pair not in edge_pairs:
            edge_pairs[pair] = []
        edge_pairs[pair].append((from_node, to_node, edge_data))

    # Draw edges and labels separately for better control
    for pair, edges in edge_pairs.items():
        if len(edges) == 1:
            # Single direction edge - draw straight
            from_node, to_node, edge_data = edges[0]
            nx.draw_networkx_edges(G, pos, [(from_node, to_node)],
                                   edge_color='gray', arrows=True,
                                   arrowsize=20, alpha=0.6, ax=ax)

            # Calculate midpoint for label placement
            x1, y1 = pos[from_node]
            x2, y2 = pos[to_node]
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2

            # Create label
            weight = edge_data.get('weight', 'N/A')
            total_fee = edge_data.get('total_fee', 'N/A')
            weight_str = f"{weight:.4f}" if isinstance(
                weight, (int, float)) else str(weight)
            total_fee_str = str(total_fee) if isinstance(
                total_fee, (int, float)) else str(total_fee)
            label_text = f"W:{weight_str}\nF:{total_fee_str}"

            ax.text(mid_x, mid_y, label_text, fontsize=font_size-1,
                    ha='center', va='center', alpha=0.8,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

        else:
            # Multiple edges (bidirectional or more) - draw all with straight lines
            for from_node, to_node, edge_data in edges:
                nx.draw_networkx_edges(G, pos, [(from_node, to_node)],
                                       edge_color='gray', arrows=True,
                                       arrowsize=20, alpha=0.6, ax=ax)

            # For multiple edges, place label at midpoint
            if edges:
                first_edge = edges[0]
                from_node, to_node, edge_data = first_edge

                x1, y1 = pos[from_node]
                x2, y2 = pos[to_node]
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2

                # Show representative information
                weight = edge_data.get('weight', 'N/A')
                total_fee = edge_data.get('total_fee', 'N/A')
                weight_str = f"{weight:.4f}" if isinstance(
                    weight, (int, float)) else str(weight)
                total_fee_str = str(total_fee) if isinstance(
                    total_fee, (int, float)) else str(total_fee)

                # Use symbols for display
                from_symbol = edge_data['from_symbol']
                to_symbol = edge_data['to_symbol']

                label_text = f"{from_symbol}↔{to_symbol}\nW:{weight_str}\nF:{total_fee_str}"

                ax.text(mid_x, mid_y, label_text, fontsize=font_size-1,
                        ha='center', va='center', alpha=0.8,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))

    plt.title("Token Exchange Graph\nShowing trading pairs and weights",
              fontsize=14, fontweight='bold')
    plt.axis('off')  # Turn off axis

    # Add legend
    legend_text = ("Legend:\nWeight shows trading efficiency\n"
                   "Yellow labels: Bidirectional pairs\n"
                   "White labels: Single direction")
    plt.text(0.02, 0.98, legend_text, transform=ax.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()

    # Only show plot if in console (not for streamlit)
    if show_plot:
        plt.show()

    return fig


# direct streamlit-specific visualization function, call in app.py
def visualize_graph_for_streamlit(G: nx.DiGraph, figsize=(12, 8), node_size=1000, font_size=8):
    '''
    Streamlit graph visualization function.

    Returns:
        fig: matplotlib figure object for st.pyplot()
    '''
    return visualize_graph(G, figsize=figsize, node_size=node_size,
                           font_size=font_size, show_plot=False)


def get_graph_statistics(G: nx.DiGraph) -> dict:
    '''
    Get comprehensive graph statistics as a dictionary (Streamlit-friendly).

    Args:
        G: NetworkX directed graph

    Returns:
        dict: Graph statistics
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    # Check for bidirectional edges
    bidirectional_pairs = 0
    edge_pairs = {}
    for from_node, to_node in G.edges():
        pair = tuple(sorted([from_node, to_node]))
        if pair not in edge_pairs:
            edge_pairs[pair] = []
        edge_pairs[pair].append((from_node, to_node))

    for pair, edges in edge_pairs.items():
        if len(edges) == 2:
            bidirectional_pairs += 1

    return {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'bidirectional_pairs': bidirectional_pairs,
        'unidirectional_edges': G.number_of_edges() - bidirectional_pairs * 2
    }


def print_graph_statistics(G: nx.DiGraph):
    '''
    Print comprehensive graph statistics including nodes, edges, and bidirectional pairs.

    Args:
        G: NetworkX directed graph
    '''
    stats = get_graph_statistics(G)

    print(f"\nGraph Statistics:")
    print(f"Number of nodes (tokens): {stats['total_nodes']}")
    print(f"Number of edges (trading pairs): {stats['total_edges']}")
    print(f"Bidirectional token pairs: {stats['bidirectional_pairs']}")
    print(f"Unidirectional edges: {stats['unidirectional_edges']}")


def get_node_symbol(graph: nx.DiGraph, node: str) -> str:
    """
    Get display symbol for a node address

    Args:
        graph: The graph containing edge data
        node: Node address to get symbol for

    Returns:
        Symbol string or shortened address if not found
    """
    # Check if node exists in graph
    for from_node, to_node, edge_data in graph.edges(data=True):
        if node == from_node:
            return edge_data['from_symbol']  # Get symbol directly
        elif node == to_node:
            return edge_data['to_symbol']


def get_edge_summary(G: nx.DiGraph, max_edges=20) -> list:
    '''
    Get edge summary as a list of dictionaries (Streamlit-friendly).

    Args:
        G: NetworkX directed graph
        max_edges: Maximum number of edges to include

    Returns:
        list: List of edge dictionaries with summary info
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    edges_data = []

    for i, (from_node, to_node, edge_data) in enumerate(G.edges(data=True), 1):
        if i > max_edges:
            break

        # Directly use symbols from edge data
        from_display = edge_data['from_symbol']
        to_display = edge_data['to_symbol']

        edges_data.append({
            'index': i,
            'from_token': from_display,
            'to_token': to_display,
            'weight': edge_data.get('weight', 'N/A'),
            'total_fee': edge_data.get('total_fee', 'N/A'),
            'price_ratio': edge_data.get('price_ratio', 'N/A'),
            'slippage_bps': edge_data.get('slippage_bps', 'N/A'),
            'price_impact_pct': edge_data.get('price_impact_pct', 'N/A')
        })

    return edges_data


def print_edge_summary(G: nx.DiGraph, max_edges=20):
    '''
    Print a summary of edges for small graphs or refer to detailed function for large graphs.

    Args:
        G: NetworkX directed graph
        max_edges: Maximum number of edges to display in summary
    '''
    edges_data = get_edge_summary(G, max_edges)

    if len(edges_data) == 0:
        print(
            f"\nGraph has {G.number_of_edges()} edges. Use print_edge_details() for full edge information.")
        return

    print(f"\nEdge Summary:")
    for edge in edges_data:
        print(f"{edge['index']:2d}. {edge['from_token']} -> {edge['to_token']}")
        print(f"    Weight: {edge['weight']}")
        print(f"    Total Fee: {edge['total_fee']}")
        print(f"    Price Ratio: {edge['price_ratio']}")
        print(f"    Slippage BPS: {edge['slippage_bps']}")

    if G.number_of_edges() > max_edges:
        print(
            f"\nShowing {max_edges} of {G.number_of_edges()} edges. Use print_edge_details() for full information.")


def print_edge_details(G: nx.DiGraph):
    '''
    Print detailed information about all edges in the graph.

    Args:
        G: NetworkX directed graph
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    print(f"Detailed Edge Information for {G.number_of_edges()} edges:")
    print("=" * 80)

    for i, (from_node, to_node, edge_data) in enumerate(G.edges(data=True), 1):
        # Directly use symbols from edge data
        from_display = edge_data['from_symbol']
        to_display = edge_data['to_symbol']

        print(f"{i:3d}. {from_display} -> {to_display}")
        print(f"     Weight: {edge_data.get('weight', 'N/A')}")
        print(f"     Total Fee: {edge_data.get('total_fee', 'N/A')}")
        print(f"     Price Ratio: {edge_data.get('price_ratio', 'N/A')}")
        print(
            f"     Price Impact: {edge_data.get('price_impact_pct', 'N/A')}%")
        print(f"     Slippage BPS: {edge_data.get('slippage_bps', 'N/A')}")
        print(f"     Platform Fee: {edge_data.get('platform_fee', 'N/A')}")

        # Display symbol information
        from_symbol = edge_data['from_symbol']
        to_symbol = edge_data['to_symbol']
        print(f"     Symbols: {from_symbol} -> {to_symbol}")
        print("-" * 60)


def analyze_graph(G: nx.DiGraph, show_visualization=True, show_edge_summary=True, show_statistics=True):
    '''
    Comprehensive graph analysis function that combines statistics, visualization, and edge information.

    Args:
        G: NetworkX directed graph
        show_visualization: Whether to display the graph visualization
        show_edge_summary: Whether to show edge summary
        show_statistics: Whether to show graph statistics
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    print("Graph Analysis Report")
    print("=" * 50)

    if show_statistics:
        print_graph_statistics(G)

    if show_edge_summary:
        print_edge_summary(G)

    if show_visualization and G.number_of_nodes() > 0:
        visualize_graph(G)
