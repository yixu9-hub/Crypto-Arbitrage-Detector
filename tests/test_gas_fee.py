"""
# Test script: Enrich Jupiter swap responses with gas fee
# This script tests the functionality of enriching Jupiter swap responses with gas fee
# by fetching swap transactions and simulating gas fees.
# It uses asyncio for concurrent requests.
"""

import sys
import os
import json
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_arbitrage_detector.utils.enrich_gas_fee import enrich_responses_with_gas_fee

async def main():
    responses = [
        {
            "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
            "inAmount": "10",
            "outputMint": "So11111111111111111111111111111111111111112",
            "outAmount": "51",
            "otherAmountThreshold": "51",
            "swapMode": "ExactIn",
            "slippageBps": 50,
            "platformFee": None,
            "priceImpactPct": "0.01558",
            "routePlan": [
                {
                    "swapInfo": {
                        "ammKey": "4uWuh9fC7rrZKrN8ZdJf69MN1e2S7FPpMqcsyY1aof6K",
                        "label": "GoonFi",
                        "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                        "outputMint": "So11111111111111111111111111111111111111112",
                        "inAmount": "10",
                        "outAmount": "51",
                        "feeAmount": "0",
                        "feeMint": "11111111111111111111111111111111"
                    },
                    "percent": 100,
                    "bps": 10000
                }
            ]
        }
    ]

    enriched = await enrich_responses_with_gas_fee(responses)
    print(json.dumps(enriched, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
