import requests
import json
import os
from datetime import datetime

class TokenDownloader:
    def __init__(self):
        self.jupiter_url = 'https://cache.jup.ag/tokens'
        self.output_file = 'data/jupiter_tokens.json'
        
    def download_and_save_tokens(self):
        """Download tokens from Jupiter API and save to JSON file"""
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        print("Downloading token list from Jupiter API...")

        try:
            # Make HTTP request
            response = requests.get(self.jupiter_url, timeout=30)
            
            if response.status_code == 200:
                tokens_data = response.json()
                
                # Add metadata
                metadata = {
                    "downloaded_at": datetime.now().isoformat(),
                    "source": self.jupiter_url,
                    "total_tokens": len(tokens_data)
                }
                
                # Save to file
                output_data = {
                    "metadata": metadata,
                    "tokens": tokens_data
                }
                
                with open(self.output_file, 'w', encoding='utf-8') as file:
                    json.dump(output_data, file, indent=2, ensure_ascii=False)
    
                        
                    print(f"Successfully saved {len(tokens_data)} tokens to {self.output_file}")
                    print(f"File size: {os.path.getsize(self.output_file) / 1024 / 1024:.2f} MB")
                    
                    # Show sample tokens
                    print("\nSample tokens:")
                    for i, token in enumerate(tokens_data[:5]):
                        print(f"   {i+1}. {token['symbol']} - {token['name']}")
                    
                    return True
                    
            else:
                print(f"Error downloading tokens: HTTP {response.status}")
                return False
                
        except Exception as e:
            print(f"Error downloading tokens: {e}")
            return False

def main():
    downloader = TokenDownloader()
    success = downloader.download_and_save_tokens()
    
    if success:
        print("\nToken download completed successfully!")
    else:
        print("\nToken download failed!")

if __name__ == "__main__":
    main()