import requests
import json
import base64
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api

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
        
        unit_price = solana_rpc_api["compute unit price"]
        compute_fee = int(estimated_units * unit_price)
        total_fee = base_fee + compute_fee

        return total_fee
        
    except Exception as e:
        base_fee = solana_rpc_api["base_fee"]
        conservative_estimate = base_fee + 20000
        return conservative_estimate

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
        if "error" in result:
            print(f"RPC error: {result['error']}, using complexity estimation")
            return estimate_gas_fee_by_complexity(base64_tx)
        
        value = result["result"]["value"]
        units = value.get("unitsConsumed", 0)
        err = value.get("err", None)
        
        if err is not None:
            # Handle account not found or other errors
            if err == "AccountNotFound":
                print(f"AccountNotFound error, using complexity estimation")
            else:
                print(f"Simulation error {err}, using complexity estimation")
            return estimate_gas_fee_by_complexity(base64_tx)
        
        if units == 0:
            # Zero compute units, possibly simulation issue, use complexity estimation
            print(f"Zero compute units consumed, using complexity estimation")
            return estimate_gas_fee_by_complexity(base64_tx)
        
        # Normal case: valid compute units consumption
        total_fee = base_fee + int(units * unit_price_lamport)
        print(f"Gas fee simulation successful: {total_fee} lamports (base: {base_fee}, units: {units})")
        return total_fee
        
    except Exception as e:
        print(f"RPC simulation failed: {e}, using complexity estimation")
        return estimate_gas_fee_by_complexity(base64_tx)