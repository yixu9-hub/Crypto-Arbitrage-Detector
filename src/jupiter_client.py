import aiohttp
import asyncio
import time
from typing import List, Dict, Optional
from data_structures import *


class JupiterAPIClient:
    def __init__(self):
        self.session = None
        self.token_cache = {}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_token_list(self) -> List[TokenInfo]:
        """Fetch all available tokens from Jupiter"""
        try:
            async with self.session.get('https://cache.jup.ag/tokens') as response:
                if response.status == 200:
                    data = await response.json()
                    tokens = []
                    # print(len(data))
                    for token_data in data:
                        try:
                            token = TokenInfo(
                                address=token_data['address'],
                                symbol=token_data['symbol'],
                                name=token_data['name'],
                                decimals=token_data['decimals'],
                                logoURI=token_data.get('logoURI',''),
                                tags=token_data.get('tags', [])
                            )
                            tokens.append(token)
                        except KeyError as e:
                            print(f"Missing required field in token data: {e}")
                            continue
                    return tokens
                else:
                    print(f"Error fetching tokens: HTTP {response.status}")
                    return []
        except Exception as e:
            print(f"Error in fetch_token_list: {e}")
            return []

async def main():
    async with JupiterAPIClient() as client:
        tokens = await client.fetch_token_list()
        print(f"Total tokens: {len(tokens)}")
        for i, token in enumerate(tokens[:5]):
            print(f"{i+1}. {token.symbol} ({token.name}) - {token.address}")

if __name__ == '__main__':
    asyncio.run(main())