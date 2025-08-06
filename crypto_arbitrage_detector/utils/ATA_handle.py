"""
This module provides utilities for handling Associated Token Accounts (ATA) on the Solana blockchain.
It includes functions to ensure that an ATA exists for a given user and mint, and to create the ATA if it does not.
It's currently discarded because the functionality is handled inherently in transaction.py
"""
import asyncio
import base58
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.instruction import Instruction as SoldersInstruction, AccountMeta
from solders.message import MessageV0
from solana.rpc.async_api import AsyncClient
from spl.token.instructions import get_associated_token_address, create_associated_token_account


# Token program + ATA program constants
#TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
#ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")


def tx_ix_to_solders_ix(ix) -> SoldersInstruction:
    """
    Convert a Solana instruction to a SoldersInstruction.
    This is useful for creating transactions with the Solders library.
    :param ix: The Solana instruction to convert.
    :return: A SoldersInstruction object.
    """
    return SoldersInstruction(
        program_id=Pubkey.from_string(str(ix.program_id)),
        accounts=[
            AccountMeta(pubkey=Pubkey.from_string(str(acc.pubkey)), is_signer=acc.is_signer, is_writable=acc.is_writable)
            for acc in ix.keys
        ],
        data=bytes(ix.data)
    )

async def ensure_single_ata_exists(
    client: AsyncClient,
    user_wallet: Pubkey,
    mint: Pubkey,
    payer: Keypair 
):
    """
    Ensure that an Associated Token Account (ATA) exists for the given user wallet and mint.
    If it does not exist, create it using the payer's account.
    :param client: The Solana AsyncClient instance.
    :param user_wallet: The user's wallet address.
    :param mint: The mint address of the token.
    :param payer: The payer's Keypair. If None, user_wallet is used as the payer.
    :return: The address of the ATA.
    """
    ata = get_associated_token_address(payer.pubkey(), mint=mint)

    # check if the ATA already exists
    resp = await client.get_account_info(ata)
    print(resp)
    if resp.value is not None:
        return ata
    
    solders_ix: SoldersInstruction = create_associated_token_account(
        payer=payer.pubkey(),
        owner=user_wallet,
        mint=mint
    )
    # Convert the instruction to SoldersInstruction
    blockhash_resp = await client.get_latest_blockhash()
    recent_blockhash = blockhash_resp.value.blockhash

    # Create the message with the instruction
    message = MessageV0.try_compile(
        payer=payer.pubkey(),
        instructions=[solders_ix],
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash
    )


    # Create the transaction
    transaction = VersionedTransaction(message, [payer])
    
    # Sign the transaction
    raw_tx = raw_tx = bytes(transaction)
    resp = await client.send_raw_transaction(raw_tx)
    print(resp)
    tx_hash = resp.value
    print(f"transaction is sent, hash: {tx_hash}")


async def ensure_atas_from_quote(
    client: AsyncClient,
    user_wallet: Pubkey,
    quote: dict,
    payer: Pubkey = None
):
    """
    Ensure that all Associated Token Accounts (ATAs) for the tokens in the quote exist.
    If they do not exist, create them using the payer's account.
    :param user_wallet: The user's wallet address.
    :param quote: The quote data containing the token mints.
    :param payer: The payer's Keypair. If None, user_wallet is used as the payer.
    :return: A list of ATA addresses for the tokens in the quote.
    """
    if payer is None:
        payer = user_wallet

    # Collect all unique mints
    all_mints = set()
    for hop in quote["routePlan"]:
        all_mints.add(hop["swapInfo"]["inputMint"])
        all_mints.add(hop["swapInfo"]["outputMint"])

    mint_pubkeys = [Pubkey.from_string(mint) for mint in all_mints]

    # Create tasks to ensure each ATA
    tasks = [
        ensure_single_ata_exists(client, user_wallet, mint, payer)
        for mint in mint_pubkeys
    ]
    results = await asyncio.gather(*tasks)
    return results  # list of ATA addresses



async def main():
    """
    Example usage of ensure_single_ata_exists.
    This function creates an Associated Token Account (ATA) for a given mint and user wallet.
    It connects to the Solana mainnet RPC and uses a test Keypair for the payer.
    """
    # Replace with your mint address and user wallet
    mint = Pubkey.from_string("BWBHrYqfcjAh5dSiRwzPnY4656cApXVXmkeDmAfwBKQG")
    public_key = "2ZwR1odHjrohqrTma9us4cHfGQcbCkVSnkJZo1MeDPU1"
    private_key = "" # Replace with your private key in base58 format
    public_key = Pubkey.from_string(public_key)
    payer_keypair = Keypair.from_bytes(base58.b58decode(private_key))
    # Connect to mainnet RPC
    client = AsyncClient("https://api.mainnet-beta.solana.com")

    # Create ATA if it does not exist
    ata = await ensure_single_ata_exists(
        client=client,
        user_wallet=public_key,
        mint=mint,
        payer=payer_keypair,
    )

    print(f"✅ ATA address: {ata}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())