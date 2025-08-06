import os
import sys
import subprocess
from datetime import datetime, timedelta
import pickle
import networkx as nx
from typing import List
from crypto_arbitrage_detector.utils.data_structures import EdgePairs, TokenInfo
from crypto_arbitrage_detector.utils.get_quote_pair import get_edge_pairs
from crypto_arbitrage_detector.scripts.token_loader import TokenLoader
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.utils.graph_utils import analyze_graph
from crypto_arbitrage_detector.configs.request_config import jupiter_quote_api, jupiter_swap_api


# Function to check if token file exists and is fresh
def check_token_file():
    """
    Check if both Jupiter tokens and enriched tokens files exist and are fresh
    Args:
        jupiter_file (str): The file to save the Jupiter tokens to
        enriched_file (str): The file to save the volume enriched tokens to
    Returns:
        bool: True if the tokens were downloaded and saved successfully, False otherwise
        jupiter_status (str): The status of the Jupiter tokens
        enriched_status (str): The status of the enriched tokens
    """
    jupiter_file = "data/jupiter_tokens.json"
    enriched_file = "data/enriched_tokens.pkl"
    
    # Check Jupiter tokens (weekly refresh - 7 days)
    jupiter_ok = True
    jupiter_status = "Jupiter tokens are fresh"
    if not os.path.exists(jupiter_file):
        jupiter_ok = False
        jupiter_status = "Jupiter token file not found"
    else:
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(jupiter_file))
            max_age = timedelta(hours=7*24)  # 7 days
            
            if datetime.now() - file_mtime > max_age:
                jupiter_ok = False
                jupiter_status = "Jupiter tokens are outdated (older than 7 days)"
        except Exception as e:
            jupiter_ok = False
            jupiter_status = f"Error checking Jupiter tokens: {str(e)}"
    
    # Check enriched tokens (daily refresh - 24 hours)
    enriched_ok = True
    enriched_status = "Enriched tokens are fresh"
    if not os.path.exists(enriched_file):
        enriched_ok = False
        enriched_status = "Enriched token file not found"
    else:
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(enriched_file))
            max_age = timedelta(hours=24)  # 24 hours
            
            if datetime.now() - file_mtime > max_age:
                enriched_ok = False
                enriched_status = "Enriched tokens are outdated (older than 24 hours)"
        except Exception as e:
            enriched_ok = False
            enriched_status = f"Error checking enriched tokens: {str(e)}"
    
    return jupiter_ok, enriched_ok, jupiter_status, enriched_status

