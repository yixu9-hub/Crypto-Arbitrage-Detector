#!/usr/bin/env python3
"""
Download the latest Jupiter token list and save it to data/jupiter_tokens.json
This script should be run weekly to keep the token list fresh.
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List

def download_jupiter_tokens() -> Dict:
    """Download the latest token list from Jupiter API"""
    
    url = "https://cache.jup.ag/tokens"
    
    try:
        print("🔄 Downloading latest Jupiter token list...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        tokens = response.json()
        print(f"✅ Downloaded {len(tokens)} tokens from Jupiter")
        
        return tokens
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading tokens: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        return []

def save_tokens_with_metadata(tokens: List[Dict], filename: str = "data/jupiter_tokens.json"):
    """Save tokens with metadata including download timestamp"""
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Create data structure with metadata
    data = {
        "tokens": tokens,
        "metadata": {
            "downloaded_at": datetime.now().isoformat(),
            "source": "https://cache.jup.ag/tokens",
            "total_tokens": len(tokens),
            "description": "Jupiter token list with basic token information"
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Token list saved to {filename}")
        print(f"📊 Total tokens: {len(tokens)}")
        print(f"🕒 Downloaded at: {data['metadata']['downloaded_at']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")
        return False

def main():
    """Main function to download and save Jupiter tokens"""
    
    print("🚀 Jupiter Token Downloader")
    print("=" * 40)
    
    # Download tokens
    tokens = download_jupiter_tokens()
    
    if not tokens:
        print("❌ Failed to download tokens. Exiting.")
        return False
    
    # Save tokens with metadata
    success = save_tokens_with_metadata(tokens)
    
    if success:
        print("\n✅ Token download completed successfully!")
        print("💡 This file will be refreshed weekly (7 days)")
        return True
    else:
        print("\n❌ Token download failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)