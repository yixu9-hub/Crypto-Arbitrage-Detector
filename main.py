"""
# main.py
# This is a console application for Solana Arbitrage Detector.
"""
import asyncio
from crypto_arbitrage_detector.configs.request_config import jupiter_quote_api, jupiter_swap_api, solana_rpc_api
from crypto_arbitrage_detector.scripts.download_tokens import TokenDownloader
from crypto_arbitrage_detector.scripts.volume_fetcher import MassVolumeRanker
from crypto_arbitrage_detector.utils.graph_structure import build_graph_from_edge_lists
from crypto_arbitrage_detector.algorithms.arbitrage_detector_integrated import IntegratedArbitrageDetector
from crypto_arbitrage_detector.utils.graph_utils import analyze_graph
from crypto_arbitrage_detector.utils.transaction import execute_path
from crypto_arbitrage_detector.utils.get_quote_pair import get_edge_pairs
from crypto_arbitrage_detector.scripts.jupiter_client import JupiterAPIClient
from data.historical_data import new_arbitrage_test_data

def get_user_input(prompt, default=None, is_float=False):
    """
    Get user input with a prompt, allowing for a default value.
    If the user presses Enter without typing anything, the default value is returned.
    If is_float is True, the input will be converted to float.
    """
    user_input = input(f"{prompt} [{'default: ' + str(default) if default is not None else 'required'}]: ")
    if not user_input:
        return default
    return float(user_input) if is_float else user_input

async def handle_option_1():
    """
    Handle the first option: update token list.
    This will download the latest token data and save it to the database.
    """
    downloader = TokenDownloader()
    success = downloader.download_and_save_tokens()
    print("\nToken download completed successfully!" if success else "\nToken download failed!")

async def handle_option_2():
    """
    Handle the second option: view historical arbitrage data.
    This will load the historical arbitrage data and allow the user to analyze it.
    """
    threshold = get_user_input("Enter minimum profit threshold (e.g., 0.005)", 0.005, is_float=True)
    risk_input = input("Enable risk evaluation? (y/n) [default: y]: ").strip().lower()
    base_amount = get_user_input("Enter base token amount for simulation (e.g., 10)", 10, is_float=True)
    risk_eval = risk_input != "n"
    graph = build_graph_from_edge_lists(new_arbitrage_test_data)
    detector = IntegratedArbitrageDetector(min_profit_threshold=threshold, base_amount=base_amount, enable_risk_evaluation=risk_eval)
    opportunities = detector.detect_arbitrage(graph, source_token="any_token", enable_bellman_ford=True,
                                              enable_triangle=True, enable_two_hop=True, enable_exhaustive_dfs=True)
    print(f"Total opportunities found: {len(opportunities)}")
    detector.print_opportunities(opportunities, max_display=len(opportunities))
    analyze_graph(graph, show_visualization=True, show_statistics=True, show_edge_summary=False)
    if opportunities:
        while True:
            choice = input("Would you like to execute a trade? (y/n): ").strip().lower()
            if choice == "y":
                print("⚠️ WARNING: make sure you have sufficient balance for transaction fees.")
                print("⚠️ WARNING: Arbitrage requires speed—insufficient token balance at any hop may lead to transaction failure.")
                idx = int(input(f"Which opportunity to trade? (1 to {len(opportunities)}): "))
                if idx < 1 or idx > len(opportunities):
                    print("❌ Invalid opportunity index.")
                    continue
                amount = get_user_input("Enter starting token amount: ", 0.001, is_float=True)
                user_pubkey = input("Enter user public key: ").strip()
                user_privkey = input("Enter user private key (base58): ").strip()
                await execute_path(opportunities[idx-1], amount, user_pubkey, user_privkey)
                break
            if choice == "n":
                print("No trade executed. Exiting...")
                break
            else:
                print("❌ Invalid input. Please enter 'y' or 'n'.")


