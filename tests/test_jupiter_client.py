import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_arbitrage_detector.scripts.jupiter_client import JupiterAPIClient


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