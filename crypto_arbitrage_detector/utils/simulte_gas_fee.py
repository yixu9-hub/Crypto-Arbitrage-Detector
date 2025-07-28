import requests
import json
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api

def fetch_swap_transaction(quote_response, user_pubkey = jupiter_swap_api["user_pubkey"]):
    """    
    Fetch the swap transaction from Jupiter API based on the quote response.
    Args:
        quote_response (dict): The response from the Jupiter quote API containing swap details.
        user_pubkey (str): The public key of the user initiating the swap.
    Returns:
        dict: The swap transaction data.
    Raises:
        Exception: If the swap transaction cannot be fetched or is not present in the response.
    """
    url = jupiter_swap_api["base_url"]
    headers = jupiter_swap_api["headers"]
    payload = {
        "userPublicKey": user_pubkey,
        "quoteResponse": quote_response,
        "prioritizationFeeLamports": None,
        "dynamicComputeUnitLimit": True
    }

    res = requests.post(url, headers=headers, json=payload)
    result = res.json()
    tx = result.get("swapTransaction", None)
    if not tx:
        raise Exception("Failed to get swapTransaction: " + json.dumps(result, indent=2))
    return tx


def simulate_gas_fee(base64_tx: str, unit_price_lamport: float = solana_rpc_api["compute unit price"], base_fee: int = solana_rpc_api["base_fee"]):
    
    """    
    Fetch the swap transaction from Jupiter API based on the quote response.
    Args:
        base64_tx (str): The base64 encoded transaction to simulate.
        unit_price_lamport (float): The price of compute units in lamports.
        base_fee (int): The base fee in lamports.
    Returns:
        int: The total fee in lamports for the simulated transaction.
    Raises:
        Exception: If the simulation fails or the result is not found.
    """
    url = solana_rpc_api["base_url"]
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

    res = requests.post(url, headers=headers, json=body)
    result = res.json()
    
    try:
        units = result["result"]["value"]["unitsConsumed"]
        total_fee = base_fee + units * unit_price_lamport
        return int(total_fee)
    except Exception as e:
        print("Simulation failed or unitsConsumed not found:")
        print(json.dumps(result, indent=2))