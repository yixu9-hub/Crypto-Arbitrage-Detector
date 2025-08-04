from typing import List
import aiohttp
import asyncio
import base64
import base58
import sys, os
import re
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.message import to_bytes_versioned
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import ArbitrageOpportunity, IntegratedArbitrageDetector
from crypto_arbitrage_detector.configs.request_config import jupiter_quote_api, jupiter_swap_api, solana_rpc_api
from crypto_arbitrage_detector.utils.ATA_handle import ensure_atas_from_quote


JUPITER_QUOTE_URL = jupiter_quote_api["base_url"]
JUPITER_SWAP_URL = jupiter_swap_api["base_url"]
RPC_URL = solana_rpc_api["base_url"]
API_KEY = jupiter_quote_api["api_key"]
HEADER = jupiter_quote_api["headers"]
USER_PUBKEY = jupiter_swap_api["user_pubkey"]

async def fetch_quote(session, input_mint, output_mint, amount, quote_url=JUPITER_QUOTE_URL, api_key=API_KEY, rpc_url=RPC_URL, user_public_key=USER_PUBKEY, user_private_key=None):
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount
    }

    headers = HEADER.copy()
    if api_key:
        headers.update({
            'Content-Type': 'application/json',
            "x-api-key": api_key
        })
    
    # Create Solana client to check ATA existence
    async with session.get(quote_url, params=params, headers=headers) as resp:
        quote = await resp.json()

    # Ensure ATAs exist for all mints in the quote
    client = AsyncClient(rpc_url)
    public_key = Pubkey.from_string(user_public_key)
    payer_keypair = Keypair.from_bytes(base58.b58decode(user_private_key))
    #async with AsyncClient(rpc_url) as client:
    #    await ensure_atas_from_quote(client, public_key, quote, payer_keypair)
    return quote


async def fetch_swap_tx(session, quote_response, user_public_key, swap_url=JUPITER_SWAP_URL):
    payload = {
        "userPublicKey": user_public_key,
        "quoteResponse": quote_response,
        "wrapUnwrapSOL": True # Wrap/unwrap SOL if needed
    }
    headers = {"Content-Type": "application/json"}
    async with session.post(swap_url, json=payload, headers=headers) as resp:
        return await resp.json()


async def execute_path(opportunity, initial_amount, user_public_key, user_private_key_base58, rpc_url=RPC_URL):
    """
    Execute a swap path using the Jupiter API.
    :param path: List of token mints in the swap path.
    :param initial_amount: Initial amount of the first token in the path.
    :param user_public_key: User's public key for the swap.
    :param user_private_key_base58: User's private key in base58 format.
    """
    path = opportunity.path
    amount = initial_amount
    solana_client = Client(rpc_url)  # connect to Solana RPC
    keypair = Keypair.from_bytes(base58.b58decode(user_private_key_base58))

    async with aiohttp.ClientSession() as session:
        for i in range(len(path) - 1):
            input_token = path[i]
            output_token = path[i + 1]
            print(f"🔄 Swapping {input_token} → {output_token}")

            # Fetch token info from the Solana client
            decimals = get_token_decimals(input_token, rpc_url)
            actual_amount = int(amount * (10 ** decimals))  # Convert to smallest unit

            # Fetch quote for the current token pair
            quote = await fetch_quote(session, input_token, output_token, actual_amount, user_private_key=user_private_key_base58)
            if "routePlan" not in quote:
                print("❌ Failed to fetch Quote, user wallet may not have an associated token account (ATA) or amount too small.")
                return
            # Fetch the swap transaction based on the quote
            swap_tx = await fetch_swap_tx(session, quote, user_public_key)
            tx_base64 = swap_tx.get("swapTransaction")
            if not tx_base64:
                print(f"❌ Failed to fetch swap tx, Amount {amount} is too small for {input_token}.")
                return

            # Sign and send the transaction
            raw_tx = VersionedTransaction.from_bytes(base64.b64decode(tx_base64))
            sig = keypair.sign_message(to_bytes_versioned(raw_tx.message))
            signed_tx = VersionedTransaction.populate(raw_tx.message, [sig])
            try:
                tx_sig = solana_client.send_raw_transaction(bytes(signed_tx))
                tx_sig = tx_sig.value
                print(f"✅ Tx sent: https://solscan.io/tx/{tx_sig}")
            except Exception as e:
                error_str = str(e)
                match = re.search(r"custom program error: (0x[0-9a-fA-F]+)", error_str)
                if match:
                    error_code = match.group(1)
                    friendly_message = {
                        "0x1": "Instruction missing or invalid",
                        "0x2": "Account missing or invalid",
                        "0x3": "Not enough account keys",
                        "0x4": "Transaction too large",
                        "0x5": "Insufficient funds",
                        "0x6": "Input amount too small or invalid",  # Jupiter or AMM pools specific
                        "0x1771": "Slippage tolerant exceeded",  # Jupiter specific
                        "0x1788": "Not enough account keys",
                        "0x177E": "Incorrect Token Program ID",
                        "0x1781": "Exact out amount not matched",
                        "0x1789": "Do not have ATA"
                    }.get(error_code, "Unknown custom error")
                    print(f"❌ Error sending transaction: {error_code} → {friendly_message}")
                else:
                    print(f"❌ Error sending transaction: {e}")
                break
            decimals = get_token_decimals(output_token, rpc_url)
            amount = float(quote["outAmount"])/(10 ** decimals)  # Update amount for the next hop


def verify_key_pair(private_key_base58: str, public_key_base58: str) -> bool:
    """ 
    Verifies if the provided private key matches the public key.
    :param private_key_base58: Base58 encoded private key.
    :param public_key_base58: Base58 encoded public key.
    :return: True if the keys match, False otherwise.
    """
    try:
        secret_bytes = base58.b58decode(private_key_base58)
        kp = Keypair.from_bytes(secret_bytes)
        expected_pubkey = Pubkey.from_string(public_key_base58)
        generated_pubkey = kp.pubkey()
        match = generated_pubkey == expected_pubkey
        print(f"✅ Match: {match}")
        if not match:
            print(f"🔍 Expected: {expected_pubkey}, Got: {generated_pubkey}")
        return match
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def get_token_decimals(mint_address: str, rpc_url) -> int:
    client = Client(rpc_url)
    pubkey = Pubkey.from_string(mint_address)
    resp = client.get_token_supply(pubkey)
    if resp.value:
        return resp.value.decimals  # Return the decimals of the token
    else:
        raise Exception(f"Failed to get decimals for token {mint_address}")


if __name__ == "__main__":
    opportunity = ArbitrageOpportunity(path=['EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS', 'So11111111111111111111111111111111111111112', '31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk', 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'], path_symbols=['EPjF...Dt1v', '31k8...Pygk', 'EPjF...Dt1v'], profit_ratio=0.027916626158513314, total_weight=-0.027534060785305847, total_fee=0.0, hop_count=2, confidence_score=0.27916626158513314, estimated_profit_sol=0.027916626158513314)
    initial_amount = 0.00001  # Initial amount
    user_pubkey = jupiter_swap_api["user_pubkey"]
    user_privkey = ""  # 🧠 替换成你实际的 base58 私钥

    asyncio.run(execute_path(opportunity, initial_amount, user_pubkey, user_privkey))
