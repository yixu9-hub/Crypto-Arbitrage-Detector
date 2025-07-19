import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import List
print("importing modules...")
from utils.get_quote_pair import get_edge_pairs  # core function to fetch edge pairs
from tests.mock_quote_pair import test_tokens   # mock data for testing
from data_structures import EdgePairs

async def test_edge_pairs() -> List[EdgePairs]:
    print("🔁 Running quote test using test_tokens...\n")
    
    # 调用主函数获取所有 token 对之间的边
    edges: List[EdgePairs] = await get_edge_pairs(test_tokens)

    print(f"✅ Total edge pairs returned: {len(edges)}\n")
    
    for i, edge in enumerate(edges):
        print(f"--- Pair {i + 1} ---")
        print(f"From: {edge.from_token}")
        print(f"To:   {edge.to_token}")
        print(f"Price Ratio:     {edge.price_ratio:.6f}")
        print(f"Weight (-log):   {edge.weight:.6f}")
        print(f"Slippage BPS:    {edge.slippage_bps}")
        print(f"Price Impact %:  {edge.priceImpactPct:.4f}")
        print(f"Platform Fee:    {edge.platformFee}")
        print(f"Total Fee (SOL): {edge.total_fee:.8f}")
        print()

    return edges

async def main():
    print("开始获取边信息...")
    edge_list = await get_edge_pairs(test_tokens)
    print(f"共获取到 {len(edge_list)} 条边")
    for edge in edge_list:
        print(edge)

if __name__ == "__main__":
    asyncio.run(main())