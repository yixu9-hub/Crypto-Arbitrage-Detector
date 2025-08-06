"""
Enrich gas fee for crypto arbitrage detection.
This module fetches swap transactions and simulates gas fees for arbitrage opportunities.
It enriches the quote responses with gas fee information.
"""
import aiohttp
import json
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api

async def fetch_swap_transaction(quote_response, 
                                 user_pubkey=jupiter_swap_api["user_pubkey"], 
                                 api_key=jupiter_swap_api["api_key"],
                                 swap_url=jupiter_swap_api["base_url"]):
    """
    Fetch the swap transaction from Jupiter API for a given quote response.
    Args:
        quote_response (Dict): The quote response from Jupiter API.
    Returns:
        str: Base64 encoded swap transaction.
    """
    url = swap_url
    headers = jupiter_swap_api["headers"].copy()
    if api_key:
        headers.update({
            "Content-Type": "application/json",
            "x-api-key": api_key
        })
    payload = {
        "userPublicKey": user_pubkey,
        "quoteResponse": quote_response,
        "simulate": True,
        "prioritizationFeeLamports": None,
        "dynamicComputeUnitLimit": True
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as res:
            result = await res.json()
            tx = result.get("swapTransaction", None)
            if not tx:
                raise Exception("Failed to get swapTransaction: " + json.dumps(result, indent=2))
            return tx


async def simulate_gas_fee(
        base64_tx: str, 
        unit_price_lamport: float = solana_rpc_api["unit_price"], 
        base_fee: int = solana_rpc_api["base_fee"],
        solana_rpc: str = solana_rpc_api["base_url"]
        ) -> int:
    """
    Simulate the gas fee for a transaction using Solana RPC.
    Args:
        base64_tx (str): Base64 encoded transaction.
        unit_price_lamport (float): Price per compute unit in lamports.
        base_fee (int): Base fee in lamports.
        solana_rpc (str): Solana RPC URL.
    Returns:
        int: Estimated gas fee in lamports.
    """
    url = solana_rpc
    headers = solana_rpc_api["headers"]
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "simulateTransaction",
        "params": [
            base64_tx,
            {
                "sigVerify": False,
                "replaceRecentBlockhash": True,
                "encoding": "base64"
            }
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=body) as res:
            result = await res.json()

            try:
                units = result["result"]["value"]["unitsConsumed"]
                total_fee = base_fee + units * unit_price_lamport
                return int(total_fee)
            except Exception as e:
                raise Exception(f"Failed to simulate gas fee: {e} | Response: {json.dumps(result, indent=2)}")
