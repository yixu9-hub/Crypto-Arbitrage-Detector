'''
Two-Hop Arbitrage Detection Algorithm
'''
import networkx as nx
import math
from typing import List, Optional
from utils.data_structures import ArbitrageOpportunity


class TwoHopArbitrage:
    """Two-hop arbitrage detection algorithm"""

    def __init__(self,
                 min_profit_threshold: float = 0.01,
                 max_hops: int = 4,
                 base_amount: float = 1.0):
        """
        Initialize algorithm

        Args:
            min_profit_threshold: Minimum profit threshold (0.01 = 1%)
            max_hops: Maximum allowed hops
            base_amount: Base trading amount (SOL)
        """
        self.min_profit_threshold = min_profit_threshold
        self.max_hops = max_hops
        self.base_amount = base_amount
        self.algorithm_name = "TwoHopArbitrage"

    def detect_opportunities(self, graph: nx.DiGraph, source_token: str = None) -> List[ArbitrageOpportunity]:
        """Detect two-hop arbitrage opportunities"""
        opportunities = []

        print(f"[{self.algorithm_name}] Searching for two-hop arbitrage paths...")

        # Find two-hop pattern: A -> B -> A
        for node_a in graph.nodes():
            for node_b in graph.successors(node_a):
                if node_b != node_a and graph.has_edge(node_b, node_a):
                    # Two-hop path: A -> B -> A
                    path = [node_a, node_b, node_a]

                    opportunity = self._create_arbitrage_opportunity(
                        graph, path)
                    if opportunity:
                        opportunities.append(opportunity)

        filtered_opportunities = self._filter_profitable_opportunities(
            opportunities)
        print(
            f"[{self.algorithm_name}] Found {len(filtered_opportunities)} two-hop arbitrage opportunities")

        return filtered_opportunities

    def _create_arbitrage_opportunity(self, graph: nx.DiGraph, path: List[str]) -> Optional[ArbitrageOpportunity]:
        """
        Create arbitrage opportunity object from path
        Considers slippage and trading platform fees
        """
        try:
            if len(path) < 2:
                return None

            # Calculate total path weight, fees, slippage, and price impact
            total_weight = 0.0
            total_fee = 0.0
            total_slippage = 0.0
            total_price_impact = 0.0
            platform_fees = 0.0

            for i in range(len(path) - 1):
                from_token = path[i]
                to_token = path[i + 1]

                if not graph.has_edge(from_token, to_token):
                    return None  # Invalid path

                edge_data = graph[from_token][to_token]
                weight = edge_data.get('weight', 0)
                fee = edge_data.get('total_fee', 0)

                slippage_bps = edge_data.get('slippage_bps', 0)  # basis points
                platform_fee = edge_data.get('platform_fee', 0)
                price_impact_pct = edge_data.get('price_impact_pct', 0)

                slippage_decimal = slippage_bps / 10000.0

                # Accumulate fees and impacts
                total_weight += weight
                total_fee += fee
                total_slippage += slippage_decimal
                # Price impact is usually negative
                total_price_impact += abs(price_impact_pct)
                platform_fees += platform_fee

            # Adjust weight considering slippage and price impact
            # Slippage and price impact reduce actual returns
            adjusted_weight = total_weight + \
                total_slippage + (total_price_impact / 100.0)

            # Calculate profit ratio (negative weight indicates arbitrage opportunity)
            # Use adjusted weight for profit calculation
            if adjusted_weight >= 0:
                return None  # No arbitrage opportunity after considering slippage

            base_profit_ratio = math.exp(-adjusted_weight) - 1

            total_all_fees = total_fee + platform_fees

            actual_profit_ratio = base_profit_ratio - \
                (total_all_fees / self.base_amount)

            # Estimated profit (SOL) - actual profit after deducting all fees
            estimated_profit = self.base_amount * actual_profit_ratio

            # Risk adjustment: reduce confidence if slippage or price impact is too high
            # Slippage risk factor
            slippage_risk = min(1.0, total_slippage * 10)
            # Price impact risk factor
            price_impact_risk = min(1.0, total_price_impact / 10)

            # Confidence score calculation (considering profit, fee ratio and market risk)
            if total_all_fees > 0:
                profit_fee_ratio = max(0, estimated_profit / total_all_fees)
                # Profit to fee ratio
                base_confidence = min(1.0, profit_fee_ratio / 5)
            else:
                base_confidence = 0.5

            # Risk-adjusted confidence
            confidence_score = base_confidence * \
                (1 - slippage_risk) * (1 - price_impact_risk)
            confidence_score = max(0.0, min(1.0, confidence_score))

            # Generate path symbols (for display)
            path_symbols = [f"{addr[:4]}...{addr[-4:]}" for addr in path]

            return ArbitrageOpportunity(
                path=path,
                path_symbols=path_symbols,
                profit_ratio=actual_profit_ratio,
                total_weight=adjusted_weight,  # Use adjusted weight
                total_fee=total_all_fees,  # Include all fees
                hop_count=len(path) - 1,
                confidence_score=confidence_score,
                estimated_profit_sol=estimated_profit
            )

        except Exception as e:
            print(
                f"Failed to create arbitrage opportunity [{self.algorithm_name}]: {e}")
            return None

    def _filter_profitable_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> List[ArbitrageOpportunity]:
        """
        Filter opportunities that meet profit threshold
        """
        filtered = [opp for opp in opportunities
                    if opp and opp.profit_ratio >= self.min_profit_threshold]
        return filtered
