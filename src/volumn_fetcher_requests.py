# modules/volume_fetcher_optimized.py
import requests
from typing import List, Dict, Tuple
from collections import defaultdict
from data_structures import TokenInfo
from jupiter_client import JupiterAPIClient

class TrulyOptimizedVolumeFetcher:
    def __init__(self):
        self.min_volume = 50000
        self.min_liquidity = 100000
        
    def get_top_volume_tokens(self, all_tokens: List[TokenInfo], 
                             limit: int = 30) -> List[TokenInfo]:
        """TRUE optimization: rank first, enrich only winners"""
        
        print("Step 1: Getting volume rankings...")
        
        # Step 1: Get ONLY volume rankings (minimal data)
        volume_rankings = self._get_volume_rankings_only()
        
        if not volume_rankings:
            print("No volume data, returning first 30 tokens")
            return all_tokens[:limit]
        
        print(f"Step 2: Got rankings for {len(volume_rankings)} tokens")
        
        # Step 2: Create Jupiter token lookup
        jupiter_lookup = {token.address: token for token in all_tokens}
        
        # Step 3: Find top N tokens that exist in our Jupiter list
        winners = []
        
        for token_address, basic_volume_info in volume_rankings:
            if token_address in jupiter_lookup:
                # Check basic thresholds before adding to winners
                if (basic_volume_info['volume_24h'] >= self.min_volume and 
                    basic_volume_info['liquidity_usd'] >= self.min_liquidity):
                    winners.append((token_address, basic_volume_info))
                
                # Stop when we have enough winners
                if len(winners) >= limit:
                    break
        
        print(f"Step 3: Found {len(winners)} winning tokens")
        
        # Step 4: NOW enrich only the winning tokens
        print("Step 4: Enriching only winners with detailed data...")
        enriched_tokens = []
        
        for i, (token_address, basic_info) in enumerate(winners):
            jupiter_token = jupiter_lookup[token_address]
            
            # Apply detailed info to token
            jupiter_token.creation_date = basic_info['pairCreatedAt']
            jupiter_token.volume_24h = basic_info['volume_24h']
            jupiter_token.liquidity = basic_info['liquidity_usd']
            
            enriched_tokens.append(jupiter_token)
            
            print(f"   {i+1:2d}. {jupiter_token.symbol:8s} - ${jupiter_token.volume_24h:>12,.0f}")
        
        return enriched_tokens
    
    def _get_volume_rankings_only(self) -> List[Tuple[str, Dict]]:
        """Get ONLY basic volume rankings - no detailed enrichment"""
        
        try:
            # Fetch raw pairs data
            all_pairs = self._fetch_pairs_data()
            
            # Create minimal volume aggregation (just for ranking)
            token_basic_info = defaultdict(lambda: {
                'creation_date': 0,
                'volume_24h': 0.0,
                'liquidity_usd': 0.0,
                'symbol': ''
            })
            
            # Minimal processing - only what we need for ranking
            for pair in all_pairs:
                try:
                    base_token = pair.get('baseToken', {})
                    quote_token = pair.get('quoteToken', {})
                    
                    volume_24h = float(pair.get('volume', {}).get('h24', 0))
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                    creation_date = int(pair.get('pairCreatedAt'),{})
                    
                    # Only process if significant volume
                    if volume_24h < 1000:  # Skip tiny pairs
                        continue
                    
                    for token_info in [base_token, quote_token]:
                        address = token_info.get('address')
                        if not address:
                            continue
                        
                        # Minimal aggregation
                        token_basic_info[address]['creation_date'] = min (
                            pair.get('pairCreatedAt'),creation_date
                        )
                        token_basic_info[address]['volume_24h'] += volume_24h
                        token_basic_info[address]['liquidity_usd'] = max(
                            token_basic_info[address]['liquidity_usd'], liquidity
                        )
                        if not token_basic_info[address]['symbol']:
                            token_basic_info[address]['symbol'] = token_info.get('symbol', '')
                            
                except Exception:
                    continue
            
            # Sort by volume and return as list
            sorted_rankings = sorted(
                token_basic_info.items(),
                key=lambda x: x[1]['volume_24h'],
                reverse=True
            )
            
            print(f"Top 10 by volume:")
            for i, (addr, info) in enumerate(sorted_rankings[:10]):
                print(f"   {i+1:2d}. {info['symbol']:8s} - ${info['volume_24h']:>12,.0f}")
            
            return sorted_rankings
            
        except Exception as e:
            print(f"Error getting rankings: {e}")
            return []
    
    
    def _fetch_pairs_data(self, all_tokens: List[TokenInfo]) -> List[Dict]:
        """Fetch pairs data efficiently"""
        try:
            # Get trending pairs (most efficient single call)
            # Use USDC as a base token to get popular Solana pairs
            token_addresses = [token.address for token in all_tokens]
            addresses_str = ",".join(token_addresses)
            # print(f"Fetching pairs data for {addresses_str[:10000]}")
            url = f"https://api.dexscreener.com/tokens/v1/solana/{addresses_str[:10000]}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"Response")
                data = response.json()
                # print(data[:1000])
                # pairs = data.get('pairs', [])
                
                # Filter for quality pairs only
                quality_pairs = [
                    p for p in data 
                    if (p.get('chainId') == 'solana' and 
                        float(p.get('volume', {}).get('h24', 0)) > 500)  # $5k minimum
                ]
                print(f'fetched successfully {len(data)}')
                
                return quality_pairs
            
            return []
            
        except Exception as e:
            print(f"Error fetching pairs: {e}")
            return []

def main():
    jupiter_client = JupiterAPIClient()
    file_info = jupiter_client.get_file_info()
    if not file_info["exists"]:
        print("Token file not found!")
        print("Please run: python scripts/download_tokens.py")
        return {}
    
    print(f"📊 Token file: {file_info['token_count']} tokens, "
            f"{file_info['size_mb']:.1f}MB")
    
    # Step 1: Load tokens from file
    print("📋 Step 1: Loading tokens from file...")
    all_tokens = jupiter_client.fetch_token_list()
    
    if not all_tokens:
        print("No tokens loaded! Please check your token file.")
        return {}
    optimizer = TrulyOptimizedVolumeFetcher()
    optimizer._fetch_pairs_data(all_tokens)
    # enriched_tokens = optimizer.get_top_volume_tokens(all_tokens)
    # print("\nSample tokens:")
    # for i, token in enumerate(enriched_tokens[:5]):
    #     print(f"   {i+1}. {token.symbol} - {token.name}, {token.volume_24h}")
    
if __name__ == "__main__":
    main()