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
import subprocess
import sys
import os
from src.token_loader import TokenLoader

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
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="Cryptocurrency Arbitrage Detector",
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

# Function to check if token file exists and is fresh
def check_token_file():
    """Check if both Jupiter tokens and enriched tokens files exist and are fresh"""
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
    """Run the Jupiter token download script"""
    try:
        # Run the download_tokens.py script
        result = subprocess.run([
            sys.executable, "scripts/download_tokens.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return True, "Jupiter tokens successfully downloaded"
        else:
            return False, f"Error downloading Jupiter tokens: {result.stderr}"
    except Exception as e:
        return False, f"Error running Jupiter token downloader: {str(e)}"

# Function to fetch enriched tokens from Jupiter
def fetch_enriched_tokens():
    """Run the volume fetcher script to get enriched tokens"""
    try:
        # Run the volume_fetcher.py script
        result = subprocess.run([
            sys.executable, "src/volume_fetcher.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return True, "Enriched tokens successfully fetched from Jupiter and DexScreener"
        else:
            return False, f"Error fetching enriched tokens: {result.stderr}"
    except Exception as e:
        return False, f"Error running volume fetcher: {str(e)}"

# Function to load popular tokens from token_loader
def load_popular_tokens():
    """Load popular tokens from the token loader"""
    try:
        token_loader = TokenLoader()
        loaded_tokens = token_loader.load_tokens()
        
        if loaded_tokens and len(loaded_tokens) > 0:
            # Extract top tokens by volume rank
            top_tokens = sorted(loaded_tokens, key=lambda x: getattr(x, 'volume_rank', 999))[:30]
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
        st.error(f"Error loading tokens: {e}")
        # Fallback to default tokens
        return [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
        ]

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
            if st.button("🔄 Refresh Jupiter Tokens", type="primary"):
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
            if st.button("📊 Refresh Volume Data", type="primary"):
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

# Show success message if tokens were just loaded
if st.session_state.tokens_loaded:
    st.markdown("""
    <div class="success-message">
        <h3>✅ Token Data Loaded</h3>
        <p>Fresh token data has been successfully loaded from Jupiter. The application is ready to use!</p>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.tokens_loaded = False  # Reset flag

# Load popular tokens from token_loader
popular_tokens = load_popular_tokens()

# Initialize selected_tokens in session state if not exists
if 'selected_tokens' not in st.session_state:
    st.session_state.selected_tokens = popular_tokens[:4] if len(popular_tokens) >= 4 else popular_tokens


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

trade_amount = st.sidebar.selectbox(
    "Trade Amount (SOL)",
    options=[0.1, 1.0, 5.0, 10.0, 50.0],
    index=2
)

max_path_length = st.sidebar.slider(
    "Maximum Path Length", 
    min_value=2, 
    max_value=6, 
    value=4
)

# Token selection
st.sidebar.subheader("Token Selection")


selected_tokens = st.sidebar.multiselect(
    "Select tokens to monitor (leave empty for all popular tokens)",
    options=popular_tokens,
    default=popular_tokens[:4]
)

# Control buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    start_detection = st.button("▶️ Start", type="primary")
with col2:
    stop_detection = st.button("⏹️ Stop")

if start_detection:
    st.session_state.is_running = True
if stop_detection:
    st.session_state.is_running = False

# Status indicator
status_color = "status-running" if st.session_state.is_running else "status-stopped"
status_text = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
st.sidebar.markdown(f'<p class="{status_color}">Status: {status_text}</p>', unsafe_allow_html=True)

if st.session_state.last_update:
    st.sidebar.write(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard",  "🔍 Arbitrage Opportunities", "📈 Price Graph","⚙️ System Logs"])

with tab1:
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        opportunities_found = len(st.session_state.arbitrage_results)
        st.metric("Opportunities Found", opportunities_found)
    
    with col2:
        if st.session_state.arbitrage_results:
            max_profit = max([result['profit_percentage'] for result in st.session_state.arbitrage_results])
            st.metric("Max Profit Found", f"{max_profit:.2f}%")
        else:
            st.metric("Max Profit Found", "0.00%")
    
    with col3:
        avg_path_length = 0
        if st.session_state.arbitrage_results:
            avg_path_length = np.mean([len(result['path']) for result in st.session_state.arbitrage_results])
        st.metric("Avg Path Length", f"{avg_path_length:.1f}")
    
    with col4:
        tokens_monitored = len(st.session_state.selected_tokens) if st.session_state.selected_tokens else len(popular_tokens)
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
            with st.expander(f"Opportunity #{i+1} - {opportunity['profit_percentage']:.2f}% Profit"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Trading Path:**")
                    path_str = " → ".join([f"Token_{token[:8]}..." for token in opportunity['path']])
                    st.code(path_str)
                    
                    st.write("**Path Details:**")
                    for j, (from_token, to_token) in enumerate(zip(opportunity['path'], opportunity['path'][1:] + [opportunity['path'][0]])):
                        st.write(f"Step {j+1}: {from_token[:8]}... → {to_token[:8]}...")
                
                with col2:
                    st.metric("Expected Profit", f"{opportunity['profit_percentage']:.2f}%")
                    st.metric("Path Length", len(opportunity['path']))
                    st.metric("Est. Gas Cost", f"{opportunity.get('gas_cost', 0.001):.4f} SOL")
                    
                    if opportunity['profit_percentage'] > 0:
                        st.success("✅ Profitable")
                    else:
                        st.error("❌ Not Profitable")
    else:
        st.info("No arbitrage opportunities detected. Start the detection system to find opportunities.")


with tab3:
    st.subheader("📈 Token Price Graph Network")
    
    # Create a sample network graph for visualization
    if st.session_state.selected_tokens or popular_tokens:
        tokens_to_show = st.session_state.selected_tokens if st.session_state.selected_tokens else popular_tokens[:6]
        
        # Create networkx graph
        G = nx.Graph()
        
        # Add nodes
        for token in tokens_to_show:
            G.add_node(f"Token_{token[:8]}...")
        
        # Add edges (sample connections)
        import random
        random.seed(42)
        nodes = list(G.nodes())
        for i in range(len(nodes)):
            for j in range(i+1, min(i+3, len(nodes))):
                weight = random.uniform(0.95, 1.05)
                G.add_edge(nodes[i], nodes[j], weight=weight)
        
        # Get positions
        pos = nx.spring_layout(G)
        
        # Create plotly graph
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(x=edge_x, y=edge_y,
                              line=dict(width=2, color='#888'),
                              hoverinfo='none',
                              mode='lines')
        
        node_x = []
        node_y = []
        node_text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
        
        node_trace = go.Scatter(x=node_x, y=node_y,
                              mode='markers+text',
                              hoverinfo='text',
                              text=node_text,
                              textposition="middle center",
                              marker=dict(size=30,
                                        color='lightblue',
                                        line=dict(width=2, color='black')))
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                            title=dict(
                                text='Token Swap Network Graph',
                                font=dict(size=16)
                            ),

                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Nodes represent tokens, edges represent possible swaps",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor="left", yanchor="bottom",
                               font=dict(size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        
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
            "Trade Amount": f"{trade_amount} SOL"
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
            f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring {len(st.session_state.selected_tokens) if st.session_state.selected_tokens else len(popular_tokens)} tokens",
            f"[{datetime.now().strftime('%H:%M:%S')}] Detection {'started' if st.session_state.is_running else 'stopped'}",
        ]
    
    for message in log_messages[-10:]:  # Show last 10 messages
        st.text(message)

# Auto-refresh when running
if st.session_state.is_running:
    # Simulate finding arbitrage opportunities
    if st.button("🔄 Refresh Data") or len(st.session_state.arbitrage_results) == 0:
        ## TODO: Replace with actual arbitrage opportunity detection
        sample_opportunity = {
            'path': st.session_state.selected_tokens[:3] if len(st.session_state.selected_tokens) >= 3 else popular_tokens[:3],
            'profit_percentage': np.random.uniform(0.5, 3.0),
            'timestamp': datetime.now(),
            'trade_volume': trade_amount,
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