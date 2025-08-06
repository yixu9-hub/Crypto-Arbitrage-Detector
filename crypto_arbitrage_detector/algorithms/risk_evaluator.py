"""
Risk Evaluator for Arbitrage Opportunities
This module evaluates the risk of arbitrage opportunities based on factors:
- Slippage risk
- Gas fee
- Transaction complexity (hop count)
"""

import math
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Dict, Optional
from crypto_arbitrage_detector.utils.data_structures import ArbitrageOpportunity
from crypto_arbitrage_detector.configs.strategy_config import get_risk_config


class ArbitrageRiskEvaluator:
    """
    Simple risk evaluator for arbitrage opportunities
    Focuses on practical risk factors: gas costs, slippage, and market impact
    """

    def __init__(self,
                 max_acceptable_slippage: float = None,
                 max_gas_cost_ratio: float = None,
                 min_confidence_threshold: float = None):
        """
        Initialize risk evaluator

        Args:
            max_acceptable_slippage: Maximum acceptable total slippage percentage
            max_gas_cost_ratio: Maximum gas cost as ratio of expected profit
            min_confidence_threshold: Minimum confidence score to consider 
        """
        # Get risk configuration
        risk_config = get_risk_config()
        
        # Set parameters from config
        self.max_acceptable_slippage = risk_config["max_acceptable_slippage"]
        self.max_gas_cost_ratio = risk_config["max_gas_cost_ratio"]
        self.min_confidence_threshold = risk_config["min_confidence_threshold"]
        
        # Risk thresholds for categorization and recommendations
        self.low_risk_threshold = risk_config["low_risk_threshold"]
        self.medium_risk_threshold = risk_config["medium_risk_threshold"]
        self.min_profit_threshold = risk_config["min_profit_threshold"]
        
        # Risk weights and default estimates
        self.risk_weights = risk_config["risk_weights"]
        self.default_gas_per_hop = risk_config["default_gas_per_hop"]
        self.default_slippage_per_hop = risk_config["default_slippage_per_hop"]
        
        # # Override with provided parameters if not None for direct control
        # if max_acceptable_slippage is not None:
        #     self.max_acceptable_slippage = max_acceptable_slippage
        # if max_gas_cost_ratio is not None:
        #     self.max_gas_cost_ratio = max_gas_cost_ratio
        # if min_confidence_threshold is not None:
        #     self.min_confidence_threshold = min_confidence_threshold

    def evaluate_opportunity(self, opportunity: ArbitrageOpportunity,
                             edge_data_list: List[Dict] = None) -> Dict:
        """
        Evaluate risk for a single arbitrage opportunity

        Args:
            opportunity: Arbitrage opportunity to evaluate
            edge_data_list: Optional list of edge data for cost calculation

        Returns:
            Dict: Risk evaluation results with scores and recommendations
        """
        if not opportunity:
            return self._create_rejection_result("Invalid opportunity")

        # Calculate execution costs
        cost_analysis = self._calculate_execution_costs(
            opportunity, edge_data_list)

        # Assess various risk factors
        slippage_risk = self._assess_slippage_risk(
            cost_analysis['total_slippage'])
        gas_risk = self._assess_gas_cost_risk(cost_analysis['gas_cost_ratio'])
        complexity_risk = self._assess_complexity_risk(opportunity.hop_count)

        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(
            slippage_risk, gas_risk, complexity_risk)

        # Determine recommendation
        recommendation = self._determine_recommendation(
            overall_risk, opportunity)

        return {
            # unique ID for the opportunity：address1-address2...lastAddr8
            'opportunity_id': f"{'-'.join(opportunity.path[:2])}...{opportunity.path[-1][:8]}",
            'profit_percentage': opportunity.profit_ratio * 100,
            'estimated_profit_sol': opportunity.estimated_profit_sol,
            'risk_score': overall_risk,
            'slippage_risk': slippage_risk,
            'gas_risk': gas_risk,
            'complexity_risk': complexity_risk,
            'total_slippage_pct': cost_analysis['total_slippage'] * 100,
            'gas_cost_sol': cost_analysis['total_gas_cost'],
            'gas_cost_ratio': cost_analysis['gas_cost_ratio'],
            'recommendation': recommendation,
            'risk_level': self._categorize_risk_level(overall_risk)
        }

    def _calculate_execution_costs(self, opportunity: ArbitrageOpportunity,
                                   edge_data_list: List[Dict] = None) -> Dict:
        """
        Calculate estimated execution costs based on available data
        """
        if edge_data_list and len(edge_data_list) > 0:
            # Use actual edge data when available
            total_gas_cost = sum(edge.get('gas_fee', 5000)
                                 for edge in edge_data_list) * 1e-9
            total_slippage = sum(edge.get('slippage_bps', 100)
                                 for edge in edge_data_list) / 10000.0
        else:
            # if no edge data, use default estimates from config
            total_gas_cost = opportunity.hop_count * self.default_gas_per_hop
            total_slippage = opportunity.hop_count * self.default_slippage_per_hop

        # Calculate gas cost as ratio of expected profit
        expected_profit = max(opportunity.estimated_profit_sol, 0.001)
        gas_cost_ratio = total_gas_cost / expected_profit

        return {
            'total_gas_cost': total_gas_cost,
            'total_slippage': total_slippage,
            'gas_cost_ratio': gas_cost_ratio
        }

    def _assess_slippage_risk(self, total_slippage: float) -> float:
        """
        Assess risk based on total expected slippage
        Returns risk score from 0.0 (low risk) to 1.0 (high risk)
        """
        if total_slippage <= 0.005:  # Less than 0.5%
            return 0.1
        elif total_slippage <= 0.01:  # 0.5% - 1%
            return 0.3
        elif total_slippage <= self.max_acceptable_slippage:  # 1% - 2%
            return 0.6
        else:  # Above 2%
            return 1.0

    def _assess_gas_cost_risk(self, gas_cost_ratio: float) -> float:
        """
        Assess risk based on gas cost relative to expected profit
        """
        if gas_cost_ratio <= 0.05:  # Less than 5% of profit
            return 0.1
        elif gas_cost_ratio <= self.max_gas_cost_ratio:  # 5% - 10%
            return 0.4
        elif gas_cost_ratio <= 0.2:  # 10% - 20%
            return 0.7
        else:  # Above 20%
            return 1.0

    def _assess_complexity_risk(self, hop_count: int) -> float:
        """
        Assess risk based on transaction complexity (number of hops)
        """
        if hop_count <= 2:
            return 0.1
        elif hop_count <= 3:
            return 0.3
        elif hop_count <= 4:
            return 0.6
        else:
            return 0.9

    def _calculate_overall_risk(self, slippage_risk: float, gas_risk: float,
                                complexity_risk: float) -> float:
        """
        Calculate weighted overall risk score using configured weights
        """
        overall_risk = (slippage_risk * self.risk_weights['slippage'] +
                        gas_risk * self.risk_weights['gas'] +
                        complexity_risk * self.risk_weights['complexity'])

        return min(1.0, overall_risk)

    def _determine_recommendation(self, overall_risk: float,
                                  opportunity: ArbitrageOpportunity) -> str:
        """
        Determine execution recommendation based on risk assessment
        """
        if overall_risk <= self.low_risk_threshold and opportunity.profit_ratio >= self.min_confidence_threshold:
            return "EXECUTE"  # Low risk and high profit
        elif overall_risk <= self.medium_risk_threshold and opportunity.profit_ratio >= self.min_profit_threshold:
            return "CONSIDER"  # Medium risk and reasonable profit
        else:
            return "AVOID"  # High risk or low profit

    def _categorize_risk_level(self, risk_score: float) -> str:
        """
        Categorize risk level for easy interpretation
        """
        if risk_score <= self.low_risk_threshold:
            return "LOW"
        elif risk_score <= self.medium_risk_threshold:
            return "MEDIUM"
        else:
            return "HIGH"

    def _create_rejection_result(self, reason: str) -> Dict:
        """
        Create result for rejected opportunities
        """
        return {
            'opportunity_id': 'INVALID',
            'profit_percentage': 0.0,
            'estimated_profit_sol': 0.0,
            'risk_score': 1.0,
            'recommendation': "AVOID",
            'risk_level': "HIGH",
            'rejection_reason': reason
        }

    def evaluate_opportunity_batch(self, opportunities: List[ArbitrageOpportunity]) -> List[Dict]:
        """
        Evaluate multiple opportunities and return sorted by risk-adjusted return
        """
        evaluations = []

        for opportunity in opportunities:
            evaluation = self.evaluate_opportunity(opportunity)
            # Calculate risk-adjusted return for sorting
            risk_adjusted_return = evaluation['profit_percentage'] * (
                1 - evaluation['risk_score'])
            evaluation['risk_adjusted_return'] = risk_adjusted_return
            evaluations.append(evaluation)

        # Sort by risk-adjusted return (highest first)
        evaluations.sort(key=lambda x: x['risk_adjusted_return'], reverse=True)

        return evaluations

    def get_execution_summary(self, evaluations: List[Dict]) -> Dict:
        """
        Generate summary statistics for a batch of evaluations
        """
        if not evaluations:
            return {'total': 0, 'executable': 0, 'consideration': 0, 'avoid': 0}
        # Total number of opportunities evaluated
        total = len(evaluations)
        
        # Count opportunities by recommendation type
        executable = 0
        consideration = 0
        avoid = 0
        
        # Sum up risk scores and profit percentages for average calculation
        total_risk_score = 0
        total_profit_percentage = 0
        
        # Process each evaluation to gather statistics
        for evaluation in evaluations:
            recommendation = evaluation['recommendation']  # Determine recommendation type
            # Count by recommendation type
            if recommendation == 'EXECUTE':
                executable += 1
            elif recommendation == 'CONSIDER':
                consideration += 1
            elif recommendation == 'AVOID':
                avoid += 1
            
            # Accumulate for average calculations
            total_risk_score += evaluation['risk_score']
            total_profit_percentage += evaluation['profit_percentage']
        
        # Calculate averages
        avg_risk = total_risk_score / total
        avg_profit = total_profit_percentage / total

        return {
            'total_opportunities': total,
            'executable': executable,
            'consideration': consideration,
            'avoid': avoid,
            'average_risk_score': avg_risk,
            'average_profit_percentage': avg_profit,
            'execution_rate': (executable / total) * 100 if total > 0 else 0
        }
