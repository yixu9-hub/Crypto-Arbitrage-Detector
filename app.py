import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import requests
import time
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
from typing import List, Dict, Tuple, Optional
import numpy as np

from crypto_arbitrage_detector.utils.helper import check_token_file, fetch_jupiter_tokens, fetch_enriched_tokens, load_popular_tokens, retrive_edges
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.utils.graph_utils import analyze_graph, visualize_graph
from crypto_arbitrage_detector.utils.data_structures import ArbitrageOpportunity
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector

# Page configuration
st.set_page_config(
    page_title="Solana Arbitrage Detector",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables 
if 'detector' not in st.session_state:
    st.session_state.detector = None
if 'arbitrage_results' not in st.session_state:
    st.session_state.arbitrage_results = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'tokens_loaded' not in st.session_state:
    st.session_state.tokens_loaded = False
if 'token_error' not in st.session_state:
    st.session_state.token_error = None

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .profit-positive {
        color: #28a745;
        font-weight: bold;
    }
    .profit-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .status-running {
        color: #28a745;
    }
    .status-stopped {
        color: #dc3545;
    }
</style>
""", unsafe_allow_html=True)

class ArbitrageDetector:
    def __init__(self):
        self.jupiter_tokens_url = "https://cache.jup.ag/tokens"
        self.jupiter_quote_url = "https://quote-api.jup.ag/v6/quote"
        self.token_list = {}
        self.price_graph = {}
        
    async def fetch_token_list(self):
        """Fetch available tokens from Jupiter API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.jupiter_tokens_url) as response:
                    if response.status == 200:
                        tokens = await response.json()
                        self.token_list = {token['address']: token for token in tokens}
                        return True
        except Exception as e:
            st.error(f"Error fetching token list: {str(e)}")
        return False
    
    async def get_quote(self, input_mint: str, output_mint: str, amount: int):
        """Get quote for token swap"""
        try:
            params = {
                'inputMint': input_mint,
                'outputMint': output_mint,
                'amount': amount,
                'slippageBps': 50  # 0.5% slippage
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(self.jupiter_quote_url, params=params) as response:
                    if response.status == 200:
                        quote_data = await response.json()
                        return quote_data
        except Exception as e:
            st.error(f"Error getting quote: {str(e)}")
        return None
    
    def bellman_ford_arbitrage(self, graph: Dict, start_token: str, min_profit_threshold: float = 0.01):
        """
        Modified Bellman-Ford algorithm to detect negative cycles (arbitrage opportunities)
        Returns: List of arbitrage cycles found
        """
        # Convert to log prices for additive property
        log_graph = {}
        for token_a in graph:
            log_graph[token_a] = {}
            for token_b in graph[token_a]:
                if graph[token_a][token_b] > 0:
                    log_graph[token_a][token_b] = -np.log(graph[token_a][token_b])
                else:
                    log_graph[token_a][token_b] = float('inf')
        
        tokens = list(log_graph.keys())
        distances = {token: float('inf') for token in tokens}
        predecessors = {token: None for token in tokens}
        distances[start_token] = 0
        
        # Relax edges V-1 times
        for _ in range(len(tokens) - 1):
            for token_a in log_graph:
                for token_b in log_graph[token_a]:
                    if distances[token_a] + log_graph[token_a][token_b] < distances[token_b]:
                        distances[token_b] = distances[token_a] + log_graph[token_a][token_b]
                        predecessors[token_b] = token_a
        
        # Check for negative cycles
        arbitrage_cycles = []
        for token_a in log_graph:
            for token_b in log_graph[token_a]:
                if distances[token_a] + log_graph[token_a][token_b] < distances[token_b]:
                    # Negative cycle detected, reconstruct the cycle
                    cycle = self.reconstruct_cycle(predecessors, token_b, graph)
                    if cycle and self.calculate_cycle_profit(cycle, graph) > min_profit_threshold:
                        arbitrage_cycles.append(cycle)
        
        return arbitrage_cycles
    
    def reconstruct_cycle(self, predecessors: Dict, start_token: str, graph: Dict):
        """Reconstruct arbitrage cycle from predecessors"""
        cycle = []
        current = start_token
        visited = set()
        
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = predecessors.get(current)
            if current is None:
                break
        
        if current in visited:
            cycle_start_idx = cycle.index(current)
            return cycle[cycle_start_idx:]
        
        return None
    
    def calculate_cycle_profit(self, cycle: List[str], graph: Dict):
        """Calculate expected profit from an arbitrage cycle"""
        if len(cycle) < 2:
            return 0
        
        total_rate = 1.0
        for i in range(len(cycle)):
            current_token = cycle[i]
            next_token = cycle[(i + 1) % len(cycle)]
            if current_token in graph and next_token in graph[current_token]:
                total_rate *= graph[current_token][next_token]
        
        return total_rate - 1.0

# Initialize the arbitrage detector if not already done
if st.session_state.detector is None:
    st.session_state.detector = ArbitrageDetector()

# Check token file status
jupiter_ok, enriched_ok, jupiter_status, enriched_status = check_token_file()

# Show error message and refresh buttons if needed
if not jupiter_ok or not enriched_ok:
    st.markdown("""
    <div class="error-message">
        <h3>⚠️ Token Data Issues</h3>
        <p>The application needs fresh token data to function properly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show specific issues
    if not jupiter_ok:
        st.error(f"**Jupiter Token Issue:** {jupiter_status}")
    if not enriched_ok:
        st.error(f"**Enriched Token Issue:** {enriched_status}")
    
    # Refresh buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if not jupiter_ok:
            if st.button("Refresh Jupiter Tokens", type="primary"):
                with st.spinner("Downloading fresh Jupiter token list..."):
                    success, message = fetch_jupiter_tokens()
                    
                    if success:
                        st.success("✅ Jupiter tokens refreshed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to refresh Jupiter tokens: {message}")
        else:
            st.success("✅ Jupiter tokens are up to date")
    
    with col2:
        if not enriched_ok:
            if st.button("Refresh Volume Data", type="primary"):
                with st.spinner("Fetching fresh volume data from DexScreener..."):
                    success, message = fetch_enriched_tokens()
                    
                    if success:
                        st.success("✅ Volume data refreshed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to refresh volume data: {message}")
        else:
            st.success("✅ Volume data is up to date")
    
    # Info panel
    st.info("""
    **What these buttons do:**
    
    **🔄 Refresh Jupiter Tokens:**
    - Downloads the latest token list from Jupiter API
    - Refreshed weekly (7 days)
    - Contains basic token information (symbol, name, decimals)
    
    **📊 Refresh Volume Data:**
    - Fetches volume and liquidity data from DexScreener
    - Refreshed daily (24 hours)
    - Enriches tokens with trading metrics
    
    Both processes may take a few minutes.
    """)
    
    # Don't show the main app until both are loaded
    st.stop()

# Main UI
st.markdown('<h1 class="main-header">🔄 Solana Arbitrage Opportunity Detective</h1>', unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Detection parameters
st.sidebar.subheader("Detection Parameters")
min_profit_threshold = st.sidebar.slider(
    "Minimum Profit Threshold (%)", 
    min_value=0.1, 
    max_value=5.0, 
    value=1.0, 
    step=0.1
) / 100

max_slippage = st.sidebar.slider(
    "Maximum Slippage (%)", 
    min_value=0.1, 
    max_value=2.0, 
    value=0.5, 
    step=0.1
) / 100

base_amount = st.sidebar.selectbox(
    "Base Amount",
    options=[0.1, 1.0, 5.0, 10.0, 50.0],
    index=2
)

max_hops = st.sidebar.slider(
    "Maximum Path Length", 
    min_value=2, 
    max_value=6, 
    value=4
)

# Algorithm selection
st.sidebar.subheader("Algorithm Selection")
selected_algorithms = st.sidebar.multiselect(
    "Select algorithms to use (choose 1, 2, or all)",
    options=["bellman_ford", "triangle", "two_hop"],
    default=["bellman_ford"]
)
enable_bellman_ford = "bellman_ford" in selected_algorithms
enable_triangle = "triangle" in selected_algorithms
enable_two_hop = "two_hop" in selected_algorithms

# Token selection
st.sidebar.subheader("Token Selection")
popular_tokens = [
    "So11111111111111111111111111111111111111112",  # WSOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
]

selected_tokens = st.sidebar.multiselect(
    "Select tokens to monitor (leave empty for all popular tokens)",
    options=popular_tokens,
    default=popular_tokens[:10]
)

edges = asyncio.run(retrive_edges())
G = build_graph_from_edge_lists(edges)

# Control buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    start_detection = st.button("▶️ Start", type="primary")
with col2:
    stop_detection = st.button("⏹️ Stop")

if start_detection:
    st.session_state.is_running = True
    detector = IntegratedArbitrageDetector(min_profit_threshold, max_hops, base_amount)
    st.session_state.arbitrage_results = detector.detect_arbitrage(G, None, enable_bellman_ford, enable_triangle, enable_two_hop )
if stop_detection:
    st.session_state.is_running = False

# Status indicator
status_color = "status-running" if st.session_state.is_running else "status-stopped"
status_text = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
st.sidebar.markdown(f'<p class="{status_color}">Status: {status_text}</p>', unsafe_allow_html=True)

if st.session_state.last_update:
    st.sidebar.write(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Arbitrage Opportunities", "📈 Price Graph", "⚙️ System Logs"])

with tab1:
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.arbitrage_results:
            opportunities_found = 0
        else:
            for result in st.session_state.arbitrage_results:
                if result.estimated_profit_sol > 0:
                    opportunities_found += 1
        st.metric("Opportunities Found", opportunities_found)
    
    with col2:
        if st.session_state.arbitrage_results:
            # Handle both ArbitrageOpportunity objects and dictionaries
            if hasattr(st.session_state.arbitrage_results[0], 'estimated_profit_sol'):
                # ArbitrageOpportunity objects
                max_profit = max([result.estimated_profit_sol for result in st.session_state.arbitrage_results])
                st.metric("Max Profit Found", f"{max_profit:.4f} SOL")
            else:
                # Dictionary objects
                max_profit = max([result.get('estimated_profit_sol', 0) for result in st.session_state.arbitrage_results])
                st.metric("Max Profit Found", f"{max_profit:.4f} SOL")
        else:
            st.metric("Max Profit Found", "0.0000 SOL")
    
    with col3:
        avg_path_length = 0
        if st.session_state.arbitrage_results:
            avg_path_length = np.mean([len(result['path']) for result in st.session_state.arbitrage_results])
        st.metric("Avg Path Length", f"{avg_path_length:.1f}")
    
    with col4:
        tokens_monitored = len(selected_tokens) if selected_tokens else len(popular_tokens)
        st.metric("Tokens Monitored", tokens_monitored)
    
    # Real-time chart placeholder
    st.subheader("📈 Real-time Arbitrage Opportunities")
    
    # Create sample data for demonstration
    if st.session_state.arbitrage_results:
        df = pd.DataFrame(st.session_state.arbitrage_results)
        fig = px.scatter(df, x='timestamp', y='profit_percentage', 
                        size='trade_volume', color='path_length',
                        title="Arbitrage Opportunities Over Time",
                        labels={'profit_percentage': 'Profit %', 'timestamp': 'Time'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start detection to see real-time arbitrage opportunities")

with tab2:
    st.subheader("🔍 Current Arbitrage Opportunities")
    
    if st.session_state.arbitrage_results:
        for i, opportunity in enumerate(st.session_state.arbitrage_results):
            # Handle both ArbitrageOpportunity objects and dictionaries
            if hasattr(opportunity, 'estimated_profit_sol'):
                # ArbitrageOpportunity object
                profit = opportunity.estimated_profit_sol
                path = opportunity.path
                total_fee = opportunity.total_fee
            else:
                # Dictionary object
                profit = opportunity.get('estimated_profit_sol', 0)
                path = opportunity.get('path', [])
                total_fee = opportunity.get('total_fee', 0.001)
            
            with st.expander(f"Opportunity #{i+1} - {profit:.4f} SOL Profit"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Trading Path:**")
                    path_str = " → ".join([f"Token_{token[:8]}..." for token in path])
                    st.code(path_str)
                    
                    st.write("**Path Details:**")
                    for j, (from_token, to_token) in enumerate(zip(path, path[1:] + [path[0]])):
                        st.write(f"Step {j+1}: {from_token[:8]}... → {to_token[:8]}...")
                
                with col2:
                    st.metric("Expected Profit", f"{profit:.4f} SOL")
                    st.metric("Path Length", len(path))
                    st.metric("Est. Gas Cost", f"{total_fee:.4f} SOL")
                    
                    if profit > 0:
                        st.success("✅ Profitable")
                    else:
                        st.error("❌ Not Profitable")
    else:
        st.info("No arbitrage opportunities detected. Start the detection system to find opportunities.")

with tab3:
    st.subheader("📈 Token Price Graph Network")
    
    # Create a network graph for visualization
    if selected_tokens or popular_tokens:
        # Create Plotly network graph from the built graph
        if G.number_of_nodes() > 0:
            # Get positions for nodes
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
                
                edge_text.append(f"W:{weight_str}<br>F:{total_fee_str}<br>P:{price_ratio_str}")
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='text',
                text=edge_text,
                mode='lines',
                name='Edges'
            )
            
            # Create node traces
            node_x = []
            node_y = []
            node_text = []
            
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                # Shorten long addresses for display
                if len(node) > 10:
                    node_text.append(node[:6] + "..." + node[-4:])
                else:
                    node_text.append(node)
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(
                    size=30,
                    color='lightblue',
                    line=dict(width=2, color='black')
                ),
                name='Nodes'
            )
            
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title=dict(
                                   text=f'Token Swap Network Graph ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)',
                                   font=dict(size=16)
                               ),
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               annotations=[dict(
                                   text="Nodes represent tokens, edges represent possible swaps",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor="left", yanchor="bottom",
                                   font=dict(size=12)
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                           ))
        else:
            st.info("No graph data available")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select tokens to visualize the price graph network")

with tab4:
    st.subheader("⚙️ System Logs & Debug Info")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**System Status:**")
        st.json({
            "Detection Active": st.session_state.is_running,
            "Last Update": str(st.session_state.last_update) if st.session_state.last_update else "Never",
            "Opportunities Found": len(st.session_state.arbitrage_results),
            "Min Profit Threshold": f"{min_profit_threshold*100:.1f}%",
            "Max Slippage": f"{max_slippage*100:.1f}%",
            "Base Amount": f"{base_amount} SOL"
        })
    
    with col2:
        st.write("**API Endpoints:**")
        st.code("""
            Jupiter Tokens: https://cache.jup.ag/tokens
            Jupiter Quote: https://quote-api.jup.ag/v6/quote
        """)
    
    # Log messages
    st.write("**Recent Log Messages:**")
    log_messages = [
        f"[{datetime.now().strftime('%H:%M:%S')}] System initialized",
        f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring {len(selected_tokens) if selected_tokens else len(popular_tokens)} tokens",
        f"[{datetime.now().strftime('%H:%M:%S')}] Detection {'started' if st.session_state.is_running else 'stopped'}",
    ]
    
    for message in log_messages[-10:]:  # Show last 10 messages
        st.text(message)

# Auto-refresh when running
if st.session_state.is_running:
    # Simulate finding arbitrage opportunities
    if st.button("🔄 Refresh Data") or len(st.session_state.arbitrage_results) == 0:
        # Generate sample arbitrage opportunity for demonstration
        sample_opportunity = {
            'path': selected_tokens[:3] if len(selected_tokens) >= 3 else popular_tokens[:3],
            'profit_percentage': np.random.uniform(0.5, 3.0),
            'timestamp': datetime.now(),
            'trade_volume': base_amount,
            'path_length': 3,
            'gas_cost': np.random.uniform(0.001, 0.01)
        }
        
        st.session_state.arbitrage_results.append(sample_opportunity)
        st.session_state.last_update = datetime.now()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚠️ This is a demonstration system for educational purposes only. Not financial advice.</p>
    <p>Built with Streamlit • Powered by Jupiter API</p>
</div>
""", unsafe_allow_html=True)