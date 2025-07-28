import asyncio
from typing import List, Dict
from crypto_arbitrage_detector.utils.simulte_gas_fee import fetch_swap_transaction, simulate_gas_fee
from crypto_arbitrage_detector.configs.request_config import solana_rpc_api, jupiter_swap_api

# main procedure: quote responses → enrich with tx + gas
async def enrich_responses_with_gas_fee(responses: List[Dict]) -> List[Dict]:
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
    for resp in responses:
        tx_tasks.append(fetch_swap_transaction(resp))

    tx_results = await asyncio.gather(*tx_tasks, return_exceptions=True)

    simulate_tasks = []

    for i, tx in enumerate(tx_results):
        resp = responses[i]
        if isinstance(tx, Exception):
            print(f"Fetch tx failed for response {i}: {tx}")
            resp["gasFee"] = solana_rpc_api["fallback_fee"]
        else:
            simulate_tasks.append(safe_simulate_gas_fee(tx))
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
            resp["gasFee"] = solana_rpc_api["fallback_fee"]
        else:
            resp["gasFee"] = fee
        gas_index += 1

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
async def safe_simulate_gas_fee(base64_tx: str, unit_price: float = solana_rpc_api["unit_price"], base_fee: int = solana_rpc_api["base_fee"], fallback_units: int = solana_rpc_api["fallback_units"]) -> int:
    """ 
    Simulate gas fee with a fallback mechanism.
    Args:
        base64_tx (str): The base64 encoded transaction.
        unit_price (float): The price per compute unit in lamports.
        base_fee (int): The base fee in lamports.       
        fallback_units (int): Fallback units to use if simulation fails.
    Returns:
        int: The total gas fee in lamports.
    """
    try:
        if is_too_large(base64_tx):
            return int(base_fee + fallback_units * unit_price)
        return await simulate_gas_fee(base64_tx, unit_price, base_fee)
    except Exception as e:
        print(f"Simulation failed: {e}")
        return int(base_fee + fallback_units * unit_price)