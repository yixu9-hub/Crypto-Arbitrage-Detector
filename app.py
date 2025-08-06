"""
This is the main file for Solana Arbitrage Detector.
It is used to create the UI and the logic for the arbitrage detector.
"""
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
import hashlib

from crypto_arbitrage_detector.utils.frontend_utils import check_token_file, fetch_jupiter_tokens, fetch_enriched_tokens, load_popular_tokens, retrive_edges,visualize_graph_streamlit
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.utils.data_structures import ArbitrageOpportunity
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector
from data.historical_data import new_arbitrage_test_data
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
if 'edges' not in st.session_state:
    st.session_state.edges = None
if 'graph' not in st.session_state:
    st.session_state.graph = None
if 'detection_run' not in st.session_state:
    st.session_state.detection_run = False
if 'detection_message' not in st.session_state:
    st.session_state.detection_message = None


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

# Display detection message if available
if st.session_state.detection_message:
    st.success(st.session_state.detection_message)
    # Clear the message after displaying it
    st.session_state.detection_message = None

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Detection parameters
st.sidebar.subheader("🔍 Detection Parameters")
min_profit_threshold = st.sidebar.slider(
    "Minimum Profit Threshold (%)", 
    min_value=0.1, 
    max_value=5.0, 
    value=0.5, 
    step=0.1
) / 100

max_slippage = st.sidebar.slider(
    "Maximum Slippage (%)", 
    min_value=0.1, 
    max_value=2.0, 
    value=0.5, 
    step=0.1
) / 100

base_amount = st.sidebar.number_input(
    "Base Amount (SOL)",
    min_value=0.01,
    value=5.0,
    step=0.1,
    format="%.2f"
)

max_hops = st.sidebar.slider(
    "Maximum Path Length", 
    min_value=2, 
    max_value=6, 
    value=4
)

# Data Source Selection
st.sidebar.subheader("📊 Data Source")
data_source = st.sidebar.selectbox(
    "Choose data source for arbitrage detection",
    options=[
        "🎯 Historical Token Data",
        "🆓 Free API (Limited, May Fail)",
        "💎 Premium API (Jupiter Membership Required)"
    ],
    help="Select your preferred data source for testing arbitrage opportunities"
)

# Token selection (disabled for Historical Token Data)
if data_source == "🎯 Historical Token Data":
    st.sidebar.info("📊 Using predefined historical token data")
else:
    st.sidebar.info("📊 Using top 10 popular tokens data")

# API Configuration for Premium
api_key = None
quote_url = None
swap_url = None

if data_source == "💎 Premium API (Jupiter Membership Required)":
    st.sidebar.subheader("🔑 Premium API Configuration")
    
    # Info about Jupiter membership
    st.sidebar.info("""
    **Jupiter Premium Membership Required**
    
    Get unlimited API access at: [portal.jup.ag/onboard](https://portal.jup.ag/onboard)
    
    After purchasing membership, you'll receive:
    - API Key
    - Quote URL
    - Swap URL
    """)
    
    api_key = st.sidebar.text_input(
        "API Key",
        type="password",
        help="Enter your Jupiter API key"
    )
    
    quote_url = st.sidebar.text_input(
        "Quote URL",
        value="https://quote-api.jup.ag/v6/quote",
        help="Jupiter quote API endpoint"
    )
    
    swap_url = st.sidebar.text_input(
        "Swap URL", 
        value="https://quote-api.jup.ag/v6/swap",
        help="Jupiter swap API endpoint"
    )


# Algorithm selection
st.sidebar.subheader("🧮 Algorithm Selection")
selected_algorithms = st.sidebar.multiselect(
    "Select algorithms to use (leave empty for all)",
    options=["bellman_ford", "triangle", "two_hop", "exhaustive_DFS"],
    default=["bellman_ford", "triangle", "two_hop", "exhaustive_DFS"]
)
enable_bellman_ford = "bellman_ford" in selected_algorithms
enable_triangle = "triangle" in selected_algorithms
enable_two_hop = "two_hop" in selected_algorithms
enable_exhaustive_DFS = "exhaustive_DFS" in selected_algorithms

# Risk evaluation configuration
st.sidebar.subheader("⚠️ Risk Evaluation")
enable_risk_evaluation = st.sidebar.checkbox(
    "Enable Risk Evaluation",
    value=True,
    help="Evaluate risk factors including slippage, liquidity, and market volatility"
)

# Initialize detector hash tracking
if 'detector_hash' not in st.session_state:
    st.session_state.detector_hash = None

