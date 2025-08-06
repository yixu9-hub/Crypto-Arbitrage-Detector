import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto_arbitrage_detector.scripts.token_loader import TokenLoader

def main():
    loaded_tokens = TokenLoader().load_tokens(filename="data/enriched_tokens.pkl")
    if loaded_tokens is not None:
        for winner in loaded_tokens:
            print(f" {winner.volume_rank:2d}. {winner.symbol:10s} -{winner.creation_date} - ${winner.volume_24h:>12,.0f}")

if __name__ == "__main__":
    main()