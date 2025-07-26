'''
Graph utility functions for visualization and detailed information display
'''
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def visualize_graph(G: nx.DiGraph, figsize=(12, 8), node_size=1000, font_size=8):
    '''
    Visualizes a directed graph with edge labels showing weight and total_fee.
    Handles bidirectional edges by drawing them separately with labels on each side.

    Args:
        G: NetworkX directed graph to visualize
        figsize: Figure size as (width, height) tuple
        node_size: Size of nodes in the visualization
        font_size: Font size for labels
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    if G.number_of_nodes() == 0:
        print("Warning: Graph has no nodes to visualize")
        return

    fig, ax = plt.subplots(figsize=figsize)

    # Create layout for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50)

    # Draw nodes with token symbols (shortened for readability)
    node_labels = {}
    for node in G.nodes():
        # Shorten long addresses for display
        if len(node) > 10:
            node_labels[node] = node[:6] + "..." + node[-4:]
        else:
            node_labels[node] = node

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

        elif len(edges) == 2:
            # Bidirectional edges - draw with curvature and separate labels
            for i, (from_node, to_node, edge_data) in enumerate(edges):
                # Draw curved edges
                connectionstyle = f"arc3,rad={0.15 if i == 0 else -0.15}"
                nx.draw_networkx_edges(G, pos, [(from_node, to_node)],
                                       edge_color='gray', arrows=True,
                                       arrowsize=20, alpha=0.6,
                                       connectionstyle=connectionstyle, ax=ax)

                # Calculate positions for labels
                x1, y1 = pos[from_node]
                x2, y2 = pos[to_node]

                # Calculate curve midpoint and offset direction
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2

                # Calculate perpendicular direction for label offset
                dx = x2 - x1
                dy = y2 - y1
                length = np.sqrt(dx**2 + dy**2)
                if length > 0:
                    # Normalize and get perpendicular vector
                    perp_x = -dy / length
                    perp_y = dx / length

                    # Offset distance for label placement
                    offset_distance = 0.1 if i == 0 else -0.1
                    label_x = mid_x + perp_x * offset_distance
                    label_y = mid_y + perp_y * offset_distance
                else:
                    label_x, label_y = mid_x, mid_y

                # Create separate labels for each direction
                weight = edge_data.get('weight', 'N/A')
                total_fee = edge_data.get('total_fee', 'N/A')
                weight_str = f"{weight:.4f}" if isinstance(
                    weight, (int, float)) else str(weight)
                total_fee_str = str(total_fee) if isinstance(
                    total_fee, (int, float)) else str(total_fee)

                # Shorter node names for cleaner display
                from_short = from_node[:4] if len(from_node) > 4 else from_node
                to_short = to_node[:4] if len(to_node) > 4 else to_node

                label_text = f"{from_short}→{to_short}\nW:{weight_str}\nF:{total_fee_str}"

                ax.text(label_x, label_y, label_text, fontsize=font_size-2,
                        ha='center', va='center', alpha=0.9,
                        bbox=dict(boxstyle='round,pad=0.15',
                                  facecolor='lightblue' if i == 0 else 'lightgreen',
                                  alpha=0.8, edgecolor='gray'))

    plt.title("Token Exchange Graph (Bidirectional)\nEach edge shows its own data",
              fontsize=14, fontweight='bold')
    plt.axis('off')  # Turn off axis

    # Add legend
    legend_text = ("Legend:\nW: Weight (trading efficiency)\nF: Total Fee\n"
                   "Blue labels: First direction\nGreen labels: Reverse direction")
    plt.text(0.02, 0.98, legend_text, transform=ax.transAxes,
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    plt.show()


def print_graph_statistics(G: nx.DiGraph):
    '''
    Print comprehensive graph statistics including nodes, edges, and bidirectional pairs.
    
    Args:
        G: NetworkX directed graph
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    print(f"\nGraph Statistics:")
    print(f"Number of nodes (tokens): {G.number_of_nodes()}")
    print(f"Number of edges (trading pairs): {G.number_of_edges()}")

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

    print(f"Bidirectional token pairs: {bidirectional_pairs}")
    print(f"Unidirectional edges: {G.number_of_edges() - bidirectional_pairs * 2}")


def print_edge_summary(G: nx.DiGraph, max_edges=20):
    '''
    Print a summary of edges for small graphs or refer to detailed function for large graphs.
    
    Args:
        G: NetworkX directed graph
        max_edges: Maximum number of edges to display in summary
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    # Print detailed edge information for small graphs only
    if G.number_of_edges() <= max_edges:
        print(f"\nEdge Summary:")
        for i, (from_node, to_node, edge_data) in enumerate(G.edges(data=True), 1):
            # Smart truncation: keep symbol names, truncate long addresses
            from_short = from_node if len(from_node) <= 10 else from_node[:8] + "..." + from_node[-4:]
            to_short = to_node if len(to_node) <= 10 else to_node[:8] + "..." + to_node[-4:]
            print(f"{i:2d}. {from_short} -> {to_short}")
            print(f"    Weight: {edge_data.get('weight', 'N/A')}")
            print(f"    Total Fee: {edge_data.get('total_fee', 'N/A')}")
            print(f"    Price Ratio: {edge_data.get('price_ratio', 'N/A')}")
            print(f"    Slippage BPS: {edge_data.get('slippage_bps', 'N/A')}")
    else:
        print(f"\nGraph has {G.number_of_edges()} edges. Use print_edge_details() for full edge information.")


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
        # Address for both start and end for better identification
        from_short = from_node if len(from_node) <= 15 else from_node[:10] + "..." + from_node[-4:]
        to_short = to_node if len(to_node) <= 15 else to_node[:10] + "..." + to_node[-4:]

        print(f"{i:3d}. {from_short} -> {to_short}")
        print(f"     Weight: {edge_data.get('weight', 'N/A')}")
        print(f"     Total Fee: {edge_data.get('total_fee', 'N/A')}")
        print(f"     Price Ratio: {edge_data.get('price_ratio', 'N/A')}")
        print(f"     Price Impact: {edge_data.get('price_impact_pct', 'N/A')}%")
        print(f"     Slippage BPS: {edge_data.get('slippage_bps', 'N/A')}")
        print(f"     Platform Fee: {edge_data.get('platform_fee', 'N/A')}")
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

    print("📊 Graph Analysis Report")
    print("=" * 50)
    
    if show_statistics:
        print_graph_statistics(G)
    
    if show_edge_summary:
        print_edge_summary(G)
    
    if show_visualization and G.number_of_nodes() > 0:
        print("\n🎨 Displaying graph visualization...")
        visualize_graph(G)
