import asyncio
import json
import os
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from crypto_arbitrage_detector.utils.data_structures import TokenInfo

class JupiterAPIClient:
    def __init__(self, token_file_path: str = "data/jupiter_tokens.json"):
        self.token_file_path = token_file_path
        self.tokens_cache = []
    
    def fetch_token_list(self, max_age_hours: int = 24) -> List[TokenInfo]:
        """Load token list from local JSON file with freshness check"""
        
        # Check if file exists and is fresh
        if not self._is_token_file_fresh(max_age_hours):
            print("Token file is missing or outdated.")
            print("Run: python scripts/download_tokens.py")
            return []
        
        try:
            with open(self.token_file_path, 'r', encoding='utf-8') as file:
                file_data = json.load(file)
            
            # Handle different file formats
            # if isinstance(file_data, list):
            #     # Old format: direct token list
            #     tokens_data = file_data
            #     metadata = None
            # else:
                # New format: with metadata
                tokens_data = file_data.get('tokens', [])
                metadata = file_data.get('metadata', {})
            
            tokens = self._process_token_list(tokens_data)
            
            if metadata:
                print(f"Loaded {len(tokens)} tokens from file")
                print(f"Downloaded: {metadata.get('downloaded_at', 'Unknown')}")
            else:
                print(f"Loaded {len(tokens)} tokens from file")
            
            return tokens
            
        except Exception as e:
            print(f"Error loading token file: {e}")
            return []
    
    def _is_token_file_fresh(self, max_age_hours: int) -> bool:
        """Check if token file exists and is recent enough"""
        if not os.path.exists(self.token_file_path):
            return False
        
        try:
            # Check file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(self.token_file_path))
            max_age = timedelta(hours=max_age_hours)
            
            return datetime.now() - file_mtime < max_age
            
        except:
            return False
    
    def _process_token_list(self, data: List[dict]) -> List[TokenInfo]:
        """Process token list data into TokenInfo objects"""
        tokens = []
        skipped = 0
        
        for token_data in data:
            try:
                # Validate required fields
                required_fields = ['address', 'symbol', 'name', 'decimals']
                if not all(field in token_data for field in required_fields):
                    skipped += 1
                    continue
                
                # Basic quality filters
                if (len(token_data['symbol']) < 1 or 
                    len(token_data['symbol']) > 20 or
                    token_data['decimals'] > 15):
                    skipped += 1
                    continue
                
                token = TokenInfo(
                    address=token_data['address'],
                    symbol=token_data['symbol'].strip(),
                    name=token_data['name'].strip(),
                    decimals=int(token_data['decimals']),
                    logoURI=token_data.get('logoURI', ''),
                    tags=token_data.get('tags', [])
                )
                tokens.append(token)
                
            except (KeyError, ValueError, TypeError):
                skipped += 1
                continue
        
        if skipped > 0:
            print(f"Skipped {skipped} invalid tokens")
        
        return tokens
    
    def get_file_info(self) -> Dict:
        """Get information about the token file"""
        if not os.path.exists(self.token_file_path):
            return {"exists": False}
        
        try:
            stat = os.stat(self.token_file_path)
            
            with open(self.token_file_path, 'r') as file:
                data = json.load(file)
            
            if isinstance(data, list):
                token_count = len(data)
                metadata = None
            else:
                token_count = len(data.get('tokens', []))
                metadata = data.get('metadata', {})
            
            return {
                "exists": True,
                "size_mb": stat.st_size / 1024 / 1024,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "token_count": token_count,
                "metadata": metadata
            }
            
        except Exception as e:
            return {"exists": True, "error": str(e)}

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
    
    print("\nSample tokens:")
    for i, token in enumerate(all_tokens[:5]):
        print(f"   {i+1}. {token.symbol} - {token.name}")

if __name__ == "__main__":
    main()