import aiohttp
import asyncio
import base64
from solders.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"
RPC_URL = "https://api.mainnet-beta.solana.com"  # 可改为 devnet

async def fetch_quote(session, input_mint, output_mint, amount):
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,
        "slippageBps": 50,
    }
    async with session.get(JUPITER_QUOTE_URL, params=params) as resp:
        return await resp.json()

async def fetch_swap_tx(session, quote_response, user_public_key):
    payload = {
        "userPublicKey": user_public_key,
        "quoteResponse": quote_response
    }
    headers = {"Content-Type": "application/json"}
    async with session.post(JUPITER_SWAP_URL, json=payload, headers=headers) as resp:
        return await resp.json()

async def execute_path(path, initial_amount, user_public_key, user_private_key):
    async with aiohttp.ClientSession() as session:
        amount = initial_amount
        for i in range(len(path) - 1):
            input_token = path[i]
            output_token = path[i + 1]
            print(f"🔄 Swapping {input_token} → {output_token}")

            quote = await fetch_quote(session, input_token, output_token, amount)
            if "routePlan" not in quote:
                print("❌ Quote failed")
                return

            swap_tx = await fetch_swap_tx(session, quote, user_public_key)
            tx_base64 = swap_tx.get("swapTransaction")
            if not tx_base64:
                print("❌ Failed to fetch swap tx")
                return

            # Sign and send
            client = AsyncClient(RPC_URL)
            tx_bytes = base64.b64decode(tx_base64)
            from solana.transaction import VersionedTransaction
            tx = VersionedTransaction.deserialize(tx_bytes)
            keypair = Keypair.from_base58_string(user_private_key)
            tx.sign([keypair])
            sig = await client.send_transaction(tx, opts=TxOpts(skip_preflight=True, preflight_commitment=Confirmed))
            print(f"✅ Sent Tx: https://solscan.io/tx/{sig['result']}")
            await client.close()

            # Update amount (use quote["outAmount"])
            amount = int(quote["outAmount"])

# Example usage
if __name__ == "__main__":
    path = [
        "So11111111111111111111111111111111111111112",  # SOL
        "Es9vMFrzaCERbXyP1gmV8dQJoKkzqgdcG7gkhbrFbNfk",  # USDT
        "7XS3bDaLL7ejvTuGyy1zXJ9ij3WHwZVvmCSKTFeKaq9n"   # BONK
    ]
    initial_amount = 10000000  # 0.01 SOL in lamports
    user_pubkey = "你的钱包地址"
    user_privkey = "你的 base58 私钥"

    asyncio.run(execute_path(path, initial_amount, user_pubkey, user_privkey))
