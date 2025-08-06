"""
This script is used to load the token objects from the saved pickle file.
"""
import pickle
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import List
from datetime import datetime, timedelta
from crypto_arbitrage_detector.utils.data_structures import TokenInfo

class TokenLoader:
    def __init__(self, filename: str = "data/enriched_tokens.pkl"):
        self.filename = filename
        self.tokens_cache = []
    
    def load_tokens(self, filename="data/enriched_tokens.pkl", max_age_hours: int = 24) -> List[TokenInfo]:
        """
        Load tokens from a pickle file
        Args:
            filename (str): The name of the pickle file
            max_age_hours (int): The maximum age of the token file in hours
        Returns:
            List[TokenInfo]: A list of TokenInfo objects
        """
        if not self._is_token_pickle_file_fresh(filename, max_age_hours):
            print("Token file is missing or outdated.")
            print("Run: python src/volume_fetcher.py")
            return []
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
   
    def _is_token_pickle_file_fresh(self, filename: str, max_age_hours: int) -> bool:
        """
        Check if token pickle file exists and is recent enough
        Args:
            filename (str): The name of the pickle file
            max_age_hours (int): The maximum age of the token file in hours
        Returns:
            bool: True if the token file is fresh, False otherwise
        """
        if not os.path.exists(filename):
            return False
        
        try:
            # Check file modification time
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filename))
            max_age = timedelta(hours=max_age_hours)
            print(f"File modification time: {file_mtime}")
            print(f"Is fresh: {datetime.now() - file_mtime < max_age}")
            return datetime.now() - file_mtime < max_age
            
        except:
            return False
def main():
    loaded_tokens = TokenLoader().load_tokens(filename="data/enriched_tokens.pkl")
    if loaded_tokens is not None:
        for winner in loaded_tokens:
            print(f" {winner.volume_rank:2d}. {winner.symbol:10s} -{winner.creation_date} - ${winner.volume_24h:>12,.0f}")

if __name__ == "__main__":
    main()