# Function to fetch Jupiter tokens
def fetch_jupiter_tokens():
    """
    Run the Jupiter token download script
    Args:
        jupiter_file (str): The file to save the Jupiter tokens to
        enriched_file (str): The file to save the volume enriched tokens to
    Returns:
        bool: True if the tokens were downloaded and saved successfully, False otherwise
    """
    try:
        # Run the download_tokens.py script
        result = subprocess.run([
            sys.executable, "crypto_arbitrage_detector/scripts/download_tokens.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return True, "Jupiter tokens successfully downloaded"
        else:
            return False, f"Error downloading Jupiter tokens: {result.stderr}"
    except Exception as e:
        return False, f"Error running Jupiter token downloader: {str(e)}"

# Function to fetch enriched tokens from Jupiter
def fetch_enriched_tokens():
    """
    Run the volume fetcher script to get enriched tokens
    Args:
        enriched_file (str): The file to save the volume enriched tokens to
    Returns:
        bool: True if the tokens were fetched and saved successfully, False otherwise
    """
    try:
        # Run the volume_fetcher.py script
        result = subprocess.run([
            sys.executable, "crypto_arbitrage_detector/scripts/volume_fetcher.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return True, "Enriched tokens successfully fetched from Jupiter and DexScreener"
        else:
            return False, f"Error fetching enriched tokens: {result.stderr}"
    except Exception as e:
        return False, f"Error running volume fetcher: {str(e)}"

# Function to load popular tokens from token_loader
def load_popular_tokens():
    """
    Load popular tokens from the token loader

    Returns:
        list: A list of popular tokens
    """
    try:
        token_loader = TokenLoader()
        loaded_tokens = token_loader.load_tokens()
        
        if loaded_tokens and len(loaded_tokens) > 0:
            # Extract top tokens by volume rank
            top_tokens = sorted(loaded_tokens, key=lambda x: getattr(x, 'volume_rank', 999))[:8]
            return [token.address for token in top_tokens]
        else:
            # Fallback to default tokens if loading fails
            return [
                "So11111111111111111111111111111111111111112",  # WSOL
                "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
                "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
            ]
    except Exception as e:
        # Fallback to default tokens
        return [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
        ]

# Function to retrieve edges from token data
async def retrive_edges(api_key: str = jupiter_quote_api["api_key"],
        quote_url: str = jupiter_quote_api["base_url"],
        swap_url: str = jupiter_swap_api["base_url"]):
    """
    Retrieve edges from token data.
    Args:
        api_key (str): The API key for the quote and swap endpoints
        quote_url (str): The URL for the quote endpoint
        swap_url (str): The URL for the swap endpoint
    Returns:
        list: A list of edges relaxed by price ratio and weight
    """
    try:
        with open("data/enriched_tokens.pkl", "rb") as f:
            TokenLists: List[TokenInfo] = pickle.load(f)
        edges: List[EdgePairs] = await get_edge_pairs(
            token_list = TokenLists, api_key = api_key,
            quote_url= quote_url,
            swap_url = swap_url)
        return edges
        
    except FileNotFoundError:
        print("❌ enriched_tokens.pkl file not found")
        return []
    except Exception as e:
        print(f"❌ Error in retrive_edges: {str(e)}")
        return []

def visualize_graph_streamlit(G: nx.DiGraph):
    '''
    Streamlit graph visualization function using Plotly.
    Shows nodes as points and edges with detailed information on hover.

    Args:
        G: NetworkX directed graph

    Returns:
        fig: Plotly figure object for st.plotly_chart()
    '''
    if G is None:
        raise ValueError("Graph cannot be None")

    if not isinstance(G, nx.DiGraph):
        raise TypeError(f"Expected nx.DiGraph, got {type(G)}")

    if G.number_of_nodes() == 0:
        raise ValueError("Graph has no nodes to visualize")

    import plotly.graph_objects as go
    
    # Create layout for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50)

    # Create edge traces
    edge_x = []
    edge_y = []
    edge_text = []
    
    for from_node, to_node, edge_data in G.edges(data=True):
        x0, y0 = pos[from_node]
        x1, y1 = pos[to_node]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        # Create edge label with weight and fee info
        weight = edge_data.get('weight', 'N/A')
        total_fee = edge_data.get('total_fee', 'N/A')
        price_ratio = edge_data.get('price_ratio', 'N/A')
        
        weight_str = f"{weight:.4f}" if isinstance(weight, (int, float)) else str(weight)
        total_fee_str = f"{total_fee:.4f}" if isinstance(total_fee, (int, float)) else str(total_fee)
        price_ratio_str = f"{price_ratio:.4f}" if isinstance(price_ratio, (int, float)) else str(price_ratio)
        
        # Get symbols for display
        from_symbol = edge_data.get('from_symbol', from_node[:8])
        to_symbol = edge_data.get('to_symbol', to_node[:8])
        
        edge_text.append(f"{from_symbol} → {to_symbol}<br>Weight: {weight_str}<br>Fee: {total_fee_str}<br>Price Ratio: {price_ratio_str}")
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=3, color='#1f77b4'),
        hoverinfo='text',
        text=edge_text,
        mode='lines',
        name='Edges',
        opacity=0.8
    )
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_hover_text = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Get symbol for display
        symbol = get_node_symbol(G, node)
        if symbol:
            node_text.append(symbol)
            node_hover_text.append(f"Token: {symbol}<br>Address: {node[:8]}...")
        else:
            # Shorten long addresses for display
            if len(node) > 10:
                display_text = node[:6] + "..." + node[-4:]
            else:
                display_text = node
            node_text.append(display_text)
            node_hover_text.append(f"Token: {display_text}<br>Address: {node}")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        hovertext=node_hover_text,
        textposition="middle center",
        marker=dict(
            size=25,
            color='lightblue',
            line=dict(width=2, color='black')
        ),
        name='Nodes'
    )
    
    # Create edge annotations for direct display on graph
    edge_annotations = []
    for from_node, to_node, edge_data in G.edges(data=True):
        x0, y0 = pos[from_node]
        x1, y1 = pos[to_node]
        
        # Calculate midpoint for annotation
        mid_x = (x0 + x1) / 2
        mid_y = (y0 + y1) / 2
        
        # Get symbols for display
        from_symbol = edge_data.get('from_symbol', from_node[:8])
        to_symbol = edge_data.get('to_symbol', to_node[:8])
        
        # Create annotation text
        weight = edge_data.get('weight', 'N/A')
        weight_str = f"{weight:.2f}" if isinstance(weight, (int, float)) else str(weight)
        
        annotation_text = f"{from_symbol}→{to_symbol}<br>W:{weight_str}"
        
        edge_annotations.append(dict(
            x=mid_x,
            y=mid_y,
            text=annotation_text,
            showarrow=False,
            font=dict(size=10, color='red'),
            bgcolor='white',
            bordercolor='black',
            borderwidth=1
        ))
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title=dict(
                           text=f'Token Swap Network Graph ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)',
                           font=dict(size=16)
                       ),
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20, l=5, r=5, t=40),
                       annotations=edge_annotations + [dict(
                           text="Edge labels show: Symbol→Symbol<br>W:Weight",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor="left", yanchor="bottom",
                           font=dict(size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                   ))
    
    return fig

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
