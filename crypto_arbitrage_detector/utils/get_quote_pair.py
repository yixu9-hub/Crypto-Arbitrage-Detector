import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import aiohttp
from typing import List, Dict
from dataclasses import dataclass, field
from crypto_arbitrage_detector.utils.data_structures import TokenInfo, EdgePairs
from crypto_arbitrage_detector.configs.request_config import jupiter_quote_api, scraper_config, solana_rpc_api
from crypto_arbitrage_detector.utils.simulate_gas_fee import fetch_swap_transaction, simulate_gas_fee
from crypto_arbitrage_detector.utils.enrich_gas_fee import enrich_responses_with_gas_fee

import math

# Function to prepare single request from Jupiter quote API
async def fetch_quote(
        session: aiohttp.ClientSession, 
        input_mint: str, 
        output_mint: str, 
        #semaphore: asyncio.Semaphore, 
        amount: int = jupiter_quote_api["default_tx_amount"]) -> Dict:
    '''
    Fetch quote from Jupiter API for a given token pair.
    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        input_mint (str): The mint address of the input token.
        output_mint (str): The mint address of the output token.
        amount (int): The amount of input token to swap.
    Returns:
        Dict: The quote data from the API.
    '''
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,
        "slippageBps": jupiter_quote_api["default_slippage_bps"]
    }
    # Set headers to mimic a browser request
    headers = jupiter_quote_api["headers"]
    #async with semaphore:
    try:
        async with session.get(
            jupiter_quote_api["base_url"], 
            params=params, 
            headers=headers, 
            #proxy=strategy_config.PROXY_URL, 
            #timeout=15
            #ssl=False
            ) as resp:
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
async def get_edge_pairs(token_list: List[TokenInfo], tx_amount: int = jupiter_quote_api["default_tx_amount"]) -> List[EdgePairs]:
    '''
    Fetch edge pairs from Jupiter API for all token combinations.
    Args:
        token_list (List[TokenInfo]): List of TokenInfo objects.
    Returns:
        List[EdgePairs]: List of EdgePairs objects containing quote data.
    '''
    #semaphore = asyncio.Semaphore(5)
    edge_pairs = []
    # create all requests for each token pair
    async with aiohttp.ClientSession() as session:
        tasks = []
        for token_in in token_list:
            for token_out in token_list:
                if token_in.address != token_out.address:
                    tasks.append(fetch_quote(
                        session, 
                        token_in.address, 
                        token_out.address,
                        #semaphore,
                        tx_amount
                        ))

    # execute all requests concurrently
        responses = await asyncio.gather(*tasks)
        responses = await enrich_responses_with_gas_fee(responses)
    
    # generate a price map in order to calculate the total_fee in SOL
    price_map = generate_price_map_from_responses(responses)

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
                platform_fee_info = data.get("platformFee")
                if isinstance(platform_fee_info, dict):
                    platform_fee = float(platform_fee_info.get("amount", 0))
                else:
                    platform_fee = 0.0

                # Create EdgePairs object
                edge = EdgePairs(
                    from_token=data["inputMint"],
                    to_token=data["outputMint"],
                    out_amount=out_amount,
                    price_ratio=price_ratio,
                    weight=weight,
                    slippage_bps=data.get("slippageBps", 0),
                    platform_fee=platform_fee if platform_fee is not None else 0.0,
                    price_impact_pct=float(data.get("priceImpactPct", 0.0)),
                    total_fee=total_fee_sol,
                    gas_fee=data["gasFee"]  # gas fee in lamports
                )
                edge_pairs.append(edge)
            except Exception as e:
                print(f"Error processing response: {e}")
                continue
    return edge_pairs


# Helper Function to generate a price map from sol to other tokens to count the price of each token in terms of SOL
def generate_price_map_from_responses(responses: List[Dict]) -> Dict[str, float]:
    '''
    Generate a price map from the responses to calculate token prices in SOL.
    Args:
        responses (List[Dict]): List of response data from Jupiter API.
    Returns:
        Dict[str, float]: A dictionary mapping token mint addresses to their price in SOL.
    '''
    sol = jupiter_quote_api['sol_mint']
    price_map = {sol: 1.0}

    for data in responses:
        try:
            in_mint = data["inputMint"]
            out_mint = data["outputMint"]
            in_amt = float(data["inAmount"])
            out_amt = float(data["outAmount"])

            if in_mint == sol and out_amt > 0:
                # 1 SOL = ? other_token
                price = 1 / (out_amt / in_amt)  # other_token/SOL → SOL/other_token
                price_map[out_mint] = price
            elif out_mint == sol and in_amt > 0:

                # 1 token = ? SOL
                price = out_amt / in_amt
                price_map[in_mint] = price
        except (KeyError, ZeroDivisionError, TypeError):
            continue
    return price_map