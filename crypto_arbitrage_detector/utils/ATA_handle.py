import asyncio
import base58
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.instruction import Instruction as SoldersInstruction, AccountMeta, CompiledInstruction
from solders.message import MessageV0
from solders.rpc.responses import GetLatestBlockhashResp
from solana.rpc.async_api import AsyncClient
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import ASSOCIATED_TOKEN_PROGRAM_ID, get_associated_token_address, create_associated_token_account
from spl.token.instructions import get_associated_token_address, create_associated_token_account
from solana.rpc.commitment import Confirmed
from spl.token.instructions import create_associated_token_account as create_ata_ix_solana





# Token program + ATA program (固定地址)
#TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
#ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")

# 根据 SPL 规则手动生成 ATA 地址
"""
def get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    seeds = [
        b"ata",
        bytes(owner),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint),
    ]
    ata, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    print(f"ATA Address: {ata}")
    return ata
"""
"""
# 构造 CreateAssociatedTokenAccount 的 Compiled Instruction（用 solders）
def create_compiled_ata_instruction(payer: Pubkey, owner: Pubkey, mint: Pubkey):

    # ATA address
    ata = get_associated_token_address(owner, mint)

    # 手动 account_keys 列表，即使 payer 和 owner 相同，也要重复放入
    account_keys = [
        payer,  # 0 - payer
        ata,    # 1 - ATA
        #owner,  # 2 - owner
        mint,   # 3 - mint
        TOKEN_PROGRAM_ID,        # 4
        SYSVAR_RENT_PUBKEY,      # 5
        ASSOCIATED_TOKEN_PROGRAM_ID  # 6
    ]

    # 构造 CompiledInstruction
    compiled_ix = CompiledInstruction(
        program_id_index=5,  # ASSOCIATED_TOKEN_PROGRAM_ID 在 account_keys 中的 index
        accounts=bytes([0, 1, 0, 2, 3, 4]),
        data=b""
    )

    return compiled_ix, account_keys
"""

def tx_ix_to_solders_ix(ix) -> SoldersInstruction:
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
    ata = get_associated_token_address(payer.pubkey(), mint=mint)

    # 检查 ATA 是否存在
    resp = await client.get_account_info(ata)
    print(resp)
    if resp.value is not None:
        return ata
    
    solders_ix: SoldersInstruction = create_associated_token_account(
        payer=payer.pubkey(),
        owner=user_wallet,
        mint=mint
    )
    #compiled_ix, account_keys = create_compiled_ata_instruction(payer.pubkey(), user_wallet, mint)
    # 1. 创建 ATA 指令 (使用 solders 类型)
    #solana_ix = create_ata_ix_solana(payer.pubkey(), user_wallet, mint)
    #solders_ix = tx_ix_to_solders_ix(solana_ix)


    # 构造 Instruction
    #header = MessageHeader(
    #    num_required_signatures=1,
    #    num_readonly_signed_accounts=0,
    #    num_readonly_unsigned_accounts=3
    #)

    # 2. 获取最近的区块哈希
    #blockhash_resp = await client.get_latest_blockhash()
    #recent_blockhash = blockhash_resp.value.blockhash
    blockhash_resp = await client.get_latest_blockhash()
    recent_blockhash = blockhash_resp.value.blockhash

    # 构造 MessageV0
    #msg = MessageV0(
    #    header=header,
    #    account_keys=account_keys,
    #    recent_blockhash=recent_blockhash,
    #    instructions=[compiled_ix],
    #    address_table_lookups=[]
    #)
    # 3. 创建消息
    message = MessageV0.try_compile(
        payer=payer.pubkey(),
        instructions=[solders_ix],
        address_lookup_table_accounts=[],
        recent_blockhash=recent_blockhash
    )


    # 构造交易
    #tx = VersionedTransaction(msg, [payer])
    #print(tx)
    # 4. 创建版本化交易
    transaction = VersionedTransaction(message, [payer])
    
    # 5. 发送交易
    raw_tx = raw_tx = bytes(transaction)
    resp = await client.send_raw_transaction(raw_tx)
    print(resp)
    tx_hash = resp.value
    print(f"交易已发送! 哈希: {tx_hash}")

    # 发送交易
    #send_resp = await client.send_transaction(tx)
    #print(f"✅ Created ATA for mint {mint} → {ata}: https://solscan.io/tx/{send_resp.value}")
    #return ata


async def ensure_atas_from_quote(
    client: AsyncClient,
    user_wallet: Pubkey,
    quote: dict,
    payer: Pubkey = None
):
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
    # 创建测试 Keypair（生产环境请用保存的密钥）
    mint = Pubkey.from_string("BWBHrYqfcjAh5dSiRwzPnY4656cApXVXmkeDmAfwBKQG")
    public_key = "2ZwR1odHjrohqrTma9us4cHfGQcbCkVSnkJZo1MeDPU1"
    private_key = ""
    public_key = Pubkey.from_string(public_key)
    payer_keypair = Keypair.from_bytes(base58.b58decode(private_key))
    # 连接到 mainnet RPC
    client = AsyncClient("https://api.mainnet-beta.solana.com")

    # 创建 ATA，如果不存在的话
    ata = await ensure_single_ata_exists(
        client=client,
        user_wallet=public_key,
        mint=mint,
        payer=payer_keypair,
    )

    print(f"✅ ATA 地址: {ata}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())