# Create hash of detector parameters
detector_params = f"{min_profit_threshold}_{max_hops}_{base_amount}_{enable_risk_evaluation}"
current_detector_hash = hashlib.md5(detector_params.encode()).hexdigest()

# Initialize or refresh detector only when parameters change
if (st.session_state.detector is None or 
    st.session_state.detector_hash != current_detector_hash):
    st.session_state.detector = IntegratedArbitrageDetector(
        min_profit_threshold, 
        max_hops, 
        base_amount,
        enable_risk_evaluation
    )
    st.session_state.detector_hash = current_detector_hash

detector = st.session_state.detector

# Add refresh buttons based on data source
if data_source == "🆓 Free API (Limited, May Fail)":
    if st.sidebar.button("🔄 Refresh Free API Data"):
        st.session_state.edges = None
        st.session_state.graph = None
        st.rerun()
elif data_source == "💎 Premium API (Jupiter Membership Required)":
    if st.sidebar.button("🔄 Refresh Premium API Data"):
        st.session_state.edges = None
        st.session_state.graph = None
        st.rerun()

# Clear edges when data source changes
if 'current_data_source' not in st.session_state:
    st.session_state.current_data_source = None

if st.session_state.current_data_source != data_source:
    st.session_state.edges = None
    st.session_state.graph = None
    st.session_state.arbitrage_results = []
    st.session_state.detection_run = False
    st.session_state.detection_message = None
    st.session_state.current_data_source = data_source

# Control buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("▶️ Start", type="primary"):
        # Load edges based on selected data source
        with st.spinner("Loading data and building graph..."):
            from crypto_arbitrage_detector.utils.data_structures import EdgePairs
            
            if data_source == "🎯 Historical Token Data":
                st.session_state.edges = new_arbitrage_test_data
                st.success(f"✅ Loaded {len(new_arbitrage_test_data)} historical edges")
                
            elif data_source == "🆓 Free API (Limited, May Fail)":
                st.warning("🆓 Using free Jupiter API - may have rate limits and potential failures")
                try:
                    edges = asyncio.run(retrive_edges())
                    st.session_state.edges = edges
                except Exception as e:
                    st.error(f"❌ Failed to fetch real-time data: {str(e)}")
                    st.info("💡 Try using 'Historical Token Data' for testing or upgrade to Premium API")
                    st.session_state.edges = []
                    st.rerun()
                    
            elif data_source == "💎 Premium API (Jupiter Membership Required)":
                if not api_key:
                    st.error("❌ API Key required for Premium API access")
                    st.info("💡 Please enter your Jupiter API key or switch to another data source")
                    st.stop()
                else:
                    st.success("💎 Using Premium Jupiter API with unlimited access")
                    try:
                        edges = asyncio.run(retrive_edges(api_key=api_key,
                            quote_url=quote_url,
                            swap_url=swap_url))
                        st.session_state.edges = edges
                        st.success(f"✅ Premium data loaded successfully - {len(edges) if edges else 0} edges")
                    except Exception as e:
                        st.error(f"❌ Failed to fetch premium data: {str(e)}")
                        st.info("💡 Please check your API key and endpoints")
                        st.stop()
            
            # Build graph from edges
            if st.session_state.edges and len(st.session_state.edges) > 0:
                st.session_state.graph = build_graph_from_edge_lists(st.session_state.edges)
            else:
                st.error("❌ No edges available to build graph. Please check your data source selection.")
                st.session_state.graph = None
                st.stop()
        
        # Run detection if graph is available
        if st.session_state.graph is not None:
            with st.spinner("Running arbitrage detection..."):
                results = st.session_state.detector.detect_arbitrage(st.session_state.graph, None, enable_bellman_ford, enable_triangle, enable_two_hop)
                st.session_state.arbitrage_results = results
                st.session_state.last_update = datetime.now()
                st.session_state.detection_run = True
                st.session_state.detection_message = f"✅ Detection complete! Found {len(results)} opportunities"
                st.rerun()  # Rerun to update the UI with the new graph
with col2:
    stop_detection = st.button("⏹️ Stop")   

# Status indicator
status_color = "status-running" if st.session_state.is_running else "status-stopped"
status_text = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
st.sidebar.markdown(f'<p class="{status_color}">Status: {status_text}</p>', unsafe_allow_html=True)

