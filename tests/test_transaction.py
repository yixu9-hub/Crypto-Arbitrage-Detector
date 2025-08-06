"""
Crypto Arbitrage Detector - Test Transaction Module
This module tests the transaction execution functionality of the Crypto Arbitrage Detector.
It includes a test for executing an arbitrage path using the Jupiter API.
"""
import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_arbitrage_detector.utils.data_structures import ArbitrageOpportunity
from crypto_arbitrage_detector.utils.transaction import execute_path
from crypto_arbitrage_detector.configs.request_config import jupiter_swap_api  # 🧠 Make sure this is defined or mocked

# Replace this with your actual base58 private key string
TEST_PRIVATE_KEY = ""

async def test_execute_arbitrage_path():
    """
    Test the execution of an arbitrage path.
    This function creates a mock arbitrage opportunity and executes it.
    """
    opportunity = ArbitrageOpportunity(
        path=[
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS',
            'So11111111111111111111111111111111111111112',
            '31k88G5Mq7ptbRDf3AM13HAq6wRQHXHikR8hik7wPygk',
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
        ],
        path_symbols=[
            'EPjF...Dt1v',
            'KMNo...',
            'So11...',
            '31k8...Pygk',
            'EPjF...Dt1v'
        ],
        profit_ratio=0.027916626158513314,
        total_weight=-0.027534060785305847,
        total_fee=0.0,
        hop_count=4,
        confidence_score=0.27916626158513314,
        estimated_profit_sol=0.027916626158513314
    )

    initial_amount = 0.0001
    user_pubkey = jupiter_swap_api["user_pubkey"]
    user_privkey = TEST_PRIVATE_KEY

    print("🚀 Executing arbitrage opportunity test...")
    await execute_path(opportunity, initial_amount, user_pubkey, user_privkey)

if __name__ == "__main__":
    asyncio.run(test_execute_arbitrage_path())
