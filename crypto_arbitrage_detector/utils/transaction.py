"""
# This module provides functionality to execute arbitrage paths using the Jupiter API.
# It includes functions to fetch quotes, execute swaps, and handle transactions on the Solana blockchain
# using the Solders library.
"""
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
from crypto_arbitrage_detector.configs.request_config import jupiter_quote_api, jupiter_swap_api, solana_rpc_api


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
    """
    Fetch quote from Jupiter API for a given token pair.
    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        input_mint (str): The mint address of the input token.
        output_mint (str): The mint address of the output token.
        amount (int): The amount of input token to swap.
    Returns:
        Dict: The quote data from the API.
    """
    # Set headers to mimic a browser request, jupiter API requires
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
    #client = AsyncClient(rpc_url)
    #public_key = Pubkey.from_string(user_public_key)
    #payer_keypair = Keypair.from_bytes(base58.b58decode(user_private_key))
    #async with AsyncClient(rpc_url) as client:
    #await ensure_atas_from_quote(client, public_key, quote, payer_keypair)
    return quote


async def fetch_swap_tx(session, quote_response, user_public_key, swap_url=JUPITER_SWAP_URL):
    """
    Fetch the swap transaction based on the quote response. 
    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        quote_response (Dict): The quote response from the Jupiter API.
        user_public_key (str): The user's public key for the swap.
        swap_url (str): The URL of the Jupiter swap API.
    Returns:
        Dict: The swap transaction data.
    """
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
    Execute the arbitrage path by swapping tokens according to the opportunity.
    Args:
        opportunity (ArbitrageOpportunity): The arbitrage opportunity to execute.
        initial_amount (float): The initial amount of the first token to swap.
        user_public_key (str): The user's public key for the swap.
        user_private_key_base58 (str): The user's private key in base58 format.
        rpc_url (str): The Solana RPC URL to use for the transaction.
    Returns:
        None
    """
    path = opportunity.path
    amount = initial_amount
    solana_client = Client(rpc_url)  # connect to Solana RPC
    #async_client = AsyncClient(rpc_url) # async client for confirmation
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
                    print(f"❌ Error sending transaction: {error_code} → {friendly_message} you may need to have suffuficient balance in your wallet.\n(This issue may also occur if the last transaction was too fast and the updated balance hasn't been reflected on-chain yet.)")
                else:
                    print(f"❌ Error sending transaction: {e}")
                break
            decimals = get_token_decimals(output_token, rpc_url)
            amount = float(quote["outAmount"])/(10 ** decimals)  # Update amount for the next hop


def verify_key_pair(private_key_base58: str, public_key_base58: str) -> bool:
    """ 
    Verify if the provided private key matches the public key.
    Args:
        private_key_base58 (str): The private key in base58 format.
        public_key_base58 (str): The expected public key in base58 format.
    Returns:
        bool: True if the private key matches the public key, False otherwise.
    Raises:
        Exception: If there is an error during verification.
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
    """
    Get the decimals of a token by its mint address.
    Args:
        mint_address (str): The mint address of the token.
        rpc_url (str): The Solana RPC URL to use for the request.
    Returns:
        int: The number of decimals for the token.
    Raises:
        Exception: If there is an error fetching the token supply.
    """
    client = Client(rpc_url)
    pubkey = Pubkey.from_string(mint_address)
    resp = client.get_token_supply(pubkey)
    if resp.value:
        return resp.value.decimals  # Return the decimals of the token
    else:
        raise Exception(f"Failed to get decimals for token {mint_address}")