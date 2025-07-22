import asyncio
import aiohttp
from typing import List, Dict
from dataclasses import dataclass, field
from data_structures import TokenInfo, EdgePairs
import strategy_config
import math

# quote api
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"

# Function to prepare single request from Jupiter quote API
async def fetch_quote(session: aiohttp.ClientSession, input_mint: str, output_mint: str, amount: int=strategy_config.DEFAULT_TX_AMOUNT) -> Dict:
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,
        "slippageBps": strategy_config.DEFAULT_SLIPPAGE_BPS
    }
    # Set headers to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://jup.ag",
        "Referer": "https://jup.ag/"
    }
    try:
        async with session.get(JUPITER_QUOTE_API, params=params, headers=headers) as resp:
            #print(f"[DEBUG] Request URL: {resp.url}")
            if resp.status == 200:
                quote_data = await resp.json()
                #print(f"[DEBUG] Response Data: {quote_data}")
                return quote_data
            else:
                print(f"Non-200 response: {resp.status} | {input_mint} {output_mint}")
                return {}
        
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return {}

# Function to request data from Jupiter API for edge pairs
async def get_edge_pairs(token_list: List[TokenInfo]) -> List[EdgePairs]:
    edge_pairs = []
    # create all requests for each token pair
    async with aiohttp.ClientSession() as session:
        tasks = []
        for token_in in token_list:
            for token_out in token_list:
                if token_in.address != token_out.address:
                    tasks.append(fetch_quote(session, token_in.address, token_out.address))

    # execute all requests concurrently
        responses = await asyncio.gather(*tasks)
    
    # generate a price map in order to calculate the total_fee in SOL
    price_map =generate_price_map_from_responses(responses)

    # process the responses and create EdgePairs
    for data in responses:
        if "outAmount" in data:
            try:
                out_amount = float(data["outAmount"])
                in_amount = float(data["inAmount"])
                price_ratio = out_amount / in_amount
                weight = -math.log(price_ratio)

                # Calculate total fee in SOL
                total_fee_sol = 0.0
                for route in data.get("routePlan", []):
                    # route can be empty, so we need to check it
                    if not route:
                        continue
                    # swap_info can be empty, so we need to check it
                    swap_info = route.get("swapInfo", {})
                    if not swap_info:
                        continue
                    fee_str = swap_info.get("feeAmount")
                    fee_mint = swap_info.get("feeMint")
                    if fee_str and fee_mint:
                        fee = float(fee_str)
                        price_in_sol = price_map.get(fee_mint, 0.0)
                        total_fee_sol += fee * price_in_sol
                
                # Handle platform fee if return null
                platform_fee_info = data.get("platformFee"),
                if isinstance(platform_fee_info, dict):
                    platform_fee = float(platform_fee_info.get("amount", 0))
                else:
                    platform_fee = 0.0
                # Create EdgePairs object
                edge = EdgePairs(
                    from_token=data["inputMint"],
                    to_token=data["outputMint"],
                    price_ratio=price_ratio,
                    weight=weight,
                    slippage_bps=data.get("slippageBps", 0),
                    platform_fee=platform_fee if platform_fee is not None else 0.0,
                    price_impact_pct=data.get("priceImpactPct", 0.0),
                    total_fee=total_fee_sol
                )
                edge_pairs.append(edge)
            except Exception as e:
                print(f"Error processing response: {e}")
                continue
    return edge_pairs


# Helper Function to generate a price map from sol to other tokens to count the price of each token in terms of SOL
def generate_price_map_from_responses(responses: List[Dict]) -> Dict[str, float]:
    price_map = {strategy_config.SOL_MINT: 1.0}

    for data in responses:
        try:
            in_mint = data["inputMint"]
            out_mint = data["outputMint"]
            in_amt = float(data["inAmount"])
            out_amt = float(data["outAmount"])

            if in_mint == strategy_config.SOL_MINT and out_amt > 0:
                # 1 SOL = ? other_token
                price = 1 / (out_amt / in_amt)  # other_token/SOL → SOL/other_token
                price_map[out_mint] = price
            elif out_mint == strategy_config.SOL_MINT and in_amt > 0:
                # 1 token = ? SOL
                price = out_amt / in_amt
                price_map[in_mint] = price
        except (KeyError, ZeroDivisionError, TypeError):
            continue

    return price_map