async def handle_option_3():
    """
    Handle the third option: view real-time data and trade.
    This will fetch the top volume tokens, get edge pairs,
    and allow the user to execute trades based on arbitrage opportunities.
    """
    print("Step 1: Loading all Jupiter tokens...")
    jupiter_client = JupiterAPIClient()
    all_tokens = jupiter_client.fetch_token_list()
    print(f"Loaded {len(all_tokens):,} tokens")
    print("Step 2: Getting top volume tokens...")
    volume_ranker = MassVolumeRanker()
    selected_tokens = await volume_ranker.get_top_tokens_optimized(
        all_tokens[:1000], 10
    )

    for winner in selected_tokens:
        print(f" {winner.volume_rank:2d}. {winner.symbol:10s} - {winner.creation_date} - ${winner.volume_24h:>12,.0f}")

    threshold = get_user_input("Enter minimum profit threshold (e.g., 0.005)", 0.005, is_float=True)
    risk_input = input("Enable risk evaluation? (y/n) [default: y]: ").strip().lower()
    risk_eval = risk_input != "n"
    base_amount = get_user_input("Enter base token amount for simulation (e.g., 10)", 10, is_float=True)

    print("⚠️ WARNING: Jupiter is a paid API. Free requests may be unreliable or rate-limited.")
    print("You can either proceed with free requests (not guaranteed to work), or provide your own Jupiter Quote & Swap API endpoints and optional API key.")
    use_free = input("Do you want to proceed with free requests? (y/n) [default: y]: ").strip().lower()
    if use_free == "n":
        quote_url = input("Enter Jupiter Quote API URL (e.g., https://quote-api.jup.ag/v6/quote): ").strip()
        swap_url = input("Enter Jupiter Swap API URL (e.g., https://quote-api.jup.ag/v6/swap): ").strip()
        api_key = input("Enter your Jupiter API Key (if you have one): ").strip()
        print("✅ Custom Jupiter API configuration set.\n")
    else:
        quote_url = jupiter_quote_api["base_url"]
        swap_url = jupiter_swap_api["base_url"]
        api_key = jupiter_quote_api["api_key"]
        print("✅ Proceeding with public (free) Jupiter API. Responses may not be reliable.\n")

    print("Do you want to use the default Solana RPC URL? (y/n) [default: y]")
    rpc_input = input().strip().lower()
    if rpc_input == "n":
        rpc_url = input("Enter your Solana RPC URL: ").strip()
    else:
        rpc_url = solana_rpc_api["base_url"]

    print("\nFetching edge pairs...")
    try:
        edges = await get_edge_pairs(
            selected_tokens, 
            base_amount, 
            api_key=api_key, 
            quote_url=quote_url, 
            swap_url=swap_url, 
            solana_rpc=rpc_url
        )
    except Exception as e:
        pass
    print(f"✅ Total edge pairs returned: {len(edges)}\n")

    graph = build_graph_from_edge_lists(edges)
    detector = IntegratedArbitrageDetector(min_profit_threshold=threshold, base_amount=base_amount, enable_risk_evaluation=risk_eval)
    opportunities = detector.detect_arbitrage(graph, source_token="any_token_ignored",
                                              enable_bellman_ford=True, enable_triangle=True,
                                              enable_two_hop=True, enable_exhaustive_dfs=True)
    detector.print_opportunities(opportunities, max_display=len(opportunities))
    analyze_graph(graph, show_visualization=True, show_statistics=True, show_edge_summary=False)
    if opportunities:
        while True:
            choice = input("Would you like to execute a trade? (y/n): ").strip().lower()
            if choice == "y":
                print("⚠️ WARNING: make sure you have sufficient balance for transaction fees.")
                print("⚠️ WARNING: Arbitrage requires speed—insufficient token balance at any hop may lead to transaction failure.")
                idx = int(input(f"Which opportunity to trade? (1 to {len(opportunities)}): "))
                if idx < 1 or idx > len(opportunities):
                    print("❌ Invalid opportunity index.")
                    continue
                amount = get_user_input("Enter starting token amount: ", 0.001, is_float=True)
                user_pubkey = input("Enter user public key: ").strip()
                user_privkey = input("Enter user private key (base58): ").strip()
                await execute_path(opportunities[idx-1], amount, user_pubkey, user_privkey)
                break
            if choice == "n":
                print("No trade executed. Exiting...")
                break
            else:
                print("❌ Invalid input. Please enter 'y' or 'n'.")


def main():
    """
    Main function to run the console application.
    It provides a simple text-based menu for the user to interact with.
    """
    while True:
        print("\nWelcome to Solana Arbitrage Console")
        print("1) Update token list")
        print("2) View historical arbitrage")
        print("3) View real-time data and trade")
        print("q) Quit")

        choice = input("Please choose an option: ").strip().lower()

        if choice == "1":
            asyncio.run(handle_option_1())
        elif choice == "2":
            asyncio.run(handle_option_2())
        elif choice == "3":
            asyncio.run(handle_option_3())
        elif choice in ("q", "quit"):
            print("Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
