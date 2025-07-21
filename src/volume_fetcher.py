import asyncio
import aiohttp
import pickle
from typing import List, Dict
from collections import defaultdict
from dataclasses import dataclass
from data_structures import TokenInfo
from jupiter_client import JupiterAPIClient

@dataclass
class VolumeRanking:
    address: str
    symbol: str
    volume_24h: float
    liquidity_usd: float
    rank: int

class MassVolumeRanker:
    def __init__(self):
        self.base_url = "https://api.dexscreener.com/tokens/v1/solana"
        self.batch_size = 30 # DexScreener API limit
        self.max_concurrent = 25 # Number of concurrents 
        self.request_delay = 0.05 # Delay between requests
        
    async def get_top_tokens_optimized(self, all_tokens: List[TokenInfo], 
                                     top_n: int = 30) -> List[TokenInfo]:
        """
        Get top N tokens by volume - rank first, enrich only winners
        """
        
        print(f"Phase 1: Ranking ALL {len(all_tokens):,} tokens by volume...")
        
        # Phase 1: Get volume rankings for ALL tokens (minimal data)
        volume_rankings = await self._get_volume_rankings_for_all(all_tokens)
        
        if not volume_rankings:
            print("No volume data found, returning first tokens")
            return all_tokens[:top_n]
        
        print(f"Phase 2: Got volume data for {len(volume_rankings):,} tokens")
        
        # Phase 2: Find top N tokens and create mapping
        jupiter_token_map = {token.address: token for token in all_tokens}
        top_winners = []
        
        for ranking in volume_rankings:
            if ranking.address in jupiter_token_map:
                top_winners.append(ranking)
                if len(top_winners) >= top_n:
                    break
        
        print(f"Phase 3: Found top {len(top_winners)} qualifying tokens")
        
        # Phase 3: Enrich ONLY the top N tokens with detailed data
        print(f"Phase 4: Enriching only the top {len(top_winners)} tokens...")
        enriched_tokens = await self._enrich_winner_tokens(top_winners, jupiter_token_map)
        
        return enriched_tokens
    
    async def _get_volume_rankings_for_all(self, all_tokens: List[TokenInfo]) -> List[VolumeRanking]:
        """Get volume rankings for all tokens - returns sorted rankings"""
        
        # Create batches
        batches = self._create_address_batches(all_tokens)
        print(f"Created {len(batches):,} batches")
        
        # Process all batches to get volume data
        all_volume_data = await self._process_all_batches_for_ranking(batches)
        
        # Convert to rankings and sort
        rankings = self._create_volume_rankings(all_volume_data)
        
        return rankings
    
    def _create_address_batches(self, tokens: List[TokenInfo]) -> List[List[str]]:
        """Create batches of addresses"""
        batches = []
        for i in range(0, len(tokens), self.batch_size):
            batch_tokens = tokens[i:i + self.batch_size]
            addresses = [token.address for token in batch_tokens]
            batches.append(addresses)
        return batches
    
    async def _process_all_batches_for_ranking(self, batches: List[List[str]]) -> Dict[str, Dict]:
        """
        Process all batches concurrently
        """
        
        all_volume_data = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        ) as session:
            
            # Process in chunks to manage memory
            chunk_size = 2000  # 2000 batches at a time
            total_processed = 0
            
            for chunk_start in range(0, len(batches), chunk_size):
                chunk_end = min(chunk_start + chunk_size, len(batches))
                chunk_batches = batches[chunk_start:chunk_end]
                
                # Create tasks for this chunk
                tasks = []
                for i, batch_addresses in enumerate(chunk_batches):
                    task = self._fetch_batch_for_ranking(
                        session, semaphore, batch_addresses, chunk_start + i
                    )
                    tasks.append(task)
                
                # Execute chunk
                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Aggregate results
                for result in chunk_results:
                    if isinstance(result, dict):
                        all_volume_data.update(result)
                
                total_processed += len(chunk_batches)
                print(f"Processed {total_processed:,} batches")
                
                # Brief pause between chunks
                if chunk_end < len(batches):
                    await asyncio.sleep(1)
        
        print(f"Total tokens with volume data: {len(all_volume_data):,}")
        return all_volume_data
    
    async def _fetch_batch_for_ranking(self, session: aiohttp.ClientSession,
                                     semaphore: asyncio.Semaphore,
                                     addresses: List[str],
                                     batch_index: int) -> Dict[str, Dict]:
        """Fetch minimal data needed for ranking"""
        
        async with semaphore:
            try:
                # Stagger requests
                await asyncio.sleep(self.request_delay * (batch_index % 20))
                
                addresses_str = ",".join(addresses)
                url = f"{self.base_url}/{addresses_str}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        
                        # Extract minimal ranking data only
                        return self._extract_ranking_data(data)
                    
                    elif response.status == 429:  # Rate limited
                        await asyncio.sleep(2)
                        return await self._fetch_batch_for_ranking(session, semaphore, addresses, batch_index)
                    
                    else:
                        if batch_index % 1000 == 0:  # Only log occasional errors
                            print(f"Batch {batch_index}: HTTP {response.status}")
                        return {}
                        
            except Exception as e:
                if batch_index % 1000 == 0:  # Only log occasional errors
                    print(f"Batch {batch_index} error: {e}")
                return {}
    
    def _extract_ranking_data(self, pairs: List[Dict]) -> Dict[str, Dict]:
        """Extract only data needed for ranking - minimal processing"""
        
        token_data = defaultdict(lambda: {
            'volume_24h': 0.0,
            'liquidity_usd': 0.0,
            'symbol': ''
        })
        
        for pair in pairs:
            try:
                if pair.get('chainId') != 'solana':
                    continue
                
                # Only extract what we need for ranking
                base_token = pair.get('baseToken', {})
                quote_token = pair.get('quoteToken', {})
                volume_24h = float(pair.get('volume', {}).get('h24', 0))
                liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                
                # Skip very low volume pairs
                if volume_24h < 100:
                    continue
                
                for token_info in [base_token, quote_token]:
                    address = token_info.get('address')
                    if not address:
                        continue
                    
                    # Minimal aggregation
                    token_data[address]['volume_24h'] += volume_24h
                    token_data[address]['liquidity_usd'] = max(
                        token_data[address]['liquidity_usd'], liquidity
                    )
                    
                    if not token_data[address]['symbol']:
                        token_data[address]['symbol'] = token_info.get('symbol', '')
                        
            except Exception:
                continue
        
        return dict(token_data)
    
    def _create_volume_rankings(self, volume_data: Dict[str, Dict]) -> List[VolumeRanking]:
        """
        Create sorted rankings from volume data
        """
        
        rankings = []
        for address, data in volume_data.items():
            if data['volume_24h'] > 0:  # Only include tokens with volume
                ranking = VolumeRanking(
                    address=address,
                    symbol=data['symbol'] or address[:8],
                    volume_24h=data['volume_24h'],
                    liquidity_usd=data['liquidity_usd'],
                    rank=0  # Will be set after sorting
                )
                rankings.append(ranking)
        
        # Sort by volume (descending)
        rankings.sort(key=lambda x: x.volume_24h, reverse=True)
        
        # Set ranks
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
        
        return rankings
    
    async def _enrich_winner_tokens(self, winners: List[VolumeRanking], 
                                   jupiter_token_map: Dict[str, TokenInfo]) -> List[TokenInfo]:
        """
        Enrich only the winning tokens with detailed data
        """
        
        enriched_tokens = []
        
        for winner in winners:
            jupiter_token = jupiter_token_map[winner.address]

            jupiter_token.volume_24h = winner.volume_24h
            jupiter_token.liquidity = winner.liquidity_usd
            jupiter_token.volume_rank = winner.rank
            
            enriched_tokens.append(jupiter_token)
        return enriched_tokens


    def save_tokens(self, enriched_tokens, filename="enriched_tokens.pkl"):
        try:
            with open(filename, "wb") as f:
                pickle.dump(enriched_tokens, f)
                print(f"TokenInfo data saved to {filename}")
        except Exception as e:
            print(f"Error saving tokens: {e}")
    
    def load_tokens(self, filename="enriched_tokens.pkl"):
        try:
            with open(filename, "rb") as f:
                enriched_tokens = pickle.load(f)
                print(f"Loaded {len(enriched_tokens)} tokens from {filename}")
                return enriched_tokens
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return None
        except Exception as e:
            print(f"Error loading tokens: {e}")
            return None
   
    
async def main(top_n_tokens: int = 30) -> Dict:
    """Ultra-optimized pipeline: rank all, enrich only winners"""
    
    # Step 1: Load all Jupiter tokens
    print("Step 1: Loading all Jupiter tokens...")
    jupiter_client = JupiterAPIClient()
    all_tokens = jupiter_client.fetch_token_list()
    print(f"Loaded {len(all_tokens):,} tokens")
    
    # Step 2: Rank ALL tokens, get top N 
    print("Step 2: Getting top volume tokens...")
    volume_ranker = MassVolumeRanker()
    top_tokens = await volume_ranker.get_top_tokens_optimized(
        all_tokens[:1000], 30
    )
    # for winner in top_tokens:
    #     print(f" {winner.volume_rank:2d}. {winner.symbol:10s} - ${winner.volume_24h:>12,.0f}")
        
    volume_ranker.save_tokens(top_tokens)

    # Loading
    loaded_tokens = volume_ranker.load_tokens()
    if loaded_tokens is not None:
        for winner in loaded_tokens:
            print(f" {winner.volume_rank:2d}. {winner.symbol:10s} - ${winner.volume_24h:>12,.0f}")

if __name__ == "__main__":
    tokens = asyncio.run(main())