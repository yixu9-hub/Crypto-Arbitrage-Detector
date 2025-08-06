"""
Enrich gas fee for crypto arbitrage detection.
This module fetches swap transactions and simulates gas fees for arbitrage opportunities.
It enriches the quote responses with gas fee information.
"""
import asyncio
import base64
from typing import List, Dict
from crypto_arbitrage_detector.utils.simulate_gas_fee import fetch_swap_transaction, simulate_gas_fee
from crypto_arbitrage_detector.configs.request_config import solana_rpc_api, jupiter_swap_api

# main procedure: quote responses → enrich with tx + gas
async def enrich_responses_with_gas_fee(
        responses: List[Dict], 
        api_key: str = jupiter_swap_api["api_key"], 
        swap_url: str = jupiter_swap_api["base_url"],
        solana_rpc: str = solana_rpc_api["base_url"]
        ) -> List[Dict]:
    """
    Enrich quote responses with gas fee by fetching swap transactions and simulating gas.
    Args:
        responses (List[Dict]): List of quote responses from Jupiter API.
    Returns:
        List[Dict]: Enriched responses with gas fee included.
    """
    tx_tasks = []
    enriched = []

    # Concurrently build swapTransaction
    for resp in responses[:jupiter_swap_api["max_request"]]:
        tx_tasks.append(fetch_swap_transaction(resp, user_pubkey=jupiter_swap_api["user_pubkey"], api_key=api_key, swap_url=swap_url))

    tx_results = await asyncio.gather(*tx_tasks, return_exceptions=True)

    simulate_tasks = []

    for i, tx in enumerate(tx_results):
        resp = responses[i]
        if isinstance(tx, Exception):
            print(f"Fetch tx failed for response {i}: {tx}")
            resp["gasFee"] = estimate_gas_fee_by_route(resp)
        else:
            simulate_tasks.append(safe_simulate_gas_fee(tx, solana_rpc))
            enriched.append({"response": resp, "tx": tx})

    # Concurrently simulate gas
    gas_fees = await asyncio.gather(*simulate_tasks, return_exceptions=True)

    # Write back gasFee
    gas_index = 0
    for item in enriched:
        resp = item["response"]
        fee = gas_fees[gas_index]
        if isinstance(fee, Exception):
            print(f"Simulation failed for tx: {fee}")
            resp["gasFee"] = estimate_gas_fee_by_complexity(item["tx"])
        else:
            resp["gasFee"] = fee
        gas_index += 1
    
    for resp in responses[jupiter_swap_api["max_request"]:]:
        resp["gasFee"] = estimate_gas_fee_by_route(resp)

    return responses


# Helper functions for checking if the base64 transaction is too large
def is_too_large(base64_tx: str, max_base64_size: int = 1644) -> bool:
    """
    Check if the base64 transaction exceeds the maximum size.
    Args:
        base64_tx (str): The base64 encoded transaction.
        max_base64_size (int): The maximum allowed size for the base64 transaction.
    Returns:
        bool: True if the transaction is too large, False otherwise.
    """
    return len(base64_tx.encode()) > max_base64_size


# Helper functions for safe simulation + fallback
async def safe_simulate_gas_fee(
        base64_tx: str, 
        solana_rpc: str = solana_rpc_api["base_url"],
        unit_price: float = solana_rpc_api["unit_price"], 
        base_fee: int = solana_rpc_api["base_fee"]) -> int:
    """ 
    Simulate gas fee with a fallback mechanism.
    Args:
        base64_tx (str): The base64 encoded transaction.
        solana_rpc (str): The Solana RPC API URL.
        unit_price (float): The price per compute unit in lamports.
        base_fee (int): The base fee in lamports.       
    Returns:
        int: The total gas fee in lamports.
    """
    try:
        if is_too_large(base64_tx):
            return estimate_gas_fee_by_complexity(base64_tx)
        try:
            # Simulate gas fee using the Solana RPC API
            gas = await simulate_gas_fee(base64_tx, unit_price, base_fee, solana_rpc)
            return gas
        except Exception as e:
            print(f"Simulation failed: {e}")
            return estimate_gas_fee_by_complexity(base64_tx)
    except Exception as e:
        print(f"Simulation failed: {e}")
        return estimate_gas_fee_by_complexity(base64_tx)



def estimate_gas_fee_by_complexity(base64_tx: str):
    """
    Estimate gas fee based on transaction complexity when URL fetch fails.
    
    Args:
        base64_tx (str): The base64 encoded transaction to analyze.
    
    Returns:
        int: Estimated total gas fee in lamports.
    """
    try:
        # Decode the transaction to analyze its complexity
        tx_bytes = base64.b64decode(base64_tx)
        base_fee = solana_rpc_api["base_fee"]

        tx_size = len(tx_bytes)
        
        if tx_size < 500:
            estimated_units = 2000
        elif tx_size < 1000:
            estimated_units = 15000
        elif tx_size < 1500:
            estimated_units = 35000
        else:
            estimated_units = 50000
        
        unit_price = solana_rpc_api["unit_price"]
        compute_fee = int(estimated_units * unit_price)
        total_fee = base_fee + compute_fee

        return total_fee
        
    except Exception as e:
        base_fee = solana_rpc_api["base_fee"]
        conservative_estimate = base_fee + 2000
        return conservative_estimate


def estimate_gas_fee_by_route(response):
    """
    Estimate gas fee based on the number of hops in the route.
    
    Args:
        response (dict): The response from the Jupiter API containing route details.
    
    Returns:
        int: Estimated gas fee in lamports.
    """
    route_hops = len(response["routePlan"])
    return 5000 + 500 * max(0, route_hops - 1)  # Base fee + variable based on hops