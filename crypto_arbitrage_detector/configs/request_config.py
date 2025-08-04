# Dexscreener API request configuration for volume_fetcher
dexscreener_api = {
    "base_url": "https://api.dexscreener.com/tokens/v1/solana",
    "batch_size": 30,  # Maximum number of tokens per request
    "max_concurrent_requests": 25,  # Maximum concurrent requests
    "request_delay": 0.05  # Delay between requests in seconds
}

# Token ranking configuration for volume_fetcher
token_ranking = {
    "top_n": 10,
    "sort_by": "volume"
}

# Jupiter API configuration for download_tokens and jupiter_client
jupiter_tokens_api = {
    "base_url": 'https://cache.jup.ag/tokens',
    "output_file": 'data/jupiter_tokens.json',
    "timeout": 30,  # Timeout for downloading tokens
    "max_age_hours": 24  # Maximum age of token file before refresh
}


# Jupiter quote API configuration for get_quote_pair
jupiter_quote_api = {
    "base_url": "https://quote-api.jup.ag/v6/quote",
    "default_slippage_bps": 100,             # 1% slippage
    "default_tx_amount": 10000,          # 10000 units of input token
    "sol_mint": "So11111111111111111111111111111111111111112",
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.133 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-CA,en;q=0.9",
        "Origin": "https://jup.ag",
        "Referer": "https://jup.ag/",
        "Connection": "keep-alive"
    },
    "api_key": ""  # quote key
}

# Jupiter swap API configuration for simulate_gas_fee and enrich_gas_fee
jupiter_swap_api = {
    "base_url": "https://quote-api.jup.ag/v6/swap",
    "headers": {"Content-Type": "application/json"},
    "user_pubkey": "2ZwR1odHjrohqrTma9us4cHfGQcbCkVSnkJZo1MeDPU1",
    "max_request": 40,  # Maximum concurrent requests
    "api_key": ""  # swap key
}

# Solana RPC API configuration for simulate_gas_fee and enrich_gas_fee
solana_rpc_api = {
    "base_url": "https://api.mainnet-beta.solana.com",
    "headers": {"Content-Type": "application/json"},
    "unit_price": 0.005,  # Price per compute unit in lamports
    #0.000001 – 0.0001 lamports	Too low — may be dropped during network congestion due to low priority.
    #0.001 – 0.002 lamports	Common range (used by Jupiter) — good balance between cost and success rate.
    #0.005 – 0.01+ lamports	High priority — helps secure faster execution or better liquidity, but with significantly higher fees.
    "base_fee": 5000,  # Base fee in lamports
    "fallback_units": 25000,  # Fallback units for gas simulation
    "fallback_fee": 8000  # Fallback fee in lamports if simulation fails
}


# Scraper proxy configuration for get_quote_pair, please ensure to replace with your actual API key
scraper_config = {
    "api_key": "962b799f81dbe3b72467b62db9474331",
    "proxy_url": "http://scraperapi:962b799f81dbe3b72467b62db9474331@proxy-server.scraperapi.com:8001"
}