if st.session_state.last_update:
    st.sidebar.write(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")

st.sidebar.write(f"**Current Data Source:** {data_source}")
if st.session_state.edges:
    st.sidebar.write(f"**Edges Loaded:** {len(st.session_state.edges)}")
else:
    st.sidebar.write("**Edges Loaded:** None")
st.sidebar.write(f"**Risk Evaluation:** {'✅ Enabled' if enable_risk_evaluation else '❌ Disabled'}")

# Main content area
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Arbitrage Opportunities", "📈 Price Graph", "⚙️ System Logs"])

with tab1:
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        opportunities_found = 0
        if st.session_state.arbitrage_results:
            for result in st.session_state.arbitrage_results:
                if result.estimated_profit_sol > 0:
                    opportunities_found += 1
        st.metric("Opportunities Found", opportunities_found)
    
    with col2:
        if st.session_state.arbitrage_results:
            max_profit = max([result.estimated_profit_sol for result in st.session_state.arbitrage_results])
            st.metric("Max Profit Found", f"{max_profit:.4f} SOL")
        else:
            st.metric("Max Profit Found", "0.0000 SOL")
    
    with col3:
        avg_path_length = 0
        if st.session_state.arbitrage_results:
            avg_path_length = np.mean([len(result.path) for result in st.session_state.arbitrage_results])
        st.metric("Avg Path Length", f"{avg_path_length:.1f}")
    
    with col4:
        # tokens_monitored = len(selected_tokens)
        tokens_monitored=10
        st.metric("Tokens Monitored", tokens_monitored)
    
    # Real-time chart placeholder
    st.subheader("📈 Real-time Arbitrage Opportunities")
    
    # Create sample data for demonstration
    if st.session_state.arbitrage_results:
        # Convert ArbitrageOpportunity objects to DataFrame
        data = []
        for i, opp in enumerate(st.session_state.arbitrage_results):
            data.append({
                'index': i,
                'profit_ratio': opp.profit_ratio * 100,  # Convert to percentage
                'estimated_profit_sol': opp.estimated_profit_sol,
                'hop_count': opp.hop_count,
                'confidence_score': opp.confidence_score
            })
        
        df = pd.DataFrame(data)
        fig = px.scatter(df, x='index', y='profit_ratio', 
                        size='estimated_profit_sol', color='hop_count',
                        title="Arbitrage Opportunities Over Time",
                        labels={'profit_ratio': 'Profit %', 'index': 'Opportunity Index'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start detection to see real-time arbitrage opportunities")

with tab2:
    st.subheader("🔍 Current Arbitrage Opportunities")
    
    if st.session_state.arbitrage_results:
        for i, opportunity in enumerate(st.session_state.arbitrage_results):
            profit = opportunity.estimated_profit_sol
            path = opportunity.path
            path_symbols = opportunity.path_symbols
            total_fee = opportunity.total_fee

            with st.expander(f"Opportunity #{i+1} - {profit:.4f} SOL Profit"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Trading Path:**")
                    if path_symbols:
                        path_str = " → ".join([f"{token}" for token in path_symbols])
                        st.code(path_str)
                    else:
                        st.code("No path available")
                    
                    st.write("**Path Details:**")
                    if len(path) > 1:
                        for j, (from_token, to_token) in enumerate(zip(path, path[1:] + [path[0]])):
                            st.write(f"Token {j+1}: {from_token}")
                    else:
                        st.write("No valid path found")
                
                with col2:
                    st.metric("Expected Profit", f"{profit:.4f} SOL")
                    st.metric("Path Length", len(path) - 1)
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
    if st.session_state.graph is not None and st.session_state.graph.number_of_nodes() > 0:
        # Create Plotly network graph from the built graph
        G = st.session_state.graph
        fig = visualize_graph_streamlit(G)
        st.plotly_chart(fig, use_container_width=True)
    else:
        if not st.session_state.edges:
            st.warning("⚠️ No edges loaded. Please check your data source selection.")
        elif G is None:
            st.error("❌ Graph could not be built from edges. Please try a different data source.")
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
        # f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring {len(selected_tokens) if selected_tokens else len(popular_tokens)} tokens",
        f"[{datetime.now().strftime('%H:%M:%S')}] Detection {'started' if st.session_state.is_running else 'stopped'}",
    ]
    
    for message in log_messages[-10:]:  # Show last 10 messages
        st.text(message)

# Auto-refresh when running
if st.session_state.is_running:
    # Simulate finding arbitrage opportunities
    if st.button("🔄 Refresh Data"):
        results = st.session_state.detector.detect_arbitrage(st.session_state.graph, None, enable_bellman_ford, enable_triangle, enable_two_hop )
        st.session_state.arbitrage_results = results
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