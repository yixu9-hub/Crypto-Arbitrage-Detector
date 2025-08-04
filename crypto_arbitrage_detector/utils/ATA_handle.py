import asyncio
import base58
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.instruction import Instruction, AccountMeta, CompiledInstruction
from solders.message import MessageV0, MessageHeader, to_bytes_versioned
from solders.rpc.responses import GetLatestBlockhashResp
from solana.rpc.async_api import AsyncClient


# Token program + ATA program (固定地址)
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1L3cPA8Fzw6R8jzBaxV6zTx4v3J2")


# 根据 SPL 规则手动生成 ATA 地址
def get_associated_token_address(owner: Pubkey, mint: Pubkey) -> Pubkey:
    seeds = [
        bytes(owner),
        bytes(TOKEN_PROGRAM_ID),
        bytes(mint),
    ]
    ata_pubkey, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
    return ata_pubkey


# 构造 CreateAssociatedTokenAccount 的 Compiled Instruction（用 solders）
def create_compiled_ata_instruction(payer: Pubkey, owner: Pubkey, mint: Pubkey):
    SYSVAR_RENT_PUBKEY = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
    ata = get_associated_token_address(owner, mint)

    # 明确 account_keys 顺序（一定要和下方 CompiledInstruction 的索引对应）
    account_keys = [
        payer,        # index 0
        ata,          # index 1
        owner,        # index 2
        mint,         # index 3
        TOKEN_PROGRAM_ID,       # index 4
        SYSVAR_RENT_PUBKEY,     # index 5
        ASSOCIATED_TOKEN_PROGRAM_ID # index 6
    ]

    # 构造 CompiledInstruction，program_id_index 是 program_id 在 account_keys 中的索引
    compiled_ix = CompiledInstruction(
        program_id_index=account_keys.index(ASSOCIATED_TOKEN_PROGRAM_ID),
        accounts=bytes([0, 1, 2, 3, 4, 5, 6]),  # 每个 account 在 account_keys 中的索引
        data=b""
    )

    return compiled_ix, account_keys


async def ensure_single_ata_exists(
    client: AsyncClient,
    user_wallet: Pubkey,
    mint: Pubkey,
    payer: Keypair 
):
    ata = get_associated_token_address(owner=user_wallet, mint=mint)

    # 检查 ATA 是否存在
    resp = await client.get_account_info(ata)
    if resp.value is not None:
        return ata

    # 构造 Instruction
    compiled_ix, account_keys = create_compiled_ata_instruction(payer.pubkey(), user_wallet, mint)

    # 构造 MessageV0 + Transaction
    header = MessageHeader(num_required_signatures=1, num_readonly_signed_accounts=0, num_readonly_unsigned_accounts=3)
    blockhash_resp: GetLatestBlockhashResp = await client.get_latest_blockhash()
    recent_blockhash: Hash = blockhash_resp.value.blockhash

    msg = MessageV0(
        header=header,
        account_keys=account_keys,  # 顺序很重要！
        recent_blockhash=recent_blockhash,
        instructions=[compiled_ix],
        address_table_lookups=[]  # 目前空
    )

    assert isinstance(header, MessageHeader)
    assert isinstance(account_keys, list) and all(isinstance(k, Pubkey) for k in account_keys)
    assert isinstance(recent_blockhash, Hash)
    assert isinstance(compiled_ix, CompiledInstruction)
    assert isinstance(msg, MessageV0)
    # 手动签名
    serialized_msg = to_bytes_versioned(msg)
    signature = payer.sign_message(serialized_msg)

    # 构造交易
    tx = VersionedTransaction(msg, [payer])

    # 发送交易
    send_resp = await client.send_transaction(tx)
    print(f"✅ Created ATA for mint {mint} → {ata}: https://solscan.io/tx/{send_resp.value}")
    return ata


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
    USDC_MINT_DEVNET = Pubkey.from_string("BXXkv6zRCZZ7eXP2G6mRa2yRxvGGnfsfY7F7dBzvLNsZ")
    public_key = "2ZwR1odHjrohqrTma9us4cHfGQcbCkVSnkJZo1MeDPU1"
    private_key = ""
    public_key = Pubkey.from_string(public_key)
    payer_keypair = Keypair.from_bytes(base58.b58decode(private_key))
    # 连接到 devnet
    client = AsyncClient("https://api.devnet.solana.com")

    # 创建 ATA，如果不存在的话
    ata = await ensure_single_ata_exists(
        client=client,
        user_wallet=public_key,
        mint=USDC_MINT_DEVNET,
        payer=payer_keypair,
    )

    print(f"✅ ATA 地址: {ata}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())