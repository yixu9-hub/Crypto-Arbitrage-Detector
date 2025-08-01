import os
import sys
import subprocess
from datetime import datetime, timedelta
import pickle
from typing import List
from crypto_arbitrage_detector.utils.data_structures import EdgePairs, TokenInfo
from crypto_arbitrage_detector.utils.get_quote_pair import get_edge_pairs
from crypto_arbitrage_detector.scripts.token_loader import TokenLoader
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.utils.graph_utils import analyze_graph

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
    """Run the volume fetcher script to get enriched tokens"""
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
        # Fallback to default tokens
        return [
            "So11111111111111111111111111111111111111112",  # WSOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
            "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",   # mSOL
        ]

# Function to retrieve edges from the test data
async def retrive_edges():
    """Retrieve edges from the test data."""
    try:
        # 读取真实数据用于测试
        with open("data/enriched_tokens.pkl", "rb") as f:
            TokenLists: List[TokenInfo] = pickle.load(f)
        print(f"✅ Loaded {len(TokenLists)} tokens from pickle file\n")
        
        if not TokenLists or len(TokenLists) == 0:
            print("❌ No tokens loaded from pickle file")
            return []
        
        # Limit to first 3 tokens for testing to avoid API rate limits
        test_tokens = TokenLists[:3]
        print(f"🔧 Using first {len(test_tokens)} tokens for testing (to avoid API rate limits)")
        
        edge_pairs: List[EdgePairs] = await get_edge_pairs(test_tokens)
        print(f"✅ Generated {len(edge_pairs)} edge pairs")
        
        if len(edge_pairs) == 0:
            print("❌ No edge pairs generated - likely due to API rate limits or errors")
            return []
            
        return edge_pairs
        
    except FileNotFoundError:
        print("❌ enriched_tokens.pkl file not found")
        return []
    except Exception as e:
        print(f"❌ Error in retrive_edges: {str(e)}")
        return []
