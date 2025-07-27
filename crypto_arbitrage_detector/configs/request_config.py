# Dexscreener API request configuration
dexscreener_api = {
    "base_url": "https://api.dexscreener.com/tokens/v1/solana",
    "batch_size": 30,  # Maximum number of tokens per request
    "max_concurrent_requests": 25,  # Maximum concurrent requests
    "request_delay": 0.05  # Delay between requests in seconds
}

token_ranking = {
    "top_n": 10,
    "sort_by": "volume"
}

jupiter_tokens_api = {
    "base_url": 'https://cache.jup.ag/tokens',
    "output_file": 'data/jupiter_tokens.json',
    "timeout": 30  # Timeout for downloading tokens
}




# Default configuration for jupiter quote API requests
DEFAULT_SLIPPAGE_BPS = 100  # Default slippage in basis points (1% slippage)
DEFAULT_TX_AMOUNT = 1000000  # Default transaction amount in lamports (1 SOL = 1,000,000 lamports)
SOL_MINT = "So11111111111111111111111111111111111111112"  # Default SOL mint

# Scraper configuration for scraping data from jupiter quote API
SCRAPER_API_KEY = "962b799f81dbe3b72467b62db9474331"
PROXY_URL = f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"