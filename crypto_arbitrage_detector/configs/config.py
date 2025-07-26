# config.py
JUPITER_CONFIG = {
    'TOKEN_LIST_URL': 'https://cache.jup.ag/tokens',
    'QUOTE_API_URL': 'https://quote-api.jup.ag/v6/quote',
    'RATE_LIMIT': {
        'requests_per_second': 300,  
        'burst_limit': 50,
        'cooldown_period': 60
    },
    'QUOTE_PARAMS': {
        'amount': 1000000,  # 1 token in lamports (6 decimals)
        'slippageBps': 50,  # 0.5% slippage
        'onlyDirectRoutes': False,
        'asLegacyTransaction': False
    }
}