import requests
import json
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api, solana_rpc_api

def fetch_swap_transaction(quote_response, user_pubkey = jupiter_swap_api["user_pubkey"]):
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

# 用你的base64交易和用户地址
tx = "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAEEjNmKiZGiOtSZ+g0//wH5kEQo3+UzictY+KlLV8hjXcs44M/Xnr+1SlZsqS6cFMQc46yj9PIsxqkycxJmXT+veJjIvefX4nhY9rY+B5qreeqTHu4mG6Xtxr5udn4MN8PnBt324e51j94YQl285GzN2rYa/E2DuQ0n/r35KNihi/zamQ6EeyeeVDvPVgUO2W3Lgt9hT+CfyqHvIa11egFPCgEDAwIBAAkDZAAAAAAAAAA="
simulate_gas_fee(tx)
