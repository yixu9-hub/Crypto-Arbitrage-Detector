import asyncio
import aiohttp
from typing import List, Dict
from data_structures import TokenInfo
from jupiter_client import JupiterAPIClient
class VolumeFetcher:
    def __init__(self):
        self.session = None
        self.dexscreener_url = "https://api.dexscreener.com/latest/dex/tokens"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def enrich_tokens_with_volume(self, tokens: List[TokenInfo]) -> List[TokenInfo]:
        """Enrich tokens with volume data from DexScreener"""
        batch_size = 30  # DexScreener API limit
        enriched_tokens = []
        
        for i in range(0, len(tokens), batch_size):
            batch = tokens[i:i + batch_size]
            addresses = [token.address for token in batch]
            
            # Fetch volume data for this batch
            volume_data = await self._fetch_volume_batch(addresses)
            
            # Enrich tokens with volume data
            for token in batch:
                if token.address in volume_data:
                    vol_info = volume_data[token.address]
                    token.volume_24h = vol_info.get('volume_24h', 0)
                    token.liquidity = vol_info.get('liquidity', 0)
                    token.price_usd = vol_info.get('price_usd', 0)
                    token.market_cap = vol_info.get('market_cap', 0)
                    token.price_change_24h = vol_info.get('price_change_24h', 0)
                
                enriched_tokens.append(token)
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        return enriched_tokens
    
    async def _fetch_volume_batch(self, addresses: List[str]) -> Dict[str, Dict]:
        """Fetch volume data for a batch of addresses"""
        if not addresses:
            return {}
        
        addresses_str = ",".join(addresses)
        url = f"{self.dexscreener_url}/{addresses_str}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_dexscreener_response(data)
                else:
                    print(f"DexScreener API error: {response.status}")
                    return {}
        except Exception as e:
            print(f"Error fetching volume data: {e}")
            return {}
    
    def _process_dexscreener_response(self, data: Dict) -> Dict[str, Dict]:
        """Process DexScreener API response"""
        volume_data = {}
        
        pairs = data.get('pairs', [])
        for pair in pairs:
            try:
                # Process both base and quote tokens
                base_token = pair.get('baseToken', {})
                quote_token = pair.get('quoteToken', {})
                
                for token_info in [base_token, quote_token]:
                    if 'address' not in token_info:
                        continue
                    
                    address = token_info['address']
                    volume_data[address] = {
                        'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                        'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                        'price_usd': float(pair.get('priceUsd', 0)),
                        'market_cap': float(pair.get('marketCap', 0)),
                        'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0))
                    }
            except (KeyError, ValueError, TypeError):
                continue
        
        return volume_data

async def main():
    async with VolumeFetcher() as fetcher:
        async with JupiterAPIClient() as client:
            tokens = await client.fetch_token_list()
        tokens = await fetcher.enrich_tokens_with_volume(tokens)
        print(f"Total tokens: {len(tokens)}")
        for i, token in enumerate(tokens[:5]):
            print(f"{i+1}. {token.symbol} ({token.name}) - {token.address} {token.volumn}")

if __name__ == '__main__':
    asyncio.run(main())