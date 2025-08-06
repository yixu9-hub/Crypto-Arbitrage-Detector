"""
Test script: Fetch edge pairs using pickle file
This script tests the functionality of fetching edge pairs between all token pairs
using a pickle file containing enriched token information.
"""
import asyncio
import pickle
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import List
print("importing modules...")
from crypto_arbitrage_detector.utils.get_quote_pair import get_edge_pairs  # core function to fetch edge pairs
from mock_quote_pair import test_tokens   # mock data for testing
from crypto_arbitrage_detector.utils.data_structures import EdgePairs, TokenInfo

async def test_edge_pairs() -> List[EdgePairs]:
    """
    Test fetching edge pairs using a pickle file.
    Returns a list of EdgePairs.
    """
    print("🔁 Running quote test using pickle file...\n")
    
    current_file_path = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    pkl_path = os.path.join(project_root, "data", "enriched_tokens.pkl")
    # Load tokens from pickle file
    with open(pkl_path, "rb") as f:
        TokenLists: List[TokenInfo] = pickle.load(f)
    print(f" Loaded {len(TokenLists)} tokens from pickle file\n")
    
    edges: List[EdgePairs] = await get_edge_pairs(TokenLists)

    print(f" Total edge pairs returned: {len(edges)}\n")
    
    for i, edge in enumerate(edges):
        print(f"--- Pair {i + 1} ---")
        print(f"From: {edge.from_token}")
        print(f"To:   {edge.to_token}")
        print(f"From Symbol: {edge.from_symbol}")
        print(f"To Symbol:   {edge.to_symbol}")
        print(f"In Amount:      {edge.in_amount:.6f}")
        print(f"Out Amount:     {edge.out_amount:.6f}")
        print(f"Price Ratio:     {edge.price_ratio:.6f}")
        print(f"Weight (-log):   {edge.weight:.6f}")
        print(f"Slippage BPS:    {edge.slippage_bps}")
        print(f"Price Impact %:  {edge.price_impact_pct:.4f}")
        print(f"Platform Fee:    {edge.platform_fee:.1f}")
        print(f"Total Fee (SOL): {edge.total_fee:.1f}")
        print(f"Gas Fee (lamports): {edge.gas_fee}\n")

    return edges

async def main():
    print("🔁 Fetching edge information...")
    edge_list = await test_edge_pairs()
    print(f"Total edge pairs fetched: {len(edge_list)}")
    for edge in edge_list:
        print(edge)

if __name__ == "__main__":
    asyncio.